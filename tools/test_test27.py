"""Test27 (1.0.9): the community directory's OpenCE co-op hosts.

Evidence (kept private): the live directory (halo.milenko.org/v1/games.txt,
2026-10-05) lists OpenCE's own co-op games beside multiplayer ones: game
engine 0, a campaign map (a10, a30, b40, c40), network version 17 or 18, up
to 32 players. OpenCE co-op is its native netcode at that version (build 128
is network 17, build 129 network 18); this app plays network 9-11 and its own
two-player co-op protocol CE02. Nothing here joins OpenCE co-op: the launcher
lists those hosts in the co-op browser only, marked and never joinable
(test_quest_browser runs the classification), and the game's own gate is
unchanged. Run with python3 tools/test_test27.py.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
BEFORE = 'a537c4b6'  # test26, 1.0.8


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def read(path, encoding='utf-8'):
    return (ROOT / path).read_text(encoding=encoding)


def git_show(path, commit=BEFORE):
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT, text=True, encoding='latin-1')


java = 'port/android/app/src/main/java/com/halo/decomp/'
browser = read(java + 'ServerBrowser.java')
listing = read(java + 'ServerListing.java')
publisher = read(java + 'CoopPublisher.java')
manager = read('source/networking/network_client_manager.c', 'latin-1')
limits = read('port/linux/include/halo_port_limits.h')
campaign_h = read('port/linux/game/network_campaign.h')
lobby = read('port/linux/src/p2p_lobby.c')
frame = read('port/linux/src/vr_frame.c')
gradle = read('port/android/app/build.gradle')
package = read('tools/package-quest.py')

# --- the protocols are untouched: native 9-11, co-op CE02, the in-game lobby at this version only
assert re.search(r'#define HALO_PORT_NETWORK_VERSION 11\b', limits)
assert re.search(r'#define HALO_PORT_NETWORK_VERSION_MINIMUM 9\b', limits) and re.search(r'#define HALO_PORT_NETWORK_VERSION_MAXIMUM 11\b', limits)
assert limits == git_show('port/linux/include/halo_port_limits.h'), 'limits as in 1.0.8'
assert re.search(r'#define HALO_CAMPAIGN_NETWORK_VERSION 0xCE02\b', campaign_h)
assert 'listing.version != HALO_PORT_NETWORK_VERSION' in lobby and lobby == git_show('port/linux/src/p2p_lobby.c')
assert '"&engine=0&players=" + players' in publisher and '"&maximum_players=2&open="' in publisher
assert 'ServerBrowser.CAMPAIGN_VERSION' in publisher and publisher == git_show(java + 'CoopPublisher.java'), \
    "this app's co-op host advertises as in 1.0.8 (CE02, two players)"
print('PASS: protocols untouched: native 9-11 (host 11), co-op CE02 two-player host listing, in-game lobby at 11 only')

# --- the join gate: its decisions as in 1.0.8; only the newer host's message says what it is
old_manager = git_show('source/networking/network_client_manager.c')
gate_name = 'network_game_client_advertised_game_compatible'
new_gate, old_gate = fn(manager, gate_name), fn(old_manager, gate_name)
strip = lambda text: re.sub(r'csprintf\(message,.*?\);', 'MESSAGE;', re.sub(r'/\*.*?\*/', '', text, flags=re.S), flags=re.S)
lines = lambda text: [line.strip() for line in strip(text).splitlines() if line.strip()]
assert lines(new_gate) == lines(old_gate), 'the gate decides as in 1.0.8'
assert 'Update the game to join this host.' not in new_gate, 'no update of this app joins a newer host'
assert '(OpenCE and other ports, their co-op included)' in new_gate
print('PASS: the game\'s join gate decides exactly as in 1.0.8; a newer host (OpenCE co-op included) is named, not "update"')

# --- the launcher: one classification for both browsers
assert 'ServerListing.listedIn(campaign, entry.kind)' in browser
assert 'ServerListing.isCampaign(entry.version) == campaign' not in browser, 'co-op of both kinds kept out of multiplayer'
assert 'ServerListing.joinable(campaign, entry.kind, entry.version, entry.maximum,' in browser
assert 'if (opence && !favorite) return;' in browser, 'an OpenCE co-op invite is not offered for saving'
assert 'if(!campaign && !opence && entry.version > BuildConfig.HALO_NETWORK_MAXIMUM)' in browser
assert 'kind = ServerListing.kind(version, object.optInt("engine", -1), map);' in browser
for key in ['enum Kind { CAMPAIGN, OPENCE_COOP, MULTIPLAYER }', 'static boolean listedIn(', 'static boolean joinable(',
            '"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"', 'case OPENCE_COOP:\n                return false;']:
    assert key in listing, key
print('PASS: launcher browsers share one classification: OpenCE co-op only in the co-op browser, marked, never joinable or saved')

# --- version and identity
assert int(re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1)) >= 35
assert int(re.search(r': "1\.0\.(\d+)"', gradle).group(1)) >= 9
assert 'HaloCE Quest test27 candidate 1.0.9 (launcher: OpenCE co-op hosts listed apart and marked' in frame
assert 'candidate_at_least(args.label, 27)' in package
print('PASS: test27 wiring (version 1.0.9 / 35, identity, package markers)')
