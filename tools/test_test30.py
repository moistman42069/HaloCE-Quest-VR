"""Test30 (1.0.12): in VR the main menu's X did nothing, so a profile could
not be deleted; the launcher's co-op host gets a server name.

The gameplay button table (vr.button_*) gave the menus no Xbox X: the
Quest's X throws a grenade, and the game's X (use, reload) is on the Quest's
B, which in the menus is also the pointer's back. In the menus the Quest's
face buttons are now the Xbox's of the same letter. Run with
python3 tools/test_test30.py.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test30'; OUT.mkdir(parents=True, exist_ok=True)


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


def run(name, source):
    p = OUT / (name + '.c'); p.write_text(source)
    subprocess.run(['clang', '-std=gnu11', '-O1', '-Wall', '-Wno-unused-function', '-Wno-unused-variable',
                    '-fsanitize=address,undefined', '-I', str(ROOT), str(p), '-lm', '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)


frame = read('port/linux/src/vr_frame.c')
session = read('port/linux/game/network_campaign_session.c')
coop = read('port/android/app/src/main/java/com/halo/decomp/CoopLauncher.java')
gradle = read('port/android/app/build.gradle')
package = read('tools/package-quest.py')

# --- 1. the menus' face buttons: the Xbox's of the same letter (X deletes a profile); one back; no grenade
layout = fn(frame, 'layout_controls')
block = between(layout, '\t/* test30: in the menus', '\t/* the off hand\'s trigger zooms */')
assert layout.index('buttons |= touch_buttons(right, left, seconds, &grenade_down);') < layout.index(block[:40]), 'after the table'
assert layout.index(block[:40]) < layout.index('vr.pad_buttons = buttons;') < layout.index('if (vr.touch_layout && grenade_down)')
run('menu_letters', r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "port/android/include/halo_android_abi.h"
static struct { struct halo_xr_frame frame; int menus_active, touch_layout, controls_mirrored, x_hold_switched;
 double grenade_pulse, x_held; } vr;
static unsigned int run(unsigned int buttons, unsigned int right, unsigned int left, int *grenade){
 int grenade_down = *grenade;
 vr.frame.hand_buttons[1]=right; vr.frame.hand_buttons[0]=left;
''' + block + r'''
 *grenade = grenade_down; return buttons; }
int main(void){
 const unsigned int A=HALO_XR_BUTTON_A, B=HALO_XR_BUTTON_B, X=HALO_XR_BUTTON_X, Y=HALO_XR_BUTTON_Y, BLACK=HALO_XR_BUTTON_BLACK;
 const unsigned int S=HALO_XR_HAND_SOUTH, E=HALO_XR_HAND_EAST;
 int g;
 vr.touch_layout=1; vr.menus_active=1;
 /* the report: the Quest's X in a menu (the gameplay table: a grenade, no Xbox button) is the Xbox's X */
 g=1; vr.grenade_pulse=0.1; assert(run(0, 0, S, &g)==X && g==0 && vr.grenade_pulse==0.0 && vr.x_hold_switched==1);
 /* A is A; Y is Y; B (the pointer's back) is nothing else: one back, and no X from the table's use/reload */
 g=0; assert(run(0, S, 0, &g)==A); assert(run(0, 0, E, &g)==Y); assert(run(X, E, 0, &g)==0);
 /* the table's other buttons the face buttons gave are replaced; the rest (Start, sticks, Back) kept */
 assert(run(BLACK|HALO_XR_BUTTON_START|HALO_XR_BUTTON_BACK, 0, 0, &g)==(HALO_XR_BUTTON_START|HALO_XR_BUTTON_BACK));
 /* left-handed (mirrored): the pointer's back is the left's upper (Y); B is the Xbox's B */
 vr.controls_mirrored=1; assert(run(0, E, 0, &g)==B); assert(run(0, 0, E, &g)==0); assert(run(0, 0, S, &g)==X);
 vr.controls_mirrored=0;
 /* in play (no menu), or another controller's layout: the table's buttons and the grenade as before */
 vr.menus_active=0; g=1; vr.grenade_pulse=0.1; assert(run(X|BLACK, 0, S, &g)==(X|BLACK) && g==1 && vr.grenade_pulse==0.1);
 vr.menus_active=1; vr.touch_layout=0; g=1; assert(run(X|BLACK, 0, S, &g)==(X|BLACK) && g==1);
 puts("PASS: in the menus the Quest's X is the Xbox's X (a profile deleted), A A, Y Y, B the pointer's back alone "
      "(left-handed: Y back, B the Xbox's B); no grenade from a menu; in play and on other controllers as before");
}
''')
pointer = fn(frame, 'vr_ui_pointer')
assert 'vr.menus_active = menus_active != 0;' in pointer
assert 'back_down = (vr.frame.hand_buttons[vr.controls_mirrored ? 0 : 1] & HALO_XR_HAND_EAST) != 0;' in pointer, 'the back the block leaves out'

# --- 2. the co-op host's server name: format 3, the name on its own line
reader = fn(session, 'coop_request_read')
limits = re.search(r'^enum\n\{\n\tCOOP_MINIMUM_PLAYERS.*?^\};\n', session, re.M | re.S).group(0)
assert 'COOP_NAME_LENGTH = 15,' in limits
run('coop_name', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define VALID_INDEX(i,n) ((i)>=0&&(i)<(long)(n))
static char const *missions[] = {"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"};
''' + limits + r'''
static boolean list_publicly; static short mission, difficulty, most_players;
static char host_name[COOP_NAME_LENGTH + 1];
''' + reader + r'''
int main(void){
 /* named */
 assert(coop_request_read("3 4 2 1 8\nFireteam Q\n") && mission==4 && difficulty==2 && list_publicly==1 && most_players==8 && !strcmp(host_name,"Fireteam Q"));
 assert(coop_request_read("3 0 1 0 128\r\nABCDEFGHIJKLMNO\r\n") && most_players==128 && !strcmp(host_name,"ABCDEFGHIJKLMNO"));   /* 15, CRLF */
 assert(coop_request_read("3 0 1 0 4\n~!@# $%^&*()_+{\n") && !strcmp(host_name,"~!@# $%^&*()_+{"));
 /* no name: the device's, as before (empty line, no line) */
 assert(coop_request_read("3 0 1 0 4\n\n") && host_name[0]==0); assert(coop_request_read("3 0 1 0 4\n") && host_name[0]==0);
 assert(coop_request_read("3 0 1 0 4") && host_name[0]==0);
 /* refused: 16 characters, a control character, something after the name, a malformed line */
 assert(!coop_request_read("3 0 1 0 4\nABCDEFGHIJKLMNOP\n") && host_name[0]==0);
 assert(!coop_request_read("3 0 1 0 4\nbad\tname\n")); assert(!coop_request_read("3 0 1 0 4\nname\nmore\n"));
 assert(!coop_request_read("3 0 1 0 4\nn\x01\n")); assert(!coop_request_read("3 0 1 0 4 x\nname\n"));
 assert(!coop_request_read("3 0 1 0 1\nname\n")); assert(!coop_request_read("3 10 1 0 4\nname\n"));
 /* \xe9 (not ASCII) refused */
 assert(!coop_request_read("3 0 1 0 4\ncaf\xe9\n"));
 /* the earlier formats as before, no name; nothing after their line */
 assert(coop_request_read("2 4 2 1 8\n") && most_players==8 && host_name[0]==0);
 assert(coop_request_read("1 0 1 0\n") && most_players==COOP_FORMAT_1_PLAYERS && host_name[0]==0);
 assert(!coop_request_read("2 4 2 1 8\nname\n")); assert(!coop_request_read("4 0 1 0 4\nname\n"));
 /* a line too long */
 { char t[200]; memset(t,'1',150); t[0]='3'; t[1]=' '; t[150]=0; assert(!coop_request_read(t)); }
 puts("PASS: the co-op host request's server name (format 3): 15 printable characters at most, CRLF or LF, none for the "
      "device's; control characters, non-ASCII, 16, extra lines refused; formats 1 and 2 as before");
}
''')
update = fn(session, 'network_campaign_session_update')
configured = between(update, '\tif (!configured)\n', '\tif (!player_added && menu_loaded')
assert configured.index('game->name[index] = (wchar_t)(unsigned char)host_name[index];') < \
    configured.index('network_game_server_port_set_cooperative_players(most_players);'), 'named before the game data goes out'
assert 'if (host_name[0] && game)' in configured and 'game->name[index] = 0;' in configured
assert 'host_name[0] = 0;' in fn(session, 'network_campaign_session_end')

# the launcher: an optional name, validated as the game does, remembered, sent as format 3
assert 'static final int NAME_LENGTH = 15;' in coop
valid = re.search(r'static boolean validName\(String name\) \{.*?\n    \}\n', coop, re.S).group(0)
java = OUT / 'NameCheck.java'
java.write_text('public class NameCheck {\n static final int NAME_LENGTH = 15;\n ' + valid + r'''
 static void check(boolean b){ if(!b) throw new AssertionError(); }
 public static void main(String[] a){
  check(validName("")); check(validName("Fireteam Q")); check(validName("ABCDEFGHIJKLMNO")); check(validName("~!@# $%^&*()_+{"));
  check(!validName("ABCDEFGHIJKLMNOP")); check(!validName("café")); check(!validName("a\tb")); check(!validName("a\nb")); check(!validName(null));
  System.out.println("PASS: the launcher takes the names the game takes (printable ASCII, 15 at most, empty for the device's)");
 }
}
''')
subprocess.run(['javac', '-d', str(OUT), str(java)], check=True)
subprocess.run(['java', '-cp', str(OUT), 'NameCheck'], check=True)
host = fn(coop, 'host') if False else coop
assert 'out.write(("3 " + selected + " " + difficulty.getSelectedItemPosition() + " "' in coop
assert '+ name + "\\n").getBytes(StandardCharsets.UTF_8));' in coop
assert 'String name = serverName.getText().toString().trim();' in coop and 'if (!validName(name)) {' in coop
assert coop.index('if (!validName(name)) {') < coop.index('File request = new File(root, "coop_host.txt")'), 'checked before writing'
assert 'getSharedPreferences("coop-host", 0).edit().putString("server_name", name)' in coop
print('PASS: the launcher\'s Host campaign has an optional server name, checked, remembered and sent (format 3)')

# --- 3. version, identity, package markers
assert int(re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1)) >= 38
assert int(re.search(r': "1\.0\.(\d+)(?:-test\d+[a-z]?)?"', gradle).group(1)) >= 12
assert 'HaloCE Quest test30 candidate 1.0.12 (' in frame
assert 'candidate_at_least(args.label, 30)' in package
print('PASS: test30 wiring (version 1.0.12 / 38, identity, package markers)')
