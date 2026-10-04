"""Test21: floating hands, torso-following arms, neck-pivot full body, auto
two-hand lock, the Warthog horn and multiplayer melee.

Owner video/logs (2026-10-04 12:42-12:47, v1.0.2/test20e on Quest 3):
Floating still drew arms (test20d merged it with Float + Arms); Hands Only
with floating showed cut, slivered wrists; the arms did not follow body turns;
Full Body clipped when looking down. Then: the Warthog horn did not work,
swing melee fired too easily online, and two-hand grip should lock on its own.
Production functions run under ASan/UBSan with small stubs; no headset or
game data is used. Run under Linux/WSL with clang.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test21'; OUT.mkdir(parents=True, exist_ok=True)


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def run(name, text):
    p = OUT / (name + '.c'); p.write_text(text)
    subprocess.run(['clang', '-std=gnu11', '-O1', '-Wall', '-Wextra', '-Wno-unused-function', '-Wno-unused-variable',
                    '-Wno-unused-parameter', '-Wno-missing-field-initializers', '-Wno-missing-braces',
                    '-fsanitize=address,undefined', '-I', str(ROOT), str(p), '-lm', '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)


frame = (ROOT / 'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
render = (ROOT / 'port/linux/game/vr_render.c').read_text(encoding='utf-8')
menu = (ROOT / 'port/linux/game/vr_menu.c').read_text(encoding='utf-8')
config = (ROOT / 'port/linux/src/port_config.c').read_text(encoding='utf-8')

# --- static wiring
for key, default in [('vr.two_handed', '"\\"auto\\""'), ('vr.two_hand_auto_applied', '"false"'),
                     ('vr.melee_multiplayer', '"false"'), ('vr.hand_tracking', '"\\"ik\\""')]:
    assert re.search(r'\{ "' + re.escape(key) + r'", _config_\w+, ' + re.escape(default), config), key
assert '{ "FLOATING", "vr.arms=ik;vr.hand_tracking=floating" }, { "FLOAT + ARMS", "vr.arms=ik;vr.hand_tracking=floating_arms" }' in menu
assert '{ { "AUTO LOCK", "auto" }, { "SQUEEZE", "grip" }, { "OFF", "off" } }' in menu
assert '{ "IMPACT", "vr.melee=impact;vr.melee_multiplayer=false" }' in menu and '"SWING + ONLINE"' in menu
reload = fn(frame, 'vr_reload_settings')
assert 'if (vr.hand_tracking == 3)\n\t\t\tvr.hand_tracking = 0;' in reload, 'floating (1) and floating_arms (2) are distinct'
assert 'floating_arms' not in fn(frame, 'migrate_handedness'), 'floating_arms is no longer migrated away'
ik = fn(render, 'vr_render_first_person_ik')
assert 'int tracking = vr_hand_tracking_mode();' in ik and 'if (tracking == 2 && vr_render_hands_only())' in ik
assert 'forward = vr_body_heading(unit);' in ik and 'vr_heading_forward(forward.n)' not in ik, \
    'the arms face the torso, not the stick-turn heading'
assert 'if (!vr_render_hands_only() && vr_hand_tracking_mode() != 1) return;' in fn(render, 'vr_hide_forearms')
assert 'vr_set_network_game(game_connection() != _game_connection_local);' in fn(render, 'vr_render_actions')
assert 'if (vr.seated ? vr_horn_held() : vr.crouching)' in fn(frame, 'vr_take_actions')
body = fn(render, 'vr_render_body_matrices')
assert 'vr_neck_pivot(&vr_render.head_camera.position, &vr_render.head_camera.forward,' in body
assert 'target.z -= 0.20f * units;' not in body, 'the fixed horizontal-only neck offset is gone'
aim = fn(frame, 'compute_aim_pose')
assert 'if (!vr.two_hand_held || length < 0.05f)' in aim and '0.82f' not in aim, 'auto locks instead of the old magnet'
gestures = fn(frame, 'update_gestures')
for marker in ['vr.support_dwell >= 0.12f', 'support grip locked automatically', 'vr.support_rearmed',
               'fabsf(hands_apart - vr.support_engaged_apart) > 0.20f || along < 0.5f', 'physical_melee_allowed()']:
    assert marker in gestures, marker
print('PASS: static wiring (hand modes, torso heading for arms, neck pivot, auto two-hand lock, horn, online melee)')

common = r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define PIN(x,lo,hi) ((x)<(lo)?(lo):(x)>(hi)?(hi):(x))
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef union { real n[3]; struct { real x,y,z; }; } real_point3d;
typedef union { real n[3]; struct { real i,j,k; }; } real_vector3d;
typedef struct { real scale; real_vector3d forward,left,up; real_point3d position; } real_matrix4x3;
static real units = 3.048f;
static real vr_units_per_metre(void){return units;}
static void scale_vector3d(real_vector3d const *v,real s,real_vector3d *o){for(int i=0;i<3;i++)o->n[i]=v->n[i]*s;}
static unsigned seed=21;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
'''

# --- head yaw, torso yaw and the neck pivot
run('body', common + fn(render, 'vr_length') + fn(render, 'vr_point_minus') + fn(render, 'vr_unit_vector') +
    fn(render, 'vr_head_yaw_vector') + fn(render, 'vr_body_wanted_yaw') + fn(render, 'vr_neck_pivot') + r'''
static void head(real yaw,real pitch,real_vector3d *f,real_vector3d *u){
 f->i=cosf(pitch)*cosf(yaw);f->j=cosf(pitch)*sinf(yaw);f->k=sinf(pitch);
 u->i=-sinf(pitch)*cosf(yaw);u->j=-sinf(pitch)*sinf(yaw);u->k=cosf(pitch);}
static real wrap(real a){return atan2f(sinf(a),cosf(a));}
int main(void){
 int n;
 /* the head's yaw is exact at every pitch short of vertical, where the old flattened forward broke down */
 for(n=0;n<20000;n++){real yaw=(rnd()*2-1)*3.14159f,pitch=(rnd()*2-1)*1.5698f;real_vector3d f,u,y;head(yaw,pitch,&f,&u);
  assert(vr_head_yaw_vector(&f,&u,&y));assert(fabsf(wrap(atan2f(y.j,y.i)-yaw))<2e-3f);}
 {real_vector3d f,u,y;head(0.7f,-1.57079f,&f,&u);assert(vr_head_yaw_vector(&f,&u,&y)&&fabsf(atan2f(y.j,y.i)-0.7f)<1e-3f);}
 /* the torso: the head's yaw; hands ahead pull it halfway, within 45 degrees; hands behind are ignored */
 for(n=0;n<5000;n++){real yaw=(rnd()*2-1)*3.14159f,off=(rnd()*2-1)*1.2f;real_vector3d f,u,y;real_point3d h={{0,0,1.7f*units}},hands[2];
  head(yaw,0.2f,&f,&u);vr_head_yaw_vector(&f,&u,&y);
  for(int s=0;s<2;s++){real a=yaw+off+(s?-0.3f:0.3f);hands[s].x=cosf(a)*0.45f*units;hands[s].y=sinf(a)*0.45f*units;hands[s].z=1.2f*units;}
  real w=vr_body_wanted_yaw(&y,TRUE,&h,hands);real expect=yaw+0.5f*PIN(off,-0.785f,0.785f);
  assert(fabsf(wrap(w-expect))<2e-3f);
  assert(fabsf(wrap(vr_body_wanted_yaw(&y,FALSE,&h,hands)-yaw))<1e-4f);
  for(int s=0;s<2;s++){real a=yaw+3.14159f+(s?-0.2f:0.2f);hands[s].x=cosf(a)*0.4f*units;hands[s].y=sinf(a)*0.4f*units;}
  assert(fabsf(wrap(vr_body_wanted_yaw(&y,TRUE,&h,hands)-yaw))<1e-4f);}
 /* the neck: upright 14 cm behind and 20 cm below the eyes, as before */
 {real_vector3d f,u;real_point3d e={{1,2,3}},nk;head(0.3f,0,&f,&u);vr_neck_pivot(&e,&f,&u,units,&nk);
  real back=-((nk.x-e.x)*cosf(0.3f)+(nk.y-e.y)*sinf(0.3f))/units,below=(e.z-nk.z)/units;
  assert(fabsf(back-0.14f)<1e-4f&&fabsf(below-0.20f)<1e-4f);}
 /* looking down, the eyes swing forward and down about the neck: the neck stays further behind them
    (the chest out of the camera); the pivot sits at the same height whatever the pitch */
 {real last=0;real_point3d e={{0,0,0}};for(int d=0;d<=60;d+=5){real p=-d*0.0174533f;real_vector3d f,u;real_point3d nk,eye;head(0,p,&f,&u);
   /* the eye that a fixed neck at (-0.14,0,-0.20) produces */
   eye.x=(-0.14f+0.14f*cosf(p)-0.20f*sinf(p))*units;eye.y=0;eye.z=(-0.20f+0.14f*sinf(p)+0.20f*cosf(p))*units;
   vr_neck_pivot(&eye,&f,&u,units,&nk);
   assert(fabsf(nk.x/units+0.14f)<1e-3f&&fabsf(nk.z/units+0.20f)<1e-3f);
   real behind=(eye.x-nk.x)/units;assert(behind>=last-0.002f);last=behind;}
  assert(last>0.24f);}
 /* beyond the limits the pitch is held (-60, +30 degrees): no swing past them */
 {real_vector3d f,u;real_point3d e={{0,0,0}},a,b;head(0,-1.2f,&f,&u);vr_neck_pivot(&e,&f,&u,units,&a);head(0,-1.5f,&f,&u);vr_neck_pivot(&e,&f,&u,units,&b);
  assert(fabsf(a.x-b.x)<1e-4f&&fabsf(a.z-b.z)<1e-4f);}
 puts("PASS: head yaw exact at any pitch (20000 poses); torso yaw follows hands halfway within 45 deg, ignores hands behind;");
 puts("      neck pivot keeps the upright offset, stays put as the head pitches (eyes swing ahead of it), pitch limited");
}
''')

# --- hidden arms close along the hand's own axis, also for a floating hand
run('cuff', common + r'''
struct vr_animation_graph_node { char name[32]; short parent_node_index; };
struct animation_graph { struct { short count; struct vr_animation_graph_node *elements; } nodes; };
#define TAG_BLOCK_GET_ELEMENT(block,i,type) (&((type *)(block)->elements)[i])
#define MAXIMUM_NODES_PER_ANIMATION 64
static int hands_only, tracking;
static boolean vr_render_hands_only(void){return hands_only;}
static int vr_hand_tracking_mode(void){return tracking;}
static short vr_find_node(struct animation_graph *g,const char*a,const char*b){for(short i=0;i<g->nodes.count;i++)if(strstr(g->nodes.elements[i].name,a)&&strstr(g->nodes.elements[i].name,b))return i;return NONE;}
static boolean vr_node_under(struct animation_graph *g,short node,short root){
 if(root<0)return FALSE;for(short n=node,s=0;n>=0&&s<64;n=g->nodes.elements[n].parent_node_index,s++){if(n==root)return TRUE;if(g->nodes.elements[n].parent_node_index==n)break;}return FALSE;}
''' + fn(render, 'vr_length') + fn(render, 'vr_point_minus') + fn(render, 'vr_unit_vector') + fn(render, 'vr_finger_of') +
    fn(render, 'vr_finger_nodes') + fn(render, 'vr_hand_back_axis') + fn(render, 'vr_hide_forearms') + r'''
int main(void){
 /* 0 root; 1/2 upper arms; 3/4 forearms; 5/6 wrists; 7 gun; 8-11 right finger bases; 12 left middle base */
 struct vr_animation_graph_node nodes[13]={{"frame bone24",-1},{"frame l upperarm",0},{"frame r upperarm",0},{"frame l forearm",1},
  {"frame r forearm",2},{"frame l wriste",3},{"frame r wriste",4},{"frame gun",6},{"frame r index low",6},{"frame r middle low",6},
  {"frame r ring low",6},{"frame r pinky low",6},{"frame l middlelow",5}};
 struct animation_graph g={{13,nodes}};
 short left[3]={1,3,5},right[3]={2,4,6};
 for(int trial=0;trial<2000;trial++){
  real_matrix4x3 m[13];memset(m,0,sizeof m);for(int i=0;i<13;i++)m[i].scale=1;
  real_vector3d axis={{rnd()-.5f,rnd()-.5f,rnd()-.5f}};vr_unit_vector(&axis);
  for(int s=0;s<2;s++){short w=s?6:5;real_point3d c={{(rnd()-.5f)*4,(rnd()-.5f)*4,(rnd()-.5f)*4}};m[w].position=c;
   /* the forearm bone left far away in an unrelated direction (a floating hand, no arm solve) */
   for(int k=0;k<3;k++){m[s?4:3].position.n[k]=c.n[k]+(rnd()-.5f)*3;m[s?2:1].position.n[k]=c.n[k]+(rnd()-.5f)*3;}}
  for(int f=8;f<12;f++)for(int k=0;k<3;k++)m[f].position.n[k]=m[6].position.n[k]+axis.n[k]*0.09f*units+(f-9.5f)*0.01f*units*(k==0);
  for(int k=0;k<3;k++)m[12].position.n[k]=m[5].position.n[k]+axis.n[k]*0.09f*units;
  real_matrix4x3 before[13];memcpy(before,m,sizeof m);
  tracking=trial&1?1:0;hands_only=!tracking;
  vr_hide_forearms(m,&g,left,right);
  for(int s=0;s<2;s++){short *c=s?right:left;
   for(int b=0;b<2;b++){assert(m[c[b]].scale==0);
    /* 3.5 cm back from the wrist along the knuckles-to-wrist axis, wherever the forearm bone was */
    for(int k=0;k<3;k++)assert(fabsf(m[c[b]].position.n[k]-(before[c[2]].position.n[k]-axis.n[k]*0.035f*units))<2e-3f);}
   assert(!memcmp(&m[c[2]],&before[c[2]],sizeof m[0]));}
  assert(!memcmp(&m[7],&before[7],sizeof m[0]));
 }
 /* arms shown: body IK and floating hands-and-arms draw them */
 {real_matrix4x3 m[13],b[13];memset(m,0,sizeof m);for(int i=0;i<13;i++){m[i].scale=1;m[i].position.x=(real)i;}memcpy(b,m,sizeof m);
  for(tracking=0;tracking<3;tracking+=2){hands_only=0;vr_hide_forearms(m,&g,left,right);assert(!memcmp(m,b,sizeof m));}}
 puts("PASS: Hands Only and Floating close the cuff 3.5 cm back along the hand's own axis (2000 hands, forearm bone anywhere);");
 puts("      Body IK and Float + Arms keep the arms");
}
''')

# --- online melee, the horn, the two-hand migration
run('frame_bits', common + r'''
#include <stdint.h>
#include <stdarg.h>
#include "port/android/include/halo_android_abi.h"
static struct { int active, layout_vr, seated, network_game, melee_multiplayer; float melee_speed; int melee_impact, impact_allowed;
 unsigned pad_buttons; struct { uint32_t flags; } frame; } vr;
static int logs;
static void platform_log(const char*f,...){(void)f;logs++;}
static char mode[16]="grip";static int applied,fail;
static const char *config_string(const char*k){(void)k;return mode;}
static int config_boolean(const char*k){(void)k;return applied;}
static int config_write_string(const char*k,const char*v){(void)k;if(fail)return 0;snprintf(mode,16,"%s",v);return 1;}
static int config_write_boolean(const char*k,int v){(void)k;if(fail)return 0;applied=v;return 1;}
''' + fn(frame, 'vr_set_network_game') + fn(frame, 'physical_melee_allowed') + fn(frame, 'vr_impact_melee') +
    fn(frame, 'vr_horn_held') + fn(frame, 'migrate_two_hand_auto') + r'''
int main(void){
 vr.active=1;vr.melee_speed=2;vr.melee_impact=1;vr.impact_allowed=1;
 /* offline: physical melee as set; online: off unless vr.melee_multiplayer */
 assert(physical_melee_allowed()&&vr_impact_melee());
 vr_set_network_game(1);assert(!physical_melee_allowed()&&!vr_impact_melee());
 vr.melee_multiplayer=1;assert(physical_melee_allowed()&&vr_impact_melee());
 vr.melee_multiplayer=0;vr_set_network_game(0);assert(physical_melee_allowed());
 vr.melee_speed=0;assert(!physical_melee_allowed());vr.melee_speed=2;
 /* the horn: seated, either stick click; not both (recentre), not on foot, not unfocused, not the pad layout */
 vr.layout_vr=1;vr.seated=1;vr.frame.flags=HALO_XR_FRAME_FOCUSED;
 vr.pad_buttons=HALO_XR_BUTTON_LEFT_THUMB;assert(vr_horn_held());
 vr.pad_buttons=HALO_XR_BUTTON_B;assert(vr_horn_held());
 vr.pad_buttons=HALO_XR_BUTTON_LEFT_THUMB|HALO_XR_BUTTON_RIGHT_THUMB;assert(!vr_horn_held());
 vr.pad_buttons=HALO_XR_BUTTON_A;assert(!vr_horn_held());
 vr.pad_buttons=HALO_XR_BUTTON_LEFT_THUMB;vr.seated=0;assert(!vr_horn_held());vr.seated=1;
 vr.frame.flags=0;assert(!vr_horn_held());vr.frame.flags=HALO_XR_FRAME_FOCUSED;vr.layout_vr=0;assert(!vr_horn_held());
 /* two-hand auto lock becomes the default once; a later choice is kept; a failed save retries */
 fail=1;migrate_two_hand_auto();assert(!applied&&!strcmp(mode,"grip"));fail=0;
 migrate_two_hand_auto();assert(applied&&!strcmp(mode,"auto"));
 strcpy(mode,"grip");migrate_two_hand_auto();assert(!strcmp(mode,"grip"));
 applied=0;strcpy(mode,"off");migrate_two_hand_auto();assert(applied&&!strcmp(mode,"off"));
 puts("PASS: physical melee off online unless chosen (button melee untouched); seated stick clicks sound the horn;");
 puts("      two-hand auto lock migrates once from the old default, keeps later choices, retries failed saves");
}
''')

# --- two-handed aim keeps the gun's calibrated roll (Quest OS v78 report)
run('two_hand_roll', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "port/linux/src/vr_alignment.h"
struct halo_xr_pose { float position[3], orientation[4]; };
static struct { int weapon_hand, two_handed, two_handed_enabled, two_hand_held;
 struct halo_xr_pose aim_pose; float weapon_rotation[2][4];
 struct { struct halo_xr_pose aim[2], grip[2]; unsigned hand_valid[2]; } frame; } vr;
static int vr_hand_empty(void){return 0;}
''' + fn(frame, 'rotate') + fn(frame, 'look_rotation') + fn(frame, 'compute_aim_pose') + r'''
static unsigned seed=78;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
int main(void){
 static const float xr_up[3]={0,1,0},xr_forward[3]={0,0,-1};
 vr.two_handed_enabled=1;vr.two_hand_held=1;vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3;
 for(int n=0;n<2000;n++){
  int w=n&1;float d[3]={rnd()*90-45,rnd()*360-180,rnd()*60-30},roll=(n&2)?180.f:0.f,g[3]={0,0,roll},m[3]={0,0,-roll};
  vr.weapon_hand=w;vr_alignment_rotation(d,vr.frame.aim[w].orientation);
  vr_alignment_rotation(w?g:m,vr.weapon_rotation[w]);
  /* the off hand ahead along the controller's aim, a little off-line */
  float f[3];rotate(vr.frame.aim[w].orientation,xr_forward,f);
  for(int k=0;k<3;k++){vr.frame.grip[w].position[k]=0;vr.frame.grip[1-w].position[k]=f[k]*0.35f+(rnd()-.5f)*0.04f;}
  compute_aim_pose();assert(vr.two_handed);
  float raw[3],got[3];rotate(vr.frame.aim[w].orientation,xr_up,raw);rotate(vr.aim_pose.orientation,xr_up,got);
  float dot=raw[0]*got[0]+raw[1]*got[1]+raw[2]*got[2];
  /* roll 0: the gun's up stays the controller's; Gun Roll 180: it stays flipped in two hands too */
  if(roll==0)assert(dot>0.9f);else assert(dot<-0.9f);
 }
 puts("PASS: two-handed aim keeps the gun's calibrated roll (2000 poses, both hands): Gun Roll 180 no longer re-inverts in two hands");
}
''')
