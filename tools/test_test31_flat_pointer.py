#!/usr/bin/env python3
"""Execute flat menu touch/JNI/coordinate code without a headset or SDK build."""
from pathlib import Path
import re, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]

def function(text,name):
    m=re.search(r'(?m)^(?:static )?(?:JNIEXPORT \w+ JNICALL |(?:void|int|BOOL) )'+name+r'\([^;]*?\)\n\{',text)
    assert m,name
    return text[m.start():text.index('\n}',m.end())+2]

def main():
    host=(ROOT/'port/android/host/host_sdl.c').read_text()
    render=(ROOT/'port/linux/src/d3d8_gl.c').read_text()
    platform=(ROOT/'port/linux/src/sdl_platform.c').read_text()
    java=ROOT/'port/android/app/src/main/java/com/halo/decomp'
    with tempfile.TemporaryDirectory(prefix='test31-pointer-') as directory:
        out=Path(directory)
        prefix=r'''
#include <assert.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include "halo_touch.h"
#define JNIEXPORT
#define JNICALL
#define HALO_ANDROID 1
#define TRUE 1
#define FALSE 0
typedef int BOOL,jint,jboolean;typedef float jfloat;typedef void JNIEnv;typedef void *jclass;
typedef unsigned long long Uint64;
static Uint64 SDL_GetTicks(void){return 1000;}
static pthread_mutex_t touch_lock=PTHREAD_MUTEX_INITIALIZER;
static struct halo_touch_state touch_state;
static unsigned int touch_pressed;
static Uint64 touch_look_time;
static atomic_int touch_menus;
static struct halo_touch_pointer touch_pointer;
'''
        names=['Java_com_halo_decomp_TouchControls_nativeState','Java_com_halo_decomp_TouchControls_nativePointer','host_touch_menu','host_touch_pointer_read','host_touch_read']
        code=prefix+function(host,'touch_axis')+'\n'+'\n'.join(function(host,n) for n in names)
        code+=r'''
struct platform_ui_pointer {float x,y,click_x,click_y;BOOL moved;int left_clicks,right_clicks,wheel_steps;};
static struct platform_ui_pointer ui_pointer;
static struct {BOOL ui_pointer,focused;} input_state;
static pthread_mutex_t input_lock=PTHREAD_MUTEX_INITIALIZER;
static void *platform_window;
static int ww=1920,wh=1080,pw=1920,ph=1080;
static int SDL_GetWindowSize(void *window,int*w,int*h){(void)window;*w=ww;*h=wh;return 1;}
'''+function(platform,'platform_ui_pointer_read')+r'''
static void platform_video_window_size(int*w,int*h){*w=ww;*h=wh;}
static void platform_video_drawable_size(int*w,int*h){*w=pw;*h=ph;}
struct render_target_entry {struct {int gl_width,gl_height,width,height;}target;};
static struct render_target_entry target={{854,480,854,480}};
static struct{int back_buffer;}device;
static struct render_target_entry *render_target_get(int*p){(void)p;return &target;}
static int halo_screen_width(void){return target.target.width;}
'''+function(render,'ui_point_from_window')+r'''
int main(void){
 struct halo_touch_state pad;struct halo_touch_pointer p;struct platform_ui_pointer ui;short x,y;
 Java_com_halo_decomp_TouchControls_nativeState(0,0,120,-240,0,0,HALO_TOUCH_A,0);
 host_touch_menu(1);host_touch_read(&pad);assert(!pad.buttons&&!pad.lx&&pad.generation==1);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,1,.5f,.4f);
 host_touch_read(&pad);host_touch_pointer_read(&p);assert(p.click&&p.moved&&p.x==.5f);
 host_touch_pointer_read(&p);assert(!p.click&&!p.moved);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,1,NAN,.4f);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,1,1.1f,.4f);
 host_touch_pointer_read(&p);assert(!p.click&&!p.moved);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,2,.5f,.4f);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,3,0,0);host_touch_pointer_read(&p);assert(!p.back);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,1,.5f,.4f);host_touch_menu(0);
 host_touch_pointer_read(&p);assert(!p.click);host_touch_read(&pad);assert(pad.generation==2);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,1,.5f,.4f);host_touch_pointer_read(&p);assert(!p.click);
 host_touch_menu(1);input_state.ui_pointer=input_state.focused=1;
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,1,.5f,.5f);
 assert(platform_ui_pointer_read(&ui));assert(ui.left_clicks==1&&ui.click_x==960&&ui.click_y==540);
 platform_ui_pointer_read(&ui);assert(!ui.left_clicks&&!ui.moved);
 Java_com_halo_decomp_TouchControls_nativePointer(0,0,2,.5f,.5f);platform_ui_pointer_read(&ui);assert(ui.right_clicks==1);
 input_state.focused=0;Java_com_halo_decomp_TouchControls_nativePointer(0,0,1,.5f,.5f);
 platform_ui_pointer_read(&ui);assert(!ui.left_clicks);
 // Physical SDL mouse position/scroll survives a frame without finger input.
 input_state.focused=1;ui_pointer.x=200;ui_pointer.wheel_steps=2;ui_pointer.left_clicks=1;
 platform_ui_pointer_read(&ui);assert(ui.x==200&&ui.wheel_steps==2&&ui.left_clicks==1);
 platform_ui_pointer_read(&ui);assert(!ui.wheel_steps&&!ui.left_clicks);
 ui_point_from_window(960,540,&x,&y);assert(x==320&&y==240);
 // HiDPI conversion and 4:3 letterbox use drawable and window sizes separately.
 ww=960;wh=540;ui_point_from_window(480,270,&x,&y);assert(x==320&&y==240);
 target.target.gl_width=target.target.width=640;
 ui_point_from_window(120,0,&x,&y);assert(x==0&&y==0);
 ui_point_from_window(840,540,&x,&y);assert(x==640&&y==480);
 ui_point_from_window(NAN,0,&x,&y);assert(x==-1&&y==-1);
 pw=0;ui_point_from_window(200,200,&x,&y);assert(x==-1&&y==-1);
 puts("flat pointer: JNI lifecycle, independent consumption, SDL merge and display coordinates passed");
}
'''
        c=out/'pointer.c';c.write_text(code)
        cc=shutil.which('clang') or shutil.which('gcc');assert cc
        subprocess.run([cc,'-std=c11','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I',str(ROOT/'port/android/include'),str(c),'-lm','-lpthread','-o',str(out/'pointer')],check=True)
        subprocess.run([str(out/'pointer')],check=True)
        check=out/'MenuTouchCheck.java';check.write_text('''package com.halo.decomp;
public class MenuTouchCheck {
 static void check(boolean ok){if(!ok)throw new AssertionError();}
 public static void main(String[] args){MenuTouchGesture g=new MenuTouchGesture();
  g.begin(4,100,100,false);check(g.end(4,103,100,16,false)==1);check(g.pointer()==-1);
  check(g.end(4,103,100,16,false)==0);
  g.begin(7,100,100,true);check(g.end(7,103,100,16,true)==2);
  g.begin(7,100,100,true);check(g.end(7,103,100,16,false)==0);
  g.begin(7,100,100,false);g.move(200,100,16);check(g.end(7,100,100,16,false)==0);
  g.begin(7,100,100,false);g.cancel();check(g.end(7,100,100,16,false)==0);
  g.begin(7,100,100,false);check(g.end(8,100,100,16,false)==0);check(g.pointer()==7);
  g.move(Float.NaN,100,16);check(g.end(7,100,100,16,false)==0);
  System.out.println("flat pointer: actual Java gesture tap, Back, cancel, drag and pointer ownership passed");
 }}''')
        subprocess.run(['javac','-d',str(out),str(java/'MenuTouchGesture.java'),str(check)],check=True)
        subprocess.run(['java','-cp',str(out),'com.halo.decomp.MenuTouchCheck'],check=True)
    activity=(java/'HaloActivity.java').read_text();touch=(java/'TouchControls.java').read_text()
    assert activity.index('touchControls.dispatchMenuTouch(event,mSurface)')<activity.index('return super.dispatchTouchEvent(event)')
    assert 'SDL_HINT_TOUCH_MOUSE_EVENTS, "0"' in platform
    pump=platform.split('void platform_pump_events(void)',1)[1].split('/* ---------- the menus',1)[0]
    for label in ['SDL_EVENT_MOUSE_MOTION:', 'SDL_EVENT_MOUSE_BUTTON_UP:', 'SDL_EVENT_MOUSE_WHEEL:']:
        event=pump.split(label,1)[1].split('\n\t\tcase ',1)[0]
        assert 'input_state.ui_pointer' in event and '#ifndef HALO_ANDROID' not in event
    assert '#ifndef HALO_ANDROID\n\tupdater_poll(platform_window);\n#endif' in pump
    import xml.etree.ElementTree as ET
    page=ET.parse(ROOT/'port/assets/menus/ce/main_menu.settings_select.player_setup.player_profile_edit.network_setup.xml').getroot()
    updates=[w for w in page.findall('widget') if w.get('name','').endswith('/auto_spinner')]
    assert len(updates)==2
    desktop=next(w for w in updates if w.get('platform')=='desktop')
    android=next(w for w in updates if w.get('platform')=='android')
    assert desktop.get('setting')=='update.auto' and android.get('setting') is None
    assert android.get('text')=='USE LAUNCHER' and android.get('strings') is None
    assert 'if(!menus && !menuStream) return false;' in touch and 'if(!event.isFromSource(InputDevice.SOURCE_TOUCHSCREEN)) return false;' in touch
    assert 'menus || editing || GamepadPolicy.showTouch' in touch
    assert 'input.pointer(3,0,0)' in touch
    for symbol in ['host_touch_menu','host_touch_pointer_read','host_sdl_window_size']:
        assert symbol in (ROOT/'port/android/host_imports.list').read_text().splitlines()
    print('flat pointer: activity interception, hidden-overlay access and host import guards passed')

if __name__=='__main__':main()
