"""Test20d: the held gun anchored to the controller, left-handed controls and
the simplified VR settings.

Owner log/video (2026-10-04 10:34): in passthrough comparisons the pistol sat
ahead of, above and inward of the real controller and swung around a point
behind the hand as the controller turned. The first-person model is posed from
a weapon camera placed at a fixed offset from the grip, so where the gun hand
lands depended on each weapon's animation. Test20d moves the whole model so the
gun hand's wrist sits where the empty hand's wrist would (vr_gun_anchor.h,
vr_anchor_gun). Production code runs under ASan/UBSan with small stubs; no
headset or game data is used. Run under Linux/WSL with clang.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test20d'; OUT.mkdir(parents=True, exist_ok=True)


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def block(text, start, end):
    a = text.index(start)
    return text[a:text.index(end, a) + len(end)] + '\n'


def run(name, text):
    p = OUT / (name + '.c'); p.write_text(text)
    subprocess.run(['clang', '-std=gnu11', '-O1', '-Wall', '-Wextra', '-Wno-unused-function', '-Wno-unused-variable',
                    '-Wno-unused-parameter', '-Wno-missing-field-initializers', '-fsanitize=address,undefined',
                    '-I', str(ROOT), str(p), '-lm', '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)


frame = (ROOT / 'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
render = (ROOT / 'port/linux/game/vr_render.c').read_text(encoding='utf-8')
menu = (ROOT / 'port/linux/game/vr_menu.c').read_text(encoding='utf-8')
config = (ROOT / 'port/linux/src/port_config.c').read_text(encoding='utf-8')
package = (ROOT / 'tools/package-quest.py').read_text(encoding='utf-8')

# --- the config table, as the stubs below see it
table = {}
for name, kind, default in re.findall(r'\{ "([\w.]+)", (_config_\w+), "((?:[^"\\]|\\.)*)"', config):
    table[name] = (kind, default.replace('\\"', ''))
for key, kind, default in [('vr.gun_anchor', '_config_boolean', 'true'), ('vr.gun_forward', '_config_real', '0.0'),
                           ('vr.gun_up', '_config_real', '0.0'), ('vr.gun_out', '_config_real', '0.0'),
                           ('vr.mirror_controls', '_config_string', 'auto'),
                           ('vr.handedness_applied', '_config_boolean', 'false'),
                           ('vr.left_handed', '_config_boolean', 'false'), ('vr.hand_tracking', '_config_string', 'ik'),
                           ('vr.weapon_offset_right', '_config_real', '0.10'), ('vr.weapon_offset_up', '_config_real', '-0.12'),
                           ('vr.weapon_offset_back', '_config_real', '-0.20'), ('vr.weapon_pitch', '_config_real', '0.0')]:
    assert table.get(key) == (kind, default), (key, table.get(key))

# --- static wiring
ik = fn(render, 'vr_render_first_person_ik')
call = 'vr_anchor_gun(matrices, graph, right[_vr_arm_hand], native_arms, gun_position)'
assert ik.count(call) == 1, 'the gun is anchored once per pose'
assert ik.index('vr_render_first_person_mirrored()') < ik.index(call) < ik.index('draw_arms = vr_render_hands_only()') \
    < ik.index('memcpy(authored'), 'anchor after the left-hand mirror, before arms are hidden, animated or solved'
assert 'if (gun_anchor)' in ik and 'config_boolean("vr.gun_anchor")' in ik
walls = fn(render, 'weapon_out_of_walls'); camera = fn(render, 'vr_render_weapon_camera')
assert 'pullback->i = -forward->i * back;' in walls
assert camera.index('vr_render.weapon_pullback = (real_vector3d){ 0.0f, 0.0f, 0.0f };') < camera.index('weapon_out_of_walls(')
assert 'tracking = vr_hand_tracking_mode() ? (vr_render_hands_only() ? 1 : 2) : 0;' in ik
assert 'if (!vr_render_hands_only()) return;' in fn(render, 'vr_hide_forearms')
begin = fn(frame, 'frame_begin')
assert begin.index('if (vr.controls_mirrored)') < begin.index('layout_controls();'), 'sticks swap before anything reads them'
assert 'vr.frame.thumb[0] = vr.frame.thumb[2];' in begin and 'vr.frame.thumb[2] = move[0];' in begin
assert 'back_down = (vr.frame.hand_buttons[vr.controls_mirrored ? 0 : 1] & HALO_XR_HAND_EAST) != 0;' in frame
reload = fn(frame, 'vr_reload_settings')
assert 'vr.controls_mirrored = left_handed && strcmp(config_string("vr.mirror_controls"), "off") != 0;' in reload
init = frame[frame.index('migrate_calibration_split();\n\tmigrate_handedness();'):]
assert init.index('migrate_handedness();') < init.index('vr_reload_settings()'), 'migrations run before settings load'
change = fn(menu, 'vr_menu_setting_change')
assert 'case _vr_setting_handedness:' in change and 'config_write_string("vr.vehicle_steering", to)' in change \
    and 'config_write_string("vr.move_relative", to)' in change
assert '"vr.gun_forward","vr.gun_up","vr.gun_out",' in change, 'RESET GUN covers the new gun position'
assert '!strcmp(setting->key,"both")' in change
for marker in ['b"HANDS + GUN"', 'b"MIRROR CONTROLS"', 'b"GUN GRIP"', 'b"anchored to the controller"']:
    assert marker in package, marker
print('PASS: static wiring (anchor order, wall pullback kept, merged floating mode, stick swap before input, menu reset/handedness, package markers)')

common = r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
'''

# --- the anchor's state machine
run('anchor_state', common + '#include "port/linux/game/vr_gun_anchor.h"\n' + r'''
static unsigned seed=7;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
static void frame_axes(float a[3][3]){ /* a random right-handed frame: forward, left, up */
 float f[3]={rnd()-.5f,rnd()-.5f,rnd()-.5f},u[3]={rnd()-.5f,rnd()-.5f,rnd()-.5f},l[3];float n;
 n=sqrtf(f[0]*f[0]+f[1]*f[1]+f[2]*f[2]);for(int i=0;i<3;i++)f[i]/=n;
 float d=u[0]*f[0]+u[1]*f[1]+u[2]*f[2];for(int i=0;i<3;i++)u[i]-=d*f[i];
 n=sqrtf(u[0]*u[0]+u[1]*u[1]+u[2]*u[2]);for(int i=0;i<3;i++)u[i]/=n;
 l[0]=u[1]*f[2]-u[2]*f[1];l[1]=u[2]*f[0]-u[0]*f[2];l[2]=u[0]*f[1]-u[1]*f[0];
 for(int i=0;i<3;i++){a[0][i]=f[i];a[1][i]=l[i];a[2][i]=u[i];}}
static void world(float a[3][3],const float local[3],float out[3]){for(int i=0;i<3;i++)out[i]=local[0]*a[0][i]+local[1]*a[1][i]+local[2]*a[2][i];}
static float dist(const float a[3],const float b[3]){float s=0;for(int i=0;i<3;i++)s+=(a[i]-b[i])*(a[i]-b[i]);return sqrtf(s);}
int main(void){
 static struct vr_gun_anchor a;vr_gun_anchor_reset(&a);
 int A=1,B=2;float axes[3][3],m[3],out[3],limit=1.2f;double t=0;
 /* a new weapon drawn while its ready animation owns the arm: old placement (no move) */
 frame_axes(axes);m[0]=.1f;m[1]=.2f;m[2]=-.3f;
 assert(!vr_gun_anchor_update(&a,&A,1,axes,m,1,t,limit,out)&&out[0]==0&&out[1]==0&&out[2]==0);
 /* released: eases in, then is exact */
 float prev=1e9f;int exact=0;
 for(int n=0;n<72;n++){t+=1/72.;vr_gun_anchor_update(&a,&A,1,axes,m,0,t,limit,out);float e=dist(out,m);assert(e<=prev+1e-6f);prev=e;if(e<1e-6f){exact=n;break;}}
 assert(prev<1e-6f&&exact>0&&exact<36);
 /* tracked: exact every frame whatever the controller does */
 for(int n=0;n<2000;n++){t+=1/72.;frame_axes(axes);for(int i=0;i<3;i++)m[i]=(rnd()-.5f)*.8f;
  vr_gun_anchor_update(&a,&A,1,axes,m,0,t,limit,out);assert(dist(out,m)<1e-5f);}
 /* held by an animation: the gap stays fixed in the camera's axes */
 float gap[3];for(int i=0;i<3;i++)gap[i]=m[0]*axes[0][i]*0+0; /* recompute below */
 for(int i=0;i<3;i++)gap[i]=m[0]*axes[i][0]+m[1]*axes[i][1]+m[2]*axes[i][2];
 for(int n=0;n<100;n++){float w[3];t+=1/72.;frame_axes(axes);for(int i=0;i<3;i++)m[i]=(rnd()-.5f)*.8f;
  vr_gun_anchor_update(&a,&A,1,axes,m,1,t,limit,out);world(axes,gap,w);assert(dist(out,w)<1e-5f);}
 /* another weapon, then back: the first one's grip returns at once, even mid-animation */
 frame_axes(axes);t+=1/72.;vr_gun_anchor_update(&a,&B,1,axes,m,1,t,limit,out);assert(out[0]==0&&out[1]==0&&out[2]==0);
 t+=1/72.;{float w[3];vr_gun_anchor_update(&a,&A,1,axes,m,1,t,limit,out);world(axes,gap,w);assert(dist(out,w)<1e-5f);}
 /* settling while the target keeps moving (both hands on the gun): the gun follows at once and only the
 leftover difference shrinks, to exact within half a second */
 {float held[3];for(int i=0;i<3;i++)held[i]=out[i];prev=1e9f;exact=0;
  for(int n=0;n<36;n++){t+=1/72.;frame_axes(axes);for(int i=0;i<3;i++)m[i]=(rnd()-.5f)*.8f;
   vr_gun_anchor_update(&a,&A,1,axes,m,0,t,limit,out);float e=dist(out,m);assert(e<=prev+1e-6f);prev=e;if(e<1e-6f){exact=n;break;}}
  assert(prev<1e-6f&&exact>0);(void)held;}
 /* the other hand is its own entry (the model is mirrored there) */
 t+=1/72.;vr_gun_anchor_update(&a,&A,0,axes,m,1,t,limit,out);assert(out[0]==0&&out[1]==0&&out[2]==0);
 /* a gap past the limit is clamped; a broken one holds; broken time resets */
 {float big[3]={50,0,0},bad[3]={NAN,0,0};t+=1/72.;vr_gun_anchor_update(&a,&B,1,axes,big,0,t,limit,out);
  float s=sqrtf(out[0]*out[0]+out[1]*out[1]+out[2]*out[2]);assert(s<=limit*1.0001f);
  for(int n=0;n<200;n++){t+=1/72.;vr_gun_anchor_update(&a,&B,1,axes,big,0,t,limit,out);}
  s=sqrtf(out[0]*out[0]+out[1]*out[1]+out[2]*out[2]);assert(fabsf(s-limit)<1e-4f);
  float keep[3]={out[0],out[1],out[2]};t+=1/72.;vr_gun_anchor_update(&a,&B,1,axes,bad,0,t,limit,out);
  assert(isfinite(out[0])&&dist(out,keep)<1e-5f);
  assert(!vr_gun_anchor_update(&a,&B,1,axes,m,0,NAN,limit,out)&&out[0]==0);}
 /* many weapons: the cache wraps without overrunning */
 {int g[40];for(int n=0;n<40;n++){t+=1/72.;vr_gun_anchor_update(&a,&g[n],n&1,axes,m,0,t,limit,out);}assert(a.count==VR_GUN_ANCHOR_GRAPHS);}
 puts("PASS: anchor eases in after a first draw, is exact while tracked (2000 random poses), holds its gap in camera axes through animations,");
 puts("      restores each weapon's grip per hand, clamps and survives bad input, and its weapon cache wraps safely");
}
''')

# --- the production vr_anchor_gun with the game's math stubbed
types = r'''
typedef float real; typedef int boolean;
#define TRUE 1
#define FALSE 0
#define MAXIMUM_NODES_PER_ANIMATION 64
#define PIN(x,lo,hi) ((x)<(lo)?(lo):(x)>(hi)?(hi):(x))
typedef union { struct { real x,y,z; }; real n[3]; } real_point3d;
typedef union { struct { real i,j,k; }; real n[3]; } real_vector3d;
typedef struct { real scale; real_vector3d forward,left,up; real_point3d position; } real_matrix4x3;
struct animation_graph { struct { short count; } nodes; };
struct render_camera { real_point3d position; real_vector3d forward, up; };
static struct { struct render_camera weapon_camera; boolean weapon_camera_valid; real_vector3d weapon_pullback; real_point3d game_camera_position; } vr_render;
static real units=3.048f; static int hand=1, empty, pose_ok=1; static double now;
static float grip_p[3], hand_f[3]={1,0,0}, hand_u[3]={0,0,1};
static real vr_units_per_metre(void){return units;}
static int vr_weapon_hand(void){return hand;}
static int vr_hand_empty(void){return empty;}
static double vr_pose_time(void){return now;}
static int vr_hand_pose(int h,const float*c,float*p,float*f,float*u){(void)h;(void)c;if(!pose_ok)return 0;memcpy(p,grip_p,12);memcpy(f,hand_f,12);memcpy(u,hand_u,12);return 1;}
static void scale_vector3d(real_vector3d const *v,real s,real_vector3d *o){for(int i=0;i<3;i++)o->n[i]=v->n[i]*s;}
static void cross_product3d(real_vector3d const*a,real_vector3d const*b,real_vector3d*o){real_vector3d r={{a->j*b->k-a->k*b->j,a->k*b->i-a->i*b->k,a->i*b->j-a->j*b->i}};*o=r;}
'''
run('anchor_render', common + types + '#include "port/linux/game/vr_gun_anchor.h"\n' + fn(render, 'vr_length') +
    fn(render, 'vr_unit_vector') + fn(render, 'vr_anchor_gun') + r'''
static unsigned seed=11;
static float rnd(void){seed=seed*1664525u+1013904223u;return (float)((seed>>8)&0xffff)/65535.f;}
static void pose(real_vector3d*f,real_vector3d*u){real_vector3d a={{rnd()-.5f,rnd()-.5f,rnd()-.5f}},b={{rnd()-.5f,rnd()-.5f,rnd()-.5f}};
 vr_unit_vector(&a);real d=a.i*b.i+a.j*b.j+a.k*b.k;b.i-=d*a.i;b.j-=d*a.j;b.k-=d*a.k;vr_unit_vector(&b);*f=a;*u=b;}
/* a weapon's model: its wrist (node 3) and other nodes at fixed places in the weapon camera's frame */
static void place(real_matrix4x3*m,int count,const float local[][3]){real_vector3d f=vr_render.weapon_camera.forward,u=vr_render.weapon_camera.up,l;cross_product3d(&u,&f,&l);
 for(int n=0;n<count;n++)for(int i=0;i<3;i++)m[n].position.n[i]=vr_render.weapon_camera.position.n[i]+(local[n][0]*f.n[i]+local[n][1]*l.n[i]+local[n][2]*u.n[i])*units;}
static float gap(real_matrix4x3*m,const float t[3]){float s=0;for(int i=0;i<3;i++)s+=(m[3].position.n[i]-t[i])*(m[3].position.n[i]-t[i]);return sqrtf(s)/units;}
int main(void){
 struct animation_graph pistol={{6}},rifle={{6}};real_matrix4x3 m[6],before[6];real gun[3]={0,0,0};
 /* two weapons whose animations hold the hand in different places relative to the camera */
 const float pistol_local[6][3]={{0,0,0},{.1f,-.2f,-.1f},{.2f,-.15f,-.12f},{.33f,-.09f,-.08f},{.38f,-.09f,-.06f},{.50f,-.08f,-.02f}};
 const float rifle_local[6][3]={{0,0,0},{.1f,-.2f,-.1f},{.15f,-.15f,-.15f},{.22f,-.12f,-.16f},{.30f,-.10f,-.12f},{.60f,-.06f,-.05f}};
 vr_render.weapon_camera_valid=1;
 for(int n=0;n<3000;n++){
  const float(*local)[3]=(n/50)&1?rifle_local:pistol_local;struct animation_graph*g=(n/50)&1?&rifle:&pistol;real_vector3d f,u;
  now+=1/72.;pose(&f,&u);vr_render.weapon_camera.forward=f;vr_render.weapon_camera.up=u;
  /* the weapon camera where vr_weapon_view puts it: 20 cm behind, 12 cm above and 10 cm beside the grip */
  {real_vector3d l;cross_product3d(&u,&f,&l);float side=((n/100)&1)?-1.f:1.f;
   for(int i=0;i<3;i++){grip_p[i]=(rnd()-.5f)*10;vr_render.weapon_camera.position.n[i]=grip_p[i]+(-.20f*f.n[i]+.12f*u.n[i]+side*.10f*l.n[i])*units;}}
  pose(&f,&u);memcpy(hand_f,f.n,12);memcpy(hand_u,u.n,12);
  hand=(n/100)&1;gun[0]=(rnd()-.5f)*.2f;gun[1]=(rnd()-.5f)*.2f;gun[2]=(rnd()-.5f)*.2f;
  vr_render.weapon_pullback=(real_vector3d){{0,0,0}};
  if(n%5==0)for(int i=0;i<3;i++)vr_render.weapon_pullback.n[i]=-vr_render.weapon_camera.forward.n[i]*.1f*units;
  place(m,6,local);memcpy(before,m,sizeof m);
  /* after a weapon or hand change it settles (~0.2 s); then each frame is exact */
  vr_anchor_gun(m,g,3,0,gun);
  if(n%50<30)continue;
  {real_vector3d fw=vr_render.weapon_camera.forward,up,l;up=vr_render.weapon_camera.up;cross_product3d(&up,&fw,&l);vr_unit_vector(&l);cross_product3d(&fw,&l,&up);
   float out=hand==1?-1.f:1.f,t[3];
   for(int i=0;i<3;i++)t[i]=grip_p[i]-hand_f[i]*.075f*units+vr_render.weapon_pullback.n[i]+(fw.n[i]*gun[0]+up.n[i]*gun[1]+l.n[i]*out*gun[2])*units;
   assert(gap(m,t)<1e-4f);
   /* the whole model moves as one: the gun, hands and arms keep their shape */
   for(int k=0;k<6;k++)for(int i=0;i<3;i++)assert(fabsf((m[k].position.n[i]-before[k].position.n[i])-(m[3].position.n[i]-before[3].position.n[i]))<1e-4f);}
 }
 /* gun out: right hand to the right (-left), left hand to the left (+left) */
 for(hand=0;hand<2;hand++){real_vector3d fw={{1,0,0}},up={{0,0,1}};vr_render.weapon_camera.forward=fw;vr_render.weapon_camera.up=up;
  vr_render.weapon_camera.position=(real_point3d){{0,0,0}};memset(grip_p,0,12);hand_f[0]=1;hand_f[1]=hand_f[2]=0;
  real g0[3]={0,0,0},g1[3]={0,0,.05f};float y0,y1;
  for(int k=0;k<40;k++){now+=1/72.;place(m,6,pistol_local);vr_anchor_gun(m,&pistol,3,0,g0);}y0=m[3].position.y;
  now+=1/72.;place(m,6,pistol_local);vr_anchor_gun(m,&pistol,3,0,g1);y1=m[3].position.y;
  assert(fabsf((y1-y0)-(hand?-1:1)*.05f*units)<1e-4f);}
 /* no change without a gun, a tracked hand or a weapon camera */
 hand=1;place(m,6,pistol_local);memcpy(before,m,sizeof m);
 empty=1;vr_anchor_gun(m,&pistol,3,0,gun);assert(!memcmp(m,before,sizeof m));empty=0;
 pose_ok=0;vr_anchor_gun(m,&pistol,3,0,gun);assert(!memcmp(m,before,sizeof m));pose_ok=1;
 vr_render.weapon_camera_valid=0;vr_anchor_gun(m,&pistol,3,0,gun);assert(!memcmp(m,before,sizeof m));
 puts("PASS: 1200 checked random frames (pistol- and rifle-shaped animations, both hands, gun offsets, wall pullback): the gun hand's wrist lands");
 puts("      exactly where the empty hand's wrist would and the model moves rigidly; GUN OUT mirrors per hand; no gun/hand/camera = untouched");
}
''')

# --- the menu: every combined row identifies what it wrote, and shows the defaults
rows = re.findall(r'\{ "([A-Z +\-]+)", "[\w.]+", _vr_setting_multi, (\d+), \{ (.*?) \} \},', menu)
assert {r[0] for r in rows} == {'TURNING', 'WEAPONS', 'HOLSTERS', 'HANDS', 'ARM RUN'}, rows
domains = {'vr.arms': {'ik', 'hidden', 'animated'}, 'vr.hand_tracking': {'ik', 'floating'},
           'vr.weapons': {'locked', 'physical'}}
for label, count, values in rows:
    pairs = re.findall(r'\{ "([^"]+)", "([^"]+)" \}', values)
    assert len(pairs) == int(count) <= 12, label
    for _, value in pairs:
        for pair in value.split(';'):
            key, text = pair.split('=')
            kind = table[key][0]
            if kind == '_config_boolean': assert text in ('true', 'false'), pair
            elif kind == '_config_real': float(text)
            if key in domains: assert text in domains[key], pair
pages = ''.join(block(menu, f'static struct vr_menu_setting const {name}[] =', '};')
                for name in ('vr_menu_controls', 'vr_menu_body', 'vr_menu_vr', 'vr_menu_hands'))
cfg = ',\n'.join('{"%s",%d,"%s"}' % (k, {'_config_boolean': 0, '_config_integer': 1, '_config_real': 2}.get(v[0], 3), v[1])
                 for k, v in table.items())
run('menu', common + r'''
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1L)
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
struct cfg { const char *name; int type; char text[64]; } cfg[] = {
''' + cfg + r'''
};
static struct cfg *find(const char *n){for(size_t i=0;i<NUMBEROF(cfg);i++)if(!strcmp(cfg[i].name,n))return &cfg[i];printf("unknown %s\n",n);abort();}
static int config_boolean(const char*n){return !strcmp(find(n)->text,"true");}
static double config_real(const char*n){return atof(find(n)->text);}
static const char *config_string(const char*n){return find(n)->text;}
static int config_matches(const char*n,const char*t){struct cfg*c=find(n);switch(c->type){case 0:return config_boolean(n)==!strcmp(t,"true");
 case 2:return fabs(atof(c->text)-atof(t))<0.001;default:return !strcmp(c->text,t);}}
static int config_write_text(const char*n,const char*t){struct cfg*c=find(n);if(c->type==1)return 0;snprintf(c->text,64,"%s",t);return 1;}
''' + block(menu, 'enum\n{\n\t_vr_setting_boolean,', '};') + '#define VR_MENU_MAXIMUM_VALUES 12\n' +
    block(menu, 'struct vr_menu_setting\n{', '};') + pages + fn(menu, 'vr_menu_multi') + fn(menu, 'vr_menu_hand_angle') +
    fn(menu, 'vr_menu_value_index') + r'''
static struct { struct vr_menu_setting const *rows; size_t count; } pages[]={
 {vr_menu_controls,NUMBEROF(vr_menu_controls)},{vr_menu_body,NUMBEROF(vr_menu_body)},{vr_menu_vr,NUMBEROF(vr_menu_vr)},{vr_menu_hands,NUMBEROF(vr_menu_hands)}};
int main(void){
 int multi=0,choices=0;
 /* the defaults show as a choice, never CUSTOM */
 for(size_t p=0;p<NUMBEROF(pages);p++)for(size_t r=0;r<pages[p].count;r++){struct vr_menu_setting const*s=&pages[p].rows[r];
  if(s->value_count){if(vr_menu_value_index(s)==NONE){printf("default CUSTOM: %s\n",s->label);abort();}choices++;}}
 /* each value of a combined row, written, reads back as itself (from every other value) */
 for(size_t p=0;p<NUMBEROF(pages);p++)for(size_t r=0;r<pages[p].count;r++){struct vr_menu_setting const*s=&pages[p].rows[r];
  if(s->type!=_vr_setting_multi)continue;multi++;
  for(int from=0;from<s->value_count;from++)for(int to=0;to<s->value_count;to++){boolean w=TRUE;
   assert(vr_menu_multi(s->values[from].value,TRUE,&w)&&w);assert(vr_menu_value_index(s)==from);
   assert(vr_menu_multi(s->values[to].value,TRUE,&w)&&w);assert(vr_menu_value_index(s)==to);}}
 /* hand-set combinations are CUSTOM; a malformed value is refused */
 {struct vr_menu_setting const*hands=&vr_menu_body[1];boolean w=TRUE;
  vr_menu_multi("vr.arms=hidden;vr.hand_tracking=floating",TRUE,&w);assert(vr_menu_value_index(hands)==NONE);
  assert(!vr_menu_multi("vr.arms",FALSE,NULL));}
 /* both hands' angle reads the gun hand's side, mirrored for the left */
 {boolean w=TRUE;vr_menu_multi("vr.hand_right_yaw=12;vr.hand_left_yaw=-12;vr.hand_right_pitch=-70;vr.hand_left_pitch=-70",TRUE,&w);
  assert(vr_menu_hand_angle("yaw")==12&&vr_menu_hand_angle("pitch")==-70);
  vr_menu_multi("vr.left_handed=true",TRUE,&w);assert(vr_menu_hand_angle("yaw")==12&&vr_menu_hand_angle("pitch")==-70);}
 printf("PASS: %d menu choices show their defaults; %d combined rows round-trip every value pair; custom combos show CUSTOM; both-hands angles mirror\n",choices,multi);
}
''')

# --- left-handed controls are the right-handed ones in a mirror
host = r'''
#include <stdint.h>
#include "port/android/include/halo_android_abi.h"
enum { HAND_LOOSE, HAND_HELD, HAND_EMPTY };
static struct { struct { uint32_t hand_buttons[2], buttons; float trigger[2]; int64_t predicted_display_period; } frame;
 int layout_vr, weapon_hand, touch_layout, zoom_down, view_recentred, back_pulse, heading_valid, x_hold_switched, controls_mirrored,
 grip_held[2], in_holster, hand_state, physical; unsigned pad_buttons; float pad_trigger[2]; double x_held, grenade_pulse, view_held; } vr;
static int recentres, buzzes;
static int physical_weapons(void){return vr.physical;}
static void host_xr_recenter(void){recentres++;}
static void vr_haptic(int h,float a,float s){(void)h;(void)a;(void)s;buzzes++;}
'''
run('mirror', common + host + fn(frame, 'layout_controls') + r'''
static unsigned seed=3;
static unsigned rnd(void){seed=seed*1664525u+1013904223u;return seed>>8;}
int main(void){
 const unsigned bits[]={HALO_XR_HAND_SOUTH,HALO_XR_HAND_EAST,HALO_XR_HAND_WEST,HALO_XR_HAND_NORTH,HALO_XR_HAND_STICK,HALO_XR_HAND_BUMPER,HALO_XR_HAND_MENU,HALO_XR_HAND_VIEW};
 int frames=0;
 for(int run=0;run<400;run++){
  int touch=run&1,phys=(run>>1)&1,holster=(run>>2)&1,state=run%3;
  struct { unsigned out; float t0,t1; int rec; } a[60],b[60];
  unsigned sl[60],sr[60];float tl[60],tr[60];int gl[60],gr[60];
  for(int n=0;n<60;n++){sl[n]=sr[n]=0;for(int k=0;k<8;k++){if(rnd()%5==0)sl[n]|=bits[k];if(rnd()%5==0)sr[n]|=bits[k];}
   if(rnd()%3==0){sl[n]=n?sl[n-1]:0;sr[n]=n?sr[n-1]:0;} /* holds */
   tl[n]=(rnd()%100)/99.f;tr[n]=(rnd()%100)/99.f;gl[n]=rnd()&1;gr[n]=rnd()&1;}
  for(int side=0;side<2;side++){
   memset(&vr,0,sizeof vr);recentres=0;vr.layout_vr=1;vr.touch_layout=touch;vr.physical=phys;vr.in_holster=holster;vr.hand_state=state;
   vr.frame.predicted_display_period=13888889;vr.controls_mirrored=side;vr.weapon_hand=side?0:1;
   for(int n=0;n<60;n++){
    /* side 1: the same hands, but the left-handed player's are the other way round */
    vr.frame.hand_buttons[0]=side?sr[n]:sl[n];vr.frame.hand_buttons[1]=side?sl[n]:sr[n];
    vr.frame.trigger[0]=side?tr[n]:tl[n];vr.frame.trigger[1]=side?tl[n]:tr[n];
    vr.grip_held[0]=side?gr[n]:gl[n];vr.grip_held[1]=side?gl[n]:gr[n];
    layout_controls();
    if(side){b[n].out=vr.pad_buttons;b[n].t0=vr.pad_trigger[0];b[n].t1=vr.pad_trigger[1];b[n].rec=recentres;}
    else{a[n].out=vr.pad_buttons;a[n].t0=vr.pad_trigger[0];a[n].t1=vr.pad_trigger[1];a[n].rec=recentres;}}}
  for(int n=0;n<60;n++,frames++)assert(a[n].out==b[n].out&&a[n].t0==b[n].t0&&a[n].t1==b[n].t1&&a[n].rec==b[n].rec);
 }
 /* right-handed is unchanged: A jumps, B (stick) melee; left-handed: X jumps */
 memset(&vr,0,sizeof vr);vr.layout_vr=1;vr.weapon_hand=1;vr.frame.hand_buttons[1]=HALO_XR_HAND_SOUTH;layout_controls();assert(vr.pad_buttons==HALO_XR_BUTTON_A);
 memset(&vr,0,sizeof vr);vr.layout_vr=1;vr.weapon_hand=0;vr.controls_mirrored=1;vr.frame.hand_buttons[0]=HALO_XR_HAND_SOUTH;layout_controls();assert(vr.pad_buttons==HALO_XR_BUTTON_A);
 memset(&vr,0,sizeof vr);vr.layout_vr=1;vr.weapon_hand=0;vr.controls_mirrored=0;vr.frame.hand_buttons[1]=HALO_XR_HAND_SOUTH;layout_controls();assert(vr.pad_buttons==HALO_XR_BUTTON_A);
 printf("PASS: %d frames of random buttons, triggers and grips (touch/physical/holster/hand states): left-handed output equals the right-handed mirror image;\n",frames);
 puts("      right-handed and left-handed-with-standard-controls layouts are unchanged");
}
''')

# --- one-time migrations
run('migration', common + r'''
#include <stdarg.h>
static char tracking[32]="ik",mirror[32]="auto";static int left,applied,fail,writes;
static const char *config_string(const char*k){return !strcmp(k,"vr.hand_tracking")?tracking:mirror;}
static int config_boolean(const char*k){return !strcmp(k,"vr.left_handed")?left:applied;}
static int config_write_string(const char*k,const char*v){if(fail)return 0;writes++;snprintf(!strcmp(k,"vr.hand_tracking")?tracking:mirror,32,"%s",v);return 1;}
static int config_write_boolean(const char*k,int v){(void)k;if(fail)return 0;applied=v;return 1;}
static void platform_log(const char*f,...){(void)f;}
''' + fn(frame, 'migrate_handedness') + r'''
int main(void){
 /* a right-handed config: nothing changes but the mark */
 migrate_handedness();assert(applied&&!strcmp(mirror,"auto")&&writes==0);
 /* an existing left-handed player keeps the layout they learned, once */
 applied=0;left=1;migrate_handedness();assert(applied&&!strcmp(mirror,"off"));
 strcpy(mirror,"auto");migrate_handedness();assert(!strcmp(mirror,"auto"));
 /* test20c's floating_arms becomes floating (every run, idempotent) */
 strcpy(tracking,"floating_arms");migrate_handedness();assert(!strcmp(tracking,"floating"));
 /* a failed save retries next launch */
 applied=0;fail=1;migrate_handedness();assert(!applied);
 puts("PASS: handedness migration keeps existing left-handed controls standard once, leaves right-handed configs alone, retries failed saves; floating_arms -> floating");
}
''')
