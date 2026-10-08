"""Test22: co-op campaign crash, reviewed upstream fixes, the first-person
vehicle camera, the left hand's ammo display, shot diagnostics, catch-up
tick logging and adjustable scopes.

Owner logs (2026-10-04 16:56/16:58): an Android host halted as a Quest joined
co-op ("tag_groups.c #3089: #0 is not a valid index in [#0,#0)"), symbolised
to network_damage_host_tick -> unit_unarmed_melee_damage ->
list_index_to_weapon_definition_index: a campaign map lists no multiplayer
weapons (upstream ce77db84 / PR #73). Video 16:36:07 (105-122 s): the first-
person Warthog's interior shook against the view. Production functions run
under ASan/UBSan with small stubs; no headset or game data is used. Run under
Linux/WSL with clang.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test22'; OUT.mkdir(parents=True, exist_ok=True)


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


units = (ROOT / 'source/units/units.c').read_text(encoding='latin-1')
weapons = (ROOT / 'source/items/weapons.c').read_text(encoding='latin-1')
globals_c = (ROOT / 'source/networking/network_game_globals.c').read_text(encoding='latin-1')
raster = (ROOT / 'source/rasterizer/xbox/rasterizer_xbox.c').read_text(encoding='latin-1')
render = (ROOT / 'port/linux/game/vr_render.c').read_text(encoding='utf-8')
frame = (ROOT / 'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
menu = (ROOT / 'port/linux/game/vr_menu.c').read_text(encoding='utf-8')
config = (ROOT / 'port/linux/src/port_config.c').read_text(encoding='utf-8')
signal = (ROOT / 'port/linux/src/p2p_signal.c').read_text(encoding='utf-8')
d3d = (ROOT / 'port/linux/src/d3d8_gl.c').read_text(encoding='utf-8')
interp = (ROOT / 'port/linux/game/render_interpolation.c').read_text(encoding='utf-8')

# --- the co-op campaign crash (upstream ce77db84) and the other reviewed upstream fixes
assert 'list_index_to_weapon_definition_index(0)' not in units.replace(
    'list_index_to_weapon_definition_index(0) : NONE;', ''), 'every unarmed lookup is guarded'
assert units.count('unarmed_melee_weapon_definition_index()') == 2
grenade = fn(units, 'unit_throw_grenade_begin')
assert '(weapon_index == NONE && unit->unit.parent_seat_index == NONE)' in grenade, 'upstream 1a15a171'
assert 'else if (!global_network_game_client)' in fn(globals_c, 'network_game_client_start_frame'), 'upstream 7e00135d'
assert re.search(r'"network\.signalling_brokers", _config_string,\n\t\t"\\"opence\.milenko\.org:1883,broker\.emqx\.io:1883,'
                 r'broker\.hivemq\.com:1883,test\.mosquitto\.org:1883\\""', config), 'upstream 88a7c07e broker first'
start = fn(signal, 'p2p_signal_start')
assert 'if (!strcmp(text, "broker.emqx.io:1883,broker.hivemq.com:1883,test.mosquitto.org:1883"))' in start
run('unarmed', r'''
#include <assert.h>
#include <stdio.h>
#define NONE (-1L)
struct tag_block { long count; };
struct game_globals { struct tag_block weapon_list; };
struct unit_definition { struct { struct { long index; } melee_damage; } unit; };
struct weapon_definition { struct { struct { long index; } melee_attack_damage; } weapon; };
static struct game_globals globals; static struct unit_definition biped = {{{NONE}}};
static struct weapon_definition rifle = {{{42}}}; static int lookups;
static struct game_globals *scenario_get_game_globals(void){return &globals;}
static long list_index_to_weapon_definition_index(long i){lookups++;assert(globals.weapon_list.count>0);return 9;}
static struct weapon_definition *weapon_definition_get(long i){assert(i==9);return &rifle;}
struct unit_datum { long definition_index; };
static struct unit_datum the_unit; static struct unit_datum *unit_get(long u){(void)u;return &the_unit;}
static struct unit_definition *unit_definition_get(long d){(void)d;return &biped;}
''' + fn(units, 'unarmed_melee_weapon_definition_index') + fn(units, 'unit_unarmed_melee_damage') + r'''
int main(void){
 /* a campaign map: no multiplayer weapons, a player's biped with no blow: none, and no lookup */
 globals.weapon_list.count=0; assert(unit_unarmed_melee_damage(1)==NONE && lookups==0);
 /* multiplayer: the first multiplayer weapon's blow, as before */
 globals.weapon_list.count=3; assert(unit_unarmed_melee_damage(1)==42 && lookups==1);
 /* a biped with a blow of its own keeps it */
 biped.unit.melee_damage.index=7; assert(unit_unarmed_melee_damage(1)==7);
 puts("PASS: an unarmed blow on a campaign map (no multiplayer weapons) is none, never element 0 of an empty block; "
      "multiplayer maps and bipeds with their own blow are unchanged");
}
''')
print('PASS: static wiring (unarmed lookups guarded, seat grenade guard, no-client frame guard, upstream broker first with migration)')

# --- the first-person vehicle camera
heading_fn = fn(render, 'vr_seat_frame_heading')
assert 'render_interpolation_object_node_matrices(vr_render.seat.vehicle_index)' in heading_fn
assert 'real seat_heading = vr_seat_frame_heading();' in fn(render, 'view_heading')
assert 'real seat_heading = vr_seat_frame_heading();' in fn(render, 'vr_vehicle_adjust_anchor')
assert re.search(r'unit_get_camera_position\(vr_render\.seat\.unit_index, anchor\);\n\t\tvr_seat_steady_anchor\(anchor\);\n'
                 r'\t\tvr_vehicle_adjust_anchor\(anchor\);', fn(render, 'view_anchor'))
assert 'heading = vr_render.seat.heading;' in fn(render, 'vr_player_control_facing') or \
    'real heading = vr_render.seat.heading;' in fn(render, 'vr_player_control_facing'), 'the aim keeps the tick heading'
run('seat', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1L)
#define _pi 3.14159265f
typedef union { real n[3]; struct { real x,y,z; }; } real_point3d;
typedef union { real n[3]; struct { real i,j,k; }; } real_vector3d;
typedef struct { real scale; real_vector3d forward, left, up; real_point3d position; } real_matrix4x3;
struct object_header_block_reference { long size; long offset; };
struct object_datum { struct { real_vector3d forward; struct object_header_block_reference node_matrices; } object; };
static struct { struct { long vehicle_index, unit_index; short seat_index; real heading, offset; } seat; } vr_render;
static struct object_datum vehicle; static real_matrix4x3 drawn[1], simulated[1]; static int interpolating = 1;
static double now_time;
static struct object_datum *object_try_and_get(long i){return i==5 ? &vehicle : NULL;}
static real_matrix4x3 *object_get_node_matrices(long i){(void)i;return drawn;}
static real_matrix4x3 *render_interpolation_object_node_matrices(long i){(void)i;return interpolating ? drawn : NULL;}
static void *object_header_block_get(long i, struct object_header_block_reference *r){(void)i;(void)r;return simulated;}
static double vr_pose_time(void){return now_time;}
static real vr_units_per_metre(void){return 3.2808f;}
static real vr_yaw(real_vector3d const *v){return atan2f(v->j, v->i);}
''' + fn(render, 'vr_seat_frame_heading') + fn(render, 'vr_seat_steady_anchor') + r'''
static void pose(real_matrix4x3 *m, real yaw, real pitch, real x, real y, real z){
 real cy=cosf(yaw), sy=sinf(yaw), cp=cosf(pitch), sp=sinf(pitch);
 m->scale=1; m->forward.i=cy*cp; m->forward.j=sy*cp; m->forward.k=sp;
 m->left.i=-sy; m->left.j=cy; m->left.k=0;
 m->up.i=-cy*sp; m->up.j=-sy*sp; m->up.k=cp;
 m->position.x=x; m->position.y=y; m->position.z=z;}
static real_point3d place(real_matrix4x3 const *m, real f, real l, real u){
 real_point3d p; for(int a=0;a<3;a++)p.n[a]=m->position.n[a]+m->forward.n[a]*f+m->left.n[a]*l+m->up.n[a]*u; return p;}
int main(void){
 vehicle.object.node_matrices.size=(long)sizeof(real_matrix4x3);
 vr_render.seat.vehicle_index=5; vr_render.seat.unit_index=7; vr_render.seat.seat_index=0;
 /* a seat held still in the vehicle: the anchor rides the drawn vehicle exactly, however it moves and turns */
 real worst=0;
 for(int n=0;n<2000;n++){
  now_time=n/72.0; pose(&drawn[0], n*0.01f, 0.2f*sinf(n*0.05f), n*0.1f, sinf(n*0.02f), 0.3f*sinf(n*0.3f));
  real_point3d head=place(&drawn[0],0.2f,0.1f,0.6f), a=head; vr_seat_steady_anchor(&a);
  for(int k=0;k<3;k++){real d=fabsf(a.n[k]-head.n[k]); if(d>worst)worst=d;}
 }
 assert(worst<1e-3f);
 /* the driver's head bobbing 5 cm at 6 Hz in the seat: the anchor moves a fraction of it */
 real bob_in=0,bob_out=0;
 for(int n=0;n<720;n++){
  now_time=100+n/72.0; pose(&drawn[0], 0.3f, 0, 10, 20, 1);
  real b=0.05f*3.2808f*sinf(2*_pi*6*n/72.0f); real_point3d head=place(&drawn[0],0.2f,0.1f,0.6f+b), a=head;
  vr_seat_steady_anchor(&a);
  if(n>144){ real_point3d rest=place(&drawn[0],0.2f,0.1f,0.6f); real d=fabsf(a.z-rest.z); if(d>bob_out)bob_out=d; if(fabsf(b)>bob_in)bob_in=fabsf(b);} }
 assert(bob_out<0.15f*bob_in);
 /* another seat: its head at once */
 vr_render.seat.seat_index=1; now_time+=1.0/72; { real_point3d head=place(&drawn[0],-0.5f,0.4f,0.7f), a=head;
  vr_seat_steady_anchor(&a); for(int k=0;k<3;k++)assert(fabsf(a.n[k]-head.n[k])<1e-4f); }
 /* the frame's heading: the latest heading turned back by the drawn vehicle's lag */
 vr_render.seat.offset=0; vehicle.object.forward.i=cosf(0.50f); vehicle.object.forward.j=sinf(0.50f); vehicle.object.forward.k=0;
 pose(&simulated[0],0.50f,0,0,0,0); pose(&drawn[0],0.47f,0.1f,0,0,0);
 assert(fabsf(vr_seat_frame_heading()-0.47f)<1e-4f);
 /* across the wrap at +-180 degrees */
 vehicle.object.forward.i=cosf(3.13f); vehicle.object.forward.j=sinf(3.13f);
 pose(&simulated[0],3.13f,0,0,0,0); pose(&drawn[0],-3.13f,0,0,0,0);
 { real h=vr_seat_frame_heading(); real d=fabsf(atan2f(sinf(h+3.13f),cosf(h+3.13f))); assert(d<1e-3f); }
 /* not drawing (between frames), or a jump: the latest heading */
 interpolating=0; vehicle.object.forward.i=cosf(1.0f); vehicle.object.forward.j=sinf(1.0f);
 assert(fabsf(vr_seat_frame_heading()-1.0f)<1e-5f); interpolating=1;
 pose(&simulated[0],1.0f,0,0,0,0); pose(&drawn[0],2.0f,0,0,0,0); assert(fabsf(vr_seat_frame_heading()-1.0f)<1e-5f);
 printf("PASS: the seat's anchor rides the drawn vehicle exactly (2000 frames moving, turning, pitching; worst %.1e), "
        "a 5 cm 6 Hz head bob is cut to %.0f%%, a new seat snaps; the view's heading follows the drawn vehicle, wraps, "
        "and falls back to the latest outside a frame or on a jump\n", worst, 100*bob_out/bob_in);
}
''')

# --- the left hand's ammo display, shot diagnostics, catch-up ticks
assert 'short display = vr_find_node(graph, "frame", "display");' in fn(render, 'vr_render_first_person_ik')
assert 'halo_vr_skinning_mirrored(determinant < 0.0f);' in fn(raster, 'rasterizer_set_model_skinning')
assert '#ifdef HALO_VR\n\t/* test22: the left hand' in fn(raster, 'rasterizer_set_model_skinning')
assert 'if (vr_mirror_winding && vr_skinning_mirrored)' in d3d
assert re.search(r'vr_mirror_winding = mirrored;\n\tvr_skinning_mirrored = 1;', d3d), 'each bracket starts mirrored'
fire = fn(weapons, 'trigger_create_projectiles')
assert 'vr_render_shot_diagnostic(weapon_index, player_index, &origin, &vr_aimed, &forward, vr_hand_shot);' in fire
assert re.sub(r'#ifdef HALO_VR\n(.*?)(?:#else\n(.*?))?#endif\n', lambda m: m.group(2) or '', fire, flags=re.S).count(
    'target_object_index= player_aim_projectile(player_index, &origin, &forward);') == 1, 'the flat build fires as before'
diag = fn(render, 'vr_render_shot_diagnostic')
assert 'now - logged_time < 10.0' in diag and 'local_player_index == NONE' in diag
assert 'catch_up_ticks++;' in fn(interp, 'render_interpolation_tick')
assert 'if (catch_up_most >= 3)' in fn(interp, 'render_interpolation_frame_begin')
print('PASS: static wiring (left-hand display mirrored back with its own winding, VR build only; '
      'shot diagnostics rate-limited and flat build unchanged; catch-up tick log)')

# --- adjustable scopes
for kind in ('pistol', 'sniper'):
    for part, default in (('forward', '0.0'), ('up', '0.0'), ('right', '0.0'), ('scale', '1.0')):
        assert re.search(r'\{ "vr\.scope_%s_%s", _config_real, "%s"' % (kind, part, re.escape(default)), config), (kind, part)
assert '{ "SCOPES", vr_menu_scopes, NUMBEROF(vr_menu_scopes) },' in menu
assert '{ "RESET SCOPES", "scopes", _vr_setting_reset_scopes' in menu
run('scope', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "port/linux/src/vr_alignment.h"
#define VR_SCOPE_ROUND 1
#define VR_SCOPE_SNIPER 2
#define VR_SCOPE_ROCKET 3
#define HALO_XR_LAYER_SCOPE 4u
#define VR_HAND_REACH_METRES 0.9f
struct halo_xr_pose { float position[3], orientation[4]; };
struct halo_xr_layers { unsigned flags; struct halo_xr_pose scope_pose; float scope_size[2]; };
static struct { int weapon_hand, scope_shape, zoom_level, two_handed, gun_class, settings_generation;
 float scope_size, scope_adjust[2][4]; struct halo_xr_pose aim_pose, shot_pose;
 struct { struct halo_xr_pose head; unsigned hand_valid[2]; } frame; } vr;
static void platform_log(const char *format,...){ (void)format; }
''' + fn(frame, 'rotate') + fn(frame, 'tracked_hand_origin') + fn(frame, 'place_scope') + r'''
static const float usual[3][3]={{-0.10f,0.00f,0.15f},{-0.15f,0.00f,0.15f},{0.10f,0.20f,0.10f}};
int main(void){
 float d[3]={20,30,10}; vr_alignment_rotation(d, vr.aim_pose.orientation);
 vr.aim_pose.position[0]=1; vr.aim_pose.position[1]=1.4f; vr.aim_pose.position[2]=-0.3f; vr.scope_size=0.06f;
 memcpy(vr.frame.head.position, vr.aim_pose.position, sizeof(vr.aim_pose.position));
 memcpy(vr.shot_pose.position, vr.aim_pose.position, sizeof(vr.aim_pose.position));
 memcpy(vr.shot_pose.orientation, vr.aim_pose.orientation, sizeof(vr.aim_pose.orientation));
 for(int s=0;s<2;s++) vr.scope_adjust[s][3]=1;
 for(int hand=0;hand<2;hand++) for(int shape=VR_SCOPE_ROUND;shape<=VR_SCOPE_ROCKET;shape++){
  struct halo_xr_layers l={0}; float local[3], t[3]; const float *o=usual[shape-1];
  vr.weapon_hand=hand; vr.scope_shape=shape; place_scope(&l);
  /* nothing set: exactly the usual place, size and turn */
  local[0]=hand ? -o[1] : o[1]; local[1]=o[2]; local[2]=-o[0]; rotate(vr.aim_pose.orientation, local, t);
  for(int a=0;a<3;a++) assert(fabsf(l.scope_pose.position[a]-(vr.aim_pose.position[a]+t[a]))<1e-6f);
  assert(l.scope_size[0]==0.06f && !memcmp(l.scope_pose.orientation, vr.shot_pose.orientation, sizeof(float[4])));
 }
 /* the sniper rifle's 5 cm right, 2 cm up, 3 cm forward, 150%: right is the player's right in either hand */
 vr.scope_adjust[1][0]=0.03f; vr.scope_adjust[1][1]=0.02f; vr.scope_adjust[1][2]=0.05f; vr.scope_adjust[1][3]=1.5f;
 for(int hand=0;hand<2;hand++){
  struct halo_xr_layers a={0}, b={0}; float moved[3], right[3]={1,0,0}, up[3]={0,1,0}, back[3]={0,0,1}, r[3], u[3], k[3];
  vr.weapon_hand=hand; vr.scope_shape=VR_SCOPE_SNIPER; place_scope(&b);
  float keep[4]; memcpy(keep, vr.scope_adjust[1], sizeof(keep)); memset(vr.scope_adjust[1],0,sizeof(keep)); vr.scope_adjust[1][3]=1;
  place_scope(&a); memcpy(vr.scope_adjust[1], keep, sizeof(keep));
  for(int i=0;i<3;i++) moved[i]=b.scope_pose.position[i]-a.scope_pose.position[i];
  rotate(vr.aim_pose.orientation,right,r); rotate(vr.aim_pose.orientation,up,u); rotate(vr.aim_pose.orientation,back,k);
  assert(fabsf(moved[0]*r[0]+moved[1]*r[1]+moved[2]*r[2]-0.05f)<1e-5f);
  assert(fabsf(moved[0]*u[0]+moved[1]*u[1]+moved[2]*u[2]-0.02f)<1e-5f);
  assert(fabsf(moved[0]*k[0]+moved[1]*k[1]+moved[2]*k[2]+0.03f)<1e-5f);
  assert(fabsf(b.scope_size[0]-0.09f)<1e-6f);
 }
 /* Aim calibration rotates every scope shape with the shot view while its
  * center and physical sight offset stay on the gun, in either hand. */
 for(int hand=0;hand<2;hand++) for(int shape=VR_SCOPE_ROUND;shape<=VR_SCOPE_ROCKET;shape++){
  struct halo_xr_layers base={0}, calibrated={0}; float corrected[3]={-10,25,0}, correction[4];
  vr.weapon_hand=hand; vr.scope_shape=shape;
  memcpy(vr.shot_pose.orientation,vr.aim_pose.orientation,sizeof(vr.aim_pose.orientation));
  place_scope(&base);
  vr_alignment_rotation(corrected,correction);
  vr_alignment_multiply(vr.aim_pose.orientation,correction,vr.shot_pose.orientation);
  place_scope(&calibrated);
  assert(!memcmp(calibrated.scope_pose.orientation,vr.shot_pose.orientation,sizeof(float[4])));
  for(int i=0;i<3;i++) assert(fabsf(calibrated.scope_pose.position[i]-base.scope_pose.position[i])<1e-6f);
 }
 /* Arms beyond the view reach clamp cannot pull the compositor quad away
  * from the rendered scope camera; sight offset is still applied afterward. */
 {
  struct halo_xr_layers l={0}; float origin[3]; float zero[3]={0,0,0};
  vr.frame.head.position[0]=0.2f; vr.frame.head.position[1]=1.1f; vr.frame.head.position[2]=0.3f;
  vr.aim_pose.position[0]=1.5f; vr.aim_pose.position[1]=1.1f; vr.aim_pose.position[2]=0.3f;
  memcpy(vr.shot_pose.position,vr.aim_pose.position,sizeof(vr.aim_pose.position));
  vr_alignment_rotation(zero,vr.aim_pose.orientation);
  memcpy(vr.shot_pose.orientation,vr.aim_pose.orientation,sizeof(vr.aim_pose.orientation));
  vr.scope_shape=VR_SCOPE_SNIPER; vr.weapon_hand=0;
  vr.scope_adjust[1][0]=vr.scope_adjust[1][1]=vr.scope_adjust[1][2]=0;
  tracked_hand_origin(&vr.aim_pose,origin); place_scope(&l);
  assert(fabsf(origin[0]-1.1f)<1e-6f && fabsf(origin[1]-1.1f)<1e-6f && fabsf(origin[2]-0.3f)<1e-6f);
  assert(fabsf(l.scope_pose.position[0]-origin[0])<1e-6f);
  assert(fabsf(l.scope_pose.position[1]-(origin[1]+0.15f))<1e-6f);
  assert(fabsf(l.scope_pose.position[2]-(origin[2]+0.15f))<1e-6f);
 }
 /* the pistol's own settings leave the sniper's and the rocket's alone */
 vr.scope_adjust[0][1]=0.1f; vr.weapon_hand=1; vr.scope_shape=VR_SCOPE_ROCKET;
 { struct halo_xr_layers l={0}; place_scope(&l); assert(l.scope_size[0]==0.06f); }
 puts("PASS: baseline scope placement holds for both hands; calibrated scope plane matches the shot view while its center stays on the gun; "
      "extended hands use the 90 cm reach clamp; pistol and sniper adjustments and sizes stay independent");
}
''')
