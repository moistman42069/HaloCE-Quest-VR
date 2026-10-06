"""Test27 (1.0.9): this app plays OpenCE's netcode (build 138, network 20), its
co-op included, hosting and joining with OpenCE's players and its browsers.

Evidence (kept private): the live community directory (halo.milenko.org,
2026-10-05/06) lists OpenCE's co-op beside multiplayer: game engine 0 on a
campaign map, network 17 to 20, up to 32 players; OpenCE publishes its games
through signed listings on MQTT brokers (p2p_lobby.c, opence.milenko.org
first), which the directory mirrors. Its co-op is its native netcode at that
version (exact match), so joining it means speaking it: this app's own
two-player co-op protocol (CE01/CE02, 1.0.0-1.0.8) and its v9-11 window are
retired. Networking files are OpenCE build 138's with this app's additions
named below; the co-op modules are build 138's byte for byte (hashes).
Run with python3 tools/test_test27.py.
"""
from pathlib import Path
import hashlib, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test27'; OUT.mkdir(parents=True, exist_ok=True)


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def read(path, encoding='utf-8'):
    return (ROOT / path).read_text(encoding=encoding)


def run(name, text):
    p = OUT / (name + '.c'); p.write_text(text)
    subprocess.run(['clang', '-std=gnu11', '-O1', '-Wall', '-Wextra', '-Wno-unused-function', '-Wno-unused-variable',
                    '-Wno-unused-parameter', '-fsanitize=address,undefined', '-I', str(ROOT), str(p), '-o', str(OUT / name)],
                   check=True)
    subprocess.run([str(OUT / name)], check=True)


java = 'port/android/app/src/main/java/com/halo/decomp/'
limits = read('port/linux/include/halo_port_limits.h')
distributed_h = read('port/linux/game/network_distributed.h')
distributed_c = read('port/linux/game/network_distributed.c')
objects_net = read('port/linux/game/network_objects.c')
manager = read('source/networking/network_client_manager.c', 'latin-1')
server = read('source/networking/network_server_manager.c', 'latin-1')
session = read('port/linux/game/network_campaign_session.c')
campaign_c = read('port/linux/game/network_campaign.c')
browser_c = read('port/linux/game/network_browser.c')
listing = read(java + 'ServerListing.java')
browser = read(java + 'ServerBrowser.java')
coop = read(java + 'CoopLauncher.java')
activity = read(java + 'HaloActivity.java')
frame = read('port/linux/src/vr_frame.c')
gradle = read('port/android/app/build.gradle')
package = read('tools/package-quest.py')
players = read('source/game/players.c', 'latin-1')
units = read('source/units/units.c', 'latin-1')
bipeds = read('source/units/bipeds.c', 'latin-1')

# --- 1. OpenCE's network version, exactly (the launcher reads the numbers)
assert re.search(r'#define HALO_PORT_NETWORK_VERSION 20\b', limits)
assert re.search(r'#define HALO_PORT_NETWORK_VERSION_MINIMUM 20\b', limits)
assert re.search(r'#define HALO_PORT_NETWORK_VERSION_MAXIMUM 20\b', limits)
assert '#define HALO_PORT_ADVERTISED_IN_PROGRESS_FLAG 0x02' in limits, "OpenCE's in-progress advertisement"
print('PASS: network version 20, exactly (OpenCE build 138), with its in-progress advertisement')

# --- 2. upstream's co-op and lobby modules byte for byte
UPSTREAM_138 = [
    ('port/linux/game/network_coop.c', '644b61699e51c70b6294c558281fd68f2e30789fbf67d8dc6eff968692d8d05c'),
    ('port/linux/game/network_coop.h', 'ff29c9fae0f03a3686342766ead3557f0aa7c4b4eaa9932dbf4c3a8724acf1d0'),
    ('port/linux/game/network_actors.c', '1e5cd77516670a173c0e9a35dbed0689c6101aa66d2ac5956c1de5488ced0b30'),
    ('port/linux/game/coop_scripts.c', 'be1d82f21b3625fdbfdb7ca623a35bc50605fbc098681affceccf41deffd5ae2'),
    ('port/linux/game/coop_scripts.h', '70d6085db78e176965e672198a7c164d1a470eb5a956b9f10e535d412abd74ef'),
    ('port/linux/game/coop_enemies.c', '64288778915265ec598613e1bb982f27330953b4b4f5dd7af41244e26c4a7f2a'),
    ('port/linux/game/coop_enemies.h', '8984e3e416e5f6fa1c743313e57fc5de87fc9a2a47be488be667865808a05a68'),
    ('port/linux/game/coop_spectate.c', '8ed6ccee0a4881e61b533a93b4621f236ae78b88703fd08203de36fa1bdb5afe'),
    ('port/linux/game/coop_spectate.h', '6c73fce2dfd2bbb300f784f4ed393053db1978e5b5a984d7dd8c1fa75eb58035'),
    ('port/linux/game/network_damage.c', 'fb215876f392898cd9a8af333ba16dcab9ae8abb2919e4c6d1f71270d38dba79'),
    ('port/linux/src/p2p_lobby.c', '53294de0700dac37bdc2e57840af6826061d38fc1b7a72eaf70cff5a135585a5'),
    ('port/linux/src/p2p_internal.h', 'e64480a5351379a57a126b472f382d37f2cde1784fe6a568390d1daf2af96e4f'),
    ('source/networking/network_server_message_handler.c', '3563bde27f3b5eca4bbaf9215cbb3ef4944d0ce3b70e3d3fcfb7d656f04af0f4'),
    ('source/networking/network_client_message_handler.c', '0644128da7ab7c2852d013504a731df4bb459a7c7bea4611bd495c28cce96134'),
    ('source/networking/network_game_manager.c', '5f5ef5829338abebba87fee45ed1cfaa2fa193ec3b804426b728ff42409179b1'),
]
# (this app's one patch to them, test28: the camera watching the host kept
# upright with square axes; taken out, the file must be build 138's exactly)
COOP_CAMERA_PATCH = re.compile(r'\t/\* keep the camera upright: the world\'s up made square to forward\n.*?\n\t\t}\n\t}\n}', re.S)
COOP_CAMERA_ORIGINAL = ('\t/* keep the camera upright */\n\tup->i = 0.0f;\n\tup->j = 0.0f;\n\tup->k = 1.0f;\n'
                        '\tdistributed_axes_make_valid(forward, up);\n}')
for path, digest in UPSTREAM_138:
    data = (ROOT / path).read_bytes()
    if path == 'port/linux/game/network_coop.c':
        text = data.decode('utf-8')
        assert len(COOP_CAMERA_PATCH.findall(text)) == 1, 'the one camera patch'
        data = COOP_CAMERA_PATCH.sub(lambda m: COOP_CAMERA_ORIGINAL, text).encode('utf-8')
    assert hashlib.sha256(data).hexdigest() == digest, path + ' as OpenCE build 138'
print('PASS: %d co-op, lobby and message files are OpenCE build 138\'s byte for byte' % len(UPSTREAM_138))

# --- 3. the message numbers: OpenCE's, this app's VR avatars in the free range
enum = re.search(r'enum\n\{\n\t[^}]*?_distributed_message_player_prediction = 1,.*?NUMBER_OF_DISTRIBUTED_MESSAGES\n\};', distributed_h, re.S).group(0)
expected = {'player_prediction': 1, 'unit_states': 2, 'player_statistics': 3, 'inventories': 4, 'object_changes': 5,
            'object_states': 6, 'game_state': 7, 'objects_synchronized': 8, 'client_ready': 9, 'damage_events': 10,
            'hit_reports': 11, 'vehicle_prediction': 12, 'pickups': 13, 'player_inputs': 14, 'relayed_actions': 15,
            'batch': 16, 'notice': 17, 'client_identity': 18, 'pings': 19, 'vr_pose': 37, 'vr_capability': 38,
            'actor_states': 64, 'structure_bsp': 65, 'coop_presentation': 66, 'coop_sounds_retired': 67,
            'coop_device_groups': 68, 'coop_object_names': 69, 'coop_skip_vote': 70, 'coop_events': 71,
            'coop_object_transforms': 72, 'actor_damage': 73, 'coop_object_looks': 74, 'damage_animations': 75,
            'coop_screen_effect': 76, 'coop_device_states': 77, 'NUMBER': 78}
checks = ''.join('\tassert(_distributed_message_%s == %d);\n' % (k, v) for k, v in expected.items() if k != 'NUMBER')
run('message_numbers', '#include <assert.h>\n#include <stdio.h>\n' + enum + '\nint main(void){\n' + checks +
    '\tassert(NUMBER_OF_DISTRIBUTED_MESSAGES == 78);\n\tputs("PASS: message numbers as OpenCE build 138\'s (1-19, 64-77);'
    ' this app\'s VR avatars at 37 and 38, a range OpenCE leaves free");\n}\n')

# --- 4. the receive path: OpenCE's (every co-op kind decoded), the VR avatars first
assert 'header.type > _distributed_message_pings &&' not in distributed_c, 'no filter drops OpenCE\'s co-op kinds'
receive = fn(distributed_c, 'network_distributed_handle_message')
assert receive.index('network_vr_pose_receive(') < receive.index('case _distributed_message_actor_states: entry_size')
for kind in ['actor_states', 'structure_bsp', 'coop_presentation', 'coop_events', 'coop_device_states', 'damage_animations']:
    assert receive.count('_distributed_message_' + kind) >= 1, kind
assert 'network_vr_pose_tick();' in fn(distributed_c, 'network_distributed_tick')
assert 'network_vr_pose_reset();' in fn(distributed_c, 'network_distributed_new_game')
assert 'network_objects_client_picked_up_weapon' in objects_net and 'distributed_host_rest_moved' in objects_net
print('PASS: every OpenCE kind decoded (the old filter that dropped co-op is gone); VR avatars handled first; '
      'OpenCE\'s object sync with test26\'s resting-teleport resend')

# --- 5. online gameplay OpenCE's: weapon pickup and swap, teams, unarmed melee
assert 'network_objects_client_picked_up_weapon(player->local_player_index, player->unit_index,' in players
assert 'if (unit_drop_selected_weapon(player->unit_index) &&' in players and 'boolean unit_drop_selected_weapon(' in units
assert 'player->team_index = unit->object.owner_team_index;' in players
assert 'biped->biped.player_melee_ticks = UNARMED_MELEE_TICKS;' in bipeds
print('PASS: online gameplay as OpenCE: picked-up weapons readied, a swap drops the weapon chosen, the host\'s teams, unarmed melee')

# --- 6. the join gate: this app's retired co-op hosts named, newer hosts "update"
gate = fn(manager, 'network_game_client_advertised_game_compatible')
assert 'theirs == ours && distributed' in gate, "OpenCE's exact match"
assert '(theirs & 0xFF00) == 0xCE00' in gate and 'This version plays co-op as OpenCE does' in gate
assert '(a newer OpenCE build)' in gate
assert 'network_campaign_join_token' not in manager, 'no CE02 join'
print('PASS: the join gate is OpenCE\'s (exact version); 1.0.8 co-op hosts and newer OpenCE builds are named')

# --- 7. the launcher's co-op host: an OpenCE co-op lobby, 2-16 players, public through the signed lobby
setup = fn(server, 'network_game_server_setup_game_from_playlist')
assert 'p2p_set_hosting_public(network_campaign_host_requested() ? network_coop_host_public() :' in setup
assert 'network_campaign_host_settings' not in setup, 'the retired CE02 settings'
assert 'boolean network_game_server_port_set_cooperative_players' not in server
assert 'void network_game_server_port_set_cooperative_players(' in server
assert 'configured = map_name && ui_widget_port_cooperative_level_choose(map_name, difficulty);' in session
assert 'network_game_server_port_set_cooperative_players(most_players);' in session
assert 'return FALSE && game && game->map.version == HALO_CAMPAIGN_MAP_VERSION' in campaign_c, 'CE retired'
reader = fn(session, 'coop_request_read')
run('coop_request', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define VALID_INDEX(i,n) ((i)>=0&&(i)<(long)(n))
static char const *missions[] = {"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"};
enum { COOP_MINIMUM_PLAYERS = 2, COOP_MAXIMUM_PLAYERS = 16 };
static boolean list_publicly; static short mission, difficulty, most_players;
''' + reader + r'''
int main(void){
 assert(coop_request_read("2 4 2 1 8\n") && mission==4 && difficulty==2 && list_publicly==1 && most_players==8);
 assert(coop_request_read("1 0 1 0\n") && mission==0 && most_players==16);   /* the 1.0.8 launcher's format */
 assert(!coop_request_read("2 10 1 1 4")); assert(!coop_request_read("2 1 4 1 4")); assert(!coop_request_read("2 1 1 2 4"));
 assert(!coop_request_read("2 1 1 1 1")); assert(!coop_request_read("2 1 1 1 17")); assert(!coop_request_read("2 1 1 1 4 x"));
 assert(!coop_request_read("3 1 1 1 4")); assert(!coop_request_read("")); assert(!coop_request_read("2 1 1 1"));
 for(int p=2;p<=16;p++){ char t[32]; snprintf(t,sizeof t,"2 9 3 0 %d",p); assert(coop_request_read(t) && most_players==p); }
 puts("PASS: the launcher's co-op host request: mission, difficulty, public, 2-16 players; 1.0.8's format read; malformed refused");
}
''')
assert '"2 " + selected + " " + difficulty.getSelectedItemPosition()' in coop and 'MOST_PLAYERS = 16' in coop
assert 'CoopPublisher' not in activity and not (ROOT / (java + 'CoopPublisher.java')).exists(), 'no HTTP announcer'
print('PASS: launcher co-op hosting opens an OpenCE co-op lobby (2-16, public through the signed lobby); '
      'the CE02 announcer and settings retired')

# --- 8. browsers: the launcher's (tested in test_quest_browser) and the game's; locked lobbies
assert 'ServerListing.listedIn(campaign, entry.kind)' in browser
assert 'ServerListing.joinable(campaign, entry.kind, entry.version,' in browser
assert 'case OPENCE_COOP:\n                return campaignBrowser && range;' in listing
assert 'g->locked=p->locked;' in browser_c and 'This game has a password.' in browser_c
print('PASS: the launcher lists co-op (joinable at this version) and multiplayer apart; the game\'s list marks locked lobbies')

# --- 9. version, identity, package markers
assert int(re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1)) >= 35
assert int(re.search(r': "1\.0\.(\d+)"', gradle).group(1)) >= 9
assert 'HaloCE Quest test27 candidate 1.0.9' in frame or 'test27: OpenCE build 138 netcode, network 20' in frame
assert 'candidate_at_least(args.label, 27)' in package
print('PASS: test27 wiring (version 1.0.9 / 35, identity, package markers)')
