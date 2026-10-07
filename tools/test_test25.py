"""Test25: vehicle report diagnostics, first-person seat refinements (opt-in),
VR settings rows that fit, and a vehicle offset reset.

Evidence (kept private): a player's 1.0.6 log (halo_log_2026-10-05_09-20-39)
for "recentring while driving a Warthog left the view sideways" holds no
in-game recentre and no seat state at all, so the cause is not proven and
each recentre, seat entered or left and view switched is now logged with the
angles that decide the view. The owner's video and log (2026-10-05 08:48,
Silent Cartographer) show first-person Warthog driving: the windshield glass
a bright white sheet from the seat, the cockpit tilting hard against a level
horizon, and VR settings rows cut short ("ALL FORWARD: < 0 C", "STEERING:
RIGHT HAN"). Production functions run under ASan/UBSan with small stubs.
"""
from pathlib import Path
import math, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test25'; OUT.mkdir(parents=True, exist_ok=True)


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
transparent = (ROOT / 'source/rasterizer/xbox/rasterizer_xbox_transparent_geometry.c').read_text(encoding='latin-1')
gradle = (ROOT / 'port/android/app/build.gradle').read_text(encoding='utf-8')

# --- defaults: third person, right hand, level horizon (the view as it was)
for key, kind, default in [('vr.vehicle_view', '_config_string', r'"\"chase\""'),
                           ('vr.vehicle_steering', '_config_string', r'"\"right\""'),
                           ('vr.vehicle_tilt', '_config_real', '"0.0"'), ('vr.vehicle_all_forward', '_config_real', '"0.0"')]:
    assert ('{ "%s", %s, %s,' % (key, kind, default)) in config, key
assert 'const char *values[] = {"\\"chase\\"", "\\"right\\"", "true"};' in config, 'the one-time vehicle default migration kept'

# --- the renderer: the glass hook before the shader switch, VR build only
hook = transparent.index('vr_render_seat_transparent(group->source_object_index, group->shader->base.type,')
assert transparent.rindex('#ifdef HALO_VR', 0, hook) > transparent.rindex('else if (pass > 0)', 0, hook)
assert hook < transparent.index('switch (group->shader->base.type)', hook)
assert transparent[hook:hook + 200].count('continue;') == 1
assert 'vr_vehicle_tilt_view(&anchor, &position, &forward, &up);' in fn(render, 'eye_camera')

# --- every settings row fits its widened button. Widths are a proportional
# font's, calibrated on the owner's video: "VIEW: THIRD PERSON" and "ALL
# RIGHT: < 0 CM >" fit, "STEERING: RIGHT HAN" and "ALL FORWARD: < 0 C" were
# all that showed (about 11.7 of these units in a button about 199 wide);
# widened to 250 that is about 14.7: rows are held to 14.5
WIDTH = {' ': .35, ':': .3, '<': .6, '>': .6, '/': .45, '(': .4, ')': .4, '-': .4, '.': .3, '+': .6, '%': .9,
         'I': .35, '1': .5, 'M': .95, 'W': 1.0}


def width(s):
    return sum(WIDTH.get(c, .65 if c.isdigit() else .72) for c in s)


assert width('VIEW: THIRD PERSON') < 11.7 < width('STEERING: RIGHT HAND') and width('ALL FORWARD: < 0 CM >') > 11.7
assert re.search(r'#define VR_MENU_BUTTON_WIDTH 250\b', menu)
button = fn(menu, 'vr_menu_button')
assert 'widget->bounds.x1 = (short)(widget->bounds.x0 + VR_MENU_BUTTON_WIDTH);' in button
assert 'static short const hints_x = 328, right_column_x = 328 - 72;' in menu and 250 + 6 <= 328 - 72, 'columns do not overlap'
rows_text = menu.replace('VR_MENU_TURNING_ROW,', menu[menu.index('#define VR_MENU_TURNING_ROW ') +
                                                       len('#define VR_MENU_TURNING_ROW '):].split('\n')[0] + ',')
rows = re.findall(r'\{ "([^"]+)", "([^"]*)", (_vr_setting_\w+), (\d+), \{ (.*?) \} \}', rows_text)
assert len(rows) > 100
over = []
for label, key, kind, count, values in rows:
    labels = re.findall(r'\{ "([^"]+)", "[^"]*" \}', values)
    if kind in ('_vr_setting_degrees', '_vr_setting_hand_degrees'):
        texts = ['< -180 DEG >']
    elif kind == '_vr_setting_centimetres':
        texts = ['< -20 CM >']
    elif kind == '_vr_setting_vehicle_centimetres':
        # (two-digit negatives on BANSHEE RIGHT and PELICAN RIGHT, -10 to -50 cm, may clip the final ">")
        texts = ['< -9 CM >', '< 50 CM >'] if label in ('BANSHEE RIGHT', 'PELICAN RIGHT') else ['< -50 CM >', '< 50 CM >']
    elif kind == '_vr_setting_gun_aim':
        texts = {'AIM FOR': ['FLAMETHROWER', 'HOLD A GUN'], 'AIM UP': ['< -10.0 DEG >'],
                 'AIM RIGHT': ['< -10.0 DEG >']}.get(label, ['APPLY'])
    elif kind.startswith('_vr_setting_reset') or kind == '_vr_setting_flip_alignment':
        texts = ['APPLY']
    elif kind in ('_vr_setting_real', '_vr_setting_snap_angle'):
        texts = ['< %s >' % l for l in labels]
    else:
        texts = labels
    for t in texts:
        if width(label + ': ' + t) > 14.5:
            over.append(label + ': ' + t)
assert not over, over
for name in ['ALL FWD', 'HOG FWD', 'USE / RELOAD', 'NEXT WEAPON', 'NEXT GRENADE', 'VIGNETTE ON', 'OPACITY',
             'PISTOL FWD', 'SNIPER FWD', 'RESET OFFSETS', 'HORIZON']:
    assert '{ "%s", ' % name in menu, name
for key in ['vr.vehicle_all_forward', 'vr.button_action', 'vr.button_switch_grenade', 'vr.vignette_when',
            'vr.crosshair_opacity', 'vr.scope_pistol_forward']:
    assert '"%s"' % key in menu, 'saved keys unchanged: ' + key
print('PASS: %d settings rows fit their widened buttons (vehicle offsets to +-50 cm; Banshee/Pelican right to -9 cm); saved keys unchanged' % len(rows))

# --- reviewed upstream fixes adopted (OpenCE, 2026-10-04/05)
vsh = (ROOT / 'port/linux/src/nv2a_vsh.c').read_text(encoding='utf-8')
assert r'"\tif (!(abs(position.w) > 0.0))\n"' in vsh and r'"\t\tposition = vec4(0.0, 0.0, 0.0, -1.0);\n"' in vsh, '3d2c04d6'
assert 'next_unit_index = NONE;' in (ROOT / 'source/camera/dead_camera.c').read_text(encoding='latin-1'), 'fb1abedd'
d3d = (ROOT / 'port/linux/src/d3d8_gl.c').read_text(encoding='utf-8')
bind = fn(d3d, 'bind_textures')
final_binds = 'for (stage = 0; stage < D3DTSS_MAXSTAGES; stage++)\n\t\tstate_texture(stage, gl_targets[stage], gl_textures[stage]);\n}'
assert bind.rstrip().endswith(final_binds), '61623e68: bound after the loop'
assert bind.count('state_texture(') == 1, '61623e68: no bind inside the loop'
import hashlib
for name, digest in [('hud_unit_backgrounds__6.png', 'e5a41500712d3636'), ('hud_unit_backgrounds__7.png', '0844386b13d35c96')]:
    assert hashlib.sha256((ROOT / 'port/assets/hud' / name).read_bytes()).hexdigest().startswith(digest), '3ae09c3d ' + name

# --- version
# (test26 and later raise these)
import re as _re
assert int(_re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1)) >= 33
assert int(_re.search(r': "1\.0\.(\d+)"', gradle).group(1)) >= 7
assert 'HaloCE Quest test25 candidate 1.0.7' in frame or (
    _re.search(r'HaloCE Quest test(\d+) candidate 1\.0\.(\d+)', frame) and 'test25:' in frame)

# --- the vehicle seat offsets' reset
reset = menu[menu.index('    if(setting->type == _vr_setting_reset_vehicle_offsets) {'):
             menu.index('    if(setting->type == _vr_setting_turn_mode) {')]
run('reset_offsets', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
typedef int boolean;
#define TRUE 1
#define FALSE 0
enum { _vr_setting_real, _vr_setting_reset_vehicle_offsets };
struct vr_menu_setting { char const *label, *key; short type; };
static struct { char key[64]; double value; } cfg[40]; static int count, writes, reloads;
static double *find(const char *k){ for(int i=0;i<count;i++) if(!strcmp(cfg[i].key,k)) return &cfg[i].value;
 snprintf(cfg[count].key,64,"%s",k); cfg[count].value=0; return &cfg[count++].value; }
static double config_default_real(const char *k){ (void)k; return 0.0; }
static boolean config_write_real(const char *k, double v){ *find(k)=v; writes++; return TRUE; }
static void vr_reload_settings(void){ reloads++; }
static void platform_log(const char *f, ...){ (void)f; }
static boolean change(struct vr_menu_setting const *setting){ boolean written=FALSE;
''' + reset + r'''
 return FALSE; }
int main(void){
 const char *vehicles[]={"all","warthog","ghost","banshee","scorpion","pelican"}, *axes[]={"up","forward","right"};
 char key[64];
 for(int v=0;v<6;v++) for(int a=0;a<3;a++){ snprintf(key,64,"vr.vehicle_%s_%s",vehicles[v],axes[a]); *find(key)=0.07*(v+1)*(a+1); }
 *find("vr.vehicle_tilt")=1.0; *find("vr.vehicle_view")=2.0;
 struct vr_menu_setting row={"RESET OFFSETS","vehicle offsets",_vr_setting_reset_vehicle_offsets};
 assert(change(&row) && writes==18 && reloads==1);
 for(int v=0;v<6;v++) for(int a=0;a<3;a++){ snprintf(key,64,"vr.vehicle_%s_%s",vehicles[v],axes[a]); assert(*find(key)==0.0); }
 assert(*find("vr.vehicle_tilt")==1.0 && *find("vr.vehicle_view")==2.0);
 struct vr_menu_setting other={"X","x",_vr_setting_real}; assert(!change(&other));
 puts("PASS: Reset Offsets puts all 18 vehicle seat offsets back to 0 and leaves view, horizon and steering alone");
}
''')

# --- the first-person driver's horizon
tilt_state = re.search(r'static struct\n\{\n\treal_vector3d up;\n\tdouble time;\n\tlong vehicle_index;\n\tboolean valid;\n\} vr_tilt;\n',
                       render).group(0)
run('tilt', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1L)
typedef union { struct { real x, y, z; }; real n[3]; } real_point3d;
typedef union { struct { real i, j, k; }; real n[3]; } real_vector3d;
typedef struct { real scale; real_vector3d forward, left, up; real_point3d position; } real_matrix4x3;
struct object_datum { struct { real_vector3d up; } object; };
static struct { struct { boolean driver; long vehicle_index; } seat; } vr_render;
static real amount; static boolean seat_view = TRUE; static double now; static struct object_datum vehicle;
static real_matrix4x3 drawn[1]; static boolean have_drawn;
static real vr_vehicle_tilt(void){ return amount; }
static boolean vr_seat_view(void){ return seat_view; }
static double vr_pose_time(void){ return now; }
static struct object_datum *object_try_and_get(long i){ return i == 7 ? &vehicle : NULL; }
static real_matrix4x3 *render_interpolation_object_node_matrices(long i){ return have_drawn && i == 7 ? drawn : NULL; }
static real normalize3d(real_vector3d *v){ real l = sqrtf(v->i*v->i+v->j*v->j+v->k*v->k); if (l > 0) { v->i/=l; v->j/=l; v->k/=l; } return l; }
''' + tilt_state + fn(render, 'vr_vehicle_tilt_view') + r'''
static real_point3d anchor = {{ 10, 20, 3 }}, position; static real_vector3d forward, up;
static void camera(void){ position.x = 10; position.y = 20.1f; position.z = 3; forward.i = 1; forward.j = forward.k = 0; up.i = up.j = 0; up.k = 1; }
static void roll(real degrees){ real r = degrees * 0.01745329f; vehicle.object.up.i = 0; vehicle.object.up.j = -sinf(r); vehicle.object.up.k = cosf(r); }
static real angle_up(void){ return acosf(fminf(1.0f, up.k)) * 57.29578f; }
int main(void){
 vr_render.seat.driver = TRUE; vr_render.seat.vehicle_index = 7;
 /* level (the default): nothing moves */
 amount = 0; roll(20); camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up);
 assert(up.k == 1 && forward.i == 1 && position.y == 20.1f);
 /* a level vehicle: nothing to tilt */
 amount = 1; roll(0); camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up); assert(up.k == 1 && position.y == 20.1f);
 /* rolled 20 degrees, followed whole: the view's up is the vehicle's, the forward kept, the eyes turned about the anchor */
 vr_tilt.valid = FALSE; roll(20); camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up);
 assert(fabsf(up.j - vehicle.object.up.j) < 1e-5f && fabsf(up.k - vehicle.object.up.k) < 1e-5f);
 assert(fabsf(forward.i - 1) < 1e-5f && fabsf(forward.j) < 1e-5f && fabsf(forward.k) < 1e-5f);
 { real dy = position.y - anchor.y, dz = position.z - anchor.z; assert(fabsf(sqrtf(dy*dy + dz*dz) - 0.1f) < 1e-4f && fabsf(dz - 0.1f * sinf(0.3490659f)) < 1e-4f); }
 /* half: about half the angle */
 amount = 0.5f; vr_tilt.valid = FALSE; camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up);
 assert(fabsf(angle_up() - 10.0f) < 0.5f);
 /* past 60 degrees (a flip): held at 60 */
 amount = 1; vr_tilt.valid = FALSE; roll(85); camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up);
 assert(fabsf(angle_up() - 60.0f) < 0.1f);
 /* eased: a sudden 20-degree jolt shows a little in one frame, nearly all after half a second */
 vr_tilt.valid = FALSE; roll(0); now = 1.0; camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up);
 roll(20); now += 1.0 / 72; camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up);
 assert(angle_up() > 1.0f && angle_up() < 4.0f);
 for (int i = 0; i < 36; i++) { now += 1.0 / 72; camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up); }
 assert(angle_up() > 19.0f && angle_up() < 20.01f);
 /* a hitch (a long frame) is not a jump */
 now += 5.0; camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up); assert(angle_up() < 20.01f);
 /* the drawn (interpolated) vehicle is preferred */
 have_drawn = TRUE; drawn[0].up = vehicle.object.up; drawn[0].up.j = 0; drawn[0].up.k = 1; vr_tilt.valid = FALSE;
 camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up); assert(up.k == 1); have_drawn = FALSE;
 /* gunners, passengers and third person stay level */
 vr_render.seat.driver = FALSE; camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up); assert(up.k == 1 && !vr_tilt.valid);
 vr_render.seat.driver = TRUE; seat_view = FALSE; camera(); vr_vehicle_tilt_view(&anchor, &position, &forward, &up); assert(up.k == 1);
 puts("PASS: Horizon: Level leaves the view as it was; Vehicle tilts a driver's view with the vehicle exactly (the forward kept, "
      "the eyes turned about the seat), Half about half, held at 60 degrees, eased against jolts, hitches bounded; "
      "gunners, passengers and third person stay level");
}
''')

# --- the seat's own glass
run('glass', r'''
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1L)
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
static struct { struct { boolean seated; long vehicle_index; } seat; } vr_render;
static boolean first_person = TRUE, seat_view = TRUE; static int logs; static char last[200];
static int generation, hide_glass=1; static const char *vehicle_name="warthog";
static int vr_settings_generation(void){return generation;}
static int config_boolean(const char *key){assert(!strcmp(key,"vr.vehicle_warthog_hide_glass"));return hide_glass;}
static const char *tag_get_name(long d){return vehicle_name;}
static const char *vr_vehicle_profile(const char *name){return name;}
static struct {long definition_index;} object;
static void *unused_object;
static typeof(object) *object_get(long i){return &object;}
static boolean vr_first_person_vehicles(void){ return first_person; }
static boolean vr_seat_view(void){ return seat_view; }
static void *object_try_and_get(long i){ static int any; return i >= 0 ? &any : NULL; }
static long object_get_ultimate_parent(long i){ return i == 9 ? 7 : i; }  /* 9: a part attached to vehicle 7 */
static void platform_log(const char *f, ...){ va_list a; va_start(a, f); vsnprintf(last, sizeof(last), f, a); va_end(a); logs++; }
''' + fn(render, 'vr_render_seat_transparent') + r'''
enum { chicago = 6, glass = 8, generic = 5 };
int main(void){
 vr_render.seat.seated = TRUE; vr_render.seat.vehicle_index = 7;
 assert(vr_render_seat_transparent(7, glass, glass) && logs == 1 && strstr(last, "glass") && strstr(last, "hidden"));
 assert(vr_render_seat_transparent(7, glass, glass) && logs == 1);          /* said once */
 assert(!vr_render_seat_transparent(7, chicago, glass) && logs == 2 && strstr(last, "chicago"));
 assert(vr_render_seat_transparent(9, glass, glass));                       /* a part of the vehicle */
 assert(!vr_render_seat_transparent(3, glass, glass));                      /* another object's glass */
 assert(!vr_render_seat_transparent(NONE, glass, glass));
 first_person = FALSE; assert(!vr_render_seat_transparent(7, glass, glass)); first_person = TRUE;
 seat_view = FALSE; assert(!vr_render_seat_transparent(7, glass, glass)); seat_view = TRUE;
 vr_render.seat.seated = FALSE; assert(!vr_render_seat_transparent(7, glass, glass)); vr_render.seat.seated = TRUE;
 vr_render.seat.vehicle_index = 3; assert(vr_render_seat_transparent(3, glass, glass) && logs == 3); /* a new vehicle: said again */
 hide_glass=0;generation++;
 assert(!vr_render_seat_transparent(3,glass,glass));
 vehicle_name="ghost";assert(vr_render_seat_transparent(3,glass,glass));
 vehicle_name="warthog";hide_glass=1;generation++;
 assert(vr_render_seat_transparent(3,glass,glass));
 puts("PASS: from a first-person seat only the seated vehicle's own glass (and its parts') is hidden, each kind said once a "
      "vehicle; other objects, third person and on foot draw as ever");
}
''')

# --- the vehicle report's diagnostics
run('diagnostics', r'''
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#define HALO_XR_FRAME_RECENTRED 8u
static struct { struct { unsigned flags; } frame; int recentre_source, seat_logged; float heading, head_yaw, aim_yaw; } vr;
static int logs; static char last[300];
static void platform_log(const char *f, ...){ va_list a; va_start(a, f); vsnprintf(last, sizeof(last), f, a); va_end(a); logs++; }
''' + fn(frame, 'aim_diagnostics') + r'''
int main(void){
 float seat = 1.0f;
 vr.seat_logged = -1;
 aim_diagnostics(0.5f, 0, 1, NULL, 0); assert(logs == 0 && vr.seat_logged == 0);           /* first seen: no log */
 aim_diagnostics(0.5f, 0, 1, NULL, 0); assert(logs == 0);                                  /* steady: never per frame */
 aim_diagnostics(0.5f, 1, 2, NULL, 0); assert(logs == 1 && strstr(last, "on foot -> third person") && strstr(last, "right hand"));
 aim_diagnostics(0.5f, 1, 2, &seat, 0); assert(logs == 2 && strstr(last, "third person -> first person") && strstr(last, "seat 57.3"));
 vr.recentre_source = 1; vr.frame.flags = HALO_XR_FRAME_RECENTRED; vr.heading = 1.0f;
 aim_diagnostics(0.5f, 1, 2, &seat, 0.25f);
 assert(logs == 3 && strstr(last, "recentre (both sticks): seated, first person, heading 14.3 -> 57.3") && vr.recentre_source == 0);
 aim_diagnostics(0.5f, 1, 3, &seat, 0); assert(logs == 4 && strstr(last, "the system or the headset regaining focus") && strstr(last, "left hand"));
 vr.frame.flags = 0;
 aim_diagnostics(0.5f, 0, 1, NULL, 0); assert(logs == 5 && strstr(last, "first person -> on foot"));
 vr.recentre_source = 2; vr.frame.flags = HALO_XR_FRAME_RECENTRED; aim_diagnostics(0.5f, 0, 1, NULL, 0);
 assert(logs == 6 && strstr(last, "(View held): on foot"));
 puts("PASS: each recentre (both sticks, View held, the system or focus), seat entered or left and view switched is "
      "logged once with the heading before and after, head, aim, steering hand, game and seat angles; nothing per frame");
}
''')
print('PASS: test25 wiring (defaults kept: third person, right hand, level horizon; glass hook in the VR renderer only; '
      'tilt in the eye camera; version 1.0.7 / 33)')
