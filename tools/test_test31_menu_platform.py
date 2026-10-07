"""Sanitizer tests for production menu platform helpers; no SDL/game launch.

SDL events/window/clipboard/time are deterministic doubles. The capture,
settling, key state, config refresh and window safety logic is real source.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "port/linux/src/sdl_platform.c").read_text()
header = (ROOT / "port/linux/src/sdl_platform.h").read_text()

def fn(name):
    match = re.search(r'^(?:static )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', source, re.M)
    assert match, name
    start = source.index('{', match.start())
    end, depth = start + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'

pump = fn('platform_pump_events')
assert 'if (binding_capture_event(&event))' in pump
assert pump.index('if (binding_capture_event(&event))') < pump.index('switch (event.type)')
assert 'mouse_buttons_down = 0;' in pump
assert 'binding_clear_pending();' in pump[pump.index('case SDL_EVENT_WINDOW_FOCUS_LOST:'):]
assert 'platform_quit_requested' in pump
assert 'vr_initialize();' in fn('platform_video_initialize')
assert 'SDL_GL_CreateContext' in fn('platform_video_initialize')
assert not any(s in fn('platform_display_apply') for s in ('SDL_CreateWindow', 'SDL_GL_CreateContext', 'vr_initialize', 'SDL_SetWindowSize', 'SDL_SetWindowFullscreen'))

shim = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
typedef int BOOL;
typedef unsigned char BYTE;
typedef char CHAR;
typedef uint64_t Uint64;
typedef int SDL_ThreadID;
typedef void SDL_Window;
#define FALSE 0
#define TRUE 1
#define SDL_SCANCODE_COUNT 512
#define SDL_SCANCODE_UNKNOWN 0
#define SDL_SCANCODE_A 4
#define SDL_SCANCODE_RETURN 40
#define SDL_SCANCODE_ESCAPE 41
#define SDL_SCANCODE_DELETE 76
#define SDL_SCANCODE_F11 68
#define SDL_SCANCODE_F12 69
enum { SDL_EVENT_KEY_DOWN=1,SDL_EVENT_KEY_UP,SDL_EVENT_MOUSE_BUTTON_DOWN,
 SDL_EVENT_MOUSE_BUTTON_UP,SDL_EVENT_MOUSE_WHEEL,SDL_EVENT_MOUSE_MOTION,
 SDL_EVENT_WINDOW_FOCUS_LOST,SDL_EVENT_GAMEPAD_ADDED,SDL_EVENT_FINGER_DOWN };
typedef struct { int type; struct {int scancode;bool down,repeat;} key;
 struct {unsigned button;bool down;} button;struct {float y;} wheel; } SDL_Event;
static int locks;
static void pthread_mutex_lock(int *lock){(void)lock;assert(!locks);locks++;}
static void pthread_mutex_unlock(int *lock){(void)lock;assert(locks==1);locks--;}
static Uint64 now=1;
static Uint64 SDL_GetTicks(void){return now;}
static int generation, vsync=1, interpolation=1;
static unsigned long config_changes(void){return generation;}
static int config_boolean(const char *name){return !strcmp(name,"display.interpolation")?interpolation:vsync;}
static int window_w=1920,window_h=1080,thread=7,swap_calls,last_interval,clipboard_frees;
static void SDL_GetWindowSizeInPixels(void *w,int *x,int *y){assert(w);*x=window_w;*y=window_h;}
static int SDL_GetCurrentThreadID(void){return thread;}
static void SDL_GL_SetSwapInterval(int value){swap_calls++;last_interval=value;}
static const char *clipboard="hello";
static char written_clipboard[100];
static char *SDL_GetClipboardText(void){return clipboard?strdup(clipboard):NULL;}
static void SDL_free(void *p){if(p)clipboard_frees++;free(p);}
static void SDL_SetClipboardText(const char *p){snprintf(written_clipboard,sizeof(written_clipboard),"%s",p);}
'''

globals_c = r'''
static SDL_Window *platform_window=(void*)1;
static SDL_ThreadID platform_event_thread=7;
static BOOL platform_quit_requested;
static int input_lock;
static struct platform_input_state input_state;
static unsigned char keys_pressed[SDL_SCANCODE_COUNT];
static unsigned char mouse_buttons_pressed[PLATFORM_MOUSE_BUTTON_COUNT];
#ifndef HALO_ANDROID
static struct platform_ui_pointer ui_pointer;
static float ui_pointer_wheel;
#endif
enum { _binding_capture_idle, _binding_capture_waiting, _binding_capture_taken };
static int binding_capture,binding_capture_result,binding_captured_input;
static BOOL binding_settling;
static Uint64 binding_taken_ms,binding_polled_ms;
static unsigned mouse_buttons_down;
#define BINDING_ABANDONED_MS 500
#define BINDING_UNCLAIMED_MS 2000
static unsigned long keystroke_head,keystroke_count;
'''

checks = r'''
static BOOL event(int type,int code,int repeat){
 SDL_Event e={0};e.type=type;
 if(type==SDL_EVENT_KEY_DOWN||type==SDL_EVENT_KEY_UP){e.key.scancode=code;e.key.down=type==SDL_EVENT_KEY_DOWN;e.key.repeat=repeat;}
 if(type==SDL_EVENT_MOUSE_BUTTON_DOWN||type==SDL_EVENT_MOUSE_BUTTON_UP){e.button.button=code;e.button.down=type==SDL_EVENT_MOUSE_BUTTON_DOWN;}
 if(type==SDL_EVENT_MOUSE_WHEEL)e.wheel.y=(float)code;
 pthread_mutex_lock(&input_lock);BOOL consumed=binding_capture_event(&e);pthread_mutex_unlock(&input_lock);return consumed;
}
int main(void){
 struct platform_input_state snapshot;int input=-99;long w[2]={-1,-2},h[2]={-1,-2};char text[5];
 assert(platform_display_resolutions(w,h,2)==1&&w[0]==1920&&h[0]==1080&&w[1]==-2);
 assert(platform_window_sizes(w,h,2)==1);
 assert(!platform_display_resolutions(NULL,h,1));assert(!platform_display_resolutions(w,h,0));
 window_w=0;assert(!platform_display_resolutions(w,h,1));window_w=1920;
 platform_window=NULL;assert(!platform_display_resolutions(w,h,1));platform_display_apply();assert(!swap_calls);
 platform_window=(void*)1;thread=8;platform_display_apply();assert(!swap_calls);thread=7;
 platform_display_apply();
#ifdef HALO_VR
 assert(!swap_calls);
#else
 assert(swap_calls==1&&last_interval==1);vsync=0;platform_display_apply();assert(last_interval==0);
#endif
 assert(halo_interpolation_enabled()==1);interpolation=0;generation++;assert(!halo_interpolation_enabled());
 assert(platform_clipboard_get(text,sizeof(text))&&!strcmp(text,"hell")&&clipboard_frees==1);
 assert(!platform_clipboard_get(NULL,2)&&!platform_clipboard_get(text,0));
 clipboard=NULL;assert(!platform_clipboard_get(text,sizeof(text))&&!*text);
 platform_clipboard_set("invite");platform_clipboard_set(NULL);assert(!strcmp(written_clipboard,"invite"));
 platform_request_quit();assert(platform_quit_requested&&!locks);

 platform_menus_set_active(TRUE);assert(input_state.menus);
 keystroke_count=5;keys_pressed[SDL_SCANCODE_RETURN]=1;input_state.mouse_dx=200;
 platform_binding_capture_begin();assert(!keystroke_count&&!keys_pressed[SDL_SCANCODE_RETURN]&&!input_state.mouse_dx);
 assert(!platform_binding_capture_poll(&input)&&input==-99);
 assert(event(SDL_EVENT_KEY_DOWN,SDL_SCANCODE_A,1));assert(!platform_binding_capture_poll(&input));
 assert(event(SDL_EVENT_KEY_DOWN,-1,0));assert(event(SDL_EVENT_KEY_DOWN,SDL_SCANCODE_COUNT,0));
 assert(!platform_binding_capture_poll(&input));
 assert(event(SDL_EVENT_KEY_DOWN,SDL_SCANCODE_A,0));
 assert(platform_binding_capture_poll(&input)==1&&input==SDL_SCANCODE_A);
 input_state.mouse_dx=40;platform_input_read(&snapshot,TRUE);
 assert(!snapshot.keys[SDL_SCANCODE_A]&&!snapshot.mouse_dx&&binding_settling);
 assert(event(SDL_EVENT_KEY_UP,SDL_SCANCODE_A,0));platform_input_read(&snapshot,TRUE);assert(!binding_settling);
 assert(!event(SDL_EVENT_KEY_DOWN,SDL_SCANCODE_A,0));platform_input_read(&snapshot,TRUE);assert(snapshot.keys[SDL_SCANCODE_A]);
 event(SDL_EVENT_KEY_UP,SDL_SCANCODE_A,0);

 platform_binding_capture_begin();event(SDL_EVENT_KEY_DOWN,SDL_SCANCODE_ESCAPE,0);assert(platform_binding_capture_poll(NULL)==3);
 event(SDL_EVENT_KEY_UP,SDL_SCANCODE_ESCAPE,0);platform_input_read(&snapshot,TRUE);
 platform_binding_capture_begin();event(SDL_EVENT_KEY_DOWN,SDL_SCANCODE_DELETE,0);assert(platform_binding_capture_poll(&input)==2);
 event(SDL_EVENT_KEY_UP,SDL_SCANCODE_DELETE,0);platform_input_read(&snapshot,TRUE);
 platform_binding_capture_begin();event(SDL_EVENT_KEY_DOWN,SDL_SCANCODE_F11,0);assert(!platform_binding_capture_poll(&input));
 event(SDL_EVENT_KEY_UP,SDL_SCANCODE_F11,0);
 event(SDL_EVENT_MOUSE_BUTTON_DOWN,1,0);assert(platform_binding_capture_poll(&input)==1&&input==INPUT_MOUSE+1);
 platform_input_read(&snapshot,TRUE);assert(binding_settling&&!snapshot.mouse_buttons[1]);
 event(SDL_EVENT_MOUSE_BUTTON_UP,1,0);platform_input_read(&snapshot,TRUE);assert(!binding_settling&&!input_state.mouse_buttons[1]);
 platform_binding_capture_begin();event(SDL_EVENT_MOUSE_WHEEL,-1,0);assert(platform_binding_capture_poll(&input)==1&&input==INPUT_WHEEL_DOWN);
 platform_input_read(&snapshot,TRUE);assert(!binding_settling);

 /* Screen abandoned / result unclaimed / closing menu all release capture. */
 platform_binding_capture_begin();now+=501;platform_input_read(&snapshot,TRUE);assert(!binding_capture&&!binding_settling);
 platform_binding_capture_begin();event(SDL_EVENT_MOUSE_WHEEL,1,0);now+=2001;platform_input_read(&snapshot,TRUE);assert(!binding_capture&&!binding_settling);
 platform_binding_capture_begin();assert(!event(SDL_EVENT_FINGER_DOWN,0,0));assert(!event(SDL_EVENT_GAMEPAD_ADDED,0,0));
 platform_menus_set_active(FALSE);platform_input_read(&snapshot,TRUE);assert(!binding_capture&&!binding_settling&&!snapshot.menus);
 platform_binding_capture_begin();assert(!event(SDL_EVENT_WINDOW_FOCUS_LOST,0,0));assert(platform_binding_capture_poll(&input)==3);
 platform_input_read(&snapshot,TRUE);assert(!binding_settling&&!locks);
 /* A press and release between reads remains visible once outside capture. */
 keys_pressed[SDL_SCANCODE_A]=1;mouse_buttons_pressed[1]=1;platform_input_read(&snapshot,TRUE);
 assert(snapshot.keys[SDL_SCANCODE_A]&&snapshot.mouse_buttons[1]);platform_input_read(&snapshot,TRUE);
 assert(!snapshot.keys[SDL_SCANCODE_A]&&!snapshot.mouse_buttons[1]);
 puts("PASS: menu platform capture/settling, untouched touch/gamepad events, clipboard, config refresh and safe display helpers");
}
'''

functions = ''.join(fn(n) for n in (
    'halo_interpolation_enabled','platform_display_resolutions','platform_window_sizes',
    'platform_display_apply','platform_clipboard_get','platform_clipboard_set','platform_request_quit',
    'binding_clear_pending','binding_take','binding_capture_event','platform_binding_capture_begin',
    'platform_binding_capture_poll','platform_menus_set_active','platform_input_read'))
out = ROOT / 'build/test31-menu-platform'
out.mkdir(parents=True, exist_ok=True)
cfile = out / 'menu_platform.c'
cfile.write_text(shim + re.sub(r'^#include <SDL3/[^\n]*\n', '', header, flags=re.M) + globals_c + functions + checks)
for variant, flags in (('desktop',[]),('android',['-DHALO_ANDROID']),('vr',['-DHALO_ANDROID','-DHALO_VR'])):
    exe = out / variant
    subprocess.run(['clang','-std=gnu11','-O1','-fsanitize=address,undefined',*flags,str(cfile),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
