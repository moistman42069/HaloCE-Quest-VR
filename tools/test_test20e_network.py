"""Test20e: Quest and Android multiplayer stay one implementation.

Owner logs (2026-10-04 11:39-11:45): the Quest joined a public host that the
Android phone could not reach. Both ran the same build (1.0.2, code 24). The
phone reported a strict NAT (a new public port for each destination: mobile
data) and failed at the direct UDP connection after the host had answered;
the Quest, on a lenient home NAT, connected in 0.6 s. These checks keep the
networking code free of VR-only branches and verify the stage logging and
browser reporting added for such failures. No device or network is used.
"""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


# --- one implementation: no VR-only branches anywhere on the multiplayer path
networking = sorted({*ROOT.glob('port/linux/src/p2p*.[ch]'), ROOT / 'port/linux/src/xnet.c',
                     ROOT / 'port/linux/src/posix_net.c', ROOT / 'port/linux/src/posix_upnp.c',
                     ROOT / 'port/linux/game/network_browser.c', ROOT / 'port/linux/include/network_browser.h',
                     *ROOT.glob('source/networking/**/*.[ch]'), *ROOT.glob('source/bungie_net/**/*.[ch]')})
assert len(networking) > 15, networking
for path in networking:
    text = path.read_text(encoding='utf-8', errors='replace')
    assert 'HALO_VR' not in text, f'VR-only networking branch in {path.relative_to(ROOT)}'
java = ROOT / 'port/android/app/src/main/java/com/halo/decomp'
for name in ['NetworkSettings', 'ServerBrowser', 'ServerListing', 'CoopLauncher', 'PvpLauncher']:  # (CoopPublisher retired: test27)
    text = (java / (name + '.java')).read_text(encoding='utf-8')
    assert '.vr"' not in text and 'endsWith(".vr")' not in text, f'VR-only branch in {name}.java'
assert not (ROOT / 'port/android/app/src/vr/java').exists(), 'the vr source set must not carry its own Java'
vr_manifest = read('port/android/app/src/vr/AndroidManifest.xml')
for permission in re.findall(r'uses-permission android:name="([^"]+)"', vr_manifest):
    assert 'openxr' in permission, f'non-OpenXR permission only in the VR manifest: {permission}'
main_manifest = read('port/android/app/src/main/AndroidManifest.xml')
for permission in ['INTERNET', 'ACCESS_NETWORK_STATE', 'ACCESS_WIFI_STATE', 'CHANGE_WIFI_MULTICAST_STATE']:
    assert f'android.permission.{permission}' in main_manifest, permission
config = read('port/linux/src/port_config.c')
for key, platform in re.findall(r'\{ "(network\.[a-z_]+)", _config_\w+, "(?:[^"\\]|\\.)*", "\w+", _environment_\w+,\s*(_platform_\w+)', config):
    assert platform == '_platform_all', f'{key} differs by platform ({platform})'
build = read('tools/android_build.py')
assert '-DHALO_VR=1' in build and 'posix_net.c' in build and 'posix_upnp.c' in build
print(f'PASS: {len(networking)} networking sources and 6 networking Java classes have no VR-only branches; '
      'permissions, network.* defaults and build sources are shared')

# --- stages in the log, and a reason players can act on
p2p = read('port/linux/src/p2p.c')
for marker in ['stage 1/3: asking the host through signalling', 'stage 2/3, the host answered through signalling',
               'stage 3/3, direct connection open', 'gave up joining after', '(stage 1/3 failed)',
               "keeps one public port for every", 'open (a different session or build, not a blocked path)',
               'no packet from it arrived in %d s at any of',
               'an invite arrived before Internet play started; it is joined once it is up',
               'peer->rejected++;', 'int p2p_join_status(char *text, int size, int *tries, int *active)']:
    assert marker in p2p, marker
assert p2p.count('p2p.nat_strict = 1;') == 1 and p2p.count('p2p.nat_strict = 0;') == 1
assert 'try wi-fi' in p2p.lower(), 'a strict NAT failure suggests the fix players can make'
browser = read('port/linux/game/network_browser.c')
assert 'p2p_join_status(failure,sizeof(failure),&tries,&active)' in browser
assert 'did not advertise within 30 seconds' not in browser, 'the browser follows the join, not a fixed 30 s'
for marker in ['Host answered. Opening a direct connection (try %d)', 'found no direct path; asking again',
               'join of the selected public host ended after %lu ms at stage %d']:
    assert marker in browser, marker
handler = read('source/interface/ui_widget_event_handler_functions.c')
assert 'start_network_game_if_no_advertised_servers && network_browser_active()' in handler
assert 'boolean network_browser_active(void)' in read('port/linux/include/network_browser.h')
assert 'RunLog.line("Network: " + NetworkSettings.describe(this));' in (java / 'HaloActivity.java').read_text(encoding='utf-8')
assert '" over " + NetworkSettings.describe(activity)' in (java / 'ServerBrowser.java').read_text(encoding='utf-8')
assert 'TRANSPORT_CELLULAR' in (java / 'NetworkSettings.java').read_text(encoding='utf-8')
package = read('tools/package-quest.py')
assert 'networking_parity(args.vr, args.flat)' in package and 'VR_ONLY_ENTRIES = {"lib/arm64-v8a/libopenxr_loader.so"}' in package
print('PASS: join stages 1-3, NAT class, failure reasons, queued invites, browser status and the network type are logged; '
      'the stock fallback no longer prints red; packaging enforces APK networking parity')
