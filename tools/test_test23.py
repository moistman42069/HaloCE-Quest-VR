"""Test23 (1.0.5): co-op cutscenes on campaign clients, and the Quest's
remappable buttons with the grenade on X.

Owner logs (2026-10-04, Quest 22:02:26 joined as client, phone 21:59:28
hosting, both 1.0.4): in co-op a10's opening cutscene the characters T-posed
and slid on the Quest while the hosting phone was right. Owner report: with
locked weapons the grip threw grenades; the grenade belongs on the left X
button, the grip neutral, every action remappable with a reset. Production
functions run under ASan/UBSan with small stubs; no headset or game data is
used. Run under Linux/WSL with clang.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test23'; OUT.mkdir(parents=True, exist_ok=True)


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def table(text, name):
    m = re.search(r'^static const [\w *]+\b' + re.escape(name) + r'\[[^\]]*\] =\n\{.*?\n\};\n', text, re.M | re.S)
    assert m, name
    return m.group(0)


def run(name, text):
    p = OUT / (name + '.c'); p.write_text(text)
    subprocess.run(['clang', '-std=gnu11', '-O1', '-Wall', '-Wextra', '-Wno-unused-function', '-Wno-unused-variable',
                    '-Wno-unused-parameter', '-Wno-missing-field-initializers', '-Wno-missing-braces',
                    '-fsanitize=address,undefined', '-I', str(ROOT), str(p), '-lm', '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)


frame = (ROOT / 'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
vr_h = (ROOT / 'port/linux/src/vr.h').read_text(encoding='utf-8')
menu = (ROOT / 'port/linux/game/vr_menu.c').read_text(encoding='utf-8')
config = (ROOT / 'port/linux/src/port_config.c').read_text(encoding='utf-8')
objects = (ROOT / 'port/linux/game/network_objects.c').read_text(encoding='utf-8')
script = (ROOT / 'port/linux/game/network_campaign_script.c').read_text(encoding='utf-8')
gradle = (ROOT / 'port/android/app/build.gradle').read_text(encoding='utf-8')

# --- co-op cutscenes: the dropped-cue log (test23's snap was withdrawn in test24, test_test24)
receive = fn(script, 'network_campaign_script_receive')
assert 'client dropped presentation' in receive and '++dropped <= 8 || dropped % 100 == 0' in receive
assert 'hs_campaign_replay(function, entry.arguments);' in receive, 'valid cues replay as before'

# --- version: 1.0.5 / 30 or later
code = int(__import__('re').search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1))
assert code >= 30
assert 'remappable Quest buttons with the grenade on X' in frame

# --- the buttons: settings, defaults, wiring
for key, default in [('jump', 'a'), ('action', 'b'), ('melee', 'right_stick'), ('crouch', 'left_stick'),
                     ('switch_weapon', 'y'), ('grenade', 'x'), ('switch_grenade', 'hold')]:
    assert re.search(r'"vr\.button_%s", _config_string, "\\"%s\\""' % (key, default), config), key
layout = fn(frame, 'layout_controls')
assert 'vr.grip_held' not in layout, 'the locked gun\'s grip no longer throws grenades in the layout'
assert 'buttons |= touch_buttons(right, left, seconds, &grenade_down);' in layout
assert 'if (vr.touch_layout && grenade_down)' in layout
legacy = layout[layout.index('\telse\n\t{'):layout.index('/* the off hand\'s trigger zooms */')]
for line in ['if (right & HALO_XR_HAND_SOUTH) buttons |= HALO_XR_BUTTON_A;', 'if (right & HALO_XR_HAND_EAST) buttons |= HALO_XR_BUTTON_X;',
             'if (right & HALO_XR_HAND_WEST) buttons |= HALO_XR_BUTTON_BLACK;', 'if (right & HALO_XR_HAND_NORTH) buttons |= HALO_XR_BUTTON_Y;',
             'if (right & HALO_XR_HAND_STICK) buttons |= HALO_XR_BUTTON_B;', 'if (left & HALO_XR_HAND_STICK) buttons |= HALO_XR_BUTTON_LEFT_THUMB;',
             'vr.grenade_pulse = 0.1;']:
    assert line in legacy, 'other controllers keep their layout: ' + line
assert '{ "BUTTONS", vr_menu_buttons, NUMBEROF(vr_menu_buttons) },' in menu
assert 'that button does both' in frame

enums = re.search(r'enum\n\{\n\tVR_BUTTON_ACTION_JUMP,.*?VR_BUTTON_SOURCES\n\};\n', vr_h, re.S).group(0)
names = table(frame, 'button_action_keys') + table(frame, 'button_source_values') + table(frame, 'button_defaults') + \
    fn(frame, 'vr_button_action_key') + fn(frame, 'vr_button_default') + fn(frame, 'vr_button_source_value') + \
    fn(frame, 'vr_button_source_of')

run('buttons', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "port/android/include/halo_android_abi.h"
''' + enums + r'''
static struct { int grip_held[2], weapon_hand, in_holster, button_source[VR_BUTTON_ACTIONS], x_hold_switched;
	double x_held, grenade_pulse; } vr;
static int physical;
static int physical_weapons(void){return physical;}
''' + names + fn(frame, 'touch_source_down') + fn(frame, 'touch_buttons') + r'''
#define S HALO_XR_HAND_SOUTH
#define E HALO_XR_HAND_EAST
#define K HALO_XR_HAND_STICK
static void defaults(void){for(int a=0;a<VR_BUTTON_ACTIONS;a++) vr.button_source[a]=vr_button_default(a);
	vr.x_held=vr.grenade_pulse=0; vr.x_hold_switched=0; vr.grip_held[0]=vr.grip_held[1]=0; vr.in_holster=0;}
/* the Quest's layout before 1.0.5, all but the grenade (the left X switched
grenades on a press with locked weapons; the grip threw) */
static unsigned legacy(unsigned right, unsigned left){unsigned b=0;
	if(right&S)b|=HALO_XR_BUTTON_A; if(right&E)b|=HALO_XR_BUTTON_X; if(right&K)b|=HALO_XR_BUTTON_B;
	if(left&K)b|=HALO_XR_BUTTON_LEFT_THUMB; if(left&E)b|=HALO_XR_BUTTON_Y; return b;}
static unsigned frame_(unsigned right, unsigned left, int *g){*g=0; return touch_buttons(right,left,1.0/72,g);}
int main(void){
 int g; unsigned b;
 vr.weapon_hand=1;
 /* defaults: every combination of A, B, Y and the sticks does what it did */
 for(physical=0;physical<2;physical++) for(unsigned m=0;m<32;m++){
	unsigned right=(m&1?S:0)|(m&2?E:0)|(m&4?K:0), left=(m&8?E:0)|(m&16?K:0);
	defaults(); b=frame_(right,left,&g); assert(b==legacy(right,left) && !g && vr.grenade_pulse==0);}
 /* locked weapons: the grip does nothing (it threw a grenade); at a holster it draws, elsewhere */
 physical=0; defaults(); vr.grip_held[1]=1; for(int i=0;i<200;i++){b=frame_(0,0,&g); assert(!b && !g);}
 assert(vr.grenade_pulse==0);
 /* X: a tap throws once let go, a hold of 0.4 s switches grenades once and throws nothing, either weapon mode */
 for(physical=0;physical<2;physical++){
	defaults(); for(int i=0;i<5;i++){b=frame_(0,S,&g); assert(!b&&!g);} assert(vr.grenade_pulse==0);
	frame_(0,0,&g); assert(vr.grenade_pulse==0.1); vr.grenade_pulse=0;
	int switched=0; for(int i=0;i<72;i++){b=frame_(0,S,&g); switched+=(b&HALO_XR_BUTTON_BLACK)!=0;}
	assert(switched==1); frame_(0,0,&g); assert(vr.grenade_pulse==0);}
 /* the grenade on the grip (the layout before 1.0.5): throws while held with locked
 weapons only, away from the holsters; X then switches grenades on a press */
 physical=0; defaults(); vr.button_source[VR_BUTTON_ACTION_GRENADE]=VR_BUTTON_SOURCE_GRIP;
 vr.button_source[VR_BUTTON_ACTION_SWITCH_GRENADE]=VR_BUTTON_SOURCE_X;
 vr.grip_held[1]=1; b=frame_(0,0,&g); assert(g && !b);
 vr.in_holster=1; frame_(0,0,&g); assert(!g); vr.in_holster=0;
 vr.grip_held[1]=0; vr.grip_held[0]=1; frame_(0,0,&g); assert(!g); vr.grip_held[0]=0;
 b=frame_(0,S,&g); assert(b==HALO_XR_BUTTON_BLACK && !g);
 physical=1; vr.grip_held[1]=1; frame_(0,0,&g); assert(!g); physical=0;
 /* the grip on a grenade with "hold": the grip cannot be held to switch, so it throws while held */
 defaults(); vr.button_source[VR_BUTTON_ACTION_GRENADE]=VR_BUTTON_SOURCE_GRIP; vr.grip_held[1]=1;
 frame_(0,0,&g); assert(g); assert(vr.x_held==0);
 /* remapped: jump on X, the grenade on A; none does nothing */
 defaults(); vr.button_source[VR_BUTTON_ACTION_JUMP]=VR_BUTTON_SOURCE_X; vr.button_source[VR_BUTTON_ACTION_GRENADE]=VR_BUTTON_SOURCE_A;
 b=frame_(0,S,&g); assert(b==HALO_XR_BUTTON_A); b=frame_(S,0,&g); assert(b==0); frame_(0,0,&g); assert(vr.grenade_pulse==0.1);
 defaults(); vr.button_source[VR_BUTTON_ACTION_MELEE]=VR_BUTTON_SOURCE_NONE; b=frame_(K,0,&g); assert(b==0);
 /* the settings' names: known values, an unknown value falls back to the default */
 for(int a=0;a<VR_BUTTON_ACTIONS;a++){int d=vr_button_default(a);
	assert(vr_button_source_of(vr_button_source_value(d),-1)==d); assert(vr_button_source_of("typo",d)==d);
	assert(vr_button_source_of(NULL,d)==d);}
 assert(vr_button_default(VR_BUTTON_ACTION_GRENADE)==VR_BUTTON_SOURCE_X);
 assert(!strcmp(vr_button_action_key(VR_BUTTON_ACTION_GRENADE),"vr.button_grenade"));
 puts("PASS: Quest buttons as before (A jump, B action/reload, Y switch weapon, sticks melee/crouch) in either weapon mode; "
      "the locked gun's grip throws nothing; X taps throw and holds switch grenades; the grip, if chosen, throws only "
      "with locked weapons away from the holsters; remapped buttons follow the table; unknown values keep defaults");
}
''')

run('menu_buttons', r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define NONE (-1)
typedef int boolean;
#define TRUE 1
#define FALSE 0
''' + enums + names + r'''
static char values[VR_BUTTON_ACTIONS][32];
static int key_index(const char *k){for(int a=0;a<VR_BUTTON_ACTIONS;a++) if(!strcmp(k,vr_button_action_key(a))) return a; assert(0); return 0;}
static const char *config_string(const char *k){return values[key_index(k)];}
static boolean config_write_string(const char *k, const char *v){strcpy(values[key_index(k)],v); return TRUE;}
static void platform_log(const char *f, ...){(void)f;}
''' + fn(menu, 'vr_menu_button_action') + fn(menu, 'vr_menu_button_source') + fn(menu, 'vr_menu_button_set') + r'''
static void reset(void){for(int a=0;a<VR_BUTTON_ACTIONS;a++) strcpy(values[a],vr_button_source_value(vr_button_default(a)));}
static int src(int a){return vr_menu_button_source(a);}
static void unique(void){for(int a=0;a<VR_BUTTON_ACTIONS;a++) for(int b=a+1;b<VR_BUTTON_ACTIONS;b++){
	int s=src(a); if(s!=VR_BUTTON_SOURCE_NONE && s!=VR_BUTTON_SOURCE_HOLD) assert(src(b)!=s);}}
int main(void){
 reset(); unique();
 /* jump onto X: the grenade takes jump's old A */
 vr_menu_button_set(VR_BUTTON_ACTION_JUMP,VR_BUTTON_SOURCE_X);
 assert(src(VR_BUTTON_ACTION_JUMP)==VR_BUTTON_SOURCE_X && src(VR_BUTTON_ACTION_GRENADE)==VR_BUTTON_SOURCE_A); unique();
 /* the grenade onto the grip: switching grenades takes its old button (the old locked layout) */
 reset(); vr_menu_button_set(VR_BUTTON_ACTION_GRENADE,VR_BUTTON_SOURCE_GRIP);
 assert(src(VR_BUTTON_ACTION_GRENADE)==VR_BUTTON_SOURCE_GRIP && src(VR_BUTTON_ACTION_SWITCH_GRENADE)==VR_BUTTON_SOURCE_X); unique();
 /* and back onto X: switching grenades returns to holding it */
 vr_menu_button_set(VR_BUTTON_ACTION_GRENADE,VR_BUTTON_SOURCE_X);
 assert(src(VR_BUTTON_ACTION_GRENADE)==VR_BUTTON_SOURCE_X && src(VR_BUTTON_ACTION_SWITCH_GRENADE)==VR_BUTTON_SOURCE_HOLD); unique();
 /* switching grenades onto the grenade's X: the grenade is left with no button (hold is no button) */
 reset(); vr_menu_button_set(VR_BUTTON_ACTION_SWITCH_GRENADE,VR_BUTTON_SOURCE_X);
 assert(src(VR_BUTTON_ACTION_SWITCH_GRENADE)==VR_BUTTON_SOURCE_X && src(VR_BUTTON_ACTION_GRENADE)==VR_BUTTON_SOURCE_NONE); unique();
 /* none never displaces */
 reset(); vr_menu_button_set(VR_BUTTON_ACTION_MELEE,VR_BUTTON_SOURCE_NONE);
 for(int a=0;a<VR_BUTTON_ACTIONS;a++) if(a!=VR_BUTTON_ACTION_MELEE) assert(src(a)==vr_button_default(a));
 /* any sequence of menu changes leaves no button with two actions */
 srand(23); reset();
 for(int i=0;i<20000;i++){int a=rand()%VR_BUTTON_ACTIONS, s=rand()%VR_BUTTON_SOURCES;
	if(s==VR_BUTTON_SOURCE_HOLD && a!=VR_BUTTON_ACTION_SWITCH_GRENADE) s=VR_BUTTON_SOURCE_NONE;
	vr_menu_button_set(a,s); unique(); assert(src(a)==s);}
 /* the grenade onto a grip jump had: jump takes X, so switching grenades stays on holding */
 reset(); vr_menu_button_set(VR_BUTTON_ACTION_JUMP,VR_BUTTON_SOURCE_GRIP); vr_menu_button_set(VR_BUTTON_ACTION_GRENADE,VR_BUTTON_SOURCE_GRIP);
 assert(src(VR_BUTTON_ACTION_JUMP)==VR_BUTTON_SOURCE_X && src(VR_BUTTON_ACTION_SWITCH_GRENADE)==VR_BUTTON_SOURCE_HOLD); unique();
 puts("PASS: a menu change swaps a taken button, the grip-grenade restores the old locked layout and back, "
      "and 20,000 random changes never leave one button with two actions");
}
''')
print('PASS: test23 wiring (dropped-cue log, version 1.0.5 / 30 or later, '
      'button settings, legacy layout for other controllers, BUTTONS page)')
