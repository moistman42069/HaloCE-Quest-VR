/*
HOST_DEBUG.C

Finding where the guest spends its time, or where it hangs, on a device
without root, where debuggerd cannot attach.

- The sampler: with sample_seconds in config.toml's [debug], every guest
  thread is interrupted that often and its program counter, link register
  and frame chain are logged.
- The watchdog, always: when no frame has been shown for four seconds (the
  headset's or the window's, host_debug_frame_shown), every guest thread's
  stack is logged the same way, again every fifteen seconds while it lasts,
  and the end of the stall too. A map loading, or converting its sounds,
  stalls as well; its stacks say so.

The addresses symbolize against the APK's assets/halo_guest.elf
(llvm-symbolizer --obj=halo_guest.elf 0x...). A signal handler only records
a thread's stack; the thread that sent the signals logs them, since logging
takes locks a handler must not.
*/

#include "host.h"

#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <ucontext.h>
#include <unistd.h>

#define MAXIMUM_THREADS 64
#define SAMPLE_SIGNAL SIGURG
#define STALL_MS 4000
#define STALL_REPEAT_MS 15000

static pid_t guest_threads[MAXIMUM_THREADS];
static pthread_mutex_t threads_lock = PTHREAD_MUTEX_INITIALIZER;
/* one interruption's stacks, recorded by the handler, logged by the sender */
static pthread_mutex_t sampling_lock = PTHREAD_MUTEX_INITIALIZER;
static char stack_lines[MAXIMUM_THREADS][400];
static volatile int stack_count;
static int handler_installed;
static volatile int64_t last_frame_ms;

static int64_t now_ms(void)
{
	struct timespec now;

	clock_gettime(CLOCK_MONOTONIC, &now);
	return (int64_t)now.tv_sec * 1000 + now.tv_nsec / 1000000;
}

void host_debug_frame_shown(void)
{
	last_frame_ms = now_ms();
}

void host_debug_thread_started(void)
{
	int index;

	pthread_mutex_lock(&threads_lock);
	for (index = 0; index < MAXIMUM_THREADS; index++)
	{
		if (!guest_threads[index])
		{
			guest_threads[index] = gettid();
			break;
		}
	}
	pthread_mutex_unlock(&threads_lock);
}

void host_debug_thread_exited(void)
{
	pid_t self = gettid();
	int index;

	pthread_mutex_lock(&threads_lock);
	for (index = 0; index < MAXIMUM_THREADS; index++)
	{
		if (guest_threads[index] == self)
			guest_threads[index] = 0;
	}
	pthread_mutex_unlock(&threads_lock);
}

static void sample_handler(int signal_number, siginfo_t *information, void *context)
{
	const ucontext_t *ucontext = context;
	const struct sigcontext *registers = (const struct sigcontext *)&ucontext->uc_mcontext;
	int slot = __sync_fetch_and_add(&stack_count, 1);
	char *line;
	int length, depth;
	uint64_t fp = registers->regs[29];

	(void)signal_number;
	(void)information;
	if (slot < 0 || slot >= MAXIMUM_THREADS)
		return;
	line = stack_lines[slot];
	length = snprintf(line, sizeof(stack_lines[slot]), "tid %d: pc %llx lr %llx", gettid(),
		(unsigned long long)registers->pc, (unsigned long long)registers->regs[30]);
	for (depth = 0; depth < 20 && fp && fp < 0x100000000ULL && !(fp & 7) && host_low_owns(fp, 16) &&
		length < (int)sizeof(stack_lines[slot]) - 20; depth++)
	{
		const uint64_t *frame = (const uint64_t *)fp;

		length += snprintf(line + length, sizeof(stack_lines[slot]) - length, " %llx", (unsigned long long)frame[1]);
		if (frame[0] <= fp)
			break;
		fp = frame[0];
	}
}

static void install_handler(void)
{
	struct sigaction action;

	if (handler_installed)
		return;
	memset(&action, 0, sizeof(action));
	action.sa_sigaction = sample_handler;
	action.sa_flags = SA_SIGINFO | SA_RESTART;
	sigemptyset(&action.sa_mask);
	sigaction(SAMPLE_SIGNAL, &action, NULL);
	handler_installed = 1;
}

/* interrupts every guest thread, then logs their stacks under `title` */
static void sample_all(const char *title)
{
	pid_t threads[MAXIMUM_THREADS];
	int index, count;

	pthread_mutex_lock(&sampling_lock);
	pthread_mutex_lock(&threads_lock);
	memcpy(threads, guest_threads, sizeof(threads));
	pthread_mutex_unlock(&threads_lock);
	stack_count = 0;
	for (index = 0; index < MAXIMUM_THREADS; index++)
	{
		if (threads[index])
			syscall(SYS_tgkill, getpid(), threads[index], SAMPLE_SIGNAL);
	}
	/* (the handlers run at once; a moment for all of them) */
	usleep(50 * 1000);
	count = stack_count < MAXIMUM_THREADS ? stack_count : MAXIMUM_THREADS;
	if (title)
		host_logf(HOST_LOG_WARN, "%s: %d guest threads", title, count);
	for (index = 0; index < count; index++)
		host_logf(HOST_LOG_INFO, "  %s", stack_lines[index]);
	pthread_mutex_unlock(&sampling_lock);
}

static void *sampler(void *context)
{
	unsigned int milliseconds = (unsigned int)(uintptr_t)context;

	for (;;)
	{
		usleep(milliseconds * 1000u);
		sample_all(NULL);
	}
	return NULL;
}

void host_debug_start_sampler(const char *setting)
{
	pthread_t thread;
	/* fractions of a second too: a profile wants many samples */
	unsigned int milliseconds = setting ? (unsigned int)(atof(setting) * 1000.0) : 0;

	if (!milliseconds)
		return;
	install_handler();
	if (pthread_create(&thread, NULL, sampler, (void *)(uintptr_t)milliseconds) == 0)
		pthread_detach(thread);
	host_logf(HOST_LOG_INFO, "sampling guest threads every %u ms", milliseconds);
}

static void *watchdog(void *context)
{
	int64_t stall_reported_at = 0;

	(void)context;
	for (;;)
	{
		int64_t now, last;

		usleep(1000 * 1000);
		last = last_frame_ms;
		now = now_ms();
		/* (only once frames have been shown: the start is slow anyway) */
		if (!last)
			continue;
		if (now - last >= STALL_MS)
		{
			if (!stall_reported_at || now - stall_reported_at >= STALL_REPEAT_MS)
			{
				char title[128];

				snprintf(title, sizeof(title), "[watchdog] no frame shown for %.1f s (a hang, or a map loading)",
					(now - last) / 1000.0);
				sample_all(title);
				stall_reported_at = now;
			}
		}
		else if (stall_reported_at)
		{
			host_logf(HOST_LOG_INFO, "[watchdog] frames are shown again");
			stall_reported_at = 0;
		}
	}
	return NULL;
}

void host_debug_start_watchdog(void)
{
	pthread_t thread;

	install_handler();
	if (pthread_create(&thread, NULL, watchdog, NULL) == 0)
		pthread_detach(thread);
}
