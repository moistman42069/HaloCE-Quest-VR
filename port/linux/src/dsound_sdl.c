/*
DSOUND_SDL.C

Xbox DirectSound for the Linux build: a software mixer on an SDL3 audio
stream.

The game plays everything through DirectSound streams: 16-bit stereo PCM
(music and other uncompressed sounds) and Xbox ADPCM, mono or stereo, at 22
or 44 kHz. A packet is decoded to 16-bit PCM when the game submits it, since
the sound cache may reuse its memory once the packet completes. The mixer
runs on SDL's audio thread; for every voice it resamples to the output rate
(which is how SetFrequency changes pitch) and applies:
	- the stream volume (millibels),
	- the front left and right mix bin volumes of 2D voices,
	- for 3D voices, DirectSound's inverse distance rolloff between the
	  minimum and maximum distance, an equal power pan from the source's
	  direction in listener space, and the low frequency part of the I3DL2
	  direct path, obstruction and occlusion levels.
Optional I3DL2 room reverb and high-frequency obstruction/occlusion filters
follow OpenCE 8a8e7059 (based on Tyberious #44/#46). Unlike upstream, both
are off when audio.reverb is false, preserving this port's accepted dry mix.
Doppler and cones are not modelled.

Packets the mixer has finished are completed from DirectSoundDoWork, which
the game calls every frame, and from Flush, never from the audio thread:
the game's completion callback is not meant to run concurrently with it.

Without an audio device, a clock thread runs the same mixer into a scratch
buffer, so streams still drain at their real rate.

audio.volume sets the master volume (default 1.0); audio.reverb enables the
room processing (default false); audio.enabled = false
skips opening a device (port_config.c).
*/

#include "platform.h"
#include "sdl_platform.h"
#include "port_config.h"

#include <SDL3/SDL.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define OUTPUT_RATE 48000
#define OUTPUT_CHANNELS 2
#define MAXIMUM_STREAM_PACKETS 64
#define MIX_CHUNK_FRAMES 1024

#define XBOX_ADPCM_BLOCK_BYTES 36
#define XBOX_ADPCM_BLOCK_SAMPLES 65

/* ---------- voices */

struct voice_packet
{
	XMEDIAPACKET packet;
	short *samples;           /* interleaved, source channel count */
	unsigned long frames;
	BOOL finished;            /* played out by the mixer, not yet completed */
};

struct sdl_stream
{
	/* must be first: in C an IDirectSoundStream is just { lpVtbl } */
	IDirectSoundStream object;
	struct sdl_stream *next;
	ULONG reference_count;
	LPFNXMEDIAOBJECTCALLBACK callback;
	LPVOID context;

	/* format */
	BOOL adpcm;
	unsigned long channels;
	DWORD sample_rate;
	DWORD frequency;

	BOOL paused;

	/* 2D gains */
	float volume;             /* SetVolume */
	float mix_left, mix_right;
	float headroom;

	/* 3D */
	BOOL has_3d;
	DWORD mode;
	float position[3];
	float minimum_distance, maximum_distance;
	float i3dl2_gain;
	LONG direct, direct_hf, room, room_hf;
	float room_rolloff_factor;

	struct voice_packet packets[MAXIMUM_STREAM_PACKETS];
	unsigned long packet_head;
	unsigned long packet_count;
	/* position inside the head packet, in source frames */
	double cursor;
	/* the last frame of the previous packet, for interpolating across packets */
	float previous[2];
	BOOL previous_valid;
	/* gains the mixer is ramping from, to avoid clicks */
	float current_left, current_right, current_room;
	float current_direct_lowpass, current_room_lowpass;
	float direct_lowpass[2], room_lowpass;
	BOOL gains_valid;
};

static pthread_mutex_t mixer_lock = PTHREAD_MUTEX_INITIALIZER;
static struct sdl_stream *streams;

/* the listener, in DirectSound's left-handed +y up space */
static struct
{
	float position[3];
	float front[3];
	float top[3];
	float rolloff_factor;
	float distance_factor;
} listener = { { 0, 0, 0 }, { 0, 0, 1 }, { 0, 1, 0 }, 1.0f, 1.0f };

static float master_volume = 1.0f;

/* Published under mixer_lock; DSP buffers are owned only by the mixer. */
static DSI3DL2LISTENER environment =
{
	DSBVOLUME_MIN, 0, 0.0f, 1.49f, 0.83f, -2602, 0.007f, 200, 0.011f, 100.0f, 100.0f, 5000.0f
};
static unsigned long environment_serial;
static BOOL reverb_enabled = FALSE;

/* Menu changes are read on the game thread, never in the audio callback.
The mixer reads master_volume under the same lock. Keep the existing device
lifecycle and gain ramp; enabled/disabled audio still takes effect at startup. */
static void audio_update_volume(void)
{
	static unsigned long read_at = (unsigned long)-1;
	if (read_at != config_changes())
	{
		float volume = (float)config_real("audio.volume");
		BOOL room = config_boolean("audio.reverb");
		read_at = config_changes();
		if (!isfinite(volume)) volume = 1.0f;
		if (volume < 0.0f) volume = 0.0f;
		pthread_mutex_lock(&mixer_lock);
		master_volume = volume;
		reverb_enabled = room;
		pthread_mutex_unlock(&mixer_lock);
	}
}

static float gain_from_millibels(LONG millibels)
{
	if (millibels <= DSBVOLUME_MIN)
		return 0.0f;
	return powf(10.0f, (float)millibels / 2000.0f);
}

static float flush_denormal(float value)
{
	return fabsf(value) < 1.0e-20f ? 0.0f : value;
}

static float frequency_cosine(float frequency)
{
	if (frequency < 20.0f)
		frequency = 20.0f;
	if (frequency > 0.45f * OUTPUT_RATE)
		frequency = 0.45f * OUTPUT_RATE;
	return cosf(2.0f * 3.14159265f * frequency / OUTPUT_RATE);
}

static float lowpass_coefficient(float gain, float cosine)
{
	float a, b;

	if (gain >= 1.0f)
		return 0.0f;
	if (gain < 0.001f)
		gain = 0.001f;
	a = 1.0f - gain * gain;
	b = 1.0f - gain * gain * cosine;
	return (b - sqrtf(b * b - a * a)) / a;
}

/* Finite before any float-to-integer conversion or feedback calculation. */
static float bounded_real(float value, float minimum, float maximum, float fallback)
{
	if (!isfinite(value)) return fallback;
	return value < minimum ? minimum : value > maximum ? maximum : value;
}

static LONG bounded_level(LONG value, LONG minimum, LONG maximum)
{
	return value < minimum ? minimum : value > maximum ? maximum : value;
}

/* ---------- decoding */

static const int ima_index_table[16] =
{
	-1, -1, -1, -1, 2, 4, 6, 8,
	-1, -1, -1, -1, 2, 4, 6, 8,
};

static const int ima_step_table[89] =
{
	7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45,
	50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143, 157, 173, 190, 209, 230,
	253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963,
	1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327,
	3660, 4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442,
	11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794,
	32767,
};

static int ima_expand(int nibble, int *predictor, int *index)
{
	int step = ima_step_table[*index];
	int difference = step >> 3;

	if (nibble & 1) difference += step >> 2;
	if (nibble & 2) difference += step >> 1;
	if (nibble & 4) difference += step;
	if (nibble & 8) difference = -difference;
	*predictor += difference;
	if (*predictor > 32767) *predictor = 32767;
	if (*predictor < -32768) *predictor = -32768;
	*index += ima_index_table[nibble];
	if (*index < 0) *index = 0;
	if (*index > 88) *index = 88;
	return *predictor;
}

/* Xbox ADPCM: per block, a 4-byte header per channel (predictor, step
index), then 4-byte groups of eight nibbles, low nibble first, alternating
between channels. The header's predictor is the block's first sample, the
64 nibbles the 64 after it: 65 samples per channel. (The game's own sounds
say so: a block's header sample follows the last sample of the block before
by an ordinary step between neighbouring samples, never equal to it; read
as 64 samples, one in every 65 was dropped - a buzz under everything, the
pitch 1.5% high.) */
static short *decode_adpcm(const unsigned char *source, unsigned long size, unsigned long channels,
	unsigned long *frame_count)
{
	unsigned long block_bytes = XBOX_ADPCM_BLOCK_BYTES * channels;
	unsigned long blocks = size / block_bytes;
	short *samples = malloc((blocks ? blocks : 1) * XBOX_ADPCM_BLOCK_SAMPLES * channels * sizeof(short));
	unsigned long block, channel;

	if (!samples)
	{
		*frame_count = 0;
		return NULL;
	}
	for (block = 0; block < blocks; block++)
	{
		const unsigned char *data = source + block * block_bytes;
		short *output = samples + block * XBOX_ADPCM_BLOCK_SAMPLES * channels;

		for (channel = 0; channel < channels; channel++)
		{
			const unsigned char *header = data + channel * 4;
			int predictor = (short)(header[0] | (header[1] << 8));
			int index = header[2] > 88 ? 88 : header[2];
			unsigned long group, byte;

			output[channel] = (short)predictor;
			for (group = 0; group < 8; group++)
			{
				const unsigned char *nibbles = data + 4 * channels + (group * channels + channel) * 4;

				for (byte = 0; byte < 4; byte++)
				{
					unsigned long sample = 1 + group * 8 + byte * 2;

					output[sample * channels + channel] = (short)ima_expand(nibbles[byte] & 0xf, &predictor, &index);
					output[(sample + 1) * channels + channel] = (short)ima_expand(nibbles[byte] >> 4, &predictor, &index);
				}
			}
		}
	}
	*frame_count = blocks * XBOX_ADPCM_BLOCK_SAMPLES;
	return samples;
}

static short *decode_pcm(const unsigned char *source, unsigned long size, unsigned long channels,
	unsigned long *frame_count)
{
	unsigned long frames = size / (2 * channels);
	short *samples = malloc((frames ? frames : 1) * channels * sizeof(short));

	if (samples)
		memcpy(samples, source, frames * channels * sizeof(short));
	*frame_count = samples ? frames : 0;
	return samples;
}

/* ---------- 3D */

static float dot3(const float *a, const float *b)
{
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

static void spatialize(const struct sdl_stream *stream, float *left, float *right)
{
	float offset[3], right_axis[3], distance, attenuation, pan, side, ahead;
	int axis;

	if (stream->mode == DS3DMODE_HEADRELATIVE)
	{
		for (axis = 0; axis < 3; axis++)
			offset[axis] = stream->position[axis];
		side = offset[0];
		ahead = offset[2];
	}
	else
	{
		for (axis = 0; axis < 3; axis++)
			offset[axis] = stream->position[axis] - listener.position[axis];
		/* left-handed: right = top x front */
		right_axis[0] = listener.top[1] * listener.front[2] - listener.top[2] * listener.front[1];
		right_axis[1] = listener.top[2] * listener.front[0] - listener.top[0] * listener.front[2];
		right_axis[2] = listener.top[0] * listener.front[1] - listener.top[1] * listener.front[0];
		side = dot3(offset, right_axis);
		ahead = dot3(offset, listener.front);
	}
	distance = sqrtf(dot3(offset, offset)) * listener.distance_factor;

	/* DirectSound's inverse distance law, held beyond the maximum distance */
	attenuation = 1.0f;
	if (distance > stream->minimum_distance && stream->minimum_distance > 0.0f)
	{
		float clamped = distance < stream->maximum_distance ? distance : stream->maximum_distance;

		attenuation = stream->minimum_distance /
			(stream->minimum_distance + listener.rolloff_factor * (clamped - stream->minimum_distance));
	}

	/* equal power pan; close sources and sources straight ahead or behind
	stay centred, and neither ear drops below a quarter */
	{
		float horizontal = sqrtf(side * side + ahead * ahead);
		float angle;

		pan = horizontal > 1.0e-4f ? side / horizontal : 0.0f;
		if (distance < stream->minimum_distance && stream->minimum_distance > 0.0f)
			pan *= distance / stream->minimum_distance;
		pan *= 0.75f;
		angle = (pan + 1.0f) * 0.25f * 3.14159265f;
		*left = cosf(angle) * 1.41421356f * 0.70710678f;
		*right = sinf(angle) * 1.41421356f * 0.70710678f;
	}
	*left *= attenuation * stream->i3dl2_gain;
	*right *= attenuation * stream->i3dl2_gain;
}

static void voice_gains(const struct sdl_stream *stream, float *left, float *right)
{
	if (stream->has_3d && stream->mode != DS3DMODE_DISABLE)
	{
		spatialize(stream, left, right);
	}
	else
	{
		*left = stream->mix_left;
		*right = stream->mix_right;
	}
	*left *= stream->volume * master_volume;
	*right *= stream->volume * master_volume;
}

/* Optional room path; direct gains stay exactly as the accepted dry mixer. */
static void voice_room_gains(const struct sdl_stream *stream, float *room,
	float *direct_lowpass, float *room_lowpass)
{
	float cosine, offset[3], distance, minimum, maximum, rolloff, attenuation = 1.0f;
	LONG level, high_level;
	int axis;

	*room = *direct_lowpass = *room_lowpass = 0.0f;
	if (!reverb_enabled || !stream->has_3d || stream->mode == DS3DMODE_DISABLE)
		return;
	cosine = frequency_cosine(environment.flHFReference);
	if (stream->direct_hf < stream->direct)
		*direct_lowpass = lowpass_coefficient(gain_from_millibels(stream->direct_hf - stream->direct), cosine);
	for (axis = 0; axis < 3; axis++)
		offset[axis] = stream->position[axis] - (stream->mode == DS3DMODE_HEADRELATIVE ? 0.0f : listener.position[axis]);
	/* Room attenuation uses game units, matching upstream I3DL2. Do not alter
	the established dry-distance behavior in this optional feature. */
	distance = sqrtf(dot3(offset, offset));
	minimum = bounded_real(stream->minimum_distance, 0.0f, 1.0e9f, 0.0f);
	maximum = bounded_real(stream->maximum_distance, minimum, 1.0e9f, minimum);
	rolloff = environment.flRoomRolloffFactor + stream->room_rolloff_factor;
	if (!isfinite(distance)) return;
	if (distance > maximum) distance = maximum;
	if (minimum > 0.0f && distance > minimum)
		attenuation = minimum / (minimum + rolloff * (distance - minimum));
	level = environment.lRoom + stream->room;
	high_level = environment.lRoom + environment.lRoomHF + stream->room_hf;
	*room = gain_from_millibels(level) * attenuation * stream->volume;
	if (*room > 0.0f && high_level < level)
		*room_lowpass = lowpass_coefficient(gain_from_millibels(high_level - level), cosine);
}

/* ---------- statistics

Logged every ten seconds from DirectSoundDoWork (the game's main thread),
for finding crackles: how often the device asked for sound and the longest
gap between its asks, how long mixing took, how many voices ran out of
packets inside a mix (a voice ending does too, once; a voice starved by the
main thread does every time), and the longest gap between the main thread's
calls, which complete played packets so the game can queue more. Written
from both threads without a lock: the figures are for reading, not
counting exactly. */

static struct
{
	double started_ms;
	unsigned long callbacks, frames_mixed, ran_dry, dry_frames;
	double last_callback_ms, callback_gap_max_ms, mix_max_ms, mix_total_ms;
	unsigned long work_calls;
	double last_work_ms, work_gap_max_ms;
	unsigned long voices_playing_max;
} audio_statistics;

static double audio_now_ms(void)
{
	struct timespec now;

	clock_gettime(CLOCK_MONOTONIC, &now);
	return (double)now.tv_sec * 1000.0 + (double)now.tv_nsec / 1000000.0;
}

static void audio_statistics_log(void)
{
	double now = audio_now_ms();
	double seconds = (now - audio_statistics.started_ms) / 1000.0;

	if (audio_statistics.started_ms == 0.0)
	{
		audio_statistics.started_ms = now;
		return;
	}
	if (seconds < 10.0)
		return;
	platform_log("[audio] %.1f s: %lu device asks (longest gap %.1f ms), %lu frames mixed (%.0f a second, "
		"want %d), mixing %.2f ms average, %.2f ms longest; %lu voices ran dry in a mix (%lu frames of "
		"silence), %lu voices at most; the game's sound work %lu times, longest gap %.1f ms",
		seconds, audio_statistics.callbacks, audio_statistics.callback_gap_max_ms, audio_statistics.frames_mixed,
		audio_statistics.frames_mixed / seconds, OUTPUT_RATE,
		audio_statistics.callbacks ? audio_statistics.mix_total_ms / audio_statistics.callbacks : 0.0,
		audio_statistics.mix_max_ms, audio_statistics.ran_dry, audio_statistics.dry_frames,
		audio_statistics.voices_playing_max, audio_statistics.work_calls, audio_statistics.work_gap_max_ms);
	memset(&audio_statistics, 0, sizeof(audio_statistics));
	audio_statistics.started_ms = now;
}

/* ---------- mixing */

static float packet_sample(const struct voice_packet *packet, unsigned long frame, unsigned long channel,
	unsigned long channels)
{
	return packet->samples[frame * channels + channel] * (1.0f / 32768.0f);
}

/* frame `frame` (both channels) of the packet `position` places into the
stream's queue, reaching on into the packets after it; past the last one,
its last frame held */
static void voice_frame(const struct sdl_stream *stream, unsigned long position, unsigned long frame,
	float *out_left, float *out_right)
{
	const struct voice_packet *last = NULL;

	for (; position < stream->packet_count; position++)
	{
		const struct voice_packet *packet = &stream->packets[(stream->packet_head + position) % MAXIMUM_STREAM_PACKETS];

		if (frame < packet->frames)
		{
			*out_left = packet_sample(packet, frame, 0, stream->channels);
			*out_right = packet_sample(packet, frame, stream->channels - 1, stream->channels);
			return;
		}
		frame -= packet->frames;
		if (packet->frames)
			last = packet;
	}
	if (last)
	{
		*out_left = packet_sample(last, last->frames - 1, 0, stream->channels);
		*out_right = packet_sample(last, last->frames - 1, stream->channels - 1, stream->channels);
	}
	else
	{
		*out_left = *out_right = 0.0f;
	}
}

/* the curve through four neighbouring samples, `t` of the way from the
second to the third (Catmull-Rom): resampling the game's 22 and 44 kHz
sounds up to the output's 48 with far less of the hiss and ring above their
range that straight lines between samples make */
static float catmull_rom(float p0, float p1, float p2, float p3, float t)
{
	return p1 + 0.5f * t * (p2 - p0 + t * (2.0f * p0 - 5.0f * p1 + 4.0f * p2 - p3 + t * (3.0f * (p1 - p2) + p3 - p0)));
}

/* mixes one voice into output (frames of stereo float) */
static void mix_voice(struct sdl_stream *stream, float *output, float *send, unsigned long frames)
{
	double step;
	float target_left, target_right, left, right, ramp_left, ramp_right;
	float target_room, room, ramp_room, target_direct_lowpass, target_room_lowpass;
	float direct_lowpass, room_lowpass, ramp_direct_lowpass, ramp_room_lowpass;
	unsigned long frame;

	if (stream->paused || !stream->packet_count || !stream->sample_rate)
		return;
	step = (double)(stream->frequency ? stream->frequency : stream->sample_rate) / OUTPUT_RATE;
	voice_gains(stream, &target_left, &target_right);
	voice_room_gains(stream, &target_room, &target_direct_lowpass, &target_room_lowpass);
	if (!stream->gains_valid)
	{
		stream->current_left = target_left;
		stream->current_right = target_right;
		stream->current_room = target_room;
		stream->current_direct_lowpass = target_direct_lowpass;
		stream->current_room_lowpass = target_room_lowpass;
		stream->direct_lowpass[0] = stream->direct_lowpass[1] = stream->room_lowpass = 0.0f;
		stream->gains_valid = TRUE;
	}
	left = stream->current_left;
	right = stream->current_right;
	ramp_left = (target_left - left) / (float)frames;
	ramp_right = (target_right - right) / (float)frames;
	room = stream->current_room;
	direct_lowpass = stream->current_direct_lowpass;
	room_lowpass = stream->current_room_lowpass;
	ramp_room = (target_room - room) / (float)frames;
	ramp_direct_lowpass = (target_direct_lowpass - direct_lowpass) / (float)frames;
	ramp_room_lowpass = (target_room_lowpass - room_lowpass) / (float)frames;

	for (frame = 0; frame < frames; frame++)
	{
		struct voice_packet *packet;
		unsigned long index, position = 0;
		float fraction, sample_left, sample_right;

		/* skip to the first packet that still has frames to play */
		for (;;)
		{
			packet = NULL;
			for (position = 0; position < stream->packet_count; position++)
			{
				struct voice_packet *candidate = &stream->packets[(stream->packet_head + position) % MAXIMUM_STREAM_PACKETS];

				if (!candidate->finished)
				{
					packet = candidate;
					break;
				}
			}
			if (!packet)
				break;
			if (stream->cursor < (double)packet->frames)
				break;
			stream->cursor -= (double)packet->frames;
			if (packet->frames)
			{
				unsigned long last = packet->frames - 1;

				stream->previous[0] = packet_sample(packet, last, 0, stream->channels);
				stream->previous[1] = packet_sample(packet, last, stream->channels - 1, stream->channels);
				stream->previous_valid = TRUE;
			}
			packet->finished = TRUE;
		}
		if (!packet)
		{
			audio_statistics.ran_dry++;
			audio_statistics.dry_frames += frames - frame;
			break;
		}

		index = (unsigned long)stream->cursor;
		fraction = (float)(stream->cursor - (double)index);
		{
			/* the sample before, this one and the two after, across the
			packets' joins (the one before the first: the last packet's last,
			or this one again when the stream starts) */
			float l[4], r[4];

			if (index > 0)
			{
				voice_frame(stream, position, index - 1, &l[0], &r[0]);
			}
			else if (stream->previous_valid)
			{
				l[0] = stream->previous[0];
				r[0] = stream->previous[1];
			}
			else
			{
				voice_frame(stream, position, 0, &l[0], &r[0]);
			}
			voice_frame(stream, position, index, &l[1], &r[1]);
			voice_frame(stream, position, index + 1, &l[2], &r[2]);
			voice_frame(stream, position, index + 2, &l[3], &r[3]);
			sample_left = catmull_rom(l[0], l[1], l[2], l[3], fraction);
			sample_right = catmull_rom(r[0], r[1], r[2], r[3], fraction);
		}
		/* the room send, with its own low pass */
		if (room || ramp_room)
		{
			float mono = stream->channels == 1 ? sample_left : 0.5f * (sample_left + sample_right);

			stream->room_lowpass = flush_denormal(mono + room_lowpass * (stream->room_lowpass - mono));
			send[frame] += stream->room_lowpass * room;
		}
		/* the direct path, muffled, or as it is; a mono voice's mix bins or pan
		split it across the speakers */
		if (direct_lowpass || ramp_direct_lowpass)
		{
			sample_left = flush_denormal(sample_left + direct_lowpass * (stream->direct_lowpass[0] - sample_left));
			sample_right = flush_denormal(sample_right + direct_lowpass * (stream->direct_lowpass[1] - sample_right));
		}
		stream->direct_lowpass[0] = sample_left;
		stream->direct_lowpass[1] = sample_right;
		if (stream->channels == 1)
		{
			/* a mono voice's mix bins or pan split it across the speakers */
			output[frame * 2] += sample_left * left;
			output[frame * 2 + 1] += sample_left * right;
		}
		else
		{
			output[frame * 2] += sample_left * left;
			output[frame * 2 + 1] += sample_right * right;
		}
		left += ramp_left;
		right += ramp_right;
		room += ramp_room;
		direct_lowpass += ramp_direct_lowpass;
		room_lowpass += ramp_room_lowpass;
		stream->cursor += step;
	}
	stream->current_left = target_left;
	stream->current_right = target_right;
	stream->current_room = target_room;
	stream->current_direct_lowpass = target_direct_lowpass;
	stream->current_room_lowpass = target_room_lowpass;
}

/* ---------- reverb

The Xbox ran an I3DL2 reverb on its audio DSP (the effects image the game
downloads), fed by every 3D voice's I3DL2 mix bin. The game sets the listener
properties from the sound environment the camera is in (sound_dsound_xbox.c
dsound_set_listener_properties), and each 3D voice's room send from its
reverb attenuation and occlusion (dsound_channel_set_I3DL2_properties). This
is a reverb of the I3DL2 model on those properties, not the DSP's program:
	- each 3D voice sends to a mono bus at the listener's and its own room
	  levels, occlusion included, their high frequency levels a low pass at the
	  HF reference, attenuated with distance by the room rolloff factors
	  (voice_gains);
	- the early reflections are REVERB_TAPS taps of the bus, starting the
	  reflections delay later, at the reflections level;
	- the late reverberation starts the reverb delay after the reflections:
	  all-pass diffusers as strong as the diffusion, then a feedback delay
	  network of REVERB_LINES lines, as long as the density makes them, each
	  losing what decays it by 60 dB in the decay time, and its high
	  frequencies in the decay time times the HF ratio, at the reverb level.
Both are normalized to the energy sent, so their levels are relative to the
room level, as I3DL2 gives them. A change of environment crossfades each
delay's read from its old length to its new one, and each gain, over
REVERB_FADE_FRAMES: what is reverberating carries on, without the click of a
jump or the pitch shift of a sliding delay. audio.reverb = false fades the
reverb out over as long and stops it. Once nothing has been sent for
REVERB_QUIET_FRAMES and the reverberation is 120 dB down, the reverb stops
until something is sent again (outdoors, in the menus). */

#define REVERB_DELAY_SIZE 32768 /* the reflections and reverb delays, 0.3 + 0.1 s at most, and the taps */
#define REVERB_TAPS 6
#define REVERB_DIFFUSERS 4
#define REVERB_DIFFUSER_SIZE 1024
#define REVERB_LINES 8
#define REVERB_LINE_SIZE 4096
#define REVERB_FADE_FRAMES 4096 /* 85 ms */
/* the input delays, then the diffusers, played out */
#define REVERB_QUIET_FRAMES (REVERB_DELAY_SIZE + REVERB_DIFFUSERS * REVERB_DIFFUSER_SIZE)
#define REVERB_QUIET_PEAK 1.0e-6f

/* in milliseconds: the taps after the reflections delay, the diffusers, and
the lines at full density */
static const float reverb_tap_times[REVERB_TAPS] = { 0.0f, 3.1f, 5.3f, 7.9f, 11.2f, 14.9f };
static const float reverb_tap_signs[REVERB_TAPS] = { 1.0f, 1.0f, -1.0f, 1.0f, 1.0f, -1.0f };
static const float reverb_diffuser_times[REVERB_DIFFUSERS] = { 4.7f, 3.6f, 12.7f, 9.3f };
static const float reverb_line_times[REVERB_LINES] = { 29.7f, 37.1f, 41.1f, 43.7f, 53.3f, 59.9f, 67.1f, 73.1f };
/* which lines go in negated, and the two outputs' signs of the lines */
static const float reverb_input_signs[REVERB_LINES] = { 1, -1, -1, 1, 1, -1, -1, 1 };
static const float reverb_left_signs[REVERB_LINES] = { 1, -1, 1, -1, 1, -1, 1, -1 };
static const float reverb_right_signs[REVERB_LINES] = { 1, 1, -1, -1, 1, 1, -1, -1 };

/* what an environment sets: delays in samples, and gains */
struct reverb_parameters
{
	unsigned long taps[REVERB_TAPS];
	unsigned long late_delay;
	unsigned long lengths[REVERB_LINES];
	/* each line's gain a pass, and its low pass's coefficient */
	float feedback[REVERB_LINES];
	float damping[REVERB_LINES];
	float reflections_gain, late_gain;
	float diffusion;
};

static struct
{
	/* the bus of the current mix */
	float send[MIX_CHUNK_FRAMES];
	/* the environment serial and properties of the parameters faded to */
	unsigned long serial;
	DSI3DL2LISTENER properties;
	/* the parameters fading from and to, and the frames of the fade left
	(none: from is to) */
	struct reverb_parameters from, to;
	unsigned long fade;
	/* the output's level, 1 while audio.reverb is on, moving to 0 when it
	is turned off; whether the buffers are silent; and the frames since the
	send or the output was last over REVERB_QUIET_PEAK */
	float level;
	BOOL silent;
	unsigned long quiet;

	/* the bus, delayed for the taps and the late reverberation */
	float delay[REVERB_DELAY_SIZE];
	unsigned long delay_position;

	float diffusers[REVERB_DIFFUSERS][REVERB_DIFFUSER_SIZE];
	unsigned long diffuser_lengths[REVERB_DIFFUSERS];
	unsigned long diffuser_position;

	float lines[REVERB_LINES][REVERB_LINE_SIZE];
	unsigned long line_position;
	/* each line's low pass */
	float lowpass[REVERB_LINES];
} reverb;

static float clamp_real(float value, float minimum, float maximum)
{
	return bounded_real(value, minimum, maximum, minimum);
}

/* whole samples */
static unsigned long reverb_samples(float seconds)
{
	return (unsigned long)floorf(seconds * OUTPUT_RATE + 0.5f);
}

/* the sample buffer got delay samples before position, crossfaded from the
from delay to the to delay by fade (0 to 1) */
static float reverb_read(const float *buffer, unsigned long mask, unsigned long position,
	unsigned long from_delay, unsigned long to_delay, float fade)
{
	float from_sample = buffer[(position - from_delay) & mask];

	if (from_delay == to_delay)
		return from_sample;
	return from_sample + (buffer[(position - to_delay) & mask] - from_sample) * fade;
}

static float reverb_blend(float from, float to, float fade)
{
	return from + (to - from) * fade;
}

static void reverb_parameters_set(struct reverb_parameters *parameters, const DSI3DL2LISTENER *properties)
{
	float decay = clamp_real(properties->flDecayTime, 0.1f, 20.0f);
	/* a low pass loses high frequencies; a ratio over 1 would need them to
	last longer */
	float high_decay = decay * clamp_real(properties->flDecayHFRatio, 0.1f, 1.0f);
	float scale = 0.25f + 0.75f * clamp_real(properties->flDensity / 100.0f, 0.0f, 1.0f);
	float cosine = frequency_cosine(properties->flHFReference);
	float mean_length = 0.0f, mean_feedback;
	unsigned long reflections_delay;
	int index;

	for (index = 0; index < REVERB_LINES; index++)
	{
		float length = floorf(reverb_line_times[index] * 0.001f * OUTPUT_RATE * scale + 0.5f);
		float high_feedback;

		parameters->lengths[index] = (unsigned long)length;
		parameters->feedback[index] = powf(10.0f, -3.0f * length / (decay * OUTPUT_RATE));
		high_feedback = powf(10.0f, -3.0f * length / (high_decay * OUTPUT_RATE));
		parameters->damping[index] = lowpass_coefficient(high_feedback / parameters->feedback[index], cosine);
		mean_length += length / REVERB_LINES;
	}
	mean_feedback = powf(10.0f, -3.0f * mean_length / (decay * OUTPUT_RATE));
	reflections_delay = reverb_samples(clamp_real(properties->flReflectionsDelay, 0.0f, 0.3f));
	for (index = 0; index < REVERB_TAPS; index++)
		parameters->taps[index] = reflections_delay + reverb_samples(reverb_tap_times[index] * 0.001f);
	parameters->late_delay = reflections_delay + reverb_samples(clamp_real(properties->flReverbDelay, 0.0f, 0.1f));
	/* the taps' energy, half of them to each side; the network's, whose
	sound circulates until it decays */
	parameters->reflections_gain = gain_from_millibels(properties->lReflections) /
		sqrtf((float)REVERB_TAPS / OUTPUT_CHANNELS);
	parameters->late_gain = gain_from_millibels(properties->lReverb) * sqrtf(1.0f - mean_feedback * mean_feedback);
	parameters->diffusion = 0.7f * clamp_real(properties->flDiffusion / 100.0f, 0.0f, 1.0f);
}

/* a new environment, faded to unless the reverb is silent. The game sets the
same one again several times a second in some places (Derelict), which
changes nothing */
static void reverb_update(const DSI3DL2LISTENER *properties, unsigned long serial)
{
	reverb.serial = serial;
	if (!reverb.silent && !memcmp(properties, &reverb.properties, sizeof(*properties)))
		return;
	reverb.properties = *properties;
	reverb_parameters_set(&reverb.to, properties);
	if (reverb.silent)
		reverb.from = reverb.to;
	reverb.fade = reverb.silent ? 0 : REVERB_FADE_FRAMES;
}

static void reverb_clear(void)
{
	memset(reverb.delay, 0, sizeof(reverb.delay));
	memset(reverb.diffusers, 0, sizeof(reverb.diffusers));
	memset(reverb.lines, 0, sizeof(reverb.lines));
	memset(reverb.lowpass, 0, sizeof(reverb.lowpass));
	reverb.from = reverb.to;
	reverb.fade = 0;
	reverb.silent = TRUE;
	reverb.quiet = 0;
}

static void reverb_initialize(void)
{
	int index;

	for (index = 0; index < REVERB_DIFFUSERS; index++)
		reverb.diffuser_lengths[index] = reverb_samples(reverb_diffuser_times[index] * 0.001f);
	reverb.silent = TRUE;
	reverb.level = reverb_enabled ? 1.0f : 0.0f;
	reverb_update(&environment, environment_serial);
}

/* adds the reverberation of send to output, its level moving to
target_level */
static void reverb_process(const float *send, float *output, unsigned long frames, float target_level, float output_gain)
{
	const struct reverb_parameters *from = &reverb.from, *to = &reverb.to;
	float input_scale = 1.0f / sqrtf((float)REVERB_LINES), peak = 0.0f;
	unsigned long frame;
	int index;

	reverb.silent = FALSE;
	for (frame = 0; frame < frames; frame++)
	{
		/* how far the fade from the old environment to the new is */
		float fade = 1.0f - (float)reverb.fade / REVERB_FADE_FRAMES;
		float early[OUTPUT_CHANNELS] = { 0.0f, 0.0f };
		float outputs[REVERB_LINES], late_left = 0.0f, late_right = 0.0f, feedback_sum = 0.0f, value;
		float diffusion = reverb_blend(from->diffusion, to->diffusion, fade);

		reverb.delay[reverb.delay_position & (REVERB_DELAY_SIZE - 1)] = send[frame];
		for (index = 0; index < REVERB_TAPS; index++)
		{
			early[index % OUTPUT_CHANNELS] += reverb_tap_signs[index] * reverb_read(reverb.delay, REVERB_DELAY_SIZE - 1,
				reverb.delay_position, from->taps[index], to->taps[index], fade);
		}

		/* diffusers: w = x + g w', y = w' - g w */
		value = reverb_read(reverb.delay, REVERB_DELAY_SIZE - 1, reverb.delay_position,
			from->late_delay, to->late_delay, fade);
		reverb.delay_position++;
		for (index = 0; index < REVERB_DIFFUSERS; index++)
		{
			float *buffer = reverb.diffusers[index];
			float delayed = buffer[(reverb.diffuser_position - reverb.diffuser_lengths[index]) & (REVERB_DIFFUSER_SIZE - 1)];
			float written = flush_denormal(value + diffusion * delayed);

			buffer[reverb.diffuser_position & (REVERB_DIFFUSER_SIZE - 1)] = written;
			value = delayed - diffusion * written;
		}
		reverb.diffuser_position++;

		/* the network: each line's output is damped and heard, then decayed
		and mixed back into every line by a Householder reflection */
		for (index = 0; index < REVERB_LINES; index++)
		{
			float line_output = reverb_read(reverb.lines[index], REVERB_LINE_SIZE - 1, reverb.line_position,
				from->lengths[index], to->lengths[index], fade);
			float damping = reverb_blend(from->damping[index], to->damping[index], fade);

			reverb.lowpass[index] = flush_denormal(line_output + damping * (reverb.lowpass[index] - line_output));
			late_left += reverb_left_signs[index] * reverb.lowpass[index];
			late_right += reverb_right_signs[index] * reverb.lowpass[index];
			outputs[index] = reverb.lowpass[index] * reverb_blend(from->feedback[index], to->feedback[index], fade);
			feedback_sum += outputs[index];
		}
		feedback_sum *= 2.0f / REVERB_LINES;
		for (index = 0; index < REVERB_LINES; index++)
		{
			reverb.lines[index][reverb.line_position & (REVERB_LINE_SIZE - 1)] =
				flush_denormal(outputs[index] - feedback_sum + value * reverb_input_signs[index] * input_scale);
		}
		reverb.line_position++;

		{
			float reflections_gain = reverb_blend(from->reflections_gain, to->reflections_gain, fade);
			float late_gain = reverb_blend(from->late_gain, to->late_gain, fade);
			float left = early[0] * reflections_gain + late_left * late_gain;
			float right = early[1] * reflections_gain + late_right * late_gain;

			output[frame * 2] += left * reverb.level * output_gain;
			output[frame * 2 + 1] += right * reverb.level * output_gain;
			peak = fabsf(left) > peak ? fabsf(left) : peak;
			peak = fabsf(right) > peak ? fabsf(right) : peak;
			peak = fabsf(send[frame]) > peak ? fabsf(send[frame]) : peak;
		}
		if (reverb.fade && !--reverb.fade)
			reverb.from = reverb.to;
		reverb.level = clamp_real(target_level, reverb.level - 1.0f / REVERB_FADE_FRAMES,
			reverb.level + 1.0f / REVERB_FADE_FRAMES);
	}
	reverb.quiet = peak > REVERB_QUIET_PEAK ? 0 : reverb.quiet + frames;
}

/* whether anything is sent to the reverb in send */
static BOOL reverb_sent(const float *send, unsigned long frames)
{
	unsigned long frame;

	for (frame = 0; frame < frames; frame++)
	{
		if (fabsf(send[frame]) > REVERB_QUIET_PEAK)
			return TRUE;
	}
	return FALSE;
}

static void mix(float *output, unsigned long frames)
{
	struct sdl_stream *stream;
	unsigned long sample, serial = 0;
	DSI3DL2LISTENER properties;
	BOOL enabled, changed = FALSE;
	float output_gain;

	memset(output, 0, frames * OUTPUT_CHANNELS * sizeof(float));
	pthread_mutex_lock(&mixer_lock);
	{
		unsigned long playing = 0;

		enabled = reverb_enabled;
		output_gain = master_volume;
		memset(reverb.send, 0, frames * sizeof(float));

		for (stream = streams; stream; stream = stream->next)
		{
			if (!stream->paused && stream->packet_count)
				playing++;
			mix_voice(stream, output, reverb.send, frames);
		}
		if (reverb.serial != environment_serial && !reverb.fade)
		{
			properties = environment;
			serial = environment_serial;
			changed = TRUE;
		}
		if (playing > audio_statistics.voices_playing_max)
			audio_statistics.voices_playing_max = playing;
	}
	pthread_mutex_unlock(&mixer_lock);
	if (changed) reverb_update(&properties, serial);
	if (!reverb.silent || (enabled && reverb_sent(reverb.send, frames)))
	{
		reverb_process(reverb.send, output, frames, enabled ? 1.0f : 0.0f, output_gain);
		if ((!enabled && reverb.level <= 0.0f) || reverb.quiet > REVERB_QUIET_FRAMES)
			reverb_clear();
	}
	audio_statistics.frames_mixed += frames;
	/* soft limit rather than wrap or hard clip when many voices pile up */
	for (sample = 0; sample < frames * OUTPUT_CHANNELS; sample++)
	{
		float value = output[sample];

		if (value > 0.8f || value < -0.8f)
		{
			float sign = value < 0.0f ? -1.0f : 1.0f;
			float excess = fabsf(value) - 0.8f;

			output[sample] = sign * (0.8f + 0.2f * tanhf(excess / 0.2f));
		}
	}
}

/* ---------- output */

static SDL_AudioStream *audio_stream;
static BOOL audio_started = FALSE;

static void SDLCALL audio_callback(void *userdata, SDL_AudioStream *stream, int additional_amount, int total_amount)
{
	float buffer[MIX_CHUNK_FRAMES * OUTPUT_CHANNELS];
	double start = audio_now_ms(), took;

	(void)userdata;
	(void)total_amount;
	if (audio_statistics.last_callback_ms > 0.0 && start - audio_statistics.last_callback_ms > audio_statistics.callback_gap_max_ms)
		audio_statistics.callback_gap_max_ms = start - audio_statistics.last_callback_ms;
	audio_statistics.last_callback_ms = start;
	audio_statistics.callbacks++;
	while (additional_amount > 0)
	{
		unsigned long frames = (unsigned long)additional_amount / (OUTPUT_CHANNELS * sizeof(float));

		if (frames > MIX_CHUNK_FRAMES)
			frames = MIX_CHUNK_FRAMES;
		if (!frames)
			frames = 1;
		mix(buffer, frames);
		SDL_PutAudioStreamData(stream, buffer, (int)(frames * OUTPUT_CHANNELS * sizeof(float)));
		additional_amount -= (int)(frames * OUTPUT_CHANNELS * sizeof(float));
	}
	took = audio_now_ms() - start;
	audio_statistics.mix_total_ms += took;
	if (took > audio_statistics.mix_max_ms)
		audio_statistics.mix_max_ms = took;
}

/* without a device, drain voices in real time */
static void *silent_clock_thread(void *parameter)
{
	float buffer[480 * OUTPUT_CHANNELS];
	struct timespec next;

	(void)parameter;
	clock_gettime(CLOCK_MONOTONIC, &next);
	for (;;)
	{
		mix(buffer, 480);
		next.tv_nsec += 10000000L;
		if (next.tv_nsec >= 1000000000L)
		{
			next.tv_nsec -= 1000000000L;
			next.tv_sec++;
		}
		clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
	}
	return NULL;
}

static void audio_start(void)
{
	SDL_AudioSpec spec;

	if (audio_started)
		return;
	audio_started = TRUE;
	audio_update_volume();
	reverb_initialize();

	if (config_boolean("audio.enabled") && platform_sdl_initialize())
	{
		spec.format = SDL_AUDIO_F32;
		spec.channels = OUTPUT_CHANNELS;
		spec.freq = OUTPUT_RATE;
#ifdef HALO_ANDROID
		/* a standalone headset's frames can hitch (a level loading, the
		runtime's own pauses): twice the buffer keeps the device fed through
		them, at 21 ms rather than 11 */
		SDL_SetHint(SDL_HINT_AUDIO_DEVICE_SAMPLE_FRAMES, "1024");
#else
		SDL_SetHint(SDL_HINT_AUDIO_DEVICE_SAMPLE_FRAMES, "512");
#endif
		audio_stream = SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK, &spec, audio_callback, NULL);
		if (audio_stream)
		{
			/* (the device's own format is logged where it opens: on Android
			by the host, port/android/host/host_sdl.c) */
			platform_log("[audio] mixing %d Hz stereo float into the device", OUTPUT_RATE);
			SDL_ResumeAudioStreamDevice(audio_stream);
			return;
		}
		platform_log("cannot open an audio device (%s); sound is silent", SDL_GetError());
	}
	{
		pthread_t thread;

		pthread_create(&thread, NULL, silent_clock_thread, NULL);
		pthread_detach(thread);
	}
}

/* ---------- completion */

static void packet_release(struct voice_packet *entry)
{
	free(entry->samples);
	entry->samples = NULL;
}

/* completes the head packet; called with the lock held, which the game's
callback runs without */
static void stream_complete_head(struct sdl_stream *stream, DWORD status, DWORD completed_size)
{
	struct voice_packet *entry = &stream->packets[stream->packet_head];
	XMEDIAPACKET packet = entry->packet;

	packet_release(entry);
	entry->finished = FALSE;
	stream->packet_head = (stream->packet_head + 1) % MAXIMUM_STREAM_PACKETS;
	stream->packet_count--;
	if (packet.pdwCompletedSize)
		*packet.pdwCompletedSize = completed_size;
	if (packet.pdwStatus)
		*packet.pdwStatus = status;
	if (stream->callback)
	{
		pthread_mutex_unlock(&mixer_lock);
		stream->callback(stream->context, packet.pContext, status);
		pthread_mutex_lock(&mixer_lock);
	}
	else if (packet.hCompletionEvent)
	{
		SetEvent(packet.hCompletionEvent);
	}
}

static void streams_complete_finished(void)
{
	struct sdl_stream *stream;

	pthread_mutex_lock(&mixer_lock);
	for (stream = streams; stream; stream = stream->next)
	{
		while (stream->packet_count && stream->packets[stream->packet_head].finished)
			stream_complete_head(stream, XMEDIAPACKET_STATUS_SUCCESS, stream->packets[stream->packet_head].packet.dwMaxSize);
	}
	pthread_mutex_unlock(&mixer_lock);
}

/* ---------- stream interface */

static struct sdl_stream *stream_from_interface(void *stream)
{
	return (struct sdl_stream *)stream;
}

static ULONG STDMETHODCALLTYPE stream_add_reference(IDirectSoundStream *object)
{
	struct sdl_stream *stream = stream_from_interface(object);
	ULONG count;

	pthread_mutex_lock(&mixer_lock);
	count = ++stream->reference_count;
	pthread_mutex_unlock(&mixer_lock);
	return count;
}

static HRESULT STDMETHODCALLTYPE stream_flush(IDirectSoundStream *object);

static ULONG STDMETHODCALLTYPE stream_release(IDirectSoundStream *object)
{
	struct sdl_stream *stream = stream_from_interface(object);
	struct sdl_stream **link;
	ULONG count;

	pthread_mutex_lock(&mixer_lock);
	count = --stream->reference_count;
	pthread_mutex_unlock(&mixer_lock);
	if (count)
		return count;

	stream_flush(object);
	pthread_mutex_lock(&mixer_lock);
	for (link = &streams; *link; link = &(*link)->next)
	{
		if (*link == stream)
		{
			*link = stream->next;
			break;
		}
	}
	pthread_mutex_unlock(&mixer_lock);
	free(stream);
	return 0;
}

static HRESULT STDMETHODCALLTYPE stream_get_info(IDirectSoundStream *object, LPXMEDIAINFO information)
{
	struct sdl_stream *stream = stream_from_interface(object);

	memset(information, 0, sizeof(*information));
	information->dwFlags = XMO_STREAMF_FIXED_SAMPLE_SIZE | XMO_STREAMF_INPUT_ASYNC;
	information->dwInputSize = stream->adpcm ? XBOX_ADPCM_BLOCK_BYTES * stream->channels : 2 * stream->channels;
	return S_OK;
}

static HRESULT STDMETHODCALLTYPE stream_get_status(IDirectSoundStream *object, LPDWORD status)
{
	struct sdl_stream *stream = stream_from_interface(object);

	pthread_mutex_lock(&mixer_lock);
	*status = stream->packet_count < MAXIMUM_STREAM_PACKETS ? XMO_STATUSF_ACCEPT_INPUT_DATA : 0;
	pthread_mutex_unlock(&mixer_lock);
	return S_OK;
}

static HRESULT STDMETHODCALLTYPE stream_process(IDirectSoundStream *object, LPCXMEDIAPACKET input, LPCXMEDIAPACKET output)
{
	struct sdl_stream *stream = stream_from_interface(object);
	struct voice_packet *entry;
	unsigned long frames = 0;
	short *samples;

	(void)output;
	if (!input)
		return E_INVALIDARG;
	/* decode outside the lock */
	samples = stream->adpcm ?
		decode_adpcm(input->pvBuffer, input->dwMaxSize, stream->channels, &frames) :
		decode_pcm(input->pvBuffer, input->dwMaxSize, stream->channels, &frames);
	pthread_mutex_lock(&mixer_lock);
	if (stream->packet_count == MAXIMUM_STREAM_PACKETS)
	{
		pthread_mutex_unlock(&mixer_lock);
		free(samples);
		return E_OUTOFMEMORY;
	}
	entry = &stream->packets[(stream->packet_head + stream->packet_count) % MAXIMUM_STREAM_PACKETS];
	entry->packet = *input;
	entry->samples = samples;
	entry->frames = samples ? frames : 0;
	entry->finished = FALSE;
	if (input->pdwStatus)
		*input->pdwStatus = XMEDIAPACKET_STATUS_PENDING;
	if (input->pdwCompletedSize)
		*input->pdwCompletedSize = 0;
	if (!stream->packet_count)
	{
		/* a stream that ran dry starts over */
		stream->cursor = 0.0;
		stream->gains_valid = FALSE;
		stream->previous_valid = FALSE;
	}
	stream->packet_count++;
	pthread_mutex_unlock(&mixer_lock);
	return S_OK;
}

static HRESULT STDMETHODCALLTYPE stream_discontinuity(IDirectSoundStream *object)
{
	(void)object;
	return S_OK;
}

static HRESULT STDMETHODCALLTYPE stream_flush(IDirectSoundStream *object)
{
	struct sdl_stream *stream = stream_from_interface(object);

	pthread_mutex_lock(&mixer_lock);
	while (stream->packet_count)
	{
		struct voice_packet *head = &stream->packets[stream->packet_head];

		stream_complete_head(stream, head->finished ? XMEDIAPACKET_STATUS_SUCCESS : XMEDIAPACKET_STATUS_FLUSHED,
			head->finished ? head->packet.dwMaxSize : 0);
	}
	stream->cursor = 0.0;
	stream->previous_valid = FALSE;
	pthread_mutex_unlock(&mixer_lock);
	return S_OK;
}

static IDirectSoundStreamVtbl stream_vtable =
{
	stream_add_reference,
	stream_release,
	stream_get_info,
	stream_get_status,
	stream_process,
	stream_discontinuity,
	stream_flush,
};

/* ---------- the DirectSound object */

struct sdl_direct_sound
{
	ULONG reference_count;
};

static struct sdl_direct_sound direct_sound = { 0 };

HRESULT WINAPI DirectSoundCreate(LPGUID device_id, LPDIRECTSOUND *result, LPUNKNOWN outer)
{
	(void)device_id;
	(void)outer;
	audio_start();
	direct_sound.reference_count++;
	*result = (LPDIRECTSOUND)&direct_sound;
	return DS_OK;
}

ULONG WINAPI IDirectSound_Release(LPDIRECTSOUND sound)
{
	(void)sound;
	return direct_sound.reference_count ? --direct_sound.reference_count : 0;
}

VOID WINAPI DirectSoundDoWork(void)
{
	double now = audio_now_ms();

	audio_update_volume();
	if (audio_statistics.last_work_ms > 0.0 && now - audio_statistics.last_work_ms > audio_statistics.work_gap_max_ms)
		audio_statistics.work_gap_max_ms = now - audio_statistics.last_work_ms;
	audio_statistics.last_work_ms = now;
	audio_statistics.work_calls++;
	streams_complete_finished();
	audio_statistics_log();
}

VOID WINAPI DirectSoundUseFullHRTF(void)
{
}

HRESULT WINAPI IDirectSound_GetCaps(LPDIRECTSOUND sound, LPDSCAPS caps)
{
	(void)sound;
	memset(caps, 0, sizeof(*caps));
	caps->dwFree2DBuffers = 64;
	caps->dwFree3DBuffers = 64;
	caps->dwFreeBufferSGEs = 2047;
	caps->dwMemoryAllocated = 0;
	return DS_OK;
}

HRESULT WINAPI IDirectSound_GetSpeakerConfig(LPDIRECTSOUND sound, LPDWORD speaker_config)
{
	(void)sound;
	*speaker_config = DSSPEAKER_STEREO;
	return DS_OK;
}

HRESULT WINAPI IDirectSound_DownloadEffectsImage(LPDIRECTSOUND sound, LPCVOID image, DWORD image_size,
	LPCDSEFFECTIMAGELOC image_location, LPDSEFFECTIMAGEDESC *image_description)
{
	(void)sound;
	(void)image;
	(void)image_size;
	(void)image_location;
	if (image_description)
		*image_description = NULL;
	return DS_OK;
}

HRESULT WINAPI IDirectSound_CommitDeferredSettings(LPDIRECTSOUND sound) { (void)sound; return DS_OK; }
HRESULT WINAPI IDirectSound_SetMixBinHeadroom(LPDIRECTSOUND sound, DWORD mix_bin_mask, DWORD headroom) { (void)sound; (void)mix_bin_mask; (void)headroom; return DS_OK; }
HRESULT WINAPI IDirectSound_SetI3DL2Listener(LPDIRECTSOUND sound, LPCDSI3DL2LISTENER listener_properties, DWORD apply)
{
	DSI3DL2LISTENER value;
	(void)sound;
	(void)apply;
	if (!listener_properties) return E_INVALIDARG;
	value = *listener_properties;
	value.lRoom = bounded_level(value.lRoom, -10000, 0);
	value.lRoomHF = bounded_level(value.lRoomHF, -10000, 0);
	value.flRoomRolloffFactor = bounded_real(value.flRoomRolloffFactor, 0.0f, 10.0f, 0.0f);
	value.flDecayTime = bounded_real(value.flDecayTime, 0.1f, 20.0f, 1.49f);
	value.flDecayHFRatio = bounded_real(value.flDecayHFRatio, 0.1f, 2.0f, 0.83f);
	value.lReflections = bounded_level(value.lReflections, -10000, 1000);
	value.flReflectionsDelay = bounded_real(value.flReflectionsDelay, 0.0f, 0.3f, 0.007f);
	value.lReverb = bounded_level(value.lReverb, -10000, 2000);
	value.flReverbDelay = bounded_real(value.flReverbDelay, 0.0f, 0.1f, 0.011f);
	value.flDiffusion = bounded_real(value.flDiffusion, 0.0f, 100.0f, 100.0f);
	value.flDensity = bounded_real(value.flDensity, 0.0f, 100.0f, 100.0f);
	value.flHFReference = bounded_real(value.flHFReference, 20.0f, 20000.0f, 5000.0f);
	pthread_mutex_lock(&mixer_lock);
	environment = value;
	environment_serial++;
	pthread_mutex_unlock(&mixer_lock);
	return DS_OK;
}

HRESULT WINAPI IDirectSound_SetDistanceFactor(LPDIRECTSOUND sound, FLOAT factor, DWORD apply)
{
	(void)sound;
	(void)apply;
	pthread_mutex_lock(&mixer_lock);
	listener.distance_factor = factor > 0.0f ? factor : 1.0f;
	pthread_mutex_unlock(&mixer_lock);
	return DS_OK;
}

HRESULT WINAPI IDirectSound_SetRolloffFactor(LPDIRECTSOUND sound, FLOAT factor, DWORD apply)
{
	(void)sound;
	(void)apply;
	pthread_mutex_lock(&mixer_lock);
	listener.rolloff_factor = factor >= 0.0f ? factor : 1.0f;
	pthread_mutex_unlock(&mixer_lock);
	return DS_OK;
}

HRESULT WINAPI IDirectSound_SetPosition(LPDIRECTSOUND sound, FLOAT x, FLOAT y, FLOAT z, DWORD apply)
{
	(void)sound;
	(void)apply;
	pthread_mutex_lock(&mixer_lock);
	listener.position[0] = x;
	listener.position[1] = y;
	listener.position[2] = z;
	pthread_mutex_unlock(&mixer_lock);
	return DS_OK;
}

HRESULT WINAPI IDirectSound_SetVelocity(LPDIRECTSOUND sound, FLOAT x, FLOAT y, FLOAT z, DWORD apply) { (void)sound; (void)x; (void)y; (void)z; (void)apply; return DS_OK; }

static void normalize3(float *vector)
{
	float length = sqrtf(dot3(vector, vector));

	if (length > 1.0e-6f)
	{
		vector[0] /= length;
		vector[1] /= length;
		vector[2] /= length;
	}
}

HRESULT WINAPI IDirectSound_SetOrientation(LPDIRECTSOUND sound, FLOAT x_front, FLOAT y_front, FLOAT z_front,
	FLOAT x_top, FLOAT y_top, FLOAT z_top, DWORD apply)
{
	(void)sound;
	(void)apply;
	pthread_mutex_lock(&mixer_lock);
	listener.front[0] = x_front;
	listener.front[1] = y_front;
	listener.front[2] = z_front;
	listener.top[0] = x_top;
	listener.top[1] = y_top;
	listener.top[2] = z_top;
	normalize3(listener.front);
	normalize3(listener.top);
	pthread_mutex_unlock(&mixer_lock);
	return DS_OK;
}

HRESULT WINAPI IDirectSound_CreateSoundStream(LPDIRECTSOUND sound, LPCDSSTREAMDESC description,
	LPDIRECTSOUNDSTREAM *result, LPUNKNOWN outer)
{
	struct sdl_stream *stream = calloc(1, sizeof(*stream));
	const WAVEFORMATEX *format = description->lpwfxFormat;

	(void)sound;
	(void)outer;
	if (!stream)
		return E_OUTOFMEMORY;
	stream->object.lpVtbl = &stream_vtable;
	stream->reference_count = 1;
	stream->callback = description->lpfnCallback;
	stream->context = description->lpvContext;
	stream->adpcm = format && format->wFormatTag == WAVE_FORMAT_XBOX_ADPCM;
	stream->channels = format && format->nChannels == 2 ? 2 : 1;
	stream->sample_rate = format ? format->nSamplesPerSec : 0;
	stream->frequency = stream->sample_rate;
	stream->volume = 1.0f;
	/* DirectSound's default mix bins: a mono voice to both fronts, a
	stereo voice's channels to the front left and right */
	stream->mix_left = 1.0f;
	stream->mix_right = 1.0f;
	stream->has_3d = (description->dwFlags & DSSTREAMCAPS_CTRL3D) != 0;
	stream->mode = DS3DMODE_NORMAL;
	stream->minimum_distance = DS3D_DEFAULTMINDISTANCE;
	stream->maximum_distance = DS3D_DEFAULTMAXDISTANCE;
	stream->i3dl2_gain = 1.0f;
	pthread_mutex_lock(&mixer_lock);
	stream->next = streams;
	streams = stream;
	pthread_mutex_unlock(&mixer_lock);
	*result = &stream->object;
	return DS_OK;
}

/* January-era DirectSound exports the game declares itself
(sound_dsound_xbox.c); the XDK 3911 headers no longer carry them */

void __stdcall DirectSoundStopStream(LPDIRECTSOUNDSTREAM stream)
{
	stream_flush(stream);
}

unsigned long __stdcall DirectSoundGetStreamVoiceStatus(LPDIRECTSOUNDSTREAM stream)
{
	struct sdl_stream *record = stream_from_interface(stream);
	unsigned long active;

	pthread_mutex_lock(&mixer_lock);
	active = record->packet_count != 0;
	pthread_mutex_unlock(&mixer_lock);
	return active;
}

#define STREAM_SETTER(body) \
	struct sdl_stream *record = stream_from_interface(stream); \
	pthread_mutex_lock(&mixer_lock); \
	body; \
	pthread_mutex_unlock(&mixer_lock); \
	return DS_OK;

HRESULT WINAPI IDirectSoundStream_SetFrequency(LPDIRECTSOUNDSTREAM stream, DWORD frequency)
{
	STREAM_SETTER(record->frequency = frequency ? frequency : record->sample_rate)
}

HRESULT WINAPI IDirectSoundStream_SetVolume(LPDIRECTSOUNDSTREAM stream, LONG volume)
{
	STREAM_SETTER(record->volume = gain_from_millibels(volume))
}

HRESULT WINAPI IDirectSoundStream_SetMixBins(LPDIRECTSOUNDSTREAM stream, DWORD mix_bin_mask)
{
	STREAM_SETTER(
		record->mix_left = (mix_bin_mask & DSMIXBIN_FRONT_LEFT) ? 1.0f : 0.0f;
		record->mix_right = (mix_bin_mask & DSMIXBIN_FRONT_RIGHT) ? 1.0f : 0.0f)
}

/* volumes come in the order of the set bits of the mask */
HRESULT WINAPI IDirectSoundStream_SetMixBinVolumes(LPDIRECTSOUNDSTREAM stream, DWORD mix_bin_mask, const LONG *volumes)
{
	struct sdl_stream *record = stream_from_interface(stream);
	unsigned long bit, index = 0;

	pthread_mutex_lock(&mixer_lock);
	for (bit = 0; bit < 32; bit++)
	{
		if (!(mix_bin_mask & (1UL << bit)))
			continue;
		if ((1UL << bit) == DSMIXBIN_FRONT_LEFT)
			record->mix_left = gain_from_millibels(volumes[index]);
		else if ((1UL << bit) == DSMIXBIN_FRONT_RIGHT)
			record->mix_right = gain_from_millibels(volumes[index]);
		index++;
	}
	pthread_mutex_unlock(&mixer_lock);
	return DS_OK;
}

HRESULT WINAPI IDirectSoundStream_SetMode(LPDIRECTSOUNDSTREAM stream, DWORD mode, DWORD apply)
{
	(void)apply;
	STREAM_SETTER(record->mode = mode)
}

HRESULT WINAPI IDirectSoundStream_SetPosition(LPDIRECTSOUNDSTREAM stream, FLOAT x, FLOAT y, FLOAT z, DWORD apply)
{
	(void)apply;
	STREAM_SETTER(record->position[0] = x; record->position[1] = y; record->position[2] = z)
}

HRESULT WINAPI IDirectSoundStream_SetMinDistance(LPDIRECTSOUNDSTREAM stream, FLOAT distance, DWORD apply)
{
	(void)apply;
	STREAM_SETTER(record->minimum_distance = distance)
}

HRESULT WINAPI IDirectSoundStream_SetMaxDistance(LPDIRECTSOUNDSTREAM stream, FLOAT distance, DWORD apply)
{
	(void)apply;
	STREAM_SETTER(record->maximum_distance = distance)
}

HRESULT WINAPI IDirectSoundStream_SetI3DL2Source(LPDIRECTSOUNDSTREAM stream, LPCDSI3DL2BUFFER source, DWORD apply)
{
	LONG direct, direct_hf, room, room_hf, obstruction, occlusion, direct_base, room_base;
	float obstruction_ratio, occlusion_ratio, rolloff;
	(void)apply;
	if (!source) return E_INVALIDARG;
	direct_base = bounded_level(source->lDirect, -10000, 1000);
	room_base = bounded_level(source->lRoom, -10000, 1000);
	obstruction = bounded_level(source->Obstruction.lHFLevel, -10000, 0);
	occlusion = bounded_level(source->Occlusion.lHFLevel, -10000, 0);
	obstruction_ratio = bounded_real(source->Obstruction.flLFRatio, 0.0f, 1.0f, 0.0f);
	occlusion_ratio = bounded_real(source->Occlusion.flLFRatio, 0.0f, 1.0f, 0.0f);
	rolloff = bounded_real(source->flRoomRolloffFactor, 0.0f, 10.0f, 0.0f);
	direct = direct_base + (LONG)(obstruction * obstruction_ratio) + (LONG)(occlusion * occlusion_ratio);
	if (direct > 0) direct = 0;
	direct_hf = direct_base + bounded_level(source->lDirectHF, -10000, 0) + obstruction + occlusion;
	room = room_base + (LONG)(occlusion * occlusion_ratio);
	room_hf = room_base + bounded_level(source->lRoomHF, -10000, 0) + occlusion;
	{
		STREAM_SETTER(
			record->i3dl2_gain = gain_from_millibels(direct);
			record->direct = direct;
			record->direct_hf = direct_hf;
			record->room = room;
			record->room_hf = room_hf;
			record->room_rolloff_factor = rolloff)
	}
}

HRESULT WINAPI IDirectSoundStream_Pause(LPDIRECTSOUNDSTREAM stream, DWORD pause)
{
	STREAM_SETTER(record->paused = pause == DSSTREAMPAUSE_PAUSE)
}

HRESULT WINAPI IDirectSoundStream_SetVelocity(LPDIRECTSOUNDSTREAM stream, FLOAT x, FLOAT y, FLOAT z, DWORD apply) { (void)stream; (void)x; (void)y; (void)z; (void)apply; return DS_OK; }
HRESULT WINAPI IDirectSoundStream_SetConeAngles(LPDIRECTSOUNDSTREAM stream, DWORD inside, DWORD outside, DWORD apply) { (void)stream; (void)inside; (void)outside; (void)apply; return DS_OK; }
HRESULT WINAPI IDirectSoundStream_SetConeOrientation(LPDIRECTSOUNDSTREAM stream, FLOAT x, FLOAT y, FLOAT z, DWORD apply) { (void)stream; (void)x; (void)y; (void)z; (void)apply; return DS_OK; }
HRESULT WINAPI IDirectSoundStream_SetConeOutsideVolume(LPDIRECTSOUNDSTREAM stream, LONG volume, DWORD apply) { (void)stream; (void)volume; (void)apply; return DS_OK; }

/* ---------- buffers

The game's only buffer is a silent looping one that keeps the voice
processor busy; it needs no mixing. */

struct null_buffer
{
	ULONG reference_count;
	LPVOID data;
	DWORD size;
	BOOL playing;
};

HRESULT WINAPI DirectSoundCreateBuffer(LPCDSBUFFERDESC description, LPDIRECTSOUNDBUFFER *result)
{
	struct null_buffer *buffer = calloc(1, sizeof(*buffer));

	(void)description;
	if (!buffer)
		return E_OUTOFMEMORY;
	buffer->reference_count = 1;
	*result = (LPDIRECTSOUNDBUFFER)buffer;
	return DS_OK;
}

HRESULT WINAPI IDirectSound_CreateSoundBuffer(LPDIRECTSOUND sound, LPCDSBUFFERDESC description,
	LPDIRECTSOUNDBUFFER *result, LPUNKNOWN outer)
{
	(void)sound;
	(void)outer;
	return DirectSoundCreateBuffer(description, result);
}

ULONG WINAPI IDirectSoundBuffer_Release(LPDIRECTSOUNDBUFFER buffer)
{
	struct null_buffer *record = (struct null_buffer *)buffer;
	ULONG count = --record->reference_count;

	if (!count)
		free(record);
	return count;
}

HRESULT WINAPI IDirectSoundBuffer_SetBufferData(LPDIRECTSOUNDBUFFER buffer, LPVOID data, DWORD size)
{
	struct null_buffer *record = (struct null_buffer *)buffer;

	record->data = data;
	record->size = size;
	return DS_OK;
}

HRESULT WINAPI IDirectSoundBuffer_Play(LPDIRECTSOUNDBUFFER buffer, DWORD reserved1, DWORD reserved2, DWORD flags)
{
	(void)reserved1;
	(void)reserved2;
	(void)flags;
	((struct null_buffer *)buffer)->playing = TRUE;
	return DS_OK;
}

HRESULT WINAPI IDirectSoundBuffer_Stop(LPDIRECTSOUNDBUFFER buffer)
{
	((struct null_buffer *)buffer)->playing = FALSE;
	return DS_OK;
}

HRESULT WINAPI IDirectSoundBuffer_SetCurrentPosition(LPDIRECTSOUNDBUFFER buffer, DWORD play_cursor) { (void)buffer; (void)play_cursor; return DS_OK; }
HRESULT WINAPI IDirectSoundBuffer_SetLoopRegion(LPDIRECTSOUNDBUFFER buffer, DWORD loop_start, DWORD loop_length) { (void)buffer; (void)loop_start; (void)loop_length; return DS_OK; }
HRESULT WINAPI IDirectSoundBuffer_SetPitch(LPDIRECTSOUNDBUFFER buffer, LONG pitch) { (void)buffer; (void)pitch; return DS_OK; }
HRESULT WINAPI IDirectSoundBuffer_SetVolume(LPDIRECTSOUNDBUFFER buffer, LONG volume) { (void)buffer; (void)volume; return DS_OK; }
