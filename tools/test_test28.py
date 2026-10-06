"""Test28 (1.0.10): a client joining an OpenCE co-op game in progress halted.

Evidence (kept private): a Quest 3 log (1.0.9, 2026-10-06 10:16) joined a
public 18-player co-op game on d40 at tick 20227 with no unit yet; within a
tick: EXCEPTION halt in camera_scripting.c #370 (forward -0.990,-0.060,-0.126,
up 0,0,1). Symbolized: network_coop_client_tick -> the host's camera ->
director_update -> scripted_camera_update. OpenCE's client_watch_host_from_behind
forces up to the world's and leaves it so when distributed_axes_make_valid
refuses it (more than about 6 degrees from square); OpenCE's release builds
log the check and go on, this app's halted. Fixed: up made square to forward;
the APKs build in release mode, as OpenCE's do. Run with python3 tools/test_test28.py.
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
static real normalize3d(real_vector3d *v){ real l=sqrtf(v->i*v->i+v->j*v->j+v->k*v->k); if(l<1e-6f) return 0.f; v->i/=l; v->j/=l; v->k/=l; return l; }
static void point_from_line3d(real_point3d const *p, real_vector3d const *v, real t, real_point3d *o){ o->x=p->x+v->i*t; o->y=p->y+v->j*t; o->z=p->z+v->k*t; }
static void points_interpolate(real_point3d const *a, real_point3d const *b, real t, real_point3d *o){ for(int i=0;i<3;i++) o->n[i]=a->n[i]+(b->n[i]-a->n[i])*t; }
static void vectors_interpolate(real_vector3d const *a, real_vector3d const *b, real t, real_vector3d *o){ for(int i=0;i<3;i++) o->n[i]=a->n[i]+(b->n[i]-a->n[i])*t; }
''' + watch + r'''
/* the scripted camera's check (camera_scripting.c #370: valid_real_vector3d_axes2) */
static int square(real_vector3d const *f, real_vector3d const *u){
 real lf=f->i*f->i+f->j*f->j+f->k*f->k, lu=u->i*u->i+u->j*u->j+u->k*u->k, d=f->i*u->i+f->j*u->j+f->k*u->k;
 return fabsf(lf-1.f)<1e-3f && fabsf(lu-1.f)<1e-3f && fabsf(d)<1e-3f; }
int main(void){
 int n=0;
 for(int yaw=0;yaw<360;yaw+=7) for(int pitch=-90;pitch<=90;pitch+=3){
  real y=yaw*3.14159265f/180, p=pitch*3.14159265f/180;
  coop_presentation.watching_host_valid=FALSE;
  for(int frame=0;frame<6;frame++){
   real_point3d pos={{10,20,3}}; real_vector3d f={{cosf(p)*cosf(y),cosf(p)*sinf(y),sinf(p)}}, u={{0,0,1}};
   client_watch_host_from_behind(&pos,&f,&u);
   assert(square(&f,&u)); assert(u.k>=-1e-6f); n++; } }
 /* the logged case: forward -0.990,-0.060,-0.126 */
 { real_vector3d f={{-0.990173f,-0.060274f,-0.126194f}},u={{0,0,1}}; real_point3d pos={{-35.9f,-18.8f,1.6f}};
   normalize3d(&f); coop_presentation.watching_host_valid=FALSE; client_watch_host_from_behind(&pos,&f,&u);
   assert(square(&f,&u) && u.k>0.99f); }
 printf("PASS: %d host views (every pitch, straight up and down too): the camera watching the host is upright and its axes square"
        " (the logged d40 halt's case included)\n", n);
}
''')

# --- the APKs build in release mode, as OpenCE's: a failed check is logged and play goes on
assert 'vr) flags=(--vr --release) ;;' in build and 'flat) flags=(--release) ;;' in build
print('PASS: the APKs build with --release (HALO_RELEASE), as OpenCE ships its builds')

# --- version, identity, package markers
assert int(re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1)) >= 36
assert int(re.search(r': "1\.0\.(\d+)"', gradle).group(1)) >= 10
assert 'HaloCE Quest test28 candidate 1.0.10' in frame
assert 'candidate_at_least(args.label, 28)' in package
print('PASS: test28 wiring (version 1.0.10 / 36, identity, package markers)')
