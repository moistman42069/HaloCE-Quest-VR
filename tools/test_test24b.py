"""Test24b (1.0.6, code 32): comfort settings and the SPV1 notice.

Owner requests (2026-10-05): a player asked for snap turn and vignetting as
comfort settings; the owner added a smooth turn speed and a snap angle to
fine-tune them, and asked for SPV1 to be marked as not working yet. Snap turn
existed (Controls > Turning: snap 30/45/90); this adds a COMFORT page (turning
smooth or snap, smooth speed, snap angle, vignette, vignette when), snap 22.5
and 60 on the Controls row, and the vignette itself: a black edge drawn into
each gameplay eye while the player moves or turns by stick. Production
functions run under ASan/UBSan with small stubs; no headset is used.
"""
from pathlib import Path
import math, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test24b'; OUT.mkdir(parents=True, exist_ok=True)


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
vr_h = (ROOT / 'port/linux/src/vr.h').read_text(encoding='utf-8')
gl_h = (ROOT / 'port/linux/src/gl.h').read_text(encoding='utf-8')
d3d = (ROOT / 'port/linux/src/d3d8_gl.c').read_text(encoding='utf-8')
menu = (ROOT / 'port/linux/game/vr_menu.c').read_text(encoding='utf-8')
config = (ROOT / 'port/linux/src/port_config.c').read_text(encoding='utf-8')
gradle = (ROOT / 'port/android/app/build.gradle').read_text(encoding='utf-8')
launcher = (ROOT / 'port/android/app/src/main/java/com/halo/decomp/LauncherActivity.java').read_text(encoding='utf-8')
guide = (ROOT / 'docs/PLAYER-GUIDE.md').read_text(encoding='utf-8')

# --- settings: new keys, defaults that change nothing
for key, kind, default in [('vr.vignette', '_config_real', '"0.0"'), ('vr.vignette_when', '_config_string', r'"\"move_turn\""'),
                           ('vr.snap_turn_amount', '_config_real', '"45.0"'), ('vr.snap_turn', '_config_real', '"0.0"'),
                           ('vr.smooth_turn_speed', '_config_real', '"120.0"')]:
    assert ('{ "%s", %s, %s,' % (key, kind, default)) in config, key

# --- the menu: a COMFORT page; the Controls row keeps every earlier choice
assert '{ "COMFORT", vr_menu_comfort, NUMBEROF(vr_menu_comfort) },' in menu
comfort = menu[menu.index('static struct vr_menu_setting const vr_menu_comfort[] ='):]
comfort = comfort[:comfort.index('};')]
for row in ['"TURNING", "turn", _vr_setting_turn_mode', '"SMOOTH SPEED", "vr.smooth_turn_speed", _vr_setting_real, 12',
            '"SNAP ANGLE", "vr.snap_turn_amount", _vr_setting_snap_angle, 9', '"VIGNETTE", "vr.vignette", _vr_setting_real, 4',
            '"VIGNETTE WHEN", "vr.vignette_when", _vr_setting_string, 3', '{ "OFF", "0" }', '{ "120 DEG/S", "120" }',
            '{ "22.5 DEG", "22.5" }', '{ "45 DEG", "45" }']:
    assert row in comfort, row
turning = menu[menu.index('#define VR_MENU_TURNING_ROW'):].split('\n')[0]
for old in ['SMOOTH 60', 'SMOOTH 90', 'SMOOTH 120', 'SMOOTH 150', 'SMOOTH 180', 'SMOOTH 240', 'SMOOTH 300',
            '"vr.snap_turn=30;', '"vr.snap_turn=45;', '"vr.snap_turn=90;']:
    assert old in turning, old
assert '"vr.snap_turn=0;vr.smooth_turn_speed=120"' in turning, 'the default still reads as SMOOTH 120'
assert turning.count('{ "') == 13 and ', 12, {' in turning, 'the row and its twelve choices'
assert 'VR_MENU_TURNING_ROW,' in menu[menu.index('vr_menu_controls[]'):menu.index('vr_menu_controls[]') + 4000]

# --- the vignette's wiring
copy = fn(frame, 'copy_to_swapchain')
assert copy.index('glBlitFramebuffer(') < copy.index('if (which < 2 && vr_vignette_shown())\n\t\tdraw_vignette(which);') < \
    copy.index('host_xr_release(which);'), 'drawn into the eye after its copy, before release'
assert 'vr_resolve_eye(eye, framebuffer_get(back_buffer->target.texture, 0), (int)back_buffer->target.gl_width,\n' \
       '\t\t(int)back_buffer->target.gl_height);\n\txgpu_gl_state_invalidate();' in d3d, 'the renderer retakes its GL state after an eye'
draw = fn(frame, 'draw_vignette')
for call in re.findall(r'\b(gl[A-Z]\w+)\(', draw):
    assert ('X(%s)' % call) in gl_h, 'GL function the game imports: ' + call
assert 'glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_FALSE);' in draw and draw.rstrip().endswith(
    'glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);\n\tglDisable(GL_BLEND);\n}'), 'eye alpha untouched; state restored'
assert 'if (!vr.aiming)\n\t\tvr.vignette_amount = vr.snap_pulse = 0.0f;' in fn(frame, 'vr_present')
aim = fn(frame, 'vr_aim')
assert aim.index('if (hand_may_aim >= 0) turn();') < aim.index('comfort_update(vr.frame.predicted_display_period * 1e-9);')

# --- SPV1 marked as not working
assert 'menuButton(layout, ModInstaller.SPV1.title + " (not working yet)")' in launcher
assert 'SPV1 support is currently not functioning. It will be refined "\n        + "in a future release.' in launcher
select = fn(launcher.replace('    private void selectMod', 'void selectMod'), 'selectMod')
assert select.index('modDetails.addView(name);') < select.index('warning.setText(MOD_NOT_WORKING);') < \
    select.index('description.setText(mod.description);'), 'the warning first in the SPV1 panel'
assert '**SPV1 is currently not functioning.**' in guide

# --- version
assert 'versionCode Math.max(32, buildNumber)' in gradle and '"1.0.6"' in gradle
assert 'HaloCE Quest test24b candidate 1.0.6' in frame

# --- the vignette's shape (the shader's sum, here in Python) for a Quest-like eye
shader = frame[frame.index('static const char vignette_fragment_source[] ='):]
shader = shader[:shader.index(';\nstatic GLuint vignette_program;')]
assert 'mix(tangents.x, tangents.y, coordinate.x), mix(tangents.z, tangents.w, coordinate.y)' in shader
assert 'smoothstep(aperture, aperture + feather, length(t))' in shader
FEATHER = float(re.search(r'#define VR_VIGNETTE_FEATHER ([\d.]+)f', vr_h).group(1))
fov = [-1.028, 0.885, 0.864, -1.048]  # synthesize_views' left eye (radians: left, right, up, down)
tan = [math.tan(a) for a in fov]
corner = math.sqrt(max(tan[0] ** 2, tan[1] ** 2) + max(tan[2] ** 2, tan[3] ** 2))


def aperture(strength, amount, corner):
    narrowest = 1.0 - 0.55 * strength
    amount = min(max(amount, 0.0), 1.0)
    corner = max(corner, narrowest)
    return corner - amount * (corner - narrowest)


def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def darkened(strength, amount):
    total = 0.0; n = 0; centre = 1.0
    for i in range(41):
        for j in range(41):
            x, y = i / 40, j / 40
            t = (tan[0] + (tan[1] - tan[0]) * x, tan[2] + (tan[3] - tan[2]) * y)
            a = smoothstep(aperture(strength, amount, corner), aperture(strength, amount, corner) + FEATHER, math.hypot(*t))
            total += a; n += 1
            if math.hypot(*t) < 0.05: centre = min(centre, 1 - a)
    return total / n, centre


assert darkened(1.0, 0.0)[0] == 0.0, 'nothing at no motion, even in the corners'
previous = 0.0
for amount in [0.05, 0.25, 0.5, 0.75, 1.0]:
    share, centre = darkened(0.65, amount)
    assert share > previous and centre == 1.0, (amount, share)
    previous = share
low, medium, high = darkened(0.35, 1.0)[0], darkened(0.65, 1.0)[0], darkened(1.0, 1.0)[0]
assert 0.0 < low < medium < high < 0.95, (low, medium, high)
for strength, degrees in [(1.0, 24), (0.65, 33), (0.35, 39)]:
    assert abs(math.degrees(math.atan(aperture(strength, 1.0, corner))) - degrees) < 1.0, strength
print('PASS: vignette shape: nothing at rest (corners included), grows smoothly with motion, the centre always clear; '
      'full motion darkens %.0f%%/%.0f%%/%.0f%% of a Quest-like eye for low/medium/high' % (low * 100, medium * 100, high * 100))

# --- the comfort logic: production functions
enums = re.search(r'enum \{ VR_VIGNETTE_MOVING, VR_VIGNETTE_TURNING, VR_VIGNETTE_ALWAYS \};', vr_h).group(0)
run('comfort', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include "port/android/include/halo_android_abi.h"
''' + enums + '''
#define VR_VIGNETTE_FEATHER 0.35f
static struct { struct { float thumb[4]; int64_t predicted_display_period; unsigned int flags; float fov[2][4]; } frame;
 float snap_turn, smooth_turn_speed, heading, vignette_strength, vignette_amount, comfort_move, comfort_turn, snap_pulse;
 int snap_armed, vignette_when, stereo, cinema, aiming, aiming_last_frame, pointer_age; } vr;
''' + fn(frame, 'wrap_angle') + fn(frame, 'comfort_stick') + fn(frame, 'comfort_update') + fn(frame, 'turn') +
    fn(frame, 'vr_vignette_aperture') + fn(frame, 'vr_vignette_shown') + r'''
static void frames(int n, double s){for(int i=0;i<n;i++)comfort_update(s);}
static void reset(int when){vr.vignette_amount=vr.snap_pulse=vr.comfort_move=vr.comfort_turn=0;vr.vignette_when=when;}
int main(void){
 const double f=1.0/72;
 vr.frame.predicted_display_period=13888889; vr.frame.flags=HALO_XR_FRAME_FOCUSED;
 vr.stereo=1; vr.aiming=1; vr.vignette_strength=0.65f; vr.snap_armed=1;
 /* the sticks' dead zone: a rest is no motion, a full push is all */
 assert(comfort_stick(0.1f,0.1f)==0.0f && comfort_stick(1.0f,0.0f)==1.0f && comfort_stick(0.0f,-0.5f)>0.0f);
 /* moving: in within 0.12 s, out within 0.35 s */
 reset(VR_VIGNETTE_MOVING); vr.comfort_move=1; frames(9,f); assert(vr.vignette_amount>=0.99f);
 vr.comfort_move=0; frames(12,f); assert(vr.vignette_amount>0.4f); frames(14,f); assert(vr.vignette_amount==0.0f);
 /* turning only: moving shows nothing, a smooth turn does */
 reset(VR_VIGNETTE_TURNING); vr.comfort_move=1; frames(30,f); assert(vr.vignette_amount==0.0f);
 vr.snap_turn=0; vr.smooth_turn_speed=2.0f; vr.frame.thumb[2]=0.9f; turn(); assert(vr.comfort_turn>0.9f);
 frames(10,f); assert(vr.vignette_amount>0.9f);
 vr.frame.thumb[2]=0.0f; turn(); assert(vr.comfort_turn==0.0f);
 /* always: shown without any motion */
 reset(VR_VIGNETTE_ALWAYS); frames(10,f); assert(vr.vignette_amount==1.0f);
 /* a snap turn: one turn per push, and a brief pulse */
 reset(VR_VIGNETTE_MOVING); vr.snap_turn=0.785f; vr.heading=0; vr.snap_armed=1;
 vr.frame.thumb[2]=0.9f; turn(); assert(fabsf(vr.heading+0.785f)<1e-4f && vr.snap_pulse==1.0f && vr.comfort_turn==0.0f);
 turn(); assert(fabsf(vr.heading+0.785f)<1e-4f); /* held: no second turn */
 frames(5,f); assert(vr.vignette_amount>0.4f);
 vr.frame.thumb[2]=0.0f; turn(); frames(60,f); assert(vr.vignette_amount==0.0f && vr.snap_pulse==0.0f);
 /* a long frame (a hitch) is taken as one display period */
 reset(VR_VIGNETTE_MOVING); vr.comfort_move=1; comfort_update(5.0); assert(vr.vignette_amount<0.2f);
 /* shown only in control in stereo gameplay, set on, and some showing */
 reset(VR_VIGNETTE_ALWAYS); frames(10,f); assert(vr_vignette_shown());
 vr.cinema=1; assert(!vr_vignette_shown()); vr.cinema=0;
 vr.aiming=vr.aiming_last_frame=0; assert(!vr_vignette_shown()); vr.aiming=1;
 vr.pointer_age=3; assert(!vr_vignette_shown()); vr.pointer_age=0;
 vr.vignette_strength=0; assert(!vr_vignette_shown()); vr.vignette_strength=0.65f;
 vr.stereo=0; assert(!vr_vignette_shown()); vr.stereo=1;
 reset(VR_VIGNETTE_MOVING); assert(!vr_vignette_shown());
 /* the clear radius: the corner at nothing, narrowing to the strength's */
 assert(vr_vignette_aperture(1,0,2.0f)==2.0f && fabsf(vr_vignette_aperture(1,1,2.0f)-0.45f)<1e-5f);
 assert(vr_vignette_aperture(0.35f,1,2.0f)>vr_vignette_aperture(0.65f,1,2.0f));
 assert(vr_vignette_aperture(1,2,2.0f)==vr_vignette_aperture(1,1,2.0f)&&vr_vignette_aperture(1,-1,2.0f)==2.0f);
 puts("PASS: vignette eases in 0.12 s and out 0.35 s; turning-only ignores moving; always shows; a snap turn turns once "
      "per push with a brief pulse; hitches are bounded; never in cutscenes, the 3D screen, menus or when off");
}
''')

# --- the menu's fine turning: production change handlers
handlers = menu[menu.index('    if(setting->type == _vr_setting_turn_mode) {'):menu.index('    if(setting->type == _vr_setting_reset_buttons) {')]
run('turning_menu', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
enum { _vr_setting_real, _vr_setting_turn_mode, _vr_setting_snap_angle };
struct vr_menu_setting { char const *label, *key; short type, value_count; struct { char const *label, *value; } values[12]; };
static double snap_turn, amount = 45.0; static int reloads;
static double config_real(const char *k){ return !strcmp(k,"vr.snap_turn") ? snap_turn : !strcmp(k,"vr.snap_turn_amount") ? amount : (abort(), 0); }
static boolean config_write_real(const char *k, double v){ if(!strcmp(k,"vr.snap_turn")) snap_turn=v; else if(!strcmp(k,"vr.snap_turn_amount")) amount=v; else abort(); return TRUE; }
static void vr_reload_settings(void){ reloads++; }
static void platform_log(const char *f, ...){ (void)f; }
''' + fn(menu, 'vr_menu_snap_angle') + r'''
static boolean change(struct vr_menu_setting const *setting, long step){
 long value_index; boolean written = FALSE;
''' + handlers + r'''
 return FALSE; }
static const struct vr_menu_setting mode = { "TURNING", "turn", _vr_setting_turn_mode, 2, { { "SMOOTH", "smooth" }, { "SNAP", "snap" } } };
static const struct vr_menu_setting angle = { "SNAP ANGLE", "vr.snap_turn_amount", _vr_setting_snap_angle, 9, { { "10 DEG", "10" }, { "15 DEG", "15" }, { "20 DEG", "20" }, { "22.5 DEG", "22.5" }, { "30 DEG", "30" }, { "40 DEG", "40" }, { "45 DEG", "45" }, { "60 DEG", "60" }, { "90 DEG", "90" } } };
int main(void){
 /* smooth (the default) to snap: the kept angle */
 assert(change(&mode, 1) && snap_turn == 45.0);
 /* the angle while snapping moves the turn too */
 assert(change(&angle, 1) && amount == 60.0 && snap_turn == 60.0);
 /* back to smooth: the angle kept for later */
 assert(change(&mode, 1) && snap_turn == 0.0 && amount == 60.0);
 /* the angle while smooth: kept only, turning stays smooth */
 assert(change(&angle, -1) && amount == 45.0 && snap_turn == 0.0);
 assert(change(&angle, -1) && amount == 40.0);
 assert(change(&mode, -1) && snap_turn == 40.0);
 /* the ends hold; a value between the choices steps to the next one each way */
 for (int i = 0; i < 12; i++) change(&angle, 1); assert(amount == 90.0 && snap_turn == 90.0);
 for (int i = 0; i < 12; i++) change(&angle, -1); assert(amount == 10.0 && snap_turn == 10.0);
 snap_turn = 37; amount = 37; change(&angle, 1); assert(amount == 40.0 && snap_turn == 40.0);
 snap_turn = 37; amount = 37; change(&angle, -1); assert(amount == 30.0 && snap_turn == 30.0);
 /* snapping set from Controls (vr.snap_turn) is the angle the page shows and keeps */
 snap_turn = 22.5; amount = 45; assert(vr_menu_snap_angle() == 22.5); change(&mode, 1); assert(snap_turn == 0 && amount == 22.5);
 /* a broken kept angle falls back to 45 */
 snap_turn = 0; amount = -3; assert(vr_menu_snap_angle() == 45.0);
 /* other rows are not these handlers' */
 { struct vr_menu_setting other = mode; other.type = _vr_setting_real; assert(!change(&other, 1)); }
 printf("PASS: Turning switches smooth/snap keeping the snap angle; Snap Angle steps 10-90 (holding at the ends), moves a live "
        "snap turn and only keeps the angle while smooth; Controls' snap values show on the page (%d reloads)\n", reloads);
}
''')
print('PASS: test24b wiring (comfort settings default off/unchanged, COMFORT page, Controls turning keeps every choice, '
      'vignette drawn per gameplay eye with imported GL calls, SPV1 marked not working, version 1.0.6 / 32)')
