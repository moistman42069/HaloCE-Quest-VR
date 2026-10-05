"""Production vehicle aim/head tutorial/config checks; no device acceptance implied."""
from pathlib import Path
import re,subprocess,os,tempfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test18-checks';OUT.mkdir(parents=True,exist_ok=True)
def fn(s,name):
 m=re.search(r'^(?:static )?[\w *]+\b'+name+r'\s*\([^;{}]*\)\s*\{',s,re.M);assert m,name
 end=m.end();depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]+'\n'
def run(name,code,extra=()):
 p=OUT/(name+'.c');p.write_text(code,encoding='utf-8')
 subprocess.run(['clang','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-missing-braces','-fno-sanitize-recover=all','-fsanitize=address,undefined','-I',str(ROOT),str(p),*extra,'-lm','-pthread','-o',str(OUT/name)],check=True)
 subprocess.run([str(OUT/name)],check=True)
s=(ROOT/'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
pre=r'''
#include <assert.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#define HALO_XR_FRAME_SHOULD_RENDER 1
#define HALO_XR_FRAME_VIEWS_VALID 2
#define HALO_XR_FRAME_FOCUSED 4
#define HALO_XR_FRAME_RECENTRED 8
#define HALO_XR_BUTTON_LEFT_THUMB 1
#define HALO_XR_BUTTON_RIGHT_THUMB 2
static struct {
 int active,stereo_enabled,force_render,aiming,hand_aiming,recentre_held,hand_aim,heading_valid,aiming_last_frame,seated;
 float diag_yaw,diag_walk_speed,head_yaw,aim_yaw,heading,last_aim_yaw;
 float run_push,comfort_move,comfort_turn;
 int recentre_source;
 struct {unsigned flags,buttons,hand_valid[2];struct {float orientation[4];} head,aim[2];float thumb[4];long long predicted_display_period;} frame;
} vr;
static int frame_begin(void){return 1;}
static void synthesize_views(void){}
static void host_xr_recenter(void){}
static void update_aim_pose(void){}
static int hand_forward(float f[3]){f[0]=0;f[1]=0;f[2]=1;return 1;}
static void turn(void){}
/* test24b: the comfort vignette's motion (test_test24b) */
static float comfort_stick(float x,float y){(void)x;(void)y;return 0.0f;}
static void comfort_update(double seconds){(void)seconds;}
/* test25: the vehicle report's diagnostics (test_test25) */
static void aim_diagnostics(float g,int s,int h,const float *b,float p){(void)g;(void)s;(void)h;(void)b;(void)p;}
static struct {int valid;float yaw,pitch;} tutorial_look;
'''
helpers=''.join(fn(s,n) for n in ['rotate','to_halo','head_forward','wrap_angle','vr_aim','vr_script_head_valid','vr_head_look_reset','vr_head_look_actions'])
run('aim-tutorial',pre+helpers+r'''
static void reset(void){
 memset(&vr,0,sizeof(vr));vr.active=vr.stereo_enabled=vr.hand_aim=1;vr.frame.flags=7;
 vr.frame.head.orientation[3]=1;vr.frame.aim[1].orientation[3]=1;
 vr.frame.aim[0].orientation[1]=sinf(.4f);vr.frame.aim[0].orientation[3]=cosf(.4f);
 vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=2;vr_head_look_reset();
}
int main(void){
 float f[3],heading=0;reset();
 assert(vr_aim(0,1,2,&heading,f));assert(fabsf(f[0]-1)<1e-5&&fabsf(f[1])<1e-5&&!vr.hand_aiming);
 assert(vr_aim(0,1,3,&heading,f));assert(fabsf(f[1])>.5f&&!vr.hand_aiming);
 vr.hand_aim=0;assert(vr_aim(0,1,2,&heading,f));assert(fabsf(f[0]-1)<1e-5); /* aim setting independent */
 vr.frame.hand_valid[1]=0;assert(!vr_aim(0,1,2,&heading,f));assert(vr.aiming&&!vr.hand_aiming);
 assert(vr_aim(0,1,0,&heading,f));assert(fabsf(f[0]-1)<1e-5); /* explicit head */
 assert(!vr_aim(0,1,-1,&heading,f));assert(!vr.aiming&&vr.seated); /* stick stays native */
 vr.hand_aim=1;assert(vr_aim(0,0,1,NULL,f));assert(vr.hand_aiming&&!vr.seated); /* weapon behavior unchanged */
 reset();assert(!vr_head_look_actions());
 /* Slow movement accumulates; it is not lost to the old per-tick speed threshold. */
 unsigned bits=0;
 for(int i=1;i<=100;i++) {float pitch=.0005f*i;vr.frame.head.orientation[0]=sinf(pitch/2);vr.frame.head.orientation[3]=cosf(pitch/2);bits|=vr_head_look_actions();}
 assert(bits&1);vr.frame.head.orientation[0]=0;vr.frame.head.orientation[3]=1;assert(vr_head_look_actions()&2);
 reset();assert(!vr_head_look_actions());
 for(int i=0;i<1000;i++){vr.frame.aim[0].orientation[1]=(float)i;assert(!vr_head_look_actions());}
 vr.frame.head.orientation[1]=sinf(.15f);vr.frame.head.orientation[3]=cosf(.15f);bits=vr_head_look_actions();assert(bits&(4|8));
 vr.frame.flags=0;assert(!vr_head_look_actions());vr.frame.flags=7;assert(!vr_head_look_actions());
 vr.frame.flags|=8;assert(!vr_head_look_actions());vr.frame.flags=7;
 vr.frame.head.orientation[0]=NAN;assert(!vr_head_look_actions());
 puts("PASS: independent right/left/head/stick, lost tracking, weapon mode, slow head look, no controller false positives, recenter/focus/invalid reset");
}
''')
# Full production config, including one-time upgrade, atomic persistence and opt-out.
s=(ROOT/'port/linux/src/port_config.c').read_text(encoding='utf-8').replace('#include "platform.h"','static void platform_log(const char *s, ...) {(void)s;}').replace('#include <SDL3/SDL.h>','')
p=OUT/'config.c';p.write_text('#define HALO_ANDROID 1\n#define HALO_VR 1\n'+s+r'''
#include <assert.h>
int main(int argc,char **argv){
 assert(argc==2);config_vr_vehicle_defaults();
 assert(!strcmp(config_string("vr.vehicle_view"),atoi(argv[1])?"first_person":"chase"));
 assert(!strcmp(config_string("vr.vehicle_steering"),atoi(argv[1])?"left":"right"));return 0;
}
''',encoding='utf-8')
subprocess.run(['clang','-std=gnu11','-fsanitize=address,undefined','-I',str(ROOT/'port/linux/src'),'-I',str(ROOT/'port/third_party/tomlc17'),str(p),str(ROOT/'port/third_party/tomlc17/tomlc17.c'),'-pthread','-o',str(OUT/'config')],check=True)
for initial,expected in [(None,0),('[vr]\nvehicle_view="first_person"\nvehicle_steering="stick"\n',0),('[vr]\nvehicle_defaults_applied=true\nvehicle_view="first_person"\nvehicle_steering="left"\n',1)]:
 with tempfile.TemporaryDirectory(dir=OUT) as folder:
  p=Path(folder)/'config.toml'
  if initial:p.write_text(initial)
  env=dict(os.environ,HALO_DATA_ROOT=folder)
  for _ in range(2):subprocess.run([str(OUT/'config'),str(expected)],env=env,check=True)
  assert 'vehicle_defaults_applied=true' in p.read_text() or 'vehicle_defaults_applied = true' in p.read_text()
with tempfile.TemporaryDirectory(dir=OUT) as folder:
 p=Path(folder)/'config.toml';p.write_text('[renderer]\nvr_geometry_revision=1\n[vr]\nvehicle_view="first_person"\nvehicle_steering="stick"\n')
 blocked=Path(folder)/'config.toml.vehicle-defaults.tmp';blocked.mkdir();(blocked/'keep').write_text('keep')
 env=dict(os.environ,HALO_DATA_ROOT=folder)
 for _ in range(2):
  subprocess.run([str(OUT/'config'),'0'],env=env,check=True)
  assert 'vehicle_view="first_person"' in p.read_text()
 assert (Path(folder)/'config.toml.pre-vehicle-defaults').is_file()
print('PASS: fresh/upgrade/default persistence, explicit later choice, failed atomic write retry/backup')
r=(ROOT/'port/linux/game/vr_render.c').read_text(encoding='utf-8')
pre=r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define FLAG(x) (1u<<(x))
#define _collision_test_structure_bit 0
typedef union {struct{float x,y,z;};float n[3];} real_point3d;
typedef union {struct{float i,j,k;};float n[3];} real_vector3d;
struct unit_datum {long definition_index;};
struct collision_result {float t;};
static struct {struct {long vehicle_index,unit_index;float heading;}seat;} vr_render;
static struct unit_datum vehicle={1};
static const char *tag="vehicles\\warthog\\mp_warthog";
static float all_up,local_up,all_forward,all_right;static int collided;
static double config_real(const char *key){
 if(!strcmp(key,"vr.vehicle_all_up"))return all_up;
 if(!strcmp(key,"vr.vehicle_warthog_up"))return local_up;
 if(!strcmp(key,"vr.vehicle_all_forward"))return all_forward;
 if(!strcmp(key,"vr.vehicle_all_right"))return all_right;
 return 0;
}
static struct unit_datum *unit_try_and_get(long id){return id==42||id==100?&vehicle:NULL;}
static const char *tag_get_name(long id){assert(id==1);return tag;}
static float vr_units_per_metre(void){return 1.0f;}
static float dot_product3d(const real_vector3d *a,const real_vector3d *b){return a->i*b->i+a->j*b->j+a->k*b->k;}
static void scale_vector3d(const real_vector3d *v,float t,real_vector3d *out){out->i=v->i*t;out->j=v->j*t;out->k=v->k*t;}
static int collision_test_vector(unsigned flags,const real_point3d *p,const real_vector3d *v,long ignore,struct collision_result *out){
 (void)p;(void)v;assert(flags==1&&ignore==42);out->t=.5f;return collided;
}
static int active=1,cinematic=0,local=0,tracked=1;
static struct {long unit_index;}player={42};
static real_vector3d gaze={1,0,0};
static int vr_active(void){return active;}
static int cinematic_in_progress(void){return cinematic;}
static short local_player_get_next(long previous){assert(previous==NONE);return local;}
static long local_player_get_player_index(short i){assert(i==0);return 10;}
#define player_get(i) (&player)
static void unit_get_camera_position(long i,real_point3d *p){assert(i==42);*p=(real_point3d){1,2,3};}
static int vr_script_head_view(const float p[3],float out[3],float f[3]){memcpy(out,p,12);memcpy(f,gaze.n,12);return tracked;}
static void vector_from_points3d(const real_point3d *a,const real_point3d *b,real_vector3d *out){out->i=b->x-a->x;out->j=b->y-a->y;out->k=b->z-a->z;}
static void normalize3d(real_vector3d *v){float l=sqrtf(dot_product3d(v,v));if(l>0)scale_vector3d(v,1/l,v);}
#define cosine cosf
/* test22: the frame's seat heading (tested in test_test22); here the seat's own */
static real vr_seat_frame_heading(void){return vr_render.seat.heading;}
'''
run('seat-gaze',pre+''.join(fn(r,n) for n in ['vr_vehicle_profile','vr_vehicle_offset','vr_vehicle_adjust_anchor','vr_script_can_see_point'])+r'''
int main(void){
 assert(!vr_vehicle_profile(NULL)&&!vr_vehicle_profile("custom"));
 const char *names[]={"warthog","ghost","banshee","scorpion","pelican"};
 for(int i=0;i<5;i++)assert(!strcmp(vr_vehicle_profile(names[i]),names[i]));
 vr_render.seat.vehicle_index=100;vr_render.seat.unit_index=42;
 all_up=.15f;local_up=.10f;all_forward=.2f;all_right=.1f;
 real_point3d p={0,0,0};vr_vehicle_adjust_anchor(&p);assert(fabsf(p.x-.2f)<1e-6&&fabsf(p.y+.1f)<1e-6&&fabsf(p.z-.25f)<1e-6);
 vr_render.seat.heading=1.5707963268f;p=(real_point3d){0,0,0};vr_vehicle_adjust_anchor(&p);assert(fabsf(p.x-.1f)<1e-6&&fabsf(p.y-.2f)<1e-6);
 all_up=999;local_up=999;assert(vr_vehicle_offset("warthog","up")==.5f);
 all_up=NAN;local_up=INFINITY;assert(vr_vehicle_offset("warthog","up")==0);
 collided=1;vr_render.seat.heading=0;p=(real_point3d){0,0,0};vr_vehicle_adjust_anchor(&p);assert(fabsf(p.x-.096f)<1e-6);
 real_point3d target={5,2,3};int result=0;
 assert(vr_script_can_see_point(42,&target,.1f,&result)&&result);
 gaze=(real_vector3d){0,1,0};assert(vr_script_can_see_point(42,&target,.1f,&result)&&!result);
 target=(real_point3d){1,6,3};assert(vr_script_can_see_point(42,&target,.1f,&result)&&result);
 assert(!vr_script_can_see_point(100,&target,.1f,&result)); /* other player/AI: native */
 cinematic=1;assert(!vr_script_can_see_point(42,&target,.1f,&result));cinematic=0;
 tracked=0;assert(!vr_script_can_see_point(42,&target,.1f,&result));tracked=1;
 local=NONE;assert(!vr_script_can_see_point(42,&target,.1f,&result));local=0;
 active=0;assert(!vr_script_can_see_point(42,&target,.1f,&result));
 puts("PASS: five vehicle profiles/custom fallback, offset axes/bounds/nonfinite/collision, head gaze cones and local-only fallback guards");
}
''')
hs=(ROOT/'source/hs/hs_library_external.c').read_text(encoding='utf-8')
assert 'cutscene_flag_index >= 0 && cutscene_flag_index < global_scenario_get()->cutscene_flags.count' in fn(hs,'hs_unit_can_see_flag')
assert 'hs_script_can_see_point(' in fn(hs,'hs_unit_can_see_flag') and 'hs_script_can_see_point(' in fn(hs,'hs_unit_can_see_object')
print('PASS: flag zero accepted, sentinel/out-of-range guarded, both script target types routed through head gaze')
