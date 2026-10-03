/*
HOST_SDL.C

SDL3 on behalf of the guest (guest/runtime/guest_sdl.c). SDL objects are
64-bit pointers, which the guest cannot hold; it gets small handles into the
table here instead.

The guest calls these on its own threads, whose stacks (in guest memory) are
also the ones ART knows, so SDL may call into Java from them
(host_thread.c). SDL's audio thread is the exception: it has no guest stack,
so the audio callback is handed to a thread that has one.
*/

#include "host.h"
#include "halo_touch.h"

#include <SDL3/SDL.h>
#include <errno.h>
#include <pthread.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>
#ifndef HALO_VR
#include <jni.h>
#endif

/* Flat touch input is independent of SDL device enumeration and physical pad
 * ownership. Java writes a snapshot; only player one's input poll consumes it.
 * Pending down edges survive a tap between polls; cancellation discards them. */
#ifndef HALO_VR
static pthread_mutex_t touch_lock = PTHREAD_MUTEX_INITIALIZER;
static struct halo_touch_state touch_state;
static unsigned int touch_pressed;

static int touch_axis(int value)
{
	return value < -32767 ? -32767 : value > 32767 ? 32767 : value;
}

JNIEXPORT void JNICALL Java_com_halo_decomp_TouchControls_nativeState(
	JNIEnv *env, jclass type, jint lx, jint ly, jint rx, jint ry, jint buttons, jboolean reset)
{
	(void)env;
	(void)type;
	pthread_mutex_lock(&touch_lock);
	if (reset)
	{
		memset(&touch_state, 0, sizeof(touch_state));
		touch_pressed = 0;
	}
	else
	{
		unsigned int held = (unsigned int)buttons & 0xffffu;
		touch_pressed |= held & ~touch_state.buttons;
		touch_state.lx = touch_axis(lx);
		touch_state.ly = touch_axis(ly);
		touch_state.rx = touch_axis(rx);
		touch_state.ry = touch_axis(ry);
		touch_state.buttons = held;
	}
	pthread_mutex_unlock(&touch_lock);
}
#endif

void host_touch_read(void *buffer)
{
	struct halo_touch_state *state = buffer;
#ifndef HALO_VR
	pthread_mutex_lock(&touch_lock);
	*state = touch_state;
	state->buttons |= touch_pressed;
	touch_pressed = 0;
	pthread_mutex_unlock(&touch_lock);
#else
	memset(state, 0, sizeof(*state));
#endif
}

#define HANDLE_COUNT 256

enum handle_type
{
	_handle_free,
	_handle_window,
	_handle_context,
	_handle_gamepad,
	_handle_audio,
};

struct handle
{
	int type;
	void *object;
};

static struct handle handles[HANDLE_COUNT];
static pthread_mutex_t handle_lock = PTHREAD_MUTEX_INITIALIZER;

static uint32_t handle_new(int type, void *object)
{
	uint32_t index;

	if (!object)
		return 0;
	pthread_mutex_lock(&handle_lock);
	/* an object that already has a handle keeps it */
	for (index = 1; index < HANDLE_COUNT; index++)
	{
		if (handles[index].type == type && handles[index].object == object)
		{
			pthread_mutex_unlock(&handle_lock);
			return index;
		}
	}
	for (index = 1; index < HANDLE_COUNT; index++)
	{
		if (handles[index].type == _handle_free)
		{
			handles[index].type = type;
			handles[index].object = object;
			pthread_mutex_unlock(&handle_lock);
			return index;
		}
	}
	pthread_mutex_unlock(&handle_lock);
	host_logf(HOST_LOG_ERROR, "out of SDL handles");
	return 0;
}

static void *handle_get(uint32_t handle, int type)
{
	void *object = NULL;

	if (handle == 0 || handle >= HANDLE_COUNT)
		return NULL;
	pthread_mutex_lock(&handle_lock);
	if (handles[handle].type == type)
		object = handles[handle].object;
	pthread_mutex_unlock(&handle_lock);
	return object;
}

/* ---------- general */

int host_sdl_init(uint32_t flags)
{
	return SDL_Init((SDL_InitFlags)flags);
}

int host_sdl_set_hint(const char *name, const char *value)
{
	return SDL_SetHint(name, value);
}

void host_sdl_get_error(char *buffer, uint32_t size)
{
	SDL_strlcpy(buffer, SDL_GetError(), size);
}

int64_t host_sdl_ticks(void)
{
	return (int64_t)SDL_GetTicks();
}

int64_t host_sdl_thread_id(void)
{
	return (int64_t)SDL_GetCurrentThreadID();
}

/* ---------- video */

uint32_t host_sdl_create_window(const char *title, int width, int height, int64_t flags)
{
	return handle_new(_handle_window, SDL_CreateWindow(title, width, height, (SDL_WindowFlags)flags));
}

void host_sdl_window_size_in_pixels(uint32_t window, int *width, int *height)
{
	SDL_Window *object = handle_get(window, _handle_window);

	*width = 0;
	*height = 0;
	if (object)
		SDL_GetWindowSizeInPixels(object, width, height);
}

int host_sdl_set_relative_mouse(uint32_t window, int enabled)
{
	SDL_Window *object = handle_get(window, _handle_window);

	return object ? SDL_SetWindowRelativeMouseMode(object, enabled != 0) : 0;
}

int host_sdl_gl_set_attribute(int attribute, int value)
{
	return SDL_GL_SetAttribute((SDL_GLAttr)attribute, value);
}

uint32_t host_sdl_gl_create_context(uint32_t window)
{
	SDL_Window *object = handle_get(window, _handle_window);

	uint32_t context = object ? handle_new(_handle_context, SDL_GL_CreateContext(object)) : 0;

	/* the driver opens its trace markers with the context */
	host_gl_quiet_trace_markers();
	return context;
}

int host_sdl_gl_make_current(uint32_t window, uint32_t context)
{
	return SDL_GL_MakeCurrent(handle_get(window, _handle_window), handle_get(context, _handle_context));
}

int host_sdl_gl_set_swap_interval(int interval)
{
	return SDL_GL_SetSwapInterval(interval);
}

int host_sdl_gl_swap_window(uint32_t window)
{
	SDL_Window *object = handle_get(window, _handle_window);

	host_debug_frame_shown();
	return object ? SDL_GL_SwapWindow(object) : 0;
}

/* ---------- events */

int host_sdl_poll_event(void *event)
{
	SDL_Event host_event;

	if (!SDL_PollEvent(&host_event))
		return 0;
	/* the layouts agree except for the pointers of text, drop and user
	events, which the guest does not read */
	memcpy(event, &host_event, sizeof(host_event));
	return 1;
}

/* ---------- gamepads */

int host_sdl_get_gamepads(uint32_t *ids, int capacity)
{
	int count = 0, index;
	SDL_JoystickID *list = SDL_GetGamepads(&count);

	if (!list)
		return 0;
	if (count > capacity)
		count = capacity;
	for (index = 0; index < count; index++)
		ids[index] = list[index];
	SDL_free(list);
	return count;
}

uint32_t host_sdl_open_gamepad(uint32_t id)
{
	SDL_Gamepad *gamepad = SDL_OpenGamepad((SDL_JoystickID)id);

	if (gamepad)
		host_logf(HOST_LOG_INFO, "gamepad %u: %s (type %d, %04x:%04x)", (unsigned)id, SDL_GetGamepadName(gamepad),
			(int)SDL_GetGamepadType(gamepad), SDL_GetGamepadVendor(gamepad), SDL_GetGamepadProduct(gamepad));
	return handle_new(_handle_gamepad, gamepad);
}

uint32_t host_sdl_gamepad_from_id(uint32_t id)
{
	return handle_new(_handle_gamepad, SDL_GetGamepadFromID((SDL_JoystickID)id));
}

int host_sdl_gamepad_axis(uint32_t gamepad, int axis)
{
	SDL_Gamepad *object = handle_get(gamepad, _handle_gamepad);

	return object ? SDL_GetGamepadAxis(object, (SDL_GamepadAxis)axis) : 0;
}

int host_sdl_gamepad_button(uint32_t gamepad, int button)
{
	SDL_Gamepad *object = handle_get(gamepad, _handle_gamepad);

	return object ? SDL_GetGamepadButton(object, (SDL_GamepadButton)button) : 0;
}

int host_sdl_gamepad_type(uint32_t gamepad)
{
	SDL_Gamepad *object = handle_get(gamepad, _handle_gamepad);

	return object ? SDL_GetGamepadType(object) : SDL_GAMEPAD_TYPE_UNKNOWN;
}

int host_sdl_gamepad_vendor(uint32_t gamepad)
{
	SDL_Gamepad *object = handle_get(gamepad, _handle_gamepad);

	return object ? SDL_GetGamepadVendor(object) : 0;
}

int host_sdl_rumble_gamepad(uint32_t gamepad, uint32_t low, uint32_t high, uint32_t milliseconds)
{
	SDL_Gamepad *object = handle_get(gamepad, _handle_gamepad);

	return object ? SDL_RumbleGamepad(object, (Uint16)low, (Uint16)high, milliseconds) : 0;
}

/* ---------- audio */

/* SDL calls audio_callback on its own audio thread, which cannot run guest
code; the stream's thread (audio_thread), which can, runs the guest's
callback instead. It runs it ahead: it keeps a device buffer's worth of the
guest's mix ready in the binding's buffer (as much as the device's largest
ask), and audio_callback hands the device what is ready and wakes it to mix
the next. The device's thread so never waits on the guest's mixing (once it
waited for every buffer, and played a gap - a crackle - whenever the mixing
thread ran late on a headset whose cores the game keeps busy); only when
too little is ready does it wait, at most a buffer's time, and what it then
lacks is counted (an underrun) and played as silence.

The guest's callback puts its audio into the stream from audio_thread
(SDL_PutAudioStreamData); that is kept in the binding's buffer (audio_keep)
for audio_callback, which runs with SDL's lock on the stream held, to put
in. */

/* the most kept ready: 4096 frames of stereo float (85 ms at 48 kHz) */
#define AUDIO_MAXIMUM_LEAD_BYTES (4096 * 8)

struct audio_binding
{
	uint32_t handle;
	uint32_t callback;
	uint32_t userdata;
	/* the guest's frames: their bytes, and how many play a millisecond */
	int frame_bytes;
	double frames_per_ms;
	pthread_mutex_t lock;
	/* the mixing thread woken (to mix), the device's woken (mixed) */
	pthread_cond_t requested;
	pthread_cond_t mixed;
	/* how much to keep ready (the device's largest ask), and how much the
	device's thread is waiting for (0: none) */
	int lead;
	int wanted;
	/* what is ready, the guest's mix, in the order it mixed it */
	unsigned char *buffer;
	int buffer_length;
	int buffer_size;
	/* what the device's thread hands over, copied out of the buffer */
	unsigned char *handing;
	int handing_size;
	/* statistics (the log, every ten seconds): the device's asks, how many
	found too little ready and waited (and how long), how many were still
	short after (underruns, and the silence played), how full the buffer was
	at an ask at the least, and the mixes */
	unsigned long asks, waits, underruns, mixes;
	double wait_ms_total, wait_ms_max, silence_ms, mix_ms_total, mix_ms_max;
	int ready_least;
	struct timespec statistics_start;
};

static double audio_ms(const struct timespec *from, const struct timespec *to)
{
	return (double)(to->tv_sec - from->tv_sec) * 1000.0 + (double)(to->tv_nsec - from->tv_nsec) / 1000000.0;
}

/* the binding whose callback this thread is running, if any */
static __thread struct audio_binding *calling_back;

static void *audio_thread(void *context)
{
	struct audio_binding *binding = context;

	/* The device plays what this thread mixes: at an ordinary priority, on a
	headset whose game and render threads keep its cores busy, it runs late.
	Android lets an app's threads take its urgent audio priority. */
	if (setpriority(PRIO_PROCESS, 0, -19) == 0)
		host_logf(HOST_LOG_INFO, "[audio] the mixing thread runs at urgent audio priority, a buffer ahead of the device");
	else
		host_logf(HOST_LOG_WARN, "[audio] the mixing thread cannot take urgent audio priority (%s)", strerror(errno));
	clock_gettime(CLOCK_MONOTONIC, &binding->statistics_start);
	pthread_mutex_lock(&binding->lock);
	for (;;)
	{
		int want;
		struct timespec before, after;
		double mixed;

		/* (the lead is 0 until the device first asks: nothing is mixed
		before it plays) */
		while (binding->buffer_length >= binding->lead && binding->buffer_length >= binding->wanted)
			pthread_cond_wait(&binding->requested, &binding->lock);
		want = (binding->wanted > binding->lead ? binding->wanted : binding->lead) - binding->buffer_length;
		/* (whole frames) */
		want = (want + binding->frame_bytes - 1) / binding->frame_bytes * binding->frame_bytes;
		pthread_mutex_unlock(&binding->lock);
		clock_gettime(CLOCK_MONOTONIC, &before);
		calling_back = binding;
		host_call_guest(binding->callback, binding->userdata, binding->handle, (uint32_t)want, (uint32_t)want);
		calling_back = NULL;
		clock_gettime(CLOCK_MONOTONIC, &after);
		mixed = audio_ms(&before, &after);
		pthread_mutex_lock(&binding->lock);
		binding->mixes++;
		binding->mix_ms_total += mixed;
		if (mixed > binding->mix_ms_max)
			binding->mix_ms_max = mixed;
		pthread_cond_signal(&binding->mixed);
		/* (logged with the lock let go, so the device's thread never waits
		on the log) */
		if (audio_ms(&binding->statistics_start, &after) >= 10000.0 && binding->asks)
		{
			unsigned long asks = binding->asks, waits = binding->waits, underruns = binding->underruns;
			unsigned long mixes = binding->mixes;
			double wait_average = binding->waits ? binding->wait_ms_total / binding->waits : 0.0;
			double wait_max = binding->wait_ms_max, silence = binding->silence_ms;
			double mix_average = mixes ? binding->mix_ms_total / mixes : 0.0, mix_max = binding->mix_ms_max;
			int lead = binding->lead, least = binding->ready_least;

			binding->asks = binding->waits = binding->underruns = binding->mixes = 0;
			binding->wait_ms_total = binding->wait_ms_max = binding->silence_ms = 0.0;
			binding->mix_ms_total = binding->mix_ms_max = 0.0;
			binding->ready_least = -1;
			binding->statistics_start = after;
			pthread_mutex_unlock(&binding->lock);
			host_logf(underruns ? HOST_LOG_WARN : HOST_LOG_INFO,
				"[audio] host: %lu device asks in 10 s; %lu found too little ready and waited (%.2f ms average, "
				"%.2f longest); %lu underruns (%.1f ms of silence played); ready at an ask %d bytes at the least, "
				"%d kept ready; %lu mixes, %.2f ms average, %.2f longest",
				asks, waits, wait_average, wait_max, underruns, silence, least, lead, mixes, mix_average, mix_max);
			pthread_mutex_lock(&binding->lock);
		}
	}
	return NULL;
}

static void SDLCALL audio_callback(void *userdata, SDL_AudioStream *stream, int additional, int total)
{
	struct audio_binding *binding = userdata;
	int take;

	(void)total;
	if (additional <= 0)
		return;
	pthread_mutex_lock(&binding->lock);
	binding->asks++;
	if (binding->ready_least < 0 || binding->buffer_length < binding->ready_least)
		binding->ready_least = binding->buffer_length;
	if (additional > binding->lead)
		binding->lead = additional < AUDIO_MAXIMUM_LEAD_BYTES ? additional : AUDIO_MAXIMUM_LEAD_BYTES;
	if (binding->buffer_length < additional)
	{
		/* too little ready: the mixing thread is woken (if it was not) and
		waited for, at most the time the ask plays for */
		struct timespec before, deadline, after;
		double limit_ms = additional / (double)binding->frame_bytes / binding->frames_per_ms;
		double waited;

		binding->waits++;
		binding->wanted = additional;
		pthread_cond_signal(&binding->requested);
		clock_gettime(CLOCK_MONOTONIC, &before);
		deadline = before;
		deadline.tv_nsec += (long)(limit_ms * 1000000.0);
		while (deadline.tv_nsec >= 1000000000L)
		{
			deadline.tv_nsec -= 1000000000L;
			deadline.tv_sec++;
		}
		while (binding->buffer_length < additional)
		{
			if (pthread_cond_timedwait(&binding->mixed, &binding->lock, &deadline) == ETIMEDOUT)
				break;
		}
		binding->wanted = 0;
		clock_gettime(CLOCK_MONOTONIC, &after);
		waited = audio_ms(&before, &after);
		binding->wait_ms_total += waited;
		if (waited > binding->wait_ms_max)
			binding->wait_ms_max = waited;
	}
	take = binding->buffer_length < additional ? binding->buffer_length : additional;
	take -= take % binding->frame_bytes;
	if (take < additional)
	{
		binding->underruns++;
		binding->silence_ms += (additional - take) / (double)binding->frame_bytes / binding->frames_per_ms;
	}
	if (take > binding->handing_size)
	{
		unsigned char *handing = SDL_realloc(binding->handing, (size_t)take);

		if (handing)
		{
			binding->handing = handing;
			binding->handing_size = take;
		}
		else
		{
			take = 0;
		}
	}
	if (take)
	{
		memcpy(binding->handing, binding->buffer, (size_t)take);
		binding->buffer_length -= take;
		memmove(binding->buffer, binding->buffer + take, (size_t)binding->buffer_length);
	}
	/* the next mixed while the device plays this */
	pthread_cond_signal(&binding->requested);
	pthread_mutex_unlock(&binding->lock);
	if (take)
		SDL_PutAudioStreamData(stream, binding->handing, take);
}

/* audio the guest puts into its stream during the stream's callback, for
audio_callback to put in; 1 on success */
static int audio_keep(struct audio_binding *binding, const void *data, int length)
{
	if (length < 0)
		return 0;
	pthread_mutex_lock(&binding->lock);
	if (binding->buffer_length + length > binding->buffer_size)
	{
		int size = (binding->buffer_length + length) * 2;
		unsigned char *buffer = SDL_realloc(binding->buffer, (size_t)size);

		if (!buffer)
		{
			pthread_mutex_unlock(&binding->lock);
			return 0;
		}
		binding->buffer = buffer;
		binding->buffer_size = size;
	}
	memcpy(binding->buffer + binding->buffer_length, data, (size_t)length);
	binding->buffer_length += length;
	pthread_mutex_unlock(&binding->lock);
	return 1;
}

uint32_t host_sdl_open_audio_stream(uint32_t device, const void *spec, uint32_t callback, uint32_t userdata)
{
	struct audio_binding *binding = SDL_calloc(1, sizeof(*binding));
	SDL_AudioStream *stream;

	binding->callback = callback;
	binding->userdata = userdata;
	{
		const SDL_AudioSpec *asked = spec;

		binding->frame_bytes = SDL_AUDIO_FRAMESIZE(*asked) > 0 ? (int)SDL_AUDIO_FRAMESIZE(*asked) : 8;
		binding->frames_per_ms = asked->freq > 0 ? asked->freq / 1000.0 : 48.0;
	}
	binding->ready_least = -1;
	pthread_mutex_init(&binding->lock, NULL);
	pthread_cond_init(&binding->requested, NULL);
	/* (its waits are timed by the monotonic clock) */
	{
		pthread_condattr_t attributes;

		pthread_condattr_init(&attributes);
		pthread_condattr_setclock(&attributes, CLOCK_MONOTONIC);
		pthread_cond_init(&binding->mixed, &attributes);
		pthread_condattr_destroy(&attributes);
	}
	stream = SDL_OpenAudioDeviceStream((SDL_AudioDeviceID)device, spec,
		callback ? audio_callback : NULL, binding);
	if (!stream)
	{
		SDL_free(binding);
		return 0;
	}
	{
		SDL_AudioSpec device_spec;
		int sample_frames = 0;
		const SDL_AudioSpec *asked = spec;

		if (SDL_GetAudioDeviceFormat(SDL_GetAudioStreamDevice(stream), &device_spec, &sample_frames))
		{
			host_logf(HOST_LOG_INFO, "[audio] device '%s' (driver %s): %d Hz, %d channels, format 0x%x, %d frames a "
				"buffer (%.1f ms); the game mixes %d Hz, %d channels, format 0x%x",
				SDL_GetAudioDeviceName(SDL_GetAudioStreamDevice(stream)), SDL_GetCurrentAudioDriver(),
				device_spec.freq, device_spec.channels, (unsigned)device_spec.format, sample_frames,
				device_spec.freq > 0 ? sample_frames * 1000.0 / device_spec.freq : 0.0,
				asked->freq, asked->channels, (unsigned)asked->format);
		}
	}
	/* the device starts paused, so no callback can run before this */
	binding->handle = handle_new(_handle_audio, stream);
	if (callback && host_native_thread_create(audio_thread, binding, 256 * 1024) != 0)
		host_fatal("cannot start the audio thread");
	return binding->handle;
}

int host_sdl_put_audio_stream_data(uint32_t stream, const void *data, int length)
{
	SDL_AudioStream *object = handle_get(stream, _handle_audio);

	if (!object)
		return 0;
	if (calling_back && calling_back->handle == stream)
		return audio_keep(calling_back, data, length);
	return SDL_PutAudioStreamData(object, data, length);
}

int host_sdl_resume_audio_stream_device(uint32_t stream)
{
	SDL_AudioStream *object = handle_get(stream, _handle_audio);

	return object ? SDL_ResumeAudioStreamDevice(object) : 0;
}

/* ---------- the clipboard (internet play's invite links) */

int host_sdl_set_clipboard_text(const char *text)
{
	return SDL_SetClipboardText(text) ? 1 : 0;
}

void host_sdl_get_clipboard_text(char *buffer, uint32_t size)
{
	char *text = SDL_GetClipboardText();

	SDL_strlcpy(buffer, text ? text : "", size);
	SDL_free(text);
}

int host_sdl_show_toast(const char *message, int duration, int gravity, int x, int y)
{
	return SDL_ShowAndroidToast(message, duration, gravity, x, y) ? 1 : 0;
}

/* ---------- a message for the player (a host of another network version) */

int host_sdl_show_simple_message_box(uint32_t flags, const char *title, const char *message)
{
	return SDL_ShowSimpleMessageBox((SDL_MessageBoxFlags)flags, title, message, NULL) ? 1 : 0;
}
