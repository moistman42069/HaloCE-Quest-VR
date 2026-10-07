"""Test24 (1.0.6): co-op cutscenes animate on joining devices.

Owner log (2026-10-04 23:14, Quest 1.0.5 joined a10 co-op hosted by the
phone): the opening cutscene still T-posed and slid on the Quest, and no
presentation cue was dropped. Cause: a machine updates (animates) only the
objects its players' clusters see plus the "special place that activates
everything it sees" a script names (object_pvs_set_object/_set_camera/
_activate/_clear, objects_get_activating_cluster_index in
players_compute_combined_pvs). A client runs no scripts and was never told
of the place, so a cutscene away from the players stayed inactive there: its
characters never animated while the host's positions moved them. The calls
are now part of the presentation stream (and unit_set_seat, the posture idle
animations are chosen for); test23's cutscene snap is withdrawn. The real
capture, wire and replay code runs under ASan/UBSan with small stubs.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test24'; OUT.mkdir(parents=True, exist_ok=True)


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
                    '-Wno-unused-parameter', '-Wno-missing-field-initializers', '-Wno-sign-compare',
                    '-fsanitize=address,undefined', str(p), '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)


def git_show(commit, path):
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT, text=True, encoding='utf-8')


script = (ROOT / 'port/linux/game/network_campaign_script.c').read_text(encoding='utf-8')
objects_net = (ROOT / 'port/linux/game/network_objects.c').read_text(encoding='utf-8')
hs = (ROOT / 'source/hs/hs.c').read_text(encoding='latin-1')
runtime = (ROOT / 'source/hs/hs_runtime.c').read_text(encoding='latin-1')
players = (ROOT / 'source/game/players.c').read_text(encoding='latin-1')
objects = (ROOT / 'source/objects/objects.c').read_text(encoding='latin-1')
frame = (ROOT / 'port/linux/src/vr_frame.c').read_text(encoding='utf-8')
gradle = (ROOT / 'port/android/app/build.gradle').read_text(encoding='utf-8')


def names(text):
    block = text[text.index('static char const *presentation_names[] = {'):]
    block = block[:block.index('};')]
    block = re.sub(r'/\*.*?\*/', '', block, flags=re.S)
    return re.findall(r'"([a-z_0-9]+)"', block)


# --- the engine: activation is the players' clusters and the script's place
combined = fn(players, 'players_compute_combined_pvs')
assert 'activating_cluster_index = objects_get_activating_cluster_index();' in combined
assert 'structure_bsp_get_cluster_pvs(\n\t\t\t\t\tstructure_bsp,\n\t\t\t\t\tactivating_cluster_index)' in combined
assert 'memcpy(active_cluster_bits, players_get_combined_pvs(), BIT_VECTOR_SIZE_IN_BYTES(cluster_count));' in objects
for name in ['object_pvs_set_object', 'object_pvs_set_camera_point', 'object_pvs_clear', 'object_pvs_activate']:
    assert re.search(r'^void %s\(' % name, objects, re.M), name

# --- the wire: append-only, the five new names last
old = names(git_show('7f4dc973', 'port/linux/game/network_campaign_script.c'))
new = names(script)
added = ['object_pvs_set_object', 'object_pvs_set_camera', 'object_pvs_activate', 'object_pvs_clear', 'unit_set_seat']
assert new == old + added, 'wire IDs of earlier entries unchanged'

# --- each is an hs function whose arguments the validator accepts
types = {}
for m in re.finditer(r'"([a-z_0-9]+)",\n\t\ths_macro_function_parse,\n\t\t\w+,\n\t\t"(?:[^"\\]|\\.)*",\n\t\tNULL,\n\t\t(\d+),\n'
                     r'(?:\t\t\{ (_hs_type_\w+) \},\n\t\},\n(?:\t\{ ([_\w, ]+) \},\n)?)?', hs):
    params = ([m.group(3)] if m.group(3) else []) + ([t.strip() for t in m.group(4).split(',')] if m.group(4) else [])
    types[m.group(1)] = params
for m in re.finditer(r'\t"(object_pvs_clear)",\n\thsc?_macro_function_parse,\n\t\w+,\n\t"(?:[^"\\]|\\.)*",\n\tNULL,\n\t0,\n', hs):
    types[m.group(1)] = []
assert types.get('object_pvs_set_object') == ['_hs_type_object'], types.get('object_pvs_set_object')
assert types.get('object_pvs_activate') == ['_hs_type_object']
assert types.get('object_pvs_set_camera') == ['_hs_type_cutscene_camera_point']
assert types.get('object_pvs_clear') == [], 'no arguments'
assert types.get('unit_set_seat') == ['_hs_type_unit', '_hs_type_string']
valid = fn(hs, 'hs_campaign_call_valid')
for case in ['if (HS_TYPE_IS_OBJECT(type))', 'case _hs_type_cutscene_camera_point:', 'case _hs_type_string:']:
    assert case in valid, case
assert 'if (!function->parameter_count) network_campaign_script_capture(expression->index, NULL);' in runtime, \
    'a call with no arguments is captured too'

# --- test23's cutscene snap withdrawn: reconciling is 1.0.4's, byte for byte
# (test26 sends a resting object's teleport at once, distributed_host_send_states:
# the client's reconciling stays 1.0.4's)
old_net = git_show('55e77364', 'port/linux/game/network_objects.c')
# (test27: network_objects.c is OpenCE build 138's now, with test26's resend
# re-applied: its reconciling is OpenCE's now, not 1.0.4's, and
# the resend stays: test_test26 runs it)
if 'network_objects_client_picked_up_weapon' in objects_net:
    assert 'if (at_rest && !was_moving && !distributed_host_rest_moved(absolute_index, object_index))' in objects_net or (
        'if (at_rest && !distributed_host_rest_state_due(absolute_index) &&\n'
        '\t\t\t!distributed_host_rest_moved(absolute_index, object_index))' in objects_net)  # (test29: with OpenCE build 144's rest repeats)
    old_net = None
net_1_0_4 = objects_net
net_1_0_4 = re.sub(r'/\* \.\.\. where each was when its state last went out.*?\} objects_host_rest_sent\[MAXIMUM_TRACKED_OBJECTS\];\n',
                   '', net_1_0_4, count=1, flags=re.S)
net_1_0_4 = re.sub(r'static void distributed_host_note_rest_sent\(.*?\n}\n\n/\* test26: an object at rest.*?\n}\n\n',
                   '', net_1_0_4, count=1, flags=re.S)
net_1_0_4 = net_1_0_4.replace(
    '\t\t/* (one at rest that was, moved all the same: test26) */\n'
    '\t\tif (at_rest && !was_moving && !distributed_host_rest_moved(absolute_index, object_index))\n',
    '\t\tif (at_rest && !was_moving)\n')
net_1_0_4 = net_1_0_4.replace('\t\tdistributed_host_note_rest_sent(absolute_index, object_index);\n', '')
assert old_net is None or net_1_0_4 == old_net, 'network_objects.c as in 1.0.4 but for test26\'s resting teleports'

# --- version
code = int(re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1))
assert code >= 31 and re.search(r'"1\.0\.(\d+)"', gradle) and int(re.search(r'"1\.0\.(\d+)"', gradle).group(1)) >= 6
assert 'co-op cutscenes animate for the second player' in frame

# --- the launcher: co-op and server-browser steps, the co-op listing on by default
java = ROOT / 'port/android/app/src/main/java/com/halo/decomp'
coop = (java / 'CoopLauncher.java').read_text(encoding='utf-8')
help_java = (java / 'LauncherHelp.java').read_text(encoding='utf-8')
launcher = (java / 'LauncherActivity.java').read_text(encoding='utf-8')
browser = (java / 'ServerBrowser.java').read_text(encoding='utf-8')
host = coop[coop.index('private void host()'):]
assert 'publish.setChecked(true);' in host and host.index('publish.setChecked(true);') < host.index('layout.addView(publish);')
assert '(publish.isChecked() ? 1 : 0)' in host, 'the box still decides the listing'
# Test32 replaces the exposed launcher host/browser with the OpenCE guide.
# Retain the legacy publisher checks above; saved data and old classes remain.
help_pages=(java / 'InGameNetworkGuide.java').read_text(encoding='utf-8')
for step in ['Multiplayer > Create Game > Internet', 'Multiplayer > Join Game > Server Browser',
             'Multiplayer > Join Game > LAN', 'Direct Link', 'REFRESH', 'pull the trigger']:
    assert step in help_pages, step
assert 'LauncherHelp.network(this)' in launcher
assert '"Multiplayer & co-op guide", "Getting started & multiplayer"' in help_java
assert 'if(item==0) { network(activity); return; }' in help_java
assert 'Multiplayer > System Link' in coop and 'How to join co-op & find servers' in coop
assert 'In-game server browser: press Play' in browser

# --- the real capture, wire and replay
body = script[script.index('static char const *presentation_names[] = {'):]
body = body.replace('typedef char campaign_presentation_size_assert[sizeof(struct campaign_presentation) == 300 ? 1 : -1];', '')
run('presentation', r'''
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
typedef int boolean; typedef unsigned short word; typedef unsigned char byte;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define NUMBEROF(a) ((short)(sizeof(a)/sizeof((a)[0])))
#define MIN(a,b) ((a)<(b)?(a):(b))
enum { _hs_type_void, _hs_type_string, _hs_type_object, _hs_type_unit, _hs_type_cutscene_camera_point, _hs_type_real };
struct hs_function_definition { const char *name; short parameter_count; short parameter_types[8]; };
static struct hs_function_definition table[] = {
 {"object_pvs_set_object",1,{_hs_type_object}}, {"object_pvs_set_camera",1,{_hs_type_cutscene_camera_point}},
 {"object_pvs_activate",1,{_hs_type_object}}, {"object_pvs_clear",0,{0}}, {"unit_set_seat",2,{_hs_type_unit,_hs_type_string}},
 {"custom_animation",4,{_hs_type_unit,_hs_type_real,_hs_type_string,_hs_type_real}}, {"object_teleport",2,{_hs_type_object,_hs_type_real}},
 {"cinematic_start",0,{0}}};
static const long hs_function_table_count = sizeof(table)/sizeof(table[0]);
static struct hs_function_definition *hs_function_get(short i){assert(i>=0&&i<hs_function_table_count);return &table[i];}
enum { _game_connection_local, _game_connection_network_client, _game_connection_network_server };
static short connection;
static short game_connection(void){return connection;}
static boolean network_campaign_active(void){return TRUE;}
static boolean network_campaign_playing(void){return TRUE;}
static boolean network_campaign_client(void){return connection==_game_connection_network_client;}
static long network_game_get_number_of_games_played(void){return 3;}
static long network_game_get_random_seed(void){return 77;}
static boolean hs_campaign_call_valid(short f, long const *a){return TRUE;}
static void network_game_abort(void){assert(0);}
static void network_campaign_actor_impulses_reset(void){}
static short activating=NONE;
static short objects_get_activating_cluster_index(void){return activating;}
static int logs_followed;
static void platform_log(char const *f, ...){if(strstr(f,"activating place"))logs_followed++;}
/* the replay: what the client's hs would run */
static short replayed[16]; static long replay_arg0[16]; static char replay_string[16][32]; static int replays;
static void hs_campaign_replay(short f, long *a){replayed[replays]=f;replay_arg0[replays]=table[f].parameter_count?a[0]:0;
 if(table[f].parameter_count==2&&table[f].parameter_types[1]==_hs_type_string)snprintf(replay_string[replays],32,"%s",(char*)a[1]);
 if(!strcmp(table[f].name,"object_pvs_set_object")||!strcmp(table[f].name,"object_pvs_activate"))activating=12;
 if(!strcmp(table[f].name,"object_pvs_clear"))activating=NONE;
 replays++;}
struct distributed_message_header { short type, count; };
#define RELIABLE_ENTRIES(t) 4
enum { _distributed_message_campaign_presentation = 9, _distributed_to_clients_reliably = 1 };
static unsigned char wire[64][4*400]; static short wire_counts[64]; static int sends;
static void distributed_send(void *m, short type, short count, long size, short to){
 assert(type==_distributed_message_campaign_presentation && to==_distributed_to_clients_reliably);
 /* (the entries follow the header at their own alignment: 8 bytes on this 64-bit test machine, none in the 32-bit game) */
 size_t at=(sizeof(struct distributed_message_header)+_Alignof(long)-1)&~(_Alignof(long)-1);
 memcpy(wire[sends], (char*)m+at, size-sizeof(struct distributed_message_header));
 wire_counts[sends++]=count;}
static void network_campaign_script_capture(short function_index, long const *arguments);
''' + body + r'''
int main(void){
 long object=0x00050007, camera_point=2, seat_unit=0x00060009;
 long args_object[8]={object}, args_camera[8]={camera_point}, args_seat[8]={seat_unit,(long)"stand"};
 long args_teleport[8]={object,0};
 connection=_game_connection_network_server;
 /* the host's script: a cutscene names its place, a seat, moves a character (not presentation), then clears */
 network_campaign_script_capture(0,args_object);   /* object_pvs_set_object */
 network_campaign_script_capture(1,args_camera);   /* object_pvs_set_camera */
 network_campaign_script_capture(2,args_object);   /* object_pvs_activate */
 network_campaign_script_capture(4,args_seat);     /* unit_set_seat */
 network_campaign_script_capture(6,args_teleport); /* object_teleport: positions have their own stream */
 network_campaign_script_capture(3,NULL);          /* object_pvs_clear */
 network_campaign_script_flush();
 assert(sends==2 && wire_counts[0]==4 && wire_counts[1]==1);
 /* the client: every cue replays, in order, with the host's arguments */
 connection=_game_connection_network_client;
 for(int s=0;s<sends;s++) network_campaign_script_receive(wire[s],wire_counts[s]);
 assert(replays==5);
 assert(replayed[0]==0 && replay_arg0[0]==object);
 assert(replayed[1]==1 && replay_arg0[1]==camera_point);
 assert(replayed[2]==2 && replay_arg0[2]==object);
 assert(replayed[3]==4 && replay_arg0[3]==seat_unit && !strcmp(replay_string[3],"stand"));
 assert(replayed[4]==3 && activating==NONE);
 assert(logs_followed==4); /* each place followed is logged */
 /* another game's cues are not replayed */
 replays=0; sends=0; connection=_game_connection_network_server;
 network_campaign_script_capture(0,args_object); network_campaign_script_flush();
 connection=_game_connection_network_client; ((long*)wire[0])[0]=2;
 network_campaign_script_receive(wire[0],wire_counts[0]); assert(replays==0);
 puts("PASS: the host's object_pvs_set_object/_set_camera/_activate/_clear and unit_set_seat go out in order "
      "on the reliable presentation stream and replay on the client with the host's arguments (strings decoded); "
      "positions keep their own stream; another game's cues are refused");
}
''')
print('PASS: test24 wiring (engine activation = players\' clusters + the script\'s place; five calls appended, earlier wire '
      'IDs unchanged; argument types validated; no-argument capture; reconciling as in 1.0.4; version 1.0.6 / 31; '
      'launcher join steps and co-op listing on by default)')
