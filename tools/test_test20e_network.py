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
import contextlib
import importlib.util
import io
import re
import struct
import tempfile
import zipfile
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

# --- production APK gate: symbol/debug differences are not runtime differences.
spec = importlib.util.spec_from_file_location('package_quest', ROOT/'tools/package-quest.py')
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


def elf_fixture(bits=64, endian='<', runtime=b'browser: shared\0network.online\0',
                symbols=b'lobby_add_player\0', imports=b'p2p_peer\0', extended=False):
    """Small valid ELF section fixture: rodata/dynstr allocated, strtab/debug not."""
    header_format = endian + ('HHIIIIIHHHHHH' if bits == 32 else 'HHIQQQIHHHHHH')
    section_format = endian + ('IIIIIIIIII' if bits == 32 else 'IIQQQQIIQQ')
    header_size = 16 + struct.calcsize(header_format)
    section_size = struct.calcsize(section_format)
    data = bytearray(header_size)
    sections = [(0, 0, 0, 0, 0, 5 if extended else 0, 0, 0, 0, 0)]
    for kind, flags, contents in [(1, 2, runtime), (3, 2, imports),
                                  (3, 0, symbols), (1, 0, b'network.debug_metadata\0')]:
        sections.append((0, kind, flags, 0, len(data), len(contents), 0, 0, 1, 0))
        data.extend(contents)
    offset = len(data)
    for section in sections:
        data.extend(struct.pack(section_format, *section))
    data[:16] = b'\x7fELF' + bytes([1 if bits == 32 else 2, 1 if endian == '<' else 2, 1]) + b'\0'*9
    struct.pack_into(header_format, data, 16, 3, 40 if bits == 32 else 183, 1, 0, 0,
                     offset, 0, header_size, 0, 0, section_size, 0 if extended else len(sections), 0)
    return bytes(data)


for bits in (32, 64):
    for endian in ('<', '>'):
        for extended in (False, True):
            strings = packager.runtime_elf_strings(elf_fixture(bits, endian, extended=extended))
            assert b'browser: shared' in strings and b'network.online' in strings
            assert b'p2p_peer' in strings  # runtime import table stays covered
            assert b'lobby_add_player' not in strings and b'network.debug_metadata' not in strings


def must_reject(data):
    try:
        packager.runtime_elf_strings(data)
    except ValueError:
        return
    raise AssertionError('malformed ELF accepted')


valid = elf_fixture()
for broken in (b'', b'not an ELF', valid[:15], valid[:30], valid[:-1]):
    must_reject(broken)
for index, value in [(4, 9), (5, 0), (6, 0)]:
    broken = bytearray(valid);broken[index] = value;must_reject(broken)
for index, value in [(5, len(valid)+100), (7, 1), (10, 1), (11, 60000), (12, 60000)]:
    broken = bytearray(valid)
    header = list(struct.unpack_from('<HHIQQQIHHHHHH', broken, 16));header[index] = value
    struct.pack_into('<HHIQQQIHHHHHH', broken, 16, *header);must_reject(broken)
section_offset = struct.unpack_from('<HHIQQQIHHHHHH', valid, 16)[5]
for section in (1, 3):  # validate file ranges in runtime and metadata alike
    broken = bytearray(valid)
    struct.pack_into('<Q', broken, section_offset + section*64 + 32, len(valid)+1)
    must_reject(broken)
broken = bytearray(valid)
struct.pack_into('<Q', broken, section_offset + 8, 2)  # null section cannot be allocated
must_reject(broken)
broken = bytearray(valid)
for section in (1, 2):
    struct.pack_into('<Q', broken, section_offset + section*64 + 8, 0)
must_reject(broken)  # missing runtime-section evidence must not pass as empty sets


def apk(path, guest, vr=False, host=valid, classes=b'Lcom/halo/decomp/HaloActivity;'):
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('assets/halo_guest.elf', guest)
        archive.writestr('lib/arm64-v8a/libmain.so', host)
        archive.writestr('classes.dex', classes)
        if vr:
            archive.writestr('lib/arm64-v8a/libopenxr_loader.so', b'loader fixture')


def parity_reject(vr, flat, expected):
    try:
        packager.networking_parity(vr, flat)
    except SystemExit as error:
        assert expected in str(error), str(error)
        return
    raise AssertionError('APK parity regression was accepted')


with tempfile.TemporaryDirectory() as folder:
    vr, flat = Path(folder)/'vr.apk', Path(folder)/'flat.apk'
    apk(vr, elf_fixture(symbols=b'no local player symbols\0'), vr=True)
    apk(flat, elf_fixture(symbols=b'lobby_add_player\0lobby_join.0\0'))
    with contextlib.redirect_stdout(io.StringIO()):
        packager.networking_parity(vr, flat)  # only .strtab differs: must pass
    apk(flat, elf_fixture(runtime=b'browser: REGRESSED\0network.online\0'))
    parity_reject(vr, flat, 'Networking differs')
    apk(flat, elf_fixture(runtime=b'browser: shared\0network.other\0'))
    parity_reject(vr, flat, 'Networking differs')
    apk(flat, elf_fixture(imports=b'p2p_DIFFERENT\0'))
    parity_reject(vr, flat, 'Networking differs')
    apk(flat, valid, host=elf_fixture(runtime=b'STUN regressed\0'))
    parity_reject(vr, flat, 'lib/arm64-v8a/libmain.so')
    apk(flat, valid[:-1]);parity_reject(vr, flat, 'invalid ELF')
    apk(flat, valid, classes=b'Lcom/halo/decomp/UnexpectedActivity;')
    parity_reject(vr, flat, 'App classes differ')
    apk(flat, valid)
    with zipfile.ZipFile(flat, 'a') as archive:
        archive.writestr('unapproved-extra', b'entry')
    parity_reject(vr, flat, 'APK entries differ')
print('PASS: ELF32/64 little/big-endian allocated sections retain runtime/import strings; symbol-only '
      'differences pass, runtime/config/import/host differences and malformed ELF fail; APK/class parity retained')
