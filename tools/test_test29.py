"""Test29 (1.0.11): OpenCE build 144 (network 21); the HUD head tap held, not
passed through, and the HUD and head tap on the HUD page; the wrist HUD on
the wrist and movable; moving with a hand while holding the gun in both;
PR #1 (glasses FOV, resolution to 200%) with defaults as before.

Evidence (kept private): the live directory on 2026-10-07 listed its co-op
games (a30, a50) on network 21, which 1.0.10 (network 20) refuses; a Quest 3
log (1.0.10) hid the HUD half a second after a gun went into the right
shoulder's holster and never showed it again. Run with python3 tools/test_test29.py.
"""
from pathlib import Path
import hashlib, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test29'; OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return (ROOT / path).read_text(encoding='utf-8', errors='replace')


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def between(text, start, end):
    a = text.index(start)
    return text[a:text.index(end, a)]


def run(name, source, extra=()):
    p = OUT / (name + '.c'); p.write_text(source)
    subprocess.run(['clang', '-std=gnu11', '-O1', '-Wall', '-Wno-unused-function', '-Wno-unused-variable', '-Wno-missing-braces',
                    '-fsanitize=address,undefined', '-I', str(ROOT), str(p), '-lm', '-o', str(OUT / name), *extra], check=True)
    subprocess.run([str(OUT / name)], check=True)


limits = read('port/linux/include/halo_port_limits.h')
objects_net = read('port/linux/game/network_objects.c')
frame = read('port/linux/src/vr_frame.c')
menu = read('port/linux/game/vr_menu.c')
config = read('port/linux/src/port_config.c')
abi = read('port/android/include/halo_android_abi.h')
host_xr = read('port/android/host/host_xr.c')
gradle = read('port/android/app/build.gradle')
package = read('tools/package-quest.py')
updater = read('port/android/app/src/main/java/com/halo/decomp/Updater.java')

# --- 1. OpenCE's network version 21, exactly; its co-op, lobby and message files byte for byte
network = int(re.search(r'#define HALO_PORT_NETWORK_VERSION (\d+)\b', limits).group(1))
assert network in (21, 22)
for name in ['', '_MINIMUM', '_MAXIMUM']:
    assert re.search(r'#define HALO_PORT_NETWORK_VERSION%s %d\b' % (name, network), limits), name
UPSTREAM_144 = [
    ('port/linux/game/coop_enemies.c', '64288778915265ec598613e1bb982f27330953b4b4f5dd7af41244e26c4a7f2a'),
    ('port/linux/game/coop_enemies.h', '8984e3e416e5f6fa1c743313e57fc5de87fc9a2a47be488be667865808a05a68'),
    ('port/linux/game/coop_scripts.c', '756652fd7f6bbad39e0accef5fc199748800354ed647c1e218228a346ab80284'),
    ('port/linux/game/coop_scripts.h', 'a105eef852039f01d80cdde8e1f888c32d723fe0cbd98fd5aa27b6efc2ef3947'),
    ('port/linux/game/coop_spectate.c', '8ed6ccee0a4881e61b533a93b4621f236ae78b88703fd08203de36fa1bdb5afe'),
    ('port/linux/game/coop_spectate.h', '6c73fce2dfd2bbb300f784f4ed393053db1978e5b5a984d7dd8c1fa75eb58035'),
    ('port/linux/game/network_actors.c', 'beaa436a7da1d9e3c9efb83e796a6d7ccbe80d61ac19814b219031577dfdc4f4'),
    ('port/linux/game/network_coop.h', 'ff29c9fae0f03a3686342766ead3557f0aa7c4b4eaa9932dbf4c3a8724acf1d0'),
    ('port/linux/game/network_damage.c', 'c00195f62854a8bb8148f1971d13ba0dd53a14275c8f4eb633ff3b01081073d7'),
    ('port/linux/src/p2p_lobby.c', '53294de0700dac37bdc2e57840af6826061d38fc1b7a72eaf70cff5a135585a5'),
    ('port/linux/src/p2p_internal.h', 'e64480a5351379a57a126b472f382d37f2cde1784fe6a568390d1daf2af96e4f'),
    ('source/networking/network_client_message_handler.c', '89cd5d3c8963cfaa0cf5b410e3de66b4d4366bade65059a6b46af6432b03f0a6'),
    ('source/networking/network_connection.c', '69da59f00b832a23673391de46ce87777f4f1e5bc959b0e8242a748d80704ae5'),
    ('source/networking/network_connection.h', '9a11ece195c463d5ab7a79395e843a3c0c83d4d26909d6625ce810613723b077'),
    ('source/networking/network_game_manager.c', '661f390bb974d50213d062f31cf2c9ddc2588634b35324c98d4986d31809b92e'),
    ('source/networking/network_game_manager.h', '204beda14791cc65d729247711af3b61f20e5dbbfd04386cf7bac58e4a61ad1e'),
    ('source/networking/network_messages.c', '82846ccd5f3686652e94dee3661b8d5e214d8866da8c1c12e5b62d3b5a8ab1a3'),
    ('source/networking/network_messages.h', 'daea3a6af2f0a925e27a98f6899c741bf95ed366c9144a689801ba90cdc6aa27'),
    ('source/networking/network_server_message_handler.c', 'e14eb1ed0a60404685d9a0653892d3be327bbaf1c9241804962bae45ad88597d'),
    ('source/networking/network_game_protocol.h', 'c7a4ab43c54b02cb96921b04ac670f90d185ab2c60ae58309a616c70d21a8b2e'),
    ('port/linux/game/network_coop.c', '3bf1d6d74337fe63d9380e541f6d4952548d5afe4c3907e0dcdbca12bea02336'),
]
# (network_coop.c: this app's one patch, test28's camera kept upright, taken out)
COOP_CAMERA_PATCH = re.compile(r'\t/\* keep the camera upright: the world\'s up made square to forward\n.*?\n\t\t}\n\t}\n}', re.S)
COOP_CAMERA_ORIGINAL = ('\t/* keep the camera upright */\n\tup->i = 0.0f;\n\tup->j = 0.0f;\n\tup->k = 1.0f;\n'
                        '\tdistributed_axes_make_valid(forward, up);\n}')
for path, digest in UPSTREAM_144:
    data = (ROOT / path).read_bytes()
    if path.endswith('network_coop.c'):
        text = data.decode('utf-8')
        assert len(COOP_CAMERA_PATCH.findall(text)) == 1, 'the one camera patch'
        data = COOP_CAMERA_PATCH.sub(lambda m: COOP_CAMERA_ORIGINAL, text).encode('utf-8')
    assert hashlib.sha256(data).hexdigest() == digest, path + ' as OpenCE build 144'
assert ('OpenCE build 144 (network 21)' if network == 21 else 'OpenCE build 145 (network 22)') in updater
print('PASS: exact current network gate; %d co-op, lobby and message files are OpenCE build 144\'s byte for byte '
      '(network_coop.c with only test28\'s camera)' % len(UPSTREAM_144))

# --- 2. objects at rest: OpenCE build 144's three sends of one come to rest, and test26's resend of one at rest moved
send = fn(objects_net, 'distributed_host_send_states')
condition = between(send, '\t\tif (at_rest && was_moving)\n', '\t\tdistributed_state_from_object(')
assert condition.count('continue;') == 1
repeats = re.search(r'\tREST_STATE_REPEATS = \d+,\n\tREST_STATE_REPEAT_TICKS = \d+,\n', objects_net).group(0)
tolerances = ''.join(re.findall(r'#define REMOTE_OBJECT_(?:ANGLE_)?TOLERANCE [^\n]+\n', objects_net))
rest_state = re.search(r'static struct\n\{\n\tlong object_index;\n.*?\} objects_host_rest_sent\[MAXIMUM_TRACKED_OBJECTS\];\n',
                       objects_net, re.S).group(0)
run('rest_sends', r'''
#include <assert.h>
#include <stdio.h>
typedef int boolean; typedef float real;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
typedef union { struct { real x,y,z; }; real n[3]; } real_point3d;
typedef union { struct { real i,j,k; }; real n[3]; } real_vector3d;
#define MAXIMUM_TRACKED_OBJECTS 4
enum {
''' + repeats + r'''};
''' + tolerances + r'''
struct object_datum { struct { real_point3d position; real_vector3d forward, up; } object; };
static struct object_datum objects[4];
static struct object_datum *object_get(long i){ return &objects[i & 3]; }
static long now; static long game_time_get(void){ return now; }
static long objects_host_rest_times[MAXIMUM_TRACKED_OBJECTS];
''' + rest_state + fn(objects_net, 'distributed_host_note_rest_sent') + fn(objects_net, 'distributed_host_rest_moved') +
    fn(objects_net, 'distributed_host_rest_state_due') + r'''
/* one object's turn in the loop: sent (1) or not */
static int sent(long absolute_index, long object_index, boolean at_rest, boolean was_moving){
''' + condition.replace('continue;', 'return 0;') + r'''
	distributed_host_note_rest_sent(absolute_index, object_index);
	return 1;
}
int main(void){
 long a=0x10000; int n=0;
 objects[0].object.forward.i=1; objects[0].object.up.k=1; objects_host_rest_times[0]=NONE;
 /* moving: every tick */
 for(now=0;now<10;now++) assert(sent(0,a,FALSE,TRUE));
 /* come to rest at tick 10: sent then, 8 and 16 ticks later (three times), not between nor after */
 for(now=10;now<60;now++){ int s=sent(0,a,TRUE,now==10); if(s) n++; assert(s==(now==10||now==18||now==26)); }
 assert(n==3);
 /* at rest, then a script's teleport (moved, still at rest): sent at once (test26), once */
 objects[0].object.position.x=5; now=70; assert(sent(0,a,TRUE,FALSE)); now=71; assert(!sent(0,a,TRUE,FALSE));
 /* turned in place: sent */
 objects[0].object.forward.i=0; objects[0].object.forward.j=1; now=80; assert(sent(0,a,TRUE,FALSE)); now=81; assert(!sent(0,a,TRUE,FALSE));
 puts("PASS: an object come to rest goes to every client three times over 16 ticks (OpenCE build 144); one at rest moved or "
      "turned by a script goes at once (test26), both kept");
}
''')

# --- 3. the HUD head tap: held by the temple, slowed, not in a holster; it shows the HUD again as it hid it
tap = between(frame, '\t/* test26: the HUD tap:', '\n\t/* crouching:')
hud_defines = ''.join(re.findall(r'#define HUD_TAP_\w+ [^\n]+\n', frame))
assert hud_defines.count('#define') == 4
run('hud_hold', r'''
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include "port/android/include/halo_android_abi.h"
''' + hud_defines + r'''
static struct { float hud_tap_distance, hud_tap_dwell, hand_speed[2]; struct halo_xr_frame frame; int hud_hidden, hud_tap_armed, in_holster; } vr;
static int buzzes;
static void vr_haptic(int h, float a, float s){ (void)h; (void)a; (void)s; buzzes++; }
static void platform_log(const char *f, ...){ (void)f; }
''' + fn(frame, 'rotate') + fn(frame, 'distance3') + r'''
static void hud_tap(int w, float seconds)
{
''' + tap + r'''
}
static const float frame_seconds = 1.0f / 72.0f;
/* the hand at a place, moving at a speed, for a time */
static void hold(int w, float x, float y, float z, float speed, float seconds){
 for(float t=0;t<seconds;t+=frame_seconds){ vr.frame.grip[w].position[0]=x; vr.frame.grip[w].position[1]=y; vr.frame.grip[w].position[2]=z;
  vr.hand_speed[w]=speed; hud_tap(w, frame_seconds); } }
static void away(int w){ hold(w, 0.4f, 1.2f, -0.3f, 1.0f, 0.1f); }
int main(void){
 const float tx = HUD_TAP_OUT, ty = 1.6f, tz = HUD_TAP_BACK;
 vr.hud_tap_distance=0.1f; vr.hud_tap_armed=1; vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3;
 vr.frame.head.position[1]=1.6f; vr.frame.head.orientation[3]=1;
 /* the report: hidden by a tap, then a tap again shows it */
 hold(1, tx, ty, tz, 0.2f, 0.3f); assert(vr.hud_hidden==1 && buzzes==1);
 hold(1, tx, ty, tz, 0.2f, 1.0f); assert(vr.hud_hidden==1 && buzzes==1);                  /* held on: once */
 away(1); hold(1, tx, ty, tz, 0.2f, 0.3f); assert(vr.hud_hidden==0 && buzzes==2);          /* shown again */
 /* the controller against the skin (the old point) and a little high or forward: still a tap */
 away(1); hold(1, 0.08f, 1.6f, 0.04f, 0.1f, 0.3f); assert(vr.hud_hidden==1 && buzzes==3);
 away(1); hold(1, 0.13f, 1.66f, -0.03f, 0.1f, 0.3f); assert(vr.hud_hidden==0 && buzzes==4);
 /* passing by (the reach for the right shoulder's holster): fast, or too brief, does nothing */
 away(1); hold(1, tx, ty, tz, 1.5f, 0.5f); assert(vr.hud_hidden==0);
 away(1); hold(1, tx, ty, tz, 0.3f, 0.1f); away(1); assert(vr.hud_hidden==0);
 /* in a holster (its zone reaches this far): nothing however long */
 vr.in_holster=1; hold(1, tx, ty, tz, 0.1f, 1.0f); vr.in_holster=0; assert(vr.hud_hidden==0);
 /* held at the right shoulder's holster, a gun at the cheek or held up to aim, the other temple: nothing */
 away(1); hold(1, 0.18f, 1.45f, 0.15f, 0.1f, 1.0f); hold(1, 0.06f, 1.42f, -0.12f, 0.1f, 1.0f);
 hold(1, 0.1f, 1.5f, -0.35f, 0.1f, 1.0f); hold(1, -tx, ty, tz, 0.1f, 1.0f); assert(vr.hud_hidden==0 && buzzes==4);
 /* the head turned 90 degrees left: the temple turns with it */
 { float s=sqrtf(0.5f), side[3]={tx,0,tz}, temple[3]; vr.frame.head.orientation[1]=s; vr.frame.head.orientation[3]=s;
   rotate(vr.frame.head.orientation,side,temple);
   away(1); hold(1, tx, ty, tz, 0.1f, 0.5f); assert(vr.hud_hidden==0);
   hold(1, temple[0], 1.6f+temple[1], temple[2], 0.1f, 0.3f); assert(vr.hud_hidden==1); away(1);
   hold(1, temple[0], 1.6f+temple[1], temple[2], 0.1f, 0.3f); assert(vr.hud_hidden==0); away(1);
   vr.frame.head.orientation[1]=0; vr.frame.head.orientation[3]=1; }
 /* left-handed: the left hand at the left temple */
 hold(0, -tx, ty, tz, 0.1f, 0.3f); assert(vr.hud_hidden==1); away(0); hold(0, -tx, ty, tz, 0.1f, 0.3f); assert(vr.hud_hidden==0); away(0);
 /* off (HEAD TAP OFF) or untracked: never */
 vr.hud_tap_distance=0; hold(1, tx, ty, tz, 0.1f, 1.0f); assert(vr.hud_hidden==0 && vr.hud_tap_dwell==0);
 vr.hud_tap_distance=0.1f; vr.frame.hand_valid[1]=0; hold(1, tx, ty, tz, 0.1f, 1.0f); assert(vr.hud_hidden==0);
 puts("PASS: the HUD tap hides and shows again (the report), held by the temple for 0.15 s; a hand passing by fast or briefly, "
      "in a holster, at the shoulder's holster, a gun at the cheek or held up, the other temple, off or untracked: nothing");
}
''')
assert 'vr.hud_tap_dwell = 0.0f;' in fn(frame, 'vr_set_hud_hidden')
assert 'vr.hud_hidden = hidden != 0;' in fn(frame, 'vr_set_hud_hidden') and 'config_write' not in fn(frame, 'vr_set_hud_hidden')

# --- 4. the HUD page: HUD shown/hidden (the session's), the head tap, the wrist HUD's place and size
hud_page = between(menu, 'static struct vr_menu_setting const vr_menu_hud[] =', '};')
rows = re.findall(r'^	\{ "([A-Z ]+)", "', hud_page, re.M)
assert rows[:2] == ['HUD', 'HEAD TAP'], rows
assert rows == ['HUD', 'HEAD TAP', 'CROSSHAIR', 'CROSSHAIR SIZE', 'OPACITY', 'WRIST HUD', 'WRIST ALONG', 'WRIST ACROSS',
                'WRIST HEIGHT', 'WRIST SIZE', 'RESET WRIST'], rows
assert '{ "HUD", "hud", _vr_setting_hud_shown, 2, { { "SHOWN", "true" }, { "HIDDEN", "false" } } }' in hud_page
assert '{ "HEAD TAP", "vr.hud_tap_distance", _vr_setting_real, 6, { { "OFF", "0" },' in hud_page
gestures = between(menu, 'static struct vr_menu_setting const vr_menu_gestures[] =', '};')
assert '"HUD TAP", "vr.hud_tap_distance"' in gestures, 'still on HEAD GESTURES'
value_index = fn(menu, 'vr_menu_value_index')
assert 'case _vr_setting_hud_shown:\n\t\t\tif (!vr_hud_hidden() == !strcmp(value, "true"))' in value_index
change = fn(menu, 'vr_menu_setting_change')
assert 'vr_set_hud_hidden(!vr_hud_hidden());' in change
assert change.index('_vr_setting_hud_shown') < change.index('value_index = vr_menu_value_index(setting);\n\tif (setting->type == _vr_setting_real)')
for key in ['vr.wrist_hud_along', 'vr.wrist_hud_across', 'vr.wrist_hud_out', 'vr.wrist_hud_size']:
    assert '"%s"' % key in change, key
    assert re.search(r'\{ "%s", _config_real, "[01]", "HALO_VR_' % re.escape(key), config), key
assert re.search(r'\{ "vr.hud_tap_distance", _config_real, "0.1",', config), 'the head tap on by default (10 cm)'
print('PASS: VR SETTINGS > HUD: HUD SHOWN/HIDDEN (the session\'s, as the tap\'s, nothing written) and HEAD TAP first, '
      'on by default; the wrist HUD\'s along, across, height, size and reset')

# --- 5. the wrist HUD: on the wrist by default, moved and sized as set
wrist_defines = ''.join(re.findall(r'#define WRIST_HUD_\w+ [^\n]+\n', frame))
run('wrist_place', r'''
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "port/android/include/halo_android_abi.h"
''' + wrist_defines + r'''
static struct { int weapon_hand, two_hand_held, seated; struct halo_xr_frame frame; struct halo_xr_info info;
 float wrist_along, wrist_across, wrist_out, wrist_size; } vr;
''' + fn(frame, 'rotate') + fn(frame, 'look_rotation') + fn(frame, 'place_wrist') + r'''
static float distance(const float a[3], const float b[3]){ float d[3]={a[0]-b[0],a[1]-b[1],a[2]-b[2]}; return sqrtf(d[0]*d[0]+d[1]*d[1]+d[2]*d[2]); }
int main(void){
 struct halo_xr_layers layers;
 vr.info.width[HALO_XR_SWAPCHAIN_WRIST]=512; vr.info.height[HALO_XR_SWAPCHAIN_WRIST]=384; vr.wrist_size=1;
 vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3; vr.weapon_hand=1;
 /* the left grip at the origin, unturned (its back, -x, toward the eyes at -x) */
 vr.frame.grip[0].orientation[3]=1; vr.frame.head.position[0]=-0.5f;
 memset(&layers,0,sizeof(layers)); assert(place_wrist(&layers));
 float p0[3]; memcpy(p0,layers.wrist_pose.position,sizeof(p0));
 assert(fabsf(p0[2]-WRIST_HUD_BACK)<1e-5f && fabsf(p0[0]+WRIST_HUD_OUT)<1e-5f && fabsf(p0[1])<1e-5f);  /* 10 cm back, 4.5 out */
 assert(WRIST_HUD_BACK > 0.075f);                                                                           /* past 1.0.10's 7.5 */
 vr.wrist_along=0.03f; vr.wrist_across=0.02f; vr.wrist_out=0.01f; assert(place_wrist(&layers));
 assert(fabsf(layers.wrist_pose.position[2]-p0[2]-0.03f)<1e-5f && fabsf(layers.wrist_pose.position[1]-0.02f)<1e-5f &&
        fabsf(layers.wrist_pose.position[0]-p0[0]+0.01f)<1e-5f);
 vr.wrist_size=1.5f; assert(place_wrist(&layers) && fabsf(layers.wrist_size[0]-0.165f)<1e-5f && fabsf(layers.wrist_size[1]-0.12375f)<1e-5f);
 puts("PASS: the wrist HUD on the wrist (10 cm behind the grip, 4.5 cm out; 7.5 cm before), moved along, across and out "
      "and sized as the HUD page sets");
}
''')
reload = fn(frame, 'vr_reload_settings')
for clamp in ['vr.wrist_along = fminf(0.2f, fmaxf(-0.2f, vr.wrist_along));', 'vr.wrist_size = fminf(2.0f, fmaxf(0.5f, vr.wrist_size));']:
    assert clamp in reload, clamp

# --- 6. moving with a hand while both hands hold the gun: the gun's line stands for the hand; the head's mode as before
run('move_with', r'''
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include "port/android/include/halo_android_abi.h"
static struct { int move_relative, two_handed, weapon_hand; float head_yaw; struct halo_xr_frame frame; struct halo_xr_pose shot_pose; } vr;
''' + fn(frame, 'rotate') + fn(frame, 'to_halo') + 'static int hand_forward(float out[3]);\n' +
    between(frame, 'static float move_yaw(void)\n', '\nint vr_controller(') + fn(frame, 'hand_forward') + r'''
static void yaw_quat(float degrees, float q[4]){ float h=degrees*3.14159265f/360; q[0]=0; q[1]=sinf(h); q[2]=0; q[3]=cosf(h); }
int main(void){
 vr.weapon_hand=1; vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3; vr.head_yaw=0.5f;
 yaw_quat(0, vr.frame.aim[0].orientation); yaw_quat(0, vr.frame.aim[1].orientation); yaw_quat(0, vr.shot_pose.orientation);
 /* the head's mode: the head, two hands or not */
 vr.move_relative=0; assert(move_yaw()==0.5f); vr.two_handed=1; assert(move_yaw()==0.5f); vr.two_handed=0;
 /* the left hand's mode, one hand on the gun: the left controller (turned in 20 degrees) */
 vr.move_relative=1; yaw_quat(30, vr.frame.aim[0].orientation);
 float one = move_yaw(); assert(fabsf(one - (30*3.14159265f/180 - 0.349f)) < 1e-4f);
 /* both on the gun, the left controller turned 80 degrees on its front grip: the gun's line (here straight ahead) */
 vr.two_handed=1; yaw_quat(80, vr.frame.aim[0].orientation); assert(fabsf(move_yaw()) < 1e-4f);
 yaw_quat(-25, vr.shot_pose.orientation); assert(fabsf(move_yaw() + 25*3.14159265f/180) < 1e-4f);
 /* let go: the left controller again */
 vr.two_handed=0; assert(fabsf(move_yaw() - (80*3.14159265f/180 - 0.349f)) < 1e-4f);
 /* the right hand's mode, likewise; untracked: the head */
 vr.move_relative=2; vr.two_handed=1; assert(fabsf(move_yaw() + 25*3.14159265f/180) < 1e-4f);
 vr.frame.hand_valid[1]=0; assert(move_yaw()==0.5f);
 puts("PASS: MOVE WITH a hand: while both hands hold the gun the gun's line stands for it (a player strafed moving with the "
      "left hand on the front grip); one hand, let go, the head's mode and an untracked hand as before");
}
''')
assert 'move with %s' in fn(frame, 'vr_reload_settings')

# --- 7. PR #1 merged: the layers' layout, defaults as before, a failed resize described
assert '#define HALO_XR_LAYER_WRIST 0x200u' in abi and '#define HALO_XR_LAYER_EYE_FOV 0x400u' in abi
assert 'HALO_XR_ASSERT(sizeof(struct halo_xr_layers) == 180, "halo_xr_layers layout");' in abi
run('layers', r'''
#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include "port/android/include/halo_android_abi.h"
int main(void){ assert(sizeof(struct halo_xr_layers)==180 && offsetof(struct halo_xr_layers, wrist_pose)==112 &&
 offsetof(struct halo_xr_layers, eye_fov)==148); puts("PASS: halo_xr_layers 180 bytes: the wrist HUD's then the glasses window's"); }
''')
choose = fn(frame, 'choose_eye_size')
assert 'if (!vr.glasses && scale <= 1.0)\n\t{\n\t\tvr.eye_image_width = vr.recommended_width;' in choose
assert re.search(r'\{ "vr.fov_mode", _config_string, "\\"full\\""', config), 'full by default'
assert re.search(r'\{ "vr.resolution_scale", _config_real, "0.0"', config), 'AUTO by default'
resize = fn(host_xr, 'host_xr_resize_eyes')
assert 'result = -1;\n\t\t\tbreak;' in resize and resize.rstrip().endswith('return result;\n}')
# the sizing, run: full view at 100% or less keeps the recommended images; above, and the glasses window, remake them
run('eye_size', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
static struct { int eye_size, glasses, frame_glasses, fov_known; unsigned int recommended_width, recommended_height,
 eye_image_width, eye_image_height; float glasses_half[2], runtime_fov[2][4]; struct { char system[64]; } info; } vr;
static double scale_setting, fov_h=70, fov_v=66; static const char *mode="full";
static double config_real(const char *n){ return !strcmp(n,"vr.resolution_scale")?scale_setting:!strcmp(n,"vr.glasses_fov_h")?fov_h:fov_v; }
static const char *config_string(const char *n){ (void)n; return mode; }
static double auto_resolution_scale(const char *s){ return strstr(s,"Quest 2")?0.85:1.0; }
static void platform_log(const char *f, ...){ (void)f; }
''' + fn(frame, 'glasses_fov') + fn(frame, 'glasses_ratio') + fn(frame, 'choose_eye_size') + r'''
int main(void){
 vr.recommended_width=1680; vr.recommended_height=1760; strcpy(vr.info.system,"Meta Quest 3");
 choose_eye_size(); assert(vr.eye_size==1680 && vr.eye_image_width==1680 && vr.eye_image_height==1760);   /* AUTO: as 1.0.10 */
 strcpy(vr.info.system,"Oculus Quest 2"); vr.recommended_width=1440; vr.recommended_height=1584;
 choose_eye_size(); assert(vr.eye_size==1224 && vr.eye_image_width==1440 && vr.eye_image_height==1584);   /* Quest 2's 85%: images kept */
 scale_setting=0.7; choose_eye_size(); assert(vr.eye_size==1008 && vr.eye_image_width==1440);
 vr.recommended_width=1680; vr.recommended_height=1760; scale_setting=1.25; choose_eye_size();
 assert(vr.eye_size==2100 && vr.eye_image_width==2100 && vr.eye_image_height==2200);                        /* above 100%: remade */
 scale_setting=9; choose_eye_size(); assert(vr.eye_size==3360);                                              /* at most 200% */
 scale_setting=1; mode="glasses"; choose_eye_size(); assert(vr.glasses && vr.eye_image_width<1680 && vr.eye_image_height<1760);
 puts("PASS: eye images: AUTO and every step to 100% with the full view as 1.0.10 (Quest 3 1680x1760; Quest 2 at 85% keeps "
      "its 1440x1584); above 100% and the glasses window remake them; 200% at most");
}
''')

# --- 8. version, identity, package markers
assert int(re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1)) >= 37
assert int(re.search(r': "1\.0\.(\d+)"', gradle).group(1)) >= 11
assert 'HaloCE Quest test29 candidate 1.0.11 (OpenCE build 144 netcode, network 21;' in frame or \
    'test29: OpenCE build 144 netcode, network 21;' in frame
assert 'candidate_at_least(args.label, 29)' in package
print('PASS: test29 wiring (version 1.0.11 / 37, identity, package markers)')
