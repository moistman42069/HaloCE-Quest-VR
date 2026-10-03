"""Production Android gamepad adapter with mock SDL devices, plus UI policy.
Does not claim Bluetooth/USB, Android focus or device rumble acceptance.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test15-gamepad'
OUT.mkdir(parents=True, exist_ok=True)

def fn(text, name):
    start = text.rfind('\n', 0, text.index(name)) + 1
    brace = text.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end] + '\n'

s = (ROOT / 'port/android/host/host_sdl.c').read_text()
settings = s[s.index('static atomic_int pad_count'):s.index('\n#endif', s.index('static atomic_int pad_count'))]
handles = s[s.index('#define HANDLE_COUNT'):s.index('/* ---------- general */')]
adapters = s[s.index('/* ---------- gamepads */'):s.index('/* ---------- audio */')]
test = r'''
#include <SDL3/SDL.h>
#include <assert.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "port/android/host/gamepad_policy.h"
typedef void JNIEnv; typedef void* jclass; typedef int jint; typedef float jfloat; typedef int jboolean;
#define JNIEXPORT
#define JNICALL
#define HOST_LOG_INFO 0
#define HOST_LOG_ERROR 1
#define host_logf(...) ((void)0)
struct SDL_Gamepad { int id, live, open, complete; int axes[6]; int buttons[32]; };
static struct SDL_Gamepad device={.id=1,.live=1,.complete=1};
static SDL_Event queued;
static int opens,closes,rumble_low,rumble_high;
SDL_JoystickID *SDL_GetGamepads(int *n){*n=device.live;SDL_JoystickID *ids=malloc(sizeof(*ids));*ids=1;return ids;}
void SDL_free(void*p){free(p);}
SDL_Gamepad *SDL_GetGamepadFromID(SDL_JoystickID id){return id==1&&device.open?&device:NULL;}
SDL_Gamepad *SDL_OpenGamepad(SDL_JoystickID id){assert(id==1);opens++;device.open=1;return &device;}
void SDL_CloseGamepad(SDL_Gamepad *p){assert(p==&device);closes++;device.open=0;}
bool SDL_GamepadHasAxis(SDL_Gamepad*p,SDL_GamepadAxis a){return p->complete || a==SDL_GAMEPAD_AXIS_LEFTX;}
Sint16 SDL_GetGamepadAxis(SDL_Gamepad*p,SDL_GamepadAxis a){return p->axes[a];}
bool SDL_GetGamepadButton(SDL_Gamepad*p,SDL_GamepadButton b){return p->buttons[b];}
SDL_GamepadType SDL_GetGamepadType(SDL_Gamepad*p){(void)p;return SDL_GAMEPAD_TYPE_XBOXONE;}
Uint16 SDL_GetGamepadVendor(SDL_Gamepad*p){(void)p;return 0x45e;}
bool SDL_RumbleGamepad(SDL_Gamepad*p,Uint16 l,Uint16 h,Uint32 ms){(void)p;(void)ms;rumble_low=l;rumble_high=h;return true;}
bool SDL_PollEvent(SDL_Event*e){if(!queued.type)return false;*e=queued;queued.type=0;return true;}
''' + settings + '\n' + handles + fn(s, 'int host_sdl_poll_event(') + adapters + r'''
static int guest_dead(int value){if(value>9000)return (value-9000)*32767/23767;if(value<-9000)return (value+9000)*32768/23768;return 0;}
int main(void){
 uint32_t ids[4]; assert(host_sdl_get_gamepads(ids,4)==0); // unopened is not ready
 uint32_t h=host_sdl_open_gamepad(1);assert(h);assert(host_sdl_open_gamepad(1)==h&&opens==1);
 assert(host_sdl_get_gamepads(ids,4)==1&&Java_com_halo_decomp_GamepadSupport_nativeCount(0,0)==1);
 device.complete=0;assert(host_sdl_get_gamepads(ids,4)==0);device.complete=1;
 Java_com_halo_decomp_GamepadSupport_nativeSettings(0,0,.1f,.2f,1.f,1.f,.05f,1,0,1);
 for(int axis=0;axis<6;axis++){
  device.axes[axis]=0;assert(host_sdl_gamepad_axis(h,axis)==0);
  device.axes[axis]=32767;assert(host_sdl_gamepad_axis(h,axis)==32767);
  device.axes[axis]=-32768;assert(host_sdl_gamepad_axis(h,axis)==(axis<4?-32767:0));
 }
 device.axes[0]=3000;device.axes[2]=6000;assert(host_sdl_gamepad_axis(h,0)==0&&host_sdl_gamepad_axis(h,2)==0);
 device.buttons[SDL_GAMEPAD_BUTTON_SOUTH]=1;assert(host_sdl_gamepad_button(h,SDL_GAMEPAD_BUTTON_SOUTH));
 host_sdl_rumble_gamepad(h,100,200,100);assert(rumble_low==100&&rumble_high==200);
 Java_com_halo_decomp_GamepadSupport_nativeSettings(0,0,.1f,.2f,1,1,.05f,0,1,1);
 assert(!host_sdl_gamepad_button(h,SDL_GAMEPAD_BUTTON_SOUTH)&&host_sdl_gamepad_button(h,SDL_GAMEPAD_BUTTON_EAST));
 host_sdl_rumble_gamepad(h,100,200,100);assert(!rumble_low&&!rumble_high);
 Java_com_halo_decomp_GamepadSupport_nativeSettings(0,0,.1f,.2f,1,1,.05f,1,0,0);
 assert(!host_sdl_gamepad_button(h,SDL_GAMEPAD_BUTTON_SOUTH));
 for(int axis=0;axis<6;axis++)assert(host_sdl_gamepad_axis(h,axis)==0);
 host_sdl_rumble_gamepad(h,100,200,100);assert(!rumble_low&&!rumble_high);
 for(int raw=-32768;raw<=32767;raw++){
  // Default response retains the stock dead zone, with integer rounding only.
  assert(abs(guest_dead(halo_pad_axis(raw,9000.f/32767.f,1,0))-guest_dead(raw))<=3);
  for(int d=0;d<=45;d+=5){int v=halo_pad_axis(raw,d/100.f,1,0);assert(v>=-32767&&v<=32767);}
  int t=halo_pad_trigger(raw,.05f);assert(t>=0&&t<=32767);
 }
 assert(halo_pad_axis(10000,NAN,INFINITY,0)>=0);
 // Repeated reconnects must not exhaust the shared 256-handle table.
 for(int i=0;i<600;i++){
  device.live=0;queued.type=SDL_EVENT_GAMEPAD_REMOVED;queued.gdevice.which=1;
  SDL_Event e;assert(host_sdl_poll_event(&e));assert(!handle_get(h,_handle_gamepad));
  assert(host_sdl_get_gamepads(ids,4)==0&&Java_com_halo_decomp_GamepadSupport_nativeCount(0,0)==0);
  device.live=1;h=host_sdl_open_gamepad(1);assert(h&&h<HANDLE_COUNT);
  assert(host_sdl_get_gamepads(ids,4)==1);
 }
 assert(closes==600&&opens==601);
 puts("PASS: actual host adapter; full-pad detection, axes, dead zones, trigger bounds, layout swap, focus, rumble and 600 reconnects");
}
'''
source = OUT / 'gamepad.c'
guest=(ROOT/'port/linux/src/xinput_sdl.c').read_text()
xdk=(ROOT/'port/include/xdk/xdk_xbox.h').read_text()
macros='\n'.join(line for line in xdk.splitlines() if line.startswith('#define XINPUT_GAMEPAD_'))
mapping='''typedef int BOOL; typedef short SHORT; typedef unsigned short WORD; typedef unsigned char BYTE;
#define TRUE 1
#define FALSE 0
typedef struct {WORD wButtons; BYTE bAnalogButtons[8]; SHORT sThumbLX,sThumbLY,sThumbRX,sThumbRY;} XINPUT_GAMEPAD;
'''+macros+'\n'+fn(guest,'static SHORT stick(')+fn(guest,'static void merge_button(')+fn(guest,'static void sdl_gamepad_state(')+r'''
static void verify_mapping(void){
 static const int analog_buttons[]={SDL_GAMEPAD_BUTTON_SOUTH,SDL_GAMEPAD_BUTTON_EAST,SDL_GAMEPAD_BUTTON_WEST,SDL_GAMEPAD_BUTTON_NORTH,SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER,SDL_GAMEPAD_BUTTON_LEFT_SHOULDER};
 static const int digital_buttons[]={SDL_GAMEPAD_BUTTON_DPAD_UP,SDL_GAMEPAD_BUTTON_DPAD_DOWN,SDL_GAMEPAD_BUTTON_DPAD_LEFT,SDL_GAMEPAD_BUTTON_DPAD_RIGHT,SDL_GAMEPAD_BUTTON_START,SDL_GAMEPAD_BUTTON_BACK,SDL_GAMEPAD_BUTTON_LEFT_STICK,SDL_GAMEPAD_BUTTON_RIGHT_STICK};
 for(int i=0;i<6;i++){XINPUT_GAMEPAD out={0};memset(device.buttons,0,sizeof(device.buttons));device.buttons[analog_buttons[i]]=1;sdl_gamepad_state(&device,&out);for(int j=0;j<8;j++)assert(out.bAnalogButtons[j]==(j==i?255:0));}
 for(int i=0;i<8;i++){XINPUT_GAMEPAD out={0};memset(device.buttons,0,sizeof(device.buttons));device.buttons[digital_buttons[i]]=1;sdl_gamepad_state(&device,&out);assert(out.wButtons==(1<<i));}
 memset(device.buttons,0,sizeof(device.buttons));
 XINPUT_GAMEPAD out={0};device.axes[0]=32767;device.axes[1]=-32768;device.axes[2]=-32768;device.axes[3]=32767;device.axes[4]=16384;device.axes[5]=32767;
 sdl_gamepad_state(&device,&out);assert(out.sThumbLX==32767&&out.sThumbLY==32767&&out.sThumbRX==-32768&&out.sThumbRY==-32768);
 assert(out.bAnalogButtons[6]==127&&out.bAnalogButtons[7]==255);
 memset(device.axes,0,sizeof(device.axes));out=(XINPUT_GAMEPAD){.wButtons=1,.sThumbLX=25000};out.bAnalogButtons[0]=255;
 sdl_gamepad_state(&device,&out);assert(out.wButtons==1&&out.sThumbLX==25000&&out.bAnalogButtons[0]==255);
 puts("PASS: production Xbox mapper: 14 buttons, 4 axes, both independent analog triggers and merged input preservation");
}
'''
test=test.replace('static int guest_dead(',mapping+'\nstatic int guest_dead(',1)
test=test.replace('int main(void){\n','int main(void){\n verify_mapping();\n',1)
source.write_text(test)
subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Wno-unused-function',
    '-fsanitize=address,undefined', '-I', str(ROOT), '-I',
    str(ROOT/'build/android/third_party/SDL3/include'), str(source), '-pthread', '-lm', '-o', str(OUT/'gamepad')], check=True)
subprocess.run([str(OUT/'gamepad')], check=True)

# Exercise the patched SDL generic Android mapping, including button-only L2/R2.
sdl=ROOT/'build/android/third_party/SDL3'
mapping=(sdl/'src/joystick/SDL_gamepad.c').read_text()
(OUT/'sdl_mapping.c').write_text(r'''
#include <SDL3/SDL.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "src/joystick/usb_ids.h"
typedef struct {char text[1024];} GamepadMapping_t;
#define SDL_GAMEPAD_MAPPING_PRIORITY_DEFAULT 0
static GamepadMapping_t result;
void SDL_GetJoystickGUIDInfo(SDL_GUID g,Uint16*v,Uint16*p,Uint16*version,Uint16*crc){(void)g;(void)version;(void)crc;*v=0x45e;*p=1;}
size_t SDL_strlcpy(char*d,const char*s,size_t n){snprintf(d,n,"%s",s);return strlen(s);}
size_t SDL_strlcat(char*d,const char*s,size_t n){size_t l=strlen(d);snprintf(d+l,n-l,"%s",s);return l+strlen(s);}
bool SDL_GetHintBoolean(const char*s,bool value){(void)s;return value;}
int SDL_GetAndroidSDKVersion(void){return 35;}
static GamepadMapping_t *SDL_PrivateAddMappingForGUID(SDL_GUID g,const char*s,bool*existing,int priority){(void)g;(void)existing;(void)priority;snprintf(result.text,sizeof(result.text),"%s",s);return &result;}
'''+fn(mapping,'static GamepadMapping_t *SDL_CreateMappingForAndroidGamepad(')+r'''
int main(void){
 for(int analog=0;analog<2;analog++)for(int digital=0;digital<4;digital++){
  SDL_GUID g={{0}};g.data[12]=15;g.data[14]=(analog?0x3f:0x0f)|(digital<<6);
  const char*s=SDL_CreateMappingForAndroidGamepad(g)->text;
  assert((strstr(s,"lefttrigger:a4,")!=0)==analog);
  assert((strstr(s,"righttrigger:a5,")!=0)==analog);
  assert((strstr(s,"lefttrigger:b15,")!=0)==(!analog&&(digital&1)!=0));
  assert((strstr(s,"righttrigger:b16,")!=0)==(!analog&&(digital&2)!=0));
 }
 puts("PASS: production SDL Android analog and digital trigger mappings, independent sides and analog priority");
}
''')
subprocess.run(['clang','-std=c11','-fsanitize=address,undefined','-I',str(sdl/'include'),'-I',str(sdl),str(OUT/'sdl_mapping.c'),'-o',str(OUT/'sdl_mapping')],check=True)
subprocess.run([str(OUT/'sdl_mapping')],check=True)

android_java=(sdl/'android-project/app/src/main/java/org/libsdl/app/SDLControllerManager.java').read_text()
(OUT/'TriggerCapabilities.java').write_text('''import java.util.*;
class KeyEvent {static final int KEYCODE_BUTTON_L2=1,KEYCODE_BUTTON_R2=2;}
class MotionEvent {static final int AXIS_Z=11,AXIS_RZ=14;}
class InputDevice {
 boolean left,right; InputDevice(boolean l,boolean r){left=l;right=r;}
 boolean[] hasKeys(int...keys){return new boolean[]{left,right};}
 static class MotionRange {int axis;MotionRange(int a){axis=a;}int getAxis(){return axis;}}
}
class TriggerCapabilities {
'''+fn(android_java,'int getAxisMask(')+'''
 public static void main(String[]args){
  TriggerCapabilities c=new TriggerCapabilities();
  for(int axes:new int[]{2,4,6})for(int digital=0;digital<4;digital++){
   List<InputDevice.MotionRange> ranges=new ArrayList<>();
   for(int i=0;i<axes;i++)ranges.add(new InputDevice.MotionRange(i));
   int mask=c.getAxisMask(ranges,new InputDevice((digital&1)!=0,(digital&2)!=0));
   int expected=(axes==6?63:axes==4?15:3)|(axes<6?digital<<6:0);
   if(mask!=expected)throw new AssertionError(mask+" != "+expected);
  }
  System.out.println("PASS: production SDL Java capability masks retain analog GUIDs and independent digital trigger bits");
 }
}''')
subprocess.run(['javac','-d',str(OUT),str(OUT/'TriggerCapabilities.java')],check=True)
subprocess.run(['java','-cp',str(OUT),'TriggerCapabilities'],check=True)

java=ROOT/'port/android/app/src/main/java/com/halo/decomp'
(OUT/'PadCheck.java').write_text('''package com.halo.decomp;
class PadCheck {
 static void check(boolean b){if(!b)throw new AssertionError();}
 public static void main(String[]args){
  for(int count=0;count<5;count++){
   check(GamepadPolicy.showTouch(0,count)==(count==0));
   check(GamepadPolicy.showTouch(1,count));check(!GamepadPolicy.showTouch(2,count));
  }
  check(GamepadPolicy.showTouch(99,0));check(GamepadPolicy.direction(0,0)==0);
  check(GamepadPolicy.direction(Float.NaN,1)==0);check(GamepadPolicy.direction(.54f,0)==0);
  check(GamepadPolicy.direction(-1,0)==1);check(GamepadPolicy.direction(1,0)==2);
  check(GamepadPolicy.direction(0,-1)==3);check(GamepadPolicy.direction(0,1)==4);
  System.out.println("PASS: touch auto/show/hide, disconnect recovery and menu stick directions");
 }
}''')
subprocess.run(['javac','-d',str(OUT),str(java/'GamepadPolicy.java'),str(OUT/'PadCheck.java')],check=True)
subprocess.run(['java','-cp',str(OUT),'com.halo.decomp.PadCheck'],check=True)
