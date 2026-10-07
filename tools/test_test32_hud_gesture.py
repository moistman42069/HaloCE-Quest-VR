"""Production HUD gesture geometry/state tests; no device or app execution.

The reported log has toggles 610 and 918 ms apart. It has no controller/head
poses, so tests reproduce the source-level rearm and motion risks rather than
claiming to replay the player's movement. Compile actual production helpers.
"""
from pathlib import Path
import hashlib
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test32-hud'
OUT.mkdir(parents=True, exist_ok=True)
frame = (ROOT / 'port/linux/src/vr_frame.c').read_text()


def function(name):
    match = re.search(r'^(?:static )?[\w *]+\b' + name + r'\s*\([^;{}]*\)\s*\{', frame, re.M)
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (frame[end] == '{') - (frame[end] == '}')
        end += 1
    return frame[match.start():end] + '\n'


defines = ''.join(re.findall(r'#define HUD_TAP_\w+ [^\n]+\n', frame))
assert defines.count('#define') == 9
gesture = function('update_gestures')
assert 'update_hud_tap(w, seconds);' in gesture
focus = gesture[gesture.index('if (!(vr.frame.flags & HALO_XR_FRAME_FOCUSED))'):gesture.index('/* grips:')]
assert 'reset_hud_tap();' in focus
assert 'reset_hud_tap();' in function('vr_set_hud_hidden')
assert 'reset_hud_tap();' in function('vr_vehicle_seat')
settings = function('vr_reload_settings')
assert 'vr.hud_tap_armed = vr.hud_tap_last_valid = 0;' in settings
assert 'vr.hud_tap_dwell = vr.hud_tap_release = vr.hud_tap_cooldown = 0.0f;' in settings

flashlight = gesture[gesture.index('\t/* the flashlight:'):gesture.index('\t/* test26: the HUD tap:')]
# Review guard: accepted Test31c flashlight implementation is unchanged.
assert hashlib.sha256(flashlight.encode()).hexdigest() == '1756a36eb55436dec68641615dd0686c568486df72fd70660d6da717d22397f0'

source = r'''
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "port/android/include/halo_android_abi.h"
DEFINES
static struct {
 float hud_tap_distance, hud_tap_dwell, hud_tap_release, hud_tap_cooldown;
 float hud_tap_last[3],hud_tap_anchor[3];int hud_tap_last_valid;
 int hud_tap_armed,hud_hidden,menus_active,in_holster;
 float flashlight_distance;int flashlight_armed;unsigned int actions;
 struct halo_xr_frame frame;
} vr;
static int buzzes,logs,last_hand;
static void vr_haptic(int hand,float amplitude,float seconds){assert(amplitude==0.4f&&seconds==0.04f);last_hand=hand;buzzes++;}
static void platform_log(const char *format,...){assert(!strcmp(format,"vr: HUD %s (head tap)"));logs++;}
HELPERS
static float dt=1.f/72.f;
static void sample(int hand,float x,float y,float z){
 vr.frame.grip[hand].position[0]=x;vr.frame.grip[hand].position[1]=y;vr.frame.grip[hand].position[2]=z;update_hud_tap(hand,dt);
}
static void hold(int hand,float x,float y,float z,float seconds){
 int n=(int)ceilf(seconds/dt);while(n--)sample(hand,x,y,z);
}
static void away(int hand){hold(hand,hand?0.5f:-0.5f,1.3f,-0.3f,0.9f);}
static void temple(int hand,float seconds){hold(hand,hand?HUD_TAP_OUT:-HUD_TAP_OUT,1.6f,HUD_TAP_BACK,seconds);}
static void initialize(void){
 memset(&vr,0,sizeof(vr));buzzes=logs=0;vr.hud_tap_distance=0.1f;
 vr.frame.flags=HALO_XR_FRAME_FOCUSED|HALO_XR_FRAME_VIEWS_VALID;
 vr.frame.head.position[1]=1.6f;vr.frame.head.orientation[3]=1;
 vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3;
}
static void reset_conditions(void){
 vr.frame.flags=HALO_XR_FRAME_FOCUSED|HALO_XR_FRAME_VIEWS_VALID;vr.frame.hand_valid[1]=3;
 vr.menus_active=vr.in_holster=0;vr.hud_tap_distance=0.1f;
}
int main(void){int hand,n,k;
 for(k=0;k<4;k++){
  dt=1.f/(float[]){60,72,90,120}[k];
  for(hand=0;hand<2;hand++){
   initialize();temple(hand,1.f);assert(!logs); /* startup near head: no surprise toggle */
   away(hand);temple(hand,0.20f);assert(!logs);temple(hand,0.16f);assert(logs==1&&vr.hud_hidden&&last_hand==hand);
   temple(hand,2.f);assert(logs==1); /* never repeat while held */
   for(n=0;n<12;n++){ /* one or a few outer samples never rearm */
    hold(hand,hand?0.5f:-0.5f,1.3f,-0.3f,0.10f);temple(hand,0.40f);
   }
   assert(logs==1&&!vr.hud_tap_armed);
   away(hand);temple(hand,0.36f);assert(logs==2&&!vr.hud_hidden&&buzzes==2);
   /* prior accepted reach: skin, slightly high/forward, both hands */
   away(hand);hold(hand,hand?0.08f:-0.08f,1.6f,0.04f,0.36f);assert(logs==3);
   away(hand);hold(hand,hand?0.13f:-0.13f,1.66f,-0.03f,0.36f);assert(logs==4);
   away(hand);hold(hand,hand?-HUD_TAP_OUT:HUD_TAP_OUT,1.6f,HUD_TAP_BACK,1.f);assert(logs==4);
  }
 }
 dt=1.f/72.f;initialize();away(1);
 /* Continuous drifting through the volume cannot build a steady hold. */
 for(n=0;n<144;n++){float p=fmodf(n*dt*0.4f,0.36f);float z=0.03f+(p<0.18f?p:0.36f-p)-0.09f;sample(1,0.11f,1.6f,z);}
 assert(logs==0);
 /* A fast hand crossing the head on its way to the shoulder is not a tap. */
 for(n=0;n<30;n++)sample(1,0.11f,1.6f,0.03f+(n-15)*0.012f);
 assert(!logs);away(1);
 /* Guard the accepted shoulder, cheek aiming, forward aiming, wrong temple. */
 hold(1,0.18f,1.45f,0.15f,1.f);hold(1,0.06f,1.42f,-0.12f,1.f);
 hold(1,0.10f,1.5f,-0.35f,1.f);hold(1,-0.11f,1.6f,0.03f,1.f);assert(!logs);
 /* Dwell tolerates slight entry-boundary jitter without repeated activation. */
 away(1);sample(1,0.209f,1.6f,0.03f);
 for(n=0;n<35;n++)sample(1,0.208f+(n%2)*0.004f,1.6f,0.03f);
 assert(logs==1);hold(1,0.22f,1.6f,0.03f,1.f);temple(1,1.f);assert(logs==1);
 /* A full withdrawal is necessary, but cooldown also bounds repeat rate. */
 initialize();away(1);temple(1,0.36f);assert(logs==1);
 hold(1,0.5f,1.3f,-0.3f,0.27f);temple(1,0.50f);assert(logs==1);
 temple(1,0.4f);assert(logs==2);
 /* Focus, menu, recenter, tracking and disabled transitions discard partial
 dwell and require withdrawing again, rather than triggering upon recovery. */
 for(k=0;k<7;k++){
  initialize();away(1);temple(1,0.2f);
  if(k==0)vr.frame.flags&=~HALO_XR_FRAME_FOCUSED;
  if(k==1)vr.frame.flags&=~HALO_XR_FRAME_VIEWS_VALID;
  if(k==2)vr.frame.flags|=HALO_XR_FRAME_RECENTRED;
  if(k==3)vr.frame.hand_valid[1]=0;
  if(k==4)vr.menus_active=1;
  if(k==5)vr.hud_tap_distance=0;
  if(k==6)dt=0.2f;
  temple(1,0.4f);assert(!logs&&!vr.hud_tap_armed);
  reset_conditions();dt=1.f/72.f;temple(1,1.f);assert(!logs);
  away(1);temple(1,0.36f);assert(logs==1);
 }
 initialize();away(1);vr.in_holster=1;temple(1,1.f);assert(!logs);
 vr.in_holster=0;away(1);temple(1,0.36f);assert(logs==1);
 /* Actual head transform: 90-degree yaw and translated room-scale motion. */
 initialize();away(1);
 {float q=sqrtf(.5f),local[3]={HUD_TAP_OUT,0,HUD_TAP_BACK},world[3];
  vr.frame.head.orientation[1]=q;vr.frame.head.orientation[3]=q;
  rotate(vr.frame.head.orientation,local,world);
  for(n=0;n<40;n++){vr.frame.head.position[0]=n*.01f;vr.frame.head.position[2]=n*.02f;
   sample(1,world[0]+vr.frame.head.position[0],world[1]+1.6f,world[2]+vr.frame.head.position[2]);}
  assert(logs==1); /* shared head/hand motion >1 m/s is still a steady hold */
 }
 /* Turning the head past a stationary controller produces relative motion,
 even though the old world-space controller speed was zero. */
 initialize();away(1);
 for(n=0;n<70;n++){float a=(n-35)*dt*1.5f;vr.frame.head.orientation[1]=sinf(a*.5f);vr.frame.head.orientation[3]=cosf(a*.5f);sample(1,.11f,1.6f,.03f);}
 assert(!logs);
 /* Invalid values cannot accumulate time or poison the next gesture. */
 initialize();away(1);sample(1,NAN,1.6f,.03f);assert(!logs&&!vr.hud_tap_armed);
 vr.frame.head.orientation[3]=NAN;temple(1,.4f);assert(!logs);
 vr.frame.head.orientation[3]=0;temple(1,.4f);assert(!logs);
 vr.frame.head.orientation[3]=1;update_hud_tap(1,NAN);update_hud_tap(1,0);update_hud_tap(-1,dt);update_hud_tap(2,dt);
 assert(!logs);away(1);temple(1,.36f);assert(logs==1);
 puts("PASS HUD gesture: real helpers, both hands, 60/72/90/120Hz, deliberate hold/withdrawal, jitter, cooldown, pose/lifecycle guards");
 return 0;
}
'''.replace('DEFINES', defines).replace('HELPERS', ''.join(function(n) for n in ('rotate','distance3','reset_hud_tap','update_hud_tap')))
(OUT / 'hud.c').write_text(source)
subprocess.run(['clang','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror',
                '-fsanitize=address,undefined','-I',str(ROOT),str(OUT/'hud.c'),'-lm','-o',str(OUT/'hud')],check=True)
subprocess.run([str(OUT/'hud')],check=True)
print('PASS wiring/settings reset and unchanged flashlight implementation')
