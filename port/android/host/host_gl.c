/*
HOST_GL.C

OpenGL ES for the guest. Its generated entry points (guest_gl.c) import
hostgl_<function>, resolved here to the driver's function; the arguments
already have host types by then. Only strings need copying back.
*/

#include "host.h"

#include <EGL/egl.h>
#include <GLES3/gl32.h>
#include <dlfcn.h>
#include <dirent.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* Valve's Mesa (the Steam Frame's Lepton) writes a marker to the kernel's
trace_marker around every flush and context switch, a couple of hundred a
frame, whether or not anything is tracing. The descriptors it holds open on
that file are pointed at /dev/null instead (not closed: a reused descriptor
would take the markers somewhere else). Returns how many were. */
int host_gl_quiet_trace_markers(void)
{
	DIR *directory = opendir("/proc/self/fd");
	struct dirent *entry;
	int quieted = 0, null_fd;

	if (!directory)
		return 0;
	null_fd = open("/dev/null", O_WRONLY | O_CLOEXEC);
	while (null_fd >= 0 && (entry = readdir(directory)) != NULL)
	{
		char link[64], target[256];
		ssize_t length;
		int fd = atoi(entry->d_name);

		if (entry->d_name[0] < '0' || entry->d_name[0] > '9' || fd == null_fd)
			continue;
		snprintf(link, sizeof(link), "/proc/self/fd/%d", fd);
		length = readlink(link, target, sizeof(target) - 1);
		if (length <= 0)
			continue;
		target[length] = 0;
		if (strstr(target, "tracing/trace_marker") && dup3(null_fd, fd, O_CLOEXEC) == fd)
			quieted++;
	}
	if (null_fd >= 0)
		close(null_fd);
	closedir(directory);
	if (quieted)
		host_logf(HOST_LOG_INFO, "trace markers: %d descriptors to /dev/null", quieted);
	return quieted;
}

void *host_gl_resolve(const char *name)
{
	static void *library;
	void *function = NULL;

	if (!library)
		library = dlopen("libGLESv3.so", RTLD_NOW | RTLD_GLOBAL);
	if (library)
		function = dlsym(library, name);
	if (!function)
		function = (void *)eglGetProcAddress(name);
	return function;
}

void host_gl_get_string(uint32_t name, int index, char *buffer, uint32_t size)
{
	const GLubyte *text = index >= 0 ? glGetStringi(name, (GLuint)index) : glGetString(name);

	if (!size)
		return;
	buffer[0] = 0;
	if (text)
	{
		strncpy(buffer, (const char *)text, size - 1);
		buffer[size - 1] = 0;
	}
}

int host_gl_has_extension(const char *name)
{
	GLint count = 0, index;

	glGetIntegerv(GL_NUM_EXTENSIONS, &count);
	for (index = 0; index < count; index++)
	{
		const char *extension = (const char *)glGetStringi(GL_EXTENSIONS, (GLuint)index);

		if (extension && !strcmp(extension, name))
			return 1;
	}
	return 0;
}

/* one 32-bit word of a buffer object (the visibility test counters of
d3d8_gl.c); ES has no glGetBufferSubData, and the mapping it offers
instead is a host pointer */
uint32_t host_gl_read_buffer_word(uint32_t buffer, uint32_t offset)
{
	uint32_t value = 0;
	GLint previous = 0;
	const void *mapping;

	glGetIntegerv(GL_ATOMIC_COUNTER_BUFFER_BINDING, &previous);
	glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, buffer);
	mapping = glMapBufferRange(GL_ATOMIC_COUNTER_BUFFER, offset, sizeof(value), GL_MAP_READ_BIT);
	if (mapping)
	{
		memcpy(&value, mapping, sizeof(value));
		glUnmapBuffer(GL_ATOMIC_COUNTER_BUFFER);
	}
	glBindBuffer(GL_ATOMIC_COUNTER_BUFFER, (GLuint)previous);
	return value;
}

/* size bytes of a buffer object from offset, waiting for the GPU once for
them all (d3d8_gl.c reads every visibility counter this way, once a frame:
each map waits for the GPU's queue to drain, and on Mesa's Zink also
flushes it) */
void host_gl_read_buffer(uint32_t buffer, uint32_t offset, uint32_t size, void *data)
{
	GLint previous = 0;
	const void *mapping;

	glGetIntegerv(GL_COPY_READ_BUFFER_BINDING, &previous);
	glBindBuffer(GL_COPY_READ_BUFFER, buffer);
	mapping = glMapBufferRange(GL_COPY_READ_BUFFER, offset, size, GL_MAP_READ_BIT);
	if (mapping)
	{
		memcpy(data, mapping, size);
		glUnmapBuffer(GL_COPY_READ_BUFFER);
	}
	else
	{
		memset(data, 0, size);
	}
	glBindBuffer(GL_COPY_READ_BUFFER, (GLuint)previous);
}

/* The renderer streams each frame's vertices and indices into the next of
a ring of buffers (d3d8_gl.c). A fence marks the end of each frame's work,
and a buffer is written again only once the GPU has passed the fence of the
frame that last used it: drivers queue several frames, and a draw still
waiting to run would otherwise read a later frame's vertices. */
#define FRAME_FENCE_SLOTS 8

static GLsync frame_fences[FRAME_FENCE_SLOTS];

void host_gl_fence_frame(uint32_t slot)
{
	if (slot >= FRAME_FENCE_SLOTS)
		return;
	if (frame_fences[slot])
		glDeleteSync(frame_fences[slot]);
	frame_fences[slot] = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0);
}

void host_gl_wait_frame(uint32_t slot)
{
	if (slot >= FRAME_FENCE_SLOTS || !frame_fences[slot])
		return;
	/* at most a second: a lost context must not hang the game */
	glClientWaitSync(frame_fences[slot], GL_SYNC_FLUSH_COMMANDS_BIT, 1000000000ull);
	glDeleteSync(frame_fences[slot]);
	frame_fences[slot] = NULL;
}

/* 1 once the GPU has passed the work fenced for the slot (or nothing is
fenced there), without waiting */
int host_gl_frame_done(uint32_t slot)
{
	GLenum status;

	if (slot >= FRAME_FENCE_SLOTS || !frame_fences[slot])
		return 1;
	status = glClientWaitSync(frame_fences[slot], 0, 0);
	return status == GL_ALREADY_SIGNALED || status == GL_CONDITION_SATISFIED;
}

/* Persistently mapped buffers (GL_EXT_buffer_storage): mapped once, so a
write is a memcpy into memory the GPU reads as it is (coherent), with no GL
call - on the Steam Frame's Zink each map and unmap otherwise synchronizes
the threaded context and flushes. The renderer's ring of stream buffers
(d3d8_gl.c) keeps the GPU off the ranges it writes, as host_gl_buffer_write
promises. */
#define PERSISTENT_BUFFERS 16

static struct
{
	GLuint buffer;
	uint32_t size;
	unsigned char *mapping;
} persistent[PERSISTENT_BUFFERS];

/* gives the buffer bound to target size bytes of storage, mapped for good;
1 on success, 0 when the driver cannot (the buffer is then left without
storage: give it some the ordinary way) */
int host_gl_buffer_persist(uint32_t target, uint32_t size)
{
	static void (*buffer_storage)(GLenum, GLsizeiptr, const void *, GLbitfield);
	const GLbitfield flags = GL_MAP_WRITE_BIT | 0x0040 /* PERSISTENT */ | 0x0080 /* COHERENT */;
	GLint buffer = 0;
	GLenum binding;
	int slot;

	if (!buffer_storage)
		buffer_storage = (void (*)(GLenum, GLsizeiptr, const void *, GLbitfield))eglGetProcAddress("glBufferStorageEXT");
	if (!buffer_storage)
		return 0;
	binding = target == GL_ARRAY_BUFFER ? GL_ARRAY_BUFFER_BINDING :
		target == GL_ELEMENT_ARRAY_BUFFER ? GL_ELEMENT_ARRAY_BUFFER_BINDING : GL_COPY_WRITE_BUFFER_BINDING;
	glGetIntegerv(binding, &buffer);
	for (slot = 0; slot < PERSISTENT_BUFFERS && persistent[slot].buffer; slot++)
		;
	if (!buffer || slot == PERSISTENT_BUFFERS)
		return 0;
	buffer_storage(target, size, NULL, flags);
	persistent[slot].mapping = glMapBufferRange(target, 0, size, flags);
	if (!persistent[slot].mapping)
		return 0;
	persistent[slot].buffer = (GLuint)buffer;
	persistent[slot].size = size;
	return 1;
}

/* writes into a persistently mapped buffer; 0 if it is not one */
int host_gl_buffer_write_persistent(uint32_t buffer, uint32_t offset, uint32_t size, const void *data)
{
	int slot;

	for (slot = 0; slot < PERSISTENT_BUFFERS && persistent[slot].buffer; slot++)
	{
		if (persistent[slot].buffer == buffer)
		{
			if (offset > persistent[slot].size || size > persistent[slot].size - offset)
				return 0;
			memcpy(persistent[slot].mapping + offset, data, size);
			return 1;
		}
	}
	return 0;
}

/* writes data into the buffer bound to target. The renderer streams a
range per draw, so a frame makes hundreds of these, and the cost per call
rather than per byte is what a frame is made of.

GL_MAP_INVALIDATE_RANGE_BIT was what made that cost ruinous. It tells the
driver the range's previous contents are undefined and must be discarded,
which is the very work GL_MAP_UNSYNCHRONIZED_BIT exists to avoid: that one
promises the caller that no queued draw is reading the range. Asked to do
both, Adreno pays for the discard - about 0.85 ms a call on a Galaxy Z
Flip 4, whatever the range written - and with a few hundred calls a frame
that came to 96% of a 550 ms frame at 1.8 fps, with the GPU idle throughout.

Without the invalidation the same call is well under a microsecond and the
same game runs at the display's refresh rate. The promise unsynchronized
makes still holds: the renderer only writes ranges that no queued draw reads,
because host_gl_wait_frame releases the ring slot first. */
void host_gl_buffer_write(uint32_t target, uint32_t offset, uint32_t size, const void *data)
{
	void *mapping = glMapBufferRange(target, offset, size,
		GL_MAP_WRITE_BIT | GL_MAP_UNSYNCHRONIZED_BIT);

	if (!mapping)
	{
		glBufferSubData(target, offset, size, data);
		return;
	}
	memcpy(mapping, data, size);
	glUnmapBuffer(target);
}
