/*
AUDIO_CODECS.C

Ogg Vorbis decoding (port/third_party/stb/stb_vorbis.c) and Xbox ADPCM
encoding (audio_codecs.h).

Xbox ADPCM is IMA ADPCM in blocks of 36 bytes a channel: a 4-byte header
(the predictor, the step index, a zero) and 32 bytes of nibbles, 65 frames:
the header's predictor is the first, the nibbles the 64 after it; channels'
headers come first, then 4-byte groups of eight nibbles, low nibble first,
alternating between the channels. The encoder below is the inverse of
dsound_sdl.c's decoder, which it follows step for step, so what it writes
plays back as it predicts.
*/

#include "audio_codecs.h"

#include <stdlib.h>
#include <string.h>

#define STB_VORBIS_NO_PUSHDATA_API
#define STB_VORBIS_NO_STDIO
#include "../../third_party/stb/stb_vorbis.c"

#define XBOX_ADPCM_BLOCK_BYTES 36
#define XBOX_ADPCM_BLOCK_FRAMES 65

void halo_audio_free(void *memory)
{
	free(memory);
}

/* ---------- Ogg Vorbis */

long halo_ogg_decode(const void *data, long size, int channels, long sample_rate, short **samples)
{
	int source_channels = 0, source_rate = 0;
	short *source = NULL, *output;
	long source_frames, frames, frame;
	int channel;

	*samples = NULL;
	if (channels < 1 || channels > 2 || sample_rate <= 0 || size <= 0)
		return -1;
	source_frames = stb_vorbis_decode_memory((const unsigned char *)data, (int)size, &source_channels, &source_rate,
		&source);
	if (source_frames < 0 || !source || source_channels < 1 || source_rate <= 0)
	{
		free(source);
		return -1;
	}
	/* the frames at the wanted rate: linear interpolation between the
	stream's (speech and effects, rarely another rate than the tag's) */
	frames = source_rate == sample_rate ? source_frames :
		(long)((double)source_frames * (double)sample_rate / (double)source_rate);
	output = malloc((size_t)(frames > 0 ? frames : 1) * (size_t)channels * sizeof(short));
	if (!output)
	{
		free(source);
		return -1;
	}
	for (frame = 0; frame < frames; frame++)
	{
		double position = source_rate == sample_rate ? (double)frame :
			(double)frame * (double)source_rate / (double)sample_rate;
		long at = (long)position;
		double fraction = position - (double)at;
		long next = at + 1 < source_frames ? at + 1 : at;

		for (channel = 0; channel < channels; channel++)
		{
			double value = 0.0;
			int from, count = 0;

			/* the stream's channels for this one: its own when it has it, the
			mix of all of them for a mono sound, the first for a mono stream */
			for (from = 0; from < source_channels; from++)
			{
				if (channels == 1 || (source_channels == 1 ? from == 0 : from == channel))
				{
					double a = source[at * source_channels + from];
					double b = source[next * source_channels + from];

					value += a + (b - a) * fraction;
					count++;
				}
			}
			if (count > 1)
				value /= count;
			if (value > 32767.0) value = 32767.0;
			if (value < -32768.0) value = -32768.0;
			output[frame * channels + channel] = (short)value;
		}
	}
	free(source);
	*samples = output;
	return frames;
}

/* ---------- Xbox ADPCM */

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

/* the nibble that brings the predictor nearest `sample`, and the state the
decoder will then have (dsound_sdl.c, ima_expand) */
static int ima_encode_sample(int sample, int *predictor, int *index)
{
	int step = ima_step_table[*index];
	int difference = sample - *predictor;
	int nibble = 0, delta = step >> 3;

	if (difference < 0)
	{
		nibble = 8;
		difference = -difference;
	}
	if (difference >= step) { nibble |= 4; difference -= step; delta += step; }
	if (difference >= step >> 1) { nibble |= 2; difference -= step >> 1; delta += step >> 1; }
	if (difference >= step >> 2) { nibble |= 1; delta += step >> 2; }
	*predictor += (nibble & 8) ? -delta : delta;
	if (*predictor > 32767) *predictor = 32767;
	if (*predictor < -32768) *predictor = -32768;
	*index += ima_index_table[nibble];
	if (*index < 0) *index = 0;
	if (*index > 88) *index = 88;
	return nibble;
}

unsigned long halo_xbox_adpcm_encode(const short *samples, unsigned long frames, int channels,
	unsigned char **encoded)
{
	unsigned long blocks = (frames + XBOX_ADPCM_BLOCK_FRAMES - 1) / XBOX_ADPCM_BLOCK_FRAMES;
	unsigned long block_bytes = XBOX_ADPCM_BLOCK_BYTES * (unsigned long)channels;
	unsigned char *output;
	int predictor[2] = { 0, 0 }, index[2] = { 0, 0 };
	unsigned long block;
	int channel;

	*encoded = NULL;
	if (channels < 1 || channels > 2)
		return 0;
	if (!blocks)
		blocks = 1;
	output = calloc(blocks, block_bytes);
	if (!output)
		return 0;
	for (block = 0; block < blocks; block++)
	{
		unsigned char *data = output + block * block_bytes;

		for (channel = 0; channel < channels; channel++)
		{
			unsigned char *header = data + channel * 4;
			unsigned long first_frame = block * XBOX_ADPCM_BLOCK_FRAMES;
			unsigned long group, byte;

			/* the block's first sample, exactly, in its header: the decoder
			starts the block from it (the step index carries over) */
			predictor[channel] = first_frame < frames ? samples[first_frame * (unsigned long)channels + (unsigned long)channel] : 0;
			header[0] = (unsigned char)(predictor[channel] & 0xff);
			header[1] = (unsigned char)((predictor[channel] >> 8) & 0xff);
			header[2] = (unsigned char)index[channel];
			header[3] = 0;
			for (group = 0; group < 8; group++)
			{
				unsigned char *nibbles = data + 4 * (unsigned long)channels + (group * (unsigned long)channels + (unsigned long)channel) * 4;

				for (byte = 0; byte < 4; byte++)
				{
					unsigned long frame = first_frame + 1 + group * 8 + byte * 2;
					int low = frame < frames ? samples[frame * (unsigned long)channels + (unsigned long)channel] : 0;
					int high = frame + 1 < frames ? samples[(frame + 1) * (unsigned long)channels + (unsigned long)channel] : 0;
					int first = ima_encode_sample(low, &predictor[channel], &index[channel]);
					int second = ima_encode_sample(high, &predictor[channel], &index[channel]);

					nibbles[byte] = (unsigned char)(first | (second << 4));
				}
			}
		}
	}
	*encoded = output;
	return blocks * block_bytes;
}
