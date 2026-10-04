"""Test20c: separate hand and gun calibration, floating hands/arms, hands-only cuff.

Owner video/log (2026-10-04): the empty hands looked natural at controller pitch
-70, but that same calibration tilted the gun 70 degrees down. Test20c gives
the visible hand (vr.hand_*) and the one-handed gun (vr.weapon_*) their own
rotations, migrates saved hand-comfort values once, adds floating hand modes
and gathers hidden arms behind the wrist. Production functions run under
ASan/UBSan with small stubs; no headset or game data is used.
Run under Linux/WSL with clang.
"""
from pathlib import Path
import re, subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test20c-hands'; OUT.mkdir(parents=True,exist_ok=True)

def fn(text,name):
    m=re.search(r'^(?:static )?(?:inline )?[\w *]+\b'+re.escape(name)+r'\s*\([^;{]*\)\s*\{',text,re.M)
    assert m, name
    a=text.index('{',m.start()); b=a+1; depth=1
    while depth:
        depth+=(text[b]=='{')-(text[b]=='}'); b+=1
    return text[m.start():b]+'\n'

def run(name,text):
    p=OUT/(name+'.c'); p.write_text(text)
    subprocess.run(['clang','-std=gnu11','-O1','-Wall','-Wextra','-Wno-unused-function','-Wno-unused-variable',
                    '-Wno-unused-parameter','-fsanitize=address,undefined','-I',str(ROOT),str(p),'-lm','-o',str(OUT/name)],check=True)
    subprocess.run([str(OUT/name)],check=True)

frame=(ROOT/'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
render=(ROOT/'port/linux/game/vr_render.c').read_text(encoding='utf-8')
menu=(ROOT/'port/linux/game/vr_menu.c').read_text(encoding='utf-8')
config=(ROOT/'port/linux/src/port_config.c').read_text(encoding='utf-8')

# --- static wiring: settings, menu, separation of concerns
for key,default in [('vr.hand_left_pitch','"-70.0"'),('vr.hand_right_pitch','"-70.0"'),('vr.hand_left_yaw','"0.0"'),
                    ('vr.hand_right_roll','"0.0"'),('vr.weapon_pitch','"0.0"'),('vr.weapon_yaw','"0.0"'),
                    ('vr.weapon_roll','"0.0"'),('vr.hand_tracking','"\\"ik\\""'),('vr.calibration_split_applied','"false"')]:
    assert re.search(r'\{ "'+re.escape(key)+r'", _config_\w+, '+re.escape(default),config), key
assert '{ "HANDS", "vr.hand_tracking", _vr_setting_string, 3, { { "BODY IK", "ik" }, { "FLOATING", "floating" }, { "FLOAT + ARMS", "floating_arms" } } }' in menu
for page in ('"LEFT HAND"','"RIGHT HAND"','"GUN"','"CONTROLLER LEFT"','"CONTROLLER RIGHT"'):
    assert page in menu, page
assert 'config_default_real(key)' in menu and 'config_default_real(weapon_keys[a])' in menu
ik=fn(render,'vr_render_first_person_ik')
assert 'tracking == 0 && vr_body_setting()' in ik, 'only body IK may use the body shoulders'
assert ik.count('vr_hand_pose(controller, vr_render.game_camera_position.n, hand.n, f.n, u.n)')==1, 'free hand uses the calibrated hand pose'
assert 'vr_hand_pose(side, vr_render.game_camera_position.n' in fn(render,'vr_publish_body')
assert 'vr_float_shoulder(matrices, chain, &target, &shoulder)' in ik and 'if (tracking == 1)' in ik
aim=fn(frame,'compute_aim_pose')
assert 'vr_alignment_multiply(vr.frame.aim[w].orientation, vr.weapon_rotation[w], vr.aim_pose.orientation)' in aim
assert 'hand_rotation' not in aim, 'the hand rotation must never reach the gun'
assert 'weapon_rotation' not in fn(frame,'vr_hand_pose'), 'the gun rotation must never reach the hand'

common=r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "port/linux/src/vr_alignment.h"
'''

# --- gun angle: composition, mirroring, two-handed override, hand independence
quat=r'''
static void to_matrix(const float q[4],float m[3][3]){float x=q[0],y=q[1],z=q[2],w=q[3];
 m[0][0]=1-2*(y*y+z*z);m[0][1]=2*(x*y-z*w);m[0][2]=2*(x*z+y*w);
 m[1][0]=2*(x*y+z*w);m[1][1]=1-2*(x*x+z*z);m[1][2]=2*(y*z-x*w);
 m[2][0]=2*(x*z-y*w);m[2][1]=2*(y*z+x*w);m[2][2]=1-2*(x*x+y*y);}
'''
run('gun',common+r'''
struct halo_xr_pose { float position[3], orientation[4]; };
static struct { int weapon_hand, two_handed, two_handed_enabled, two_handed_mode, two_hand_held;
 struct halo_xr_pose aim_pose; float weapon_rotation[2][4], hand_rotation[2][4];
 struct { struct halo_xr_pose aim[2], grip[2]; unsigned hand_valid[2]; } frame; } vr;
static int empty;
static int vr_hand_empty(void){return empty;}
'''+fn(frame,'rotate')+fn(frame,'look_rotation')+aim+quat+r'''
static unsigned seed=99;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
int main(void){
 vr.two_handed_enabled=1;vr.two_handed_mode=1;vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3;
 for(int n=0;n<500;n++){
  float d[3]={rnd()*360-180,rnd()*360-180,rnd()*360-180},g[3]={5.f*(int)(rnd()*72-36),5.f*(int)(rnd()*72-36),5.f*(int)(rnd()*72-36)};
  float m[3]={g[0],-g[1],-g[2]},hand[3]={-70,rnd()*40-20,rnd()*40-20};
  for(int h=0;h<2;h++){vr_alignment_rotation(d,vr.frame.aim[h].orientation);vr.frame.aim[h].position[0]=h*.4f;}
  vr_alignment_rotation(g,vr.weapon_rotation[1]);vr_alignment_rotation(m,vr.weapon_rotation[0]);
  vr_alignment_rotation(hand,vr.hand_rotation[0]);vr_alignment_rotation(hand,vr.hand_rotation[1]);
  for(int w=0;w<2;w++){
   float expect[4];vr.weapon_hand=w;vr.two_hand_held=0;
   compute_aim_pose();assert(!vr.two_handed);
   vr_alignment_multiply(vr.frame.aim[w].orientation,vr.weapon_rotation[w],expect);
   assert(!memcmp(expect,vr.aim_pose.orientation,16));
   assert(!memcmp(vr.aim_pose.position,vr.frame.aim[w].position,12));
  }
  /* the left hand's gun angle is the right hand's seen in a mirror */
  {float r[3][3],l[3][3];to_matrix(vr.weapon_rotation[1],r);to_matrix(vr.weapon_rotation[0],l);
   for(int i=0;i<3;i++)for(int j=0;j<3;j++){float s=(i==0)!=(j==0)?-1.f:1.f;assert(fabsf(l[i][j]-s*r[i][j])<1e-4f);}}
 }
 /* zero gun calibration leaves the aim exactly as test20b */
 {float z[3]={0};vr_alignment_rotation(z,vr.weapon_rotation[1]);vr.weapon_hand=1;compute_aim_pose();
  assert(!memcmp(vr.aim_pose.orientation,vr.frame.aim[1].orientation,16));}
 /* both hands on the gun: the hands' line still decides, as before */
 {vr.weapon_hand=1;vr.two_hand_held=1;vr.frame.grip[1].position[0]=0;vr.frame.grip[0].position[0]=0;
  vr.frame.grip[0].position[2]=-0.3f;compute_aim_pose();assert(vr.two_handed);
  float f[3],fw[3]={0,0,-1};rotate(vr.aim_pose.orientation,fw,f);assert(fabsf(f[2]+1)<1e-4f);}
 puts("PASS: 500 gun calibrations compose on the controller aim for either hand, mirrored left; zero is unchanged; two-handed line overrides; hand rotation never reaches the gun");
}
''')

# --- one-time migration of saved hand-comfort rotations
mig=fn(frame,'migrate_calibration_split')
run('migration',common+r'''
#include <stdarg.h>
static const char *keys[64];static double values[64];static int count,fail,applied;
static double *slot(const char*k){for(int i=0;i<count;i++)if(!strcmp(keys[i],k))return &values[i];keys[count]=strdup(k);values[count]=0;return &values[count++];}
static double config_real(const char*k){return *slot(k);}
static int config_write_real(const char*k,double v){if(fail)return 0;*slot(k)=v;return 1;}
static int config_boolean(const char*k){(void)k;return applied;}
static int config_write_boolean(const char*k,int v){(void)k;applied=v;return 1;}
static void platform_log(const char*f,...){(void)f;}
'''+mig+r'''
static void set(const char*side,double p,double y,double r){char k[64];
 snprintf(k,64,"vr.align_%s_pitch",side);*slot(k)=p;snprintf(k,64,"vr.align_%s_yaw",side);*slot(k)=y;snprintf(k,64,"vr.align_%s_roll",side);*slot(k)=r;
 snprintf(k,64,"vr.hand_%s_pitch",side);*slot(k)=-70;snprintf(k,64,"vr.hand_%s_yaw",side);*slot(k)=0;snprintf(k,64,"vr.hand_%s_roll",side);*slot(k)=0;}
int main(void){
 /* owner's first config: both hands -70/0/-25 */
 set("left",-70,0,-25);set("right",-70,0,-25);migrate_calibration_split();
 assert(applied&&*slot("vr.hand_left_pitch")==-70&&*slot("vr.hand_left_roll")==-25&&*slot("vr.hand_right_roll")==-25);
 assert(*slot("vr.align_left_pitch")==0&&*slot("vr.align_right_roll")==0);
 /* a second run never moves anything again */
 *slot("vr.align_left_pitch")=-30;migrate_calibration_split();assert(*slot("vr.align_left_pitch")==-30&&*slot("vr.hand_left_pitch")==-70);
 /* untouched controllers keep the new -70 hand default; a firmware roll flip stays a controller fix */
 applied=0;set("left",0,0,0);set("right",-10,0,180);migrate_calibration_split();
 assert(applied&&*slot("vr.hand_left_pitch")==-70&&*slot("vr.align_right_roll")==180&&*slot("vr.align_right_pitch")==-10&&*slot("vr.hand_right_pitch")==-70);
 /* a failed save leaves the migration pending */
 applied=0;fail=1;set("left",-70,0,0);migrate_calibration_split();assert(!applied);
 puts("PASS: saved hand-comfort rotations move once to the hand; untouched and roll-flipped controllers keep theirs; failed saves retry");
}
''')

# --- floating shoulder and hidden-arm presentation
types=r'''
typedef float real; typedef int boolean; typedef short sh;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define PIN(x,lo,hi) ((x)<(lo)?(lo):(x)>(hi)?(hi):(x))
typedef union { struct { real x,y,z; }; real n[3]; } real_point3d;
typedef union { struct { real i,j,k; }; real n[3]; } real_vector3d;
typedef struct { real scale; real_vector3d forward,left,up; real_point3d position; } real_matrix4x3;
struct animation_graph { struct { short count; } nodes; short parent[16]; };
static real units=3.048f; static int hands_only, tracking;
static real vr_units_per_metre(void){return units;}
static void scale_vector3d(real_vector3d const *v,real s,real_vector3d *o){for(int i=0;i<3;i++)o->n[i]=v->n[i]*s;}
static int vr_render_hands_only(void){return hands_only;}
static int vr_hand_tracking_mode(void){return tracking;}
static short vr_find_node(struct animation_graph *g,const char*a,const char*b){(void)g;(void)a;(void)b;return 7;}
static boolean vr_node_under(struct animation_graph *g,short node,short root){
 if(root<0)return FALSE; for(short n=node;n>=0;n=g->parent[n]){if(n==root)return TRUE;if(g->parent[n]==n)break;}return FALSE;}
'''
run('arms',common+types+fn(render,'vr_length')+fn(render,'vr_point_minus')+fn(render,'vr_unit_vector')+
    fn(render,'vr_hide_forearms')+fn(render,'vr_float_shoulder')+r'''
static unsigned seed=5;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
int main(void){
 /* 0 root; 1/2 upper arms; 3/4 forearms; 5/6 hands; 7 gun (right hand); 8 left finger */
 struct animation_graph g={{9},{-1,0,0,1,2,3,4,6,5}};
 short left[3]={1,3,5},right[3]={2,4,6};
 real_matrix4x3 m[9],orig[9];
 for(int i=0;i<9;i++){memset(&m[i],0,sizeof m[i]);m[i].scale=1;m[i].position.x=(real)i;}
 m[3].position=(real_point3d){{0,0,0}};m[5].position=(real_point3d){{0.30f*units,0,0}};
 m[4].position=(real_point3d){{0,1,0}};m[6].position=(real_point3d){{0.30f*units,1,0}};
 memcpy(orig,m,sizeof m);
 tracking=0;hands_only=0;vr_hide_forearms(m,&g,left,right);assert(!memcmp(m,orig,sizeof m));
 for(int mode=0;mode<2;mode++){
  memcpy(m,orig,sizeof m);hands_only=mode==0;tracking=mode==0?0:1;vr_hide_forearms(m,&g,left,right);
  for(int s=0;s<2;s++){short *c=s?right:left;
   for(int b=0;b<2;b++){assert(m[c[b]].scale==0);
    /* gathered 3.5 cm behind the wrist toward the elbow, not onto the elbow */
    assert(fabsf(m[c[b]].position.x-(orig[c[2]].position.x-0.035f*units))<1e-4f&&fabsf(m[c[b]].position.y-orig[c[2]].position.y)<1e-4f);}
   assert(!memcmp(&m[c[2]],&orig[c[2]],sizeof m[0]));}
  assert(!memcmp(&m[7],&orig[7],sizeof m[0])&&!memcmp(&m[8],&orig[8],sizeof m[0]));
 }
 /* floating arms: the hand target is always reachable, never moved */
 for(int n=0;n<5000;n++){
  real_matrix4x3 a[9];memcpy(a,orig,sizeof a);
  a[1].position=(real_point3d){{0,0,0}};a[3].position=(real_point3d){{0.28f*units,0,0}};a[5].position=(real_point3d){{0.28f*units,0.25f*units,0}};
  real_point3d shoulder={{(rnd()-.5f)*units,(rnd()-.5f)*units,(rnd()-.5f)*units}},target={{(rnd()-.5f)*3*units,(rnd()-.5f)*3*units,(rnd()-.5f)*3*units}},t0=target;
  real_point3d before=shoulder;
  vr_float_shoulder(a,left,&target,&shoulder);
  real_vector3d d;vr_point_minus(&target,&shoulder,&d);real dist=vr_length(&d),reach=(0.28f+0.25f)*units;
  assert(!memcmp(&target,&t0,sizeof target));
  assert(dist<=reach*0.97f*1.0001f&&dist>=(fabsf(0.28f-0.25f)*1.05f+0.01f)*units*0.9999f);
  real_vector3d moved;vr_point_minus(&shoulder,&before,&moved);
  vr_point_minus(&t0,&before,&d);real original=vr_length(&d);
  if(original<=reach*0.97f&&original>=(fabsf(0.28f-0.25f)*1.05f+0.01f)*units)assert(vr_length(&moved)==0);
 }
 assert(0.97f<0.996f); /* the arm solver keeps reachable targets exactly (its clamp starts at 0.996) */
 puts("PASS: hands-only and floating hands gather arms 3.5 cm behind each wrist, hands/fingers/gun untouched; IK unchanged");
 puts("PASS: 5000 floating-arm shoulders keep every controller target within reach without moving it");
}
''')
assert '(history ? 0.996f : 0.999f)' in fn(render,'vr_solve_arm')

gl=(ROOT/'port/linux/src/d3d8_gl.c').read_text(encoding='utf-8')
assert '#define STREAM_BUFFER_SIZE (safe_geometry ? 32 * 1024 * 1024 : 16 * 1024 * 1024)' in gl, 'Safe stream slots hold a 15.6 MB Autumn frame'
print('PASS: Safe geometry stream slots are 32 MB (test20b measured 15.6 MB/frame on a10), Normal stays 16 MB')
