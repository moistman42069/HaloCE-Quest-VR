"""Test28 (1.0.10): a client joining an OpenCE co-op game in progress halted.

Evidence (kept private): a Quest 3 log (1.0.9, 2026-10-06 10:16) joined a
public 18-player co-op game on d40 at tick 20227 with no unit yet; within a
tick: EXCEPTION halt in camera_scripting.c #370 (forward -0.990,-0.060,-0.126,
up 0,0,1). Symbolized: network_coop_client_tick -> the host's camera ->
director_update -> scripted_camera_update. OpenCE's client_watch_host_from_behind
forces up to the world's and leaves it so when distributed_axes_make_valid
refuses it (more than about 6 degrees from square); OpenCE's release builds
log the check and go on, this app's halted. Fixed: up made square to forward;
the APKs build in release mode, as OpenCE's do.

Also test28: gyro aim for the flat Android port, an option (off by default):
the phone's turn reaches the game as a swipe's look turn. Its math
(GyroPolicy) is run here without Android; its wiring is checked in source.
Run with python3 tools/test_test28.py.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test28'; OUT.mkdir(parents=True, exist_ok=True)


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def run(name, text):
    p = OUT / (name + '.c'); p.write_text(text)
    subprocess.run(['clang', '-std=gnu11', '-O1', '-Wall', '-Wno-unused-function', '-fsanitize=address,undefined', str(p),
                    '-lm', '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)


coop = (ROOT / 'port/linux/game/network_coop.c').read_text(encoding='utf-8')
build = (ROOT / 'tools/build-quest.sh').read_text(encoding='utf-8')
gradle = (ROOT / 'port/android/app/build.gradle').read_text(encoding='utf-8')
frame = (ROOT / 'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
package = (ROOT / 'tools/package-quest.py').read_text(encoding='utf-8')

# --- the camera watching the host from behind: upright, its axes square, for every pitch
watch = fn(coop, 'client_watch_host_from_behind')
assert 'distributed_axes_make_valid(forward, up);' not in watch
run('watch_host', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
typedef union { struct { real x,y,z; }; real n[3]; } real_point3d;
typedef union { struct { real i,j,k; }; real n[3]; } real_vector3d;
#define WATCH_HOST_DISTANCE 3.0f
#define WATCH_HOST_HEIGHT 1.0f
#define WATCH_HOST_FOLLOW 0.2f
static struct { boolean watching_host_valid; real_point3d watching_host_position; real_vector3d watching_host_forward; } coop_presentation;
static int valid_real_vector3d_axes2(real_vector3d const *f, real_vector3d const *u);
static real normalize3d(real_vector3d *v){ real l=sqrtf(v->i*v->i+v->j*v->j+v->k*v->k); if(l<1e-6f) return 0.f; v->i/=l; v->j/=l; v->k/=l; return l; }
static void point_from_line3d(real_point3d const *p, real_vector3d const *v, real t, real_point3d *o){ o->x=p->x+v->i*t; o->y=p->y+v->j*t; o->z=p->z+v->k*t; }
static void points_interpolate(real_point3d const *a, real_point3d const *b, real t, real_point3d *o){ for(int i=0;i<3;i++) o->n[i]=a->n[i]+(b->n[i]-a->n[i])*t; }
static void vectors_interpolate(real_vector3d const *a, real_vector3d const *b, real t, real_vector3d *o){ for(int i=0;i<3;i++) o->n[i]=a->n[i]+(b->n[i]-a->n[i])*t; }
''' + watch + r'''
/* the scripted camera's check (camera_scripting.c #370: valid_real_vector3d_axes2) */
static int square(real_vector3d const *f, real_vector3d const *u){
 real lf=f->i*f->i+f->j*f->j+f->k*f->k, lu=u->i*u->i+u->j*u->j+u->k*u->k, d=f->i*u->i+f->j*u->j+f->k*u->k;
 return fabsf(lf-1.f)<1e-3f && fabsf(lu-1.f)<1e-3f && fabsf(d)<1e-3f; }
static int valid_real_vector3d_axes2(real_vector3d const *f, real_vector3d const *u){return square(f,u);}
int main(void){
 int n=0;
 for(int yaw=0;yaw<360;yaw+=7) for(int pitch=-90;pitch<=90;pitch+=3){
  real y=yaw*3.14159265f/180, p=pitch*3.14159265f/180;
  coop_presentation.watching_host_valid=FALSE;
  for(int frame=0;frame<6;frame++){
   real_point3d pos={{10,20,3}}; real_vector3d f={{cosf(p)*cosf(y),cosf(p)*sinf(y),sinf(p)}}, u={{0,0,1}};
   assert(client_watch_host_from_behind(&pos,&f,&u));
   assert(square(&f,&u)); assert(u.k>=-1e-6f); n++; } }
 /* the logged case: forward -0.990,-0.060,-0.126 */
 { real_vector3d f={{-0.990173f,-0.060274f,-0.126194f}},u={{0,0,1}}; real_point3d pos={{-35.9f,-18.8f,1.6f}};
   normalize3d(&f); coop_presentation.watching_host_valid=FALSE; client_watch_host_from_behind(&pos,&f,&u);
   assert(square(&f,&u) && u.k>0.99f); }
 /* invalid interpolated forward: decline this camera instead of handing bad axes to the engine */
 { real_vector3d f={{0,0,0}},u={{0,0,1}}; real_point3d pos={{0,0,0}};
   coop_presentation.watching_host_valid=FALSE; assert(!client_watch_host_from_behind(&pos,&f,&u)); }
 printf("PASS: %d host views (every pitch, straight up and down too): the camera watching the host is upright and its axes square"
        " (the logged d40 halt's case included)\n", n);
}
''')

# --- the APKs build in release mode, as OpenCE's: a failed check is logged and play goes on
assert 'vr) flags=(--vr --release) ;;' in build and 'flat) flags=(--release) ;;' in build
print('PASS: the APKs build with --release (HALO_RELEASE), as OpenCE ships its builds')

# --- version, identity, package markers
version_codes = re.search(r'versionCode Math\.max\((?:haloVr \? (\d+) : )?(\d+), buildNumber\)', gradle)
assert version_codes and all(int(code) >= 36 for code in version_codes.groups() if code)
assert int(re.search(r': "1\.0\.(\d+)"', gradle).group(1)) >= 10
assert ('HaloCE Quest test28 candidate 1.0.10' in frame or 'test28: co-op games entered in progress' in frame) and \
    'co-op hosted for 2 to 128 players' in frame and 'gyro aim on phones' in frame
assert 'candidate_at_least(args.label, 28)' in package
print('PASS: test28 wiring (version 1.0.10 / 36, identity, package markers)')

# --- co-op hosts as big as OpenCE's: its Server Setup offers 2 to 128 players (MAXIMUM_NETWORK_PLAYER_COUNT)
session = (ROOT / 'port/linux/game/network_campaign_session.c').read_text(encoding='utf-8')
server = (ROOT / 'source/networking/network_server_manager.c').read_text(encoding='utf-8')
launcher = (ROOT / 'port/android/app/src/main/java/com/halo/decomp/CoopLauncher.java').read_text(encoding='utf-8')
limits = (ROOT / 'port/linux/include/halo_port_limits.h').read_text(encoding='utf-8')
assert re.search(r'^#define HALO_PORT_MAXIMUM_NETWORK_PLAYERS 128$', limits, re.M)
assert 'COOP_MAXIMUM_PLAYERS = 128,' in session and 'COOP_FORMAT_1_PLAYERS = 16,' in session
assert 'server->game.maximum_players = (byte)PIN(maximum_players, 2, MAXIMUM_NETWORK_PLAYER_COUNT);' in server
assert 'MIN(16, MAXIMUM_NETWORK_PLAYER_COUNT));' not in server.split('network_game_server_port_set_cooperative_players(')[1].split('\n}')[0]
# (OpenCE's own list, menu_functions.c: maximum_players[] = { 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128 })
assert 'PLAYER_CHOICES = {2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128};' in launcher and 'DEFAULT_PLAYERS = 4;' in launcher
assert 'PLAYER_CHOICES[players.getSelectedItemPosition()] + "\\n")' in launcher or \
    'PLAYER_CHOICES[players.getSelectedItemPosition()] + "\\n"\n' in launcher  # (test30: the server's name follows)
print('PASS: co-op hosted for 2 to 128 players, as OpenCE\'s Server Setup offers (16 at most before); the old request format still 16')

# --- gyro aim (flat Android): the math, run without Android
J = ROOT / 'port/android/app/src/main/java/com/halo/decomp'
check = OUT / 'GyroCheck.java'
check.write_text(r"""
package com.halo.decomp;
public class GyroCheck {
 static void check(boolean b,String what){if(!b)throw new AssertionError(what);}
 static boolean near(float a,float b){return Math.abs(a-b)<1e-5f;}
 static float[] screen(int rotation,float x,float y,float z){float[] o=new float[3];GyroPolicy.toScreen(rotation,new float[]{x,y,z},o);return o;}
 static float[] step(float[] rate,float[] up,float dt,float gx,float gy,boolean inv){float[] o=new float[2];GyroPolicy.step(rate,up,dt,gx,gy,inv,o);return o;}
 public static void main(String[] a){
  // the screen's axes in each display rotation: ROTATION_90 is the phone turned counter-clockwise
  // (its top to the left): the phone's x (right edge) points up the screen, its y (top) to the left
  float[] v=screen(1,1,0,0);check(near(v[0],0)&&near(v[1],1),"r90 x up");
  v=screen(1,0,1,0);check(near(v[0],-1)&&near(v[1],0),"r90 y left");
  v=screen(3,1,0,0);check(near(v[0],0)&&near(v[1],-1),"r270 x down");
  v=screen(3,0,1,0);check(near(v[0],1)&&near(v[1],0),"r270 y right");
  v=screen(2,1,2,3);check(near(v[0],-1)&&near(v[1],-2)&&near(v[2],3),"r180");
  v=screen(0,1,2,3);check(near(v[0],1)&&near(v[1],2)&&near(v[2],3),"r0");
  float dt=.02f;
  // held upright: turning left (about the screen's up) turns left; tilting the top toward you looks up
  float[] up={0,9.81f,0};
  v=step(new float[]{0,1,0},up,dt,1,1,false);check(near(v[0],dt)&&near(v[1],0),"upright yaw");
  v=step(new float[]{0,-1,0},up,dt,1,1,false);check(near(v[0],-dt),"upright yaw right");
  v=step(new float[]{1,0,0},up,dt,1,1,false);check(near(v[0],0)&&near(v[1],dt),"pitch up");
  v=step(new float[]{1,0,0},up,dt,1,1,true);check(near(v[1],-dt),"pitch inverted");
  // tilted back however far: a turn of the body turns the view by the same amount
  for(int deg=0;deg<=80;deg+=10){double t=Math.toRadians(deg);float c=(float)Math.cos(t),s=(float)Math.sin(t);
   float[] u={0,9.81f*c,9.81f*s};v=step(new float[]{0,c,s},u,dt,1,1,false);check(Math.abs(v[0]-dt)<1e-4f,"player space "+deg);}
  // twisting the phone about its own screen normal while held upright is not a turn of the body
  v=step(new float[]{0,0,1},up,dt,1,1,false);check(near(v[0],0),"roll upright ignored");
  // flat on a table: turning it turns the view
  v=step(new float[]{0,0,1},new float[]{0,0,9.81f},dt,1,1,false);check(near(v[0],dt),"flat yaw");
  // no gravity sensor: the screen's own up axis turns
  v=step(new float[]{0,1,0},null,dt,1,1,false);check(near(v[0],dt),"no gravity");
  // sensitivity, bounded
  v=step(new float[]{0,1,0},up,dt,2,3,false);check(near(v[0],2*dt),"gain x");
  v=step(new float[]{1,0,0},up,dt,2,3,false);check(near(v[1],3*dt),"gain y");
  v=step(new float[]{0,1,0},up,dt,100,Float.NaN,false);check(near(v[0],4*dt),"gain bounded");
  // a phone held still does not creep; slow turns ease in
  v=step(new float[]{0,.01f,0},up,dt,1,1,false);check(near(v[0],.01f*.5f*dt),"tighten");
  v=step(new float[]{0,0,0},up,dt,1,1,false);check(v[0]==0&&v[1]==0,"still");
  // bad samples send nothing; a stalled sensor cannot jerk the view
  v=step(new float[]{Float.NaN,1,0},up,dt,1,1,false);check(v[0]==0&&v[1]==0,"nan rate");
  v=step(new float[]{0,1,0},up,0,1,1,false);check(v[0]==0,"first sample");
  v=step(new float[]{0,1,0},up,-1,1,1,false);check(v[0]==0,"backwards");
  v=step(new float[]{0,1,0},up,Float.NaN,1,1,false);check(v[0]==0,"nan time");
  v=step(new float[]{0,1,0},up,5,1,1,false);check(near(v[0],GyroPolicy.LONGEST_STEP),"stall clamped");
  v=step(new float[]{0,1,0},new float[]{Float.NaN,9.81f,0},dt,1,1,false);check(near(v[0],dt),"bad gravity: screen axis");
  v=step(new float[]{0,1,0},new float[]{0,.1f,0},dt,1,1,false);check(near(v[0],dt),"free fall: screen axis");
  // the option: off by default, bad stored values fall back to off / 1
  check(GyroPolicy.MODES.length==3,"modes");
  for(int m:new int[]{-1,3,99,Integer.MIN_VALUE})check(GyroPolicy.mode(m)==GyroPolicy.OFF,"bad mode");
  check(GyroPolicy.mode(1)==GyroPolicy.ALWAYS&&GyroPolicy.mode(2)==GyroPolicy.WHILE_TOUCHING,"modes kept");
  TouchLayout l=new TouchLayout();check(l.gyroMode==GyroPolicy.OFF&&l.gyroX==1&&l.gyroY==1&&!l.gyroInvert,"defaults");
  l.gyroMode=7;l.gyroX=Float.NaN;l.gyroY=99;l.sanitize();check(l.gyroMode==GyroPolicy.OFF&&l.gyroX==1&&l.gyroY==4,"sanitize");
  System.out.println("PASS: gyro aim math (every display rotation; upright, tilted back 0-80 degrees, flat; sensitivity, invert, still phone, bad samples, stalls; off by default)");
 }
}
""")
subprocess.run(['javac', '-d', str(OUT), str(J / 'GyroPolicy.java'), str(J / 'TouchLayout.java'), str(check)], check=True)
subprocess.run(['java', '-cp', str(OUT), 'com.halo.decomp.GyroCheck'], check=True)

# --- gyro aim wiring: flat only, follows the game's life, the option's settings shared
activity = (J / 'HaloActivity.java').read_text(encoding='utf-8')
aim = (J / 'GyroAim.java').read_text(encoding='utf-8')
touch = (J / 'TouchControls.java').read_text(encoding='utf-8')
pads = (J / 'GamepadSupport.java').read_text(encoding='utf-8')
manifest = (ROOT / 'port/android/app/src/main/AndroidManifest.xml').read_text(encoding='utf-8')
flat = activity[activity.index('if (!BuildConfig.APPLICATION_ID.endsWith(".vr") && mLayout != null)'):]
flat = flat[:flat.index('\n        }\n')]
assert 'gyro = new GyroAim(this,touchControls);' in flat and 'touchControls.setGyro(gyro);' in flat
for life in ['if (gyro != null) gyro.resume();', 'if (gyro != null) gyro.focus(hasFocus);']:
    assert activity.count(life) == 1, life
assert activity.count('if (gyro != null) gyro.pause();') == 2  # paused and destroyed
assert 'touch.gyroMode()!=GyroPolicy.OFF' in aim and 'sensors.unregisterListener(this);' in aim
assert 'SENSOR_DELAY_GAME' in aim and 'if(!touch.gyroAiming()) return;' in aim
assert 'static void look(float yaw,float pitch) { nativeLook(yaw,pitch); }' in touch
assert 'if(editing||menus||layout.gyroMode==GyroPolicy.OFF) return false;' in touch
for key in ['"gyroMode"', '"gyroX"', '"gyroY"', '"gyroInvert"']:
    assert touch.count(key) == 2 and key in pads, key  # read and saved in game; saved by the launcher
assert '<uses-feature android:name="android.hardware.sensor.gyroscope" android:required="false" />' in manifest
assert 'GyroAim' not in (ROOT / 'port/android/host/host_sdl.c').read_text(encoding='utf-8')  # no native change
print('PASS: gyro aim wiring (flat only; stops when paused, unfocused, off or editing; settings shared with the launcher; optional feature)')
