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
 unsigned pad_buttons; struct { uint32_t flags, buttons; } frame; } vr;
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
 /* the controllers' own stick clicks (frame.buttons), whatever the layout's pad says: a zoom
 (the pad's right thumb) held with a stick click is not the recentre */
 vr.frame.buttons=HALO_XR_BUTTON_LEFT_THUMB;assert(vr_horn_held());
 vr.frame.buttons=HALO_XR_BUTTON_RIGHT_THUMB;assert(vr_horn_held());
 vr.frame.buttons=HALO_XR_BUTTON_LEFT_THUMB;vr.pad_buttons=HALO_XR_BUTTON_LEFT_THUMB|HALO_XR_BUTTON_RIGHT_THUMB;assert(vr_horn_held());
 vr.pad_buttons=0;
 vr.frame.buttons=HALO_XR_BUTTON_LEFT_THUMB|HALO_XR_BUTTON_RIGHT_THUMB;assert(!vr_horn_held());
 vr.frame.buttons=HALO_XR_BUTTON_A|HALO_XR_BUTTON_B;assert(!vr_horn_held());
 vr.frame.buttons=HALO_XR_BUTTON_LEFT_THUMB;vr.seated=0;assert(!vr_horn_held());vr.seated=1;
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

# --- the pistol's shots and per-gun aim (tester, 2026-10-04: "pistol reticle
# still too low and a bit to the left, most other weapons compensate with
# wider spread"). A trigger that "uses weapon origin" fired from the unseen
# third-person gun's marker, parallel to but off the hand's reticle ray; the
# reticle also ignored the trigger's first_person_weapon_offset.
weapons = (ROOT / 'source/items/weapons.c').read_text(encoding='latin-1')
fire = fn(weapons, 'trigger_create_projectiles')
assert re.search(r'#ifdef HALO_VR\n\t\t\tif \(!vr_hand_shot\)\n#endif\n\t\t\torigin= markers\[marker_index\]\.matrix\.position;', fire)
assert 'vr_hand_shot= vr_render_hand_origin(owner_object_index, &hand) != 0;' in fire
# without HALO_VR (the flat build) the function reads exactly as before
flat_fire = re.sub(r'#ifdef HALO_VR\n.*?#endif\n', '', fire, flags=re.S)
assert ('if (TEST_FLAG(trigger_definition->flags, _weapon_trigger_uses_weapon_origin_bit))\n\t\t{\n'
        '\t\t\torigin= markers[marker_index].matrix.position;\n\t\t}') in flat_fire
assert 'vr_hand_shot' not in flat_fire
# the hand origin exists only in a local game (online shots are unchanged)
assert 'game_connection() != _game_connection_local' in fn(render, 'vr_render_hand_origin')
# shots, reticle and scope follow the shot pose; the drawn gun and the scope's
# quad keep the gun's own aim
assert 'rotate(vr.shot_pose.orientation, xr_forward, local);' in fn(frame, 'hand_forward')
assert 'hand_view(&vr.shot_pose, NULL' in fn(frame, 'vr_hand_ray')
assert 'hand_view(&vr.shot_pose, NULL' in fn(frame, 'vr_scope_view')
assert 'pose = vr.aim_pose;' in fn(frame, 'vr_weapon_view') and 'shot_pose' not in fn(frame, 'vr_weapon_view')
assert 'shot_pose' not in fn(frame, 'place_scope') and 'shot_pose' not in fn(frame, 'compute_aim_pose')
assert re.search(r'compute_aim_pose\(\);\n\tsteady_aim\(\);\n\tupdate_shot_pose\(\);', fn(frame, 'update_aim_pose'))
assert 'vr_set_gun_class(kind);' in fn(render, 'vr_render_actions')
reticle = fn(render, 'vr_render_windows')
assert 'if (vr_shot_offset(unit_index, from_hand, &direction, &shift))' in reticle
assert re.search(r'origin = camera;\n\t+from_hand = FALSE;', reticle)
kinds = ['pistol', 'plasma_pistol', 'assault_rifle', 'plasma_rifle', 'shotgun', 'sniper_rifle', 'rocket_launcher',
         'needler', 'fuel_rod', 'flamethrower', 'other']
for kind in kinds:
    for axis in ('up', 'right'):
        assert re.search(r'\{ "vr\.aim_' + kind + '_' + axis + r'", _config_real, "0\.0"', config), (kind, axis)
for row in ['{ "AIM FOR", "gun", _vr_setting_gun_aim', '{ "AIM UP", "up", _vr_setting_gun_aim',
            '{ "AIM RIGHT", "right", _vr_setting_gun_aim', '{ "RESET AIM", "reset", _vr_setting_gun_aim']:
    assert row in menu, row
change = fn(menu, 'vr_menu_setting_change')
assert 'value=step>0?(floor(value/0.5+0.00001)+1)*0.5:(ceil(value/0.5-0.00001)-1)*0.5;' in change
assert 'value=fmax(-VR_GUN_AIM_LIMIT,fmin(VR_GUN_AIM_LIMIT,value));' in change
assert 'if(kind<0||!strcmp(setting->key,"gun")) return TRUE;' in change
hands = menu[menu.index('static struct vr_menu_setting const vr_menu_hands[] ='):]
hands = hands[:hands.index('};')]
assert len(re.findall(r'^\s*\{ "', hands, re.M)) == 16, 'Hands + Gun fills exactly two screens of eight'
print('PASS: static wiring (pistol shots from the hand offline only, flat build unchanged, shot pose for shots/reticle/scope '
      'not the gun, 22 per-gun keys at 0, menu rows)')

run('gun_aim', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "port/linux/src/vr_alignment.h"
''' + re.search(r'enum\n\{\n\tVR_GUN_OTHER,.*?\};\n', (ROOT / 'port/linux/src/vr.h').read_text(encoding='utf-8'), re.S).group(0) + r'''
struct halo_xr_pose { float position[3], orientation[4]; };
static struct { int gun_class, gun_aim_turned[VR_GUN_CLASSES]; float gun_aim_rotation[VR_GUN_CLASSES][4];
 struct halo_xr_pose aim_pose, shot_pose; } vr;
''' + fn(frame, 'rotate') + fn(frame, 'gun_aim_quaternion') + fn(frame, 'update_shot_pose') +
    fn(frame, 'vr_gun_class_of_name') + r'''
static unsigned seed=21;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
static float dot(const float*a,const float*b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
int main(void){
 static const float xr_forward[3]={0,0,-1},xr_up[3]={0,1,0},xr_right[3]={1,0,0};
 static const struct { const char *name; int kind; } names[]={
  {"weapons\\pistol\\pistol",VR_GUN_PISTOL},{"weapons\\plasma pistol\\plasma pistol",VR_GUN_PLASMA_PISTOL},
  {"weapons\\assault rifle\\assault rifle",VR_GUN_ASSAULT_RIFLE},{"weapons\\plasma rifle\\plasma rifle",VR_GUN_PLASMA_RIFLE},
  {"weapons\\shotgun\\shotgun",VR_GUN_SHOTGUN},{"weapons\\sniper rifle\\sniper rifle",VR_GUN_SNIPER_RIFLE},
  {"weapons\\rocket launcher\\rocket launcher",VR_GUN_ROCKET_LAUNCHER},{"weapons\\needler\\mp_needler",VR_GUN_NEEDLER},
  {"weapons\\plasma_cannon\\plasma_cannon",VR_GUN_FUEL_ROD},{"weapons\\flamethrower\\flamethrower",VR_GUN_FLAMETHROWER},
  {"cmt\\weapons\\plasma_pistol\\plasma_pistol",VR_GUN_PLASMA_PISTOL},{"<protected>",VR_GUN_OTHER},{"weapons\\ball\\ball",VR_GUN_OTHER},
  {NULL,VR_GUN_OTHER}};
 for(unsigned i=0;i<sizeof(names)/sizeof(names[0]);i++) assert(vr_gun_class_of_name(names[i].name)==names[i].kind);
 for(int n=0;n<4000;n++){
  float d[3]={rnd()*170-85,rnd()*360-180,rnd()*360-180};
  vr_alignment_rotation(d,vr.aim_pose.orientation);
  for(int k=0;k<3;k++)vr.aim_pose.position[k]=rnd()*2-1;
  memset(vr.gun_aim_turned,0,sizeof(vr.gun_aim_turned));
  /* no adjustment, no gun, or another gun's adjustment: exactly the gun's aim, bit for bit */
  vr.gun_class=n%VR_GUN_CLASSES; update_shot_pose(); assert(!memcmp(&vr.shot_pose,&vr.aim_pose,sizeof(vr.aim_pose)));
  vr.gun_class=-1; vr.gun_aim_turned[VR_GUN_PISTOL]=1; gun_aim_quaternion(3,2,vr.gun_aim_rotation[VR_GUN_PISTOL]);
  update_shot_pose(); assert(!memcmp(&vr.shot_pose,&vr.aim_pose,sizeof(vr.aim_pose)));
  vr.gun_class=VR_GUN_ASSAULT_RIFLE; update_shot_pose(); assert(!memcmp(&vr.shot_pose,&vr.aim_pose,sizeof(vr.aim_pose)));
  /* the pistol's adjustment turns its aim up and right by the angles asked, in the gun's own frame */
  {float up=rnd()*20-10,right=rnd()*20-10,f[3],u[3],r[3],s[3];
   gun_aim_quaternion(up,right,vr.gun_aim_rotation[VR_GUN_PISTOL]); vr.gun_class=VR_GUN_PISTOL; update_shot_pose();
   assert(!memcmp(vr.shot_pose.position,vr.aim_pose.position,sizeof(vr.aim_pose.position)));
   rotate(vr.aim_pose.orientation,xr_forward,f);rotate(vr.aim_pose.orientation,xr_up,u);rotate(vr.aim_pose.orientation,xr_right,r);
   rotate(vr.shot_pose.orientation,xr_forward,s);
   float rad=0.0174532925f, gu=asinf(dot(s,u)), gr=atan2f(dot(s,r),dot(s,f));
   assert(fabsf(gu-up*rad)<1e-3f); assert(fabsf(gr-right*rad)<1e-3f);}
 }
 puts("PASS: per-gun aim: 14 tag names map to their gun (plasma before pistol, others and protected names to OTHER); "
      "no adjustment / no gun / another gun's leaves the aim bit-identical; the held gun's turns exactly up and right in its own frame (4000 poses)");
}
''')

run('shot_offset', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define FLAG(b) (1u<<(b))
#define TEST_FLAG(f,b) (((f)&FLAG(b))!=0)
typedef union { real n[3]; struct { real i,j,k; }; } real_vector3d;
typedef union { real n[3]; struct { real x,y,z; }; } real_point3d;
enum { _weapon_trigger_uses_weapon_origin_bit=5, _weapon_trigger_projectiles_cannot_be_aimed_bit=11 };
struct weapon_trigger_definition { unsigned long flags; real_point3d first_person_weapon_offset; };
struct tag_block { long count; struct weapon_trigger_definition *elements; };
struct weapon_definition { struct { struct tag_block triggers; } weapon; };
#define TAG_BLOCK_GET_ELEMENT(b,i,t) (&(b)->elements[i])
static struct weapon_trigger_definition trigger; static struct weapon_definition definition={{{1,&trigger}}};
struct unit_datum_t { struct { short current_weapon_index; } unit; }; static struct unit_datum_t unit_datum; static long held=7;
struct weapon_datum_t { long definition_index; }; static struct weapon_datum_t weapon_datum;
static struct unit_datum_t *unit_get(long u){(void)u;return &unit_datum;}
static long unit_inventory_get_weapon(long u,short i){(void)u;(void)i;return held;}
static struct weapon_datum_t *weapon_get(long w){(void)w;return &weapon_datum;}
static struct weapon_definition *weapon_definition_get(long d){(void)d;return &definition;}
static const real_vector3d up3d={{0,0,1}},left3d={{0,1,0}};
static const real_vector3d *global_up3d=&up3d,*global_left3d=&left3d;
static void cross_product3d(const real_vector3d*a,const real_vector3d*b,real_vector3d*o){real_vector3d r={{a->j*b->k-a->k*b->j,a->k*b->i-a->i*b->k,a->i*b->j-a->j*b->i}};*o=r;}
static real normalize3d(real_vector3d*v){real l=sqrtf(v->i*v->i+v->j*v->j+v->k*v->k);if(l<1e-4f)return 0;v->i/=l;v->j/=l;v->k/=l;return l;}
static void point_from_line3d(const real_point3d*p,const real_vector3d*v,real t,real_point3d*o){real_point3d r={{p->x+v->i*t,p->y+v->j*t,p->z+v->k*t}};*o=r;}
''' + fn(render, 'vr_shot_offset') + r'''
/* the engine's own lines (trigger_create_projectiles), applied to a point */
static void engine(real_vector3d forward, real_point3d *origin){
 struct weapon_trigger_definition *trigger_definition=&trigger; real_vector3d right, up;
''' + re.search(r'\t\t\t\tcross_product3d\(global_up3d, &forward, &right\);.*?trigger_definition->first_person_weapon_offset\.z,\n\t\t\t\t\t&origin\);\n',
                fire, re.S).group(0).replace('&origin', 'origin').replace('*global_left3d', '*global_left3d') + r'''}
static unsigned seed=5;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
int main(void){
 real_vector3d f, o;
 for(int n=0;n<5000;n++){
  f.i=rnd()*2-1;f.j=rnd()*2-1;f.k=rnd()*2-1; if(n<4){f.i=f.j=0;f.k=n&1?1:-1;} if(!normalize3d(&f)&&n>=4)continue;
  trigger.flags=0; for(int a=0;a<3;a++)trigger.first_person_weapon_offset.n[a]=(rnd()-.5f)*0.2f;
  real_point3d p={{0,0,0}}; engine(f,&p);
  assert(vr_shot_offset(1,TRUE,&f,&o)&&vr_shot_offset(1,FALSE,&f,&o));
  for(int a=0;a<3;a++)assert(fabsf(o.n[a]-p.n[a])<1e-5f);
  /* from the gun's model: only when the shot leaves from the hand (offline, our weapons.c) */
  trigger.flags=FLAG(_weapon_trigger_uses_weapon_origin_bit);
  assert(vr_shot_offset(1,TRUE,&f,&o)&&!vr_shot_offset(1,FALSE,&f,&o));
  trigger.flags=FLAG(_weapon_trigger_projectiles_cannot_be_aimed_bit); assert(!vr_shot_offset(1,TRUE,&f,&o));
 }
 trigger.flags=0; memset(&trigger.first_person_weapon_offset,0,sizeof(trigger.first_person_weapon_offset));
 assert(!vr_shot_offset(1,TRUE,&f,&o)); /* no offset: the reticle exactly as before */
 held=NONE; trigger.first_person_weapon_offset.y=0.05f; assert(!vr_shot_offset(1,TRUE,&f,&o));
 held=7; definition.weapon.triggers.count=0; assert(!vr_shot_offset(1,TRUE,&f,&o));
 puts("PASS: reticle shot offset equals the engine's first_person_weapon_offset shift (5000 aims incl. straight up/down); "
      "model-origin guns only when fired from the hand; unaimed, unarmed, triggerless or zero offset leave the reticle as before");
}
''')

pose = (ROOT / 'port/linux/game/network_vr_pose.c').read_text(encoding='utf-8')
tick = fn(pose, 'network_vr_pose_tick')
assert 'if (!host_nonce && !client_unsupported_logged && now - client_since > 10000)' in tick
assert tick.index('client_unsupported_logged = TRUE') < tick.index('if (game_time_get() % 2) return;')
assert 'client_since = 0; client_unsupported_logged = FALSE;' in fn(pose, 'network_vr_pose_reset')
print('PASS: a client says once, 10 s in, when its host offers no VR avatars (another build); reset each game')

# --- the reticle converges as the shot does (owner video 2026-10-04 15:33:
# impacts above and left of the reticle on the rifle and pistol). Every
# player shot is turned by player_aim_projectile toward where the camera's
# line hits, within the weapon's deviation cone; the reticle now shares that
# code (aim_assist_collision_direction) through vr_aim_assist_converge.
aim = (ROOT / 'source/game/aim_assist.c').read_text(encoding='latin-1')
project = fn(aim, 'player_aim_projectile')
assert ('aim_assist_collision_direction(player->unit_index, aiming_unit_index, camera_position, camera_direction,\n'
        '\t\t\tposition, direction, &collision_direction);') in project
assert 'collision_test_vector' not in project, 'the camera trace lives only in the shared helper'
converge = re.search(r'#ifdef HALO_VR\n/\* test21: the VR reticle.*?#endif\n', aim, re.S).group(0)
assert 'player->aim_assist_unit_index' not in converge and 'aim_assist(&' not in converge, \
    'the reticle never changes the player or searches targets'
reticle = fn(render, 'vr_render_windows')
assert re.search(r'if \(vr_shot_offset\(unit_index, from_hand, &direction, &shift\)\).*?'
                 r'aiming = direction;\n\t+vr_aim_assist_converge\(player_index, &camera, &aiming, &origin, &direction\);',
                 reticle, re.S)
run('converge', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1L)
#define MAXIMUM_COLLISION_USER_STACK_DEPTH 8
#define match_assert(...) ((void)0)
#define match_assert_valid_real_normal3d(...) ((void)0)
#define sine sinf
#define cosine cosf
typedef union { real n[3]; struct { real x,y,z; }; } real_point3d;
typedef union { real n[3]; struct { real i,j,k; }; } real_vector3d;
enum { _collision_test_for_projectiles_flags = 1, _collision_user_aim_assist = 3 };
struct collision_result { real t; real_point3d point; };
struct aim_assist_parameters { real autoaim_angle, autoaim_distance, magnetism_angle, magnetism_distance, deviation_angle, unused; };
struct aim_assist_target { real_point3d position; real autoaim_level; long object_index; };
struct player_datum { long unit_index; short team_index; long aim_assist_unit_index, aim_assist_timestamp; };
struct unit_datum { struct { real_point3d position; } object; };
static short global_current_collision_user_depth = 1; static short global_current_collision_users[8];
static struct player_datum the_player = { 7, 0, NONE, 0 }; static struct unit_datum the_unit;
static real_point3d cam; static real_vector3d cam_dir; static real deviation; static int has_assist = 1; static real floor_z;
static struct player_datum *player_get(long p){(void)p;return &the_player;}
static long unit_get_aiming_unit_index(long u){return u;}
static short unit_get_zoom_level(long u){(void)u;return NONE;}
static struct unit_datum *unit_get(long u){(void)u;return &the_unit;}
static boolean unit_get_aim_assist_parameters(long u, short z, struct aim_assist_parameters *p){(void)u;(void)z;
 memset(p,0,sizeof(*p));p->deviation_angle=deviation;return has_assist;}
static short director_camera_deterministic(long u, real_point3d *p, real_vector3d *f){(void)u;*p=cam;*f=cam_dir;return 0;}
static boolean aim_assist(struct aim_assist_parameters const *p, real_point3d const *a, real_vector3d const *b, long u, short t,
 struct aim_assist_target *g){(void)p;(void)a;(void)b;(void)u;(void)t;(void)g;return FALSE;}
static long game_time_get(void){return 0;}
static real dot_product3d(const real_vector3d*a,const real_vector3d*b){return a->i*b->i+a->j*b->j+a->k*b->k;}
static real magnitude3d(const real_vector3d*v){return sqrtf(dot_product3d(v,v));}
static real normalize3d(real_vector3d*v){real l=magnitude3d(v);if(l<1e-6f)return 0;v->i/=l;v->j/=l;v->k/=l;return l;}
static void fast_normalize3d(real_vector3d*v){normalize3d(v);}
static void vector_from_points3d(const real_point3d*a,const real_point3d*b,real_vector3d*o){o->i=b->x-a->x;o->j=b->y-a->y;o->k=b->z-a->z;}
static void scale_vector3d(const real_vector3d*v,real s,real_vector3d*o){o->i=v->i*s;o->j=v->j*s;o->k=v->k*s;}
static void set_real_point3d(real_point3d*p,real x,real y,real z){p->x=x;p->y=y;p->z=z;}
static void cross_product3d(const real_vector3d*a,const real_vector3d*b,real_vector3d*o){real_vector3d r={{a->j*b->k-a->k*b->j,a->k*b->i-a->i*b->k,a->i*b->j-a->j*b->i}};*o=r;}
static void perpendicular3d(const real_vector3d*v,real_vector3d*o){o->i=-v->j;o->j=v->i;o->k=0;}
static void rotate_vector_about_axis(real_vector3d*v,const real_vector3d*a,real s,real c){real_vector3d x;cross_product3d(a,v,&x);
 real d=dot_product3d(a,v);v->i=v->i*c+x.i*s+a->i*d*(1-c);v->j=v->j*c+x.j*s+a->j*d*(1-c);v->k=v->k*c+x.k*s+a->k*d*(1-c);}
/* the floor z = floor_z (the trace's only surface), 128 units out */
static boolean collision_test_vector(int f,const real_point3d*p,const real_vector3d*v,long ignore,struct collision_result*r){(void)f;(void)ignore;
 real t=v->k<0?(floor_z-p->z)/v->k:2;if(t<0||t>1)t=1;r->t=t;r->point.x=p->x+v->i*t;r->point.y=p->y+v->j*t;r->point.z=p->z+v->k*t;return t<1;}
''' + fn((ROOT / 'source/math/real_math.c').read_text(encoding='latin-1'), 'fast_normals_interpolate') +
    fn((ROOT / 'source/math/real_math.c').read_text(encoding='latin-1'), 'pin_normal_to_cone3d') +
    fn(aim, 'aim_assist_collision_direction') + project +
    converge.replace('#ifdef HALO_VR\n', '').replace('#endif\n', '') + r'''
static unsigned seed=33;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
int main(void){
 int pinned=0;
 for(int n=0;n<20000;n++){
  real_point3d hand; real_vector3d shot, mine;
  cam.x=rnd()*4-2;cam.y=rnd()*4-2;cam.z=0.62f+rnd()*0.1f; floor_z=0;
  the_unit.object.position.x=cam.x;the_unit.object.position.y=cam.y;the_unit.object.position.z=cam.z-0.2f;
  cam_dir.i=rnd()*2-1;cam_dir.j=rnd()*2-1;cam_dir.k=-rnd()*0.8f-0.02f;normalize3d(&cam_dir);
  /* the shot from the hand (offline) or the camera (online), shifted by a trigger's offset */
  hand.x=cam.x+(rnd()-.5f)*0.3f;hand.y=cam.y+(rnd()-.5f)*0.3f;hand.z=cam.z-0.1f-rnd()*0.2f;
  deviation=(n%4)*0.03f; has_assist=(n%7)!=0;
  shot=cam_dir; player_aim_projectile(0,&hand,&shot);
  mine=cam_dir; boolean ok=vr_aim_assist_converge(0,&cam,&cam_dir,&hand,&mine);
  assert(ok==has_assist);
  /* the reticle's direction is the shot's, bit for bit */
  assert(!memcmp(&shot,&mine,sizeof(shot)));
  if(has_assist&&dot_product3d(&shot,&cam_dir)<0.99999f)pinned++;
 }
 assert(global_current_collision_user_depth==1);
 printf("PASS: the reticle turns the shot as player_aim_projectile does, bit for bit (20000 aims, hand or camera origin, "
        "cones 0-5 deg, guns without aim assist untouched; %d turned toward the camera line's hit)\n",pinned);
}
''')

reset = fn(frame, 'migrate_gun_aim_reset')
assert 'if (config_boolean("vr.aim_reset_applied"))' in reset and 'config_write_real(key, 0.0)' in reset
assert re.search(r'migrate_two_hand_auto\(\);\n\tmigrate_gun_aim_reset\(\);\n\t(migrate_reticle_button\(\);\n\t)?vr_reload_settings\(\);', frame)
assert re.search(r'\{ "vr\.aim_reset_applied", _config_boolean, "false"', config)
assert 'unsigned int sticks = vr.frame.buttons & both;' in fn(frame, 'vr_horn_held')
assert 'horn: the vehicle %s the crouch control from its driver' in fn(render, 'vr_render_actions')
print('PASS: per-gun aim values reset once before settings load; horn reads the real stick clicks and logs its chain')
