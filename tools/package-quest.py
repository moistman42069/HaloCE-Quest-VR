#!/usr/bin/env python3
"""Package already-built VR/flat APKs and the clean committed source. No install.

Both APKs must be preserved from the same source before switching build modes.
Requires Android build-tools' apksigner and aapt via --build-tools.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = "53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def network_value(name):
    text=(ROOT / "port/linux/include/halo_port_limits.h").read_text()
    return int(re.search(r"^#define " + name + r" (\d+)$", text, re.M)[1])


# Test20e: the Quest and Android builds share every networking path; only
# these platform pieces may differ between the two APKs.
VR_ONLY_ENTRIES = {"lib/arm64-v8a/libopenxr_loader.so"}
NETWORK_STRING = re.compile(rb"Internet play|browser: |signalling|UPnP|upnp|STUN|stun\.|tunnel|invite|network\.[a-z_]+|"
                            rb"halo://join|p2p|lobby|games\.txt|joining|join requested|Multiplayer join")


def candidate_at_least(label, number, letter=""):
    """test20d, test21 ... compared as candidates (test21 follows test20e)."""
    match = re.fullmatch(r"test(\d+)([a-z]?)", label)
    if not match:
        return False
    return (int(match.group(1)), match.group(2)) >= (number, letter)


def printable_strings(data):
    return {m.group() for m in re.finditer(rb"[\x20-\x7e]{6,}", data)}


def runtime_elf_strings(data):
    """Strings in file-backed SHF_ALLOC sections, including dynamic imports.

    Local symbols/debug information are not runtime networking behavior: the
    approved VR local-player guard can remove functions from .strtab. Do not
    exclude names or patterns; .dynstr and every other allocated section stay
    checked. Bounds checks fail closed if section evidence is unavailable.
    """
    def reject(message):
        raise ValueError("invalid ELF: " + message)

    if len(data) < 16 or data[:4] != b"\x7fELF":
        reject("missing identification")
    if data[4] not in (1, 2) or data[5] not in (1, 2) or data[6] != 1:
        reject("unsupported class, byte order or version")
    endian = "<" if data[5] == 1 else ">"
    header_format = endian + ("HHIIIIIHHHHHH" if data[4] == 1 else "HHIQQQIHHHHHH")
    section_format = endian + ("IIIIIIIIII" if data[4] == 1 else "IIQQQQIIQQ")
    header_size = 16 + struct.calcsize(header_format)
    section_size = struct.calcsize(section_format)
    if len(data) < header_size:
        reject("truncated header")
    header = struct.unpack_from(header_format, data, 16)
    offset, entry_size, count, names_index = header[5], header[10], header[11], header[12]
    if header[2] != 1 or header[7] != header_size:
        reject("invalid header size or version")
    if entry_size != section_size or offset < header_size or offset > len(data) - section_size:
        reject("missing or truncated section table")
    first = struct.unpack_from(section_format, data, offset)
    if first[1] != 0 or first[2] != 0:
        reject("invalid null section")
    if count == 0:  # ELF extended section count is sh_size in section zero.
        count = first[5]
    if count < 1 or count > (len(data) - offset) // entry_size:
        reject("section table exceeds file")
    if names_index == 0xFFFF:  # SHN_XINDEX: sh_link in section zero.
        names_index = first[6]
    if names_index >= count:
        reject("section-name table index out of range")
    sections = [struct.unpack_from(section_format, data, offset + index * entry_size)
                for index in range(count)]
    result, runtime_sections = set(), 0
    for index, section in enumerate(sections):
        kind, flags, start, size = section[1], section[2], section[4], section[5]
        if kind in (0, 8):  # SHT_NULL / SHT_NOBITS have no file-backed data.
            continue
        if start > len(data) or size > len(data) - start:
            reject("section " + str(index) + " exceeds file")
        if flags & 2 and size:  # SHF_ALLOC; preserve .dynstr and import names.
            result.update(printable_strings(data[start:start + size]))
            runtime_sections += 1
    if names_index and sections[names_index][1] != 3:  # SHT_STRTAB
        reject("section-name table is not a string table")
    if not runtime_sections:
        reject("no file-backed runtime sections")
    return result


def networking_parity(vr_path, flat_path):
    """Check APK entries, allocated networking text/imports and app classes.

    Source tests separately guard shared multiplayer code. The OpenXR loader
    is VR-only; platform UI and nonruntime symbols/debug metadata may differ.
    """
    with zipfile.ZipFile(vr_path) as vr, zipfile.ZipFile(flat_path) as flat:
        vr_names = {n for n in vr.namelist() if not n.startswith("META-INF/")}
        flat_names = {n for n in flat.namelist() if not n.startswith("META-INF/")}
        if vr_names - flat_names != VR_ONLY_ENTRIES or flat_names - vr_names:
            raise SystemExit("APK entries differ beyond the OpenXR loader: VR-only "
                             + repr(sorted(vr_names - flat_names)) + ", flat-only " + repr(sorted(flat_names - vr_names)))
        for member in ["assets/halo_guest.elf", "lib/arm64-v8a/libmain.so"]:
            try:
                a = {x for x in runtime_elf_strings(vr.read(member)) if NETWORK_STRING.search(x)}
                b = {x for x in runtime_elf_strings(flat.read(member)) if NETWORK_STRING.search(x)}
            except ValueError as error:
                raise SystemExit("Cannot verify networking parity in " + member + ": " + str(error)) from error
            if a != b:
                raise SystemExit("Networking differs between the Quest and Android " + member + ": VR-only "
                                 + repr(sorted(a - b)[:8]) + ", flat-only " + repr(sorted(b - a)[:8]))
        def classes(archive):
            dex = b"".join(archive.read(n) for n in archive.namelist() if re.fullmatch(r"classes\d*\.dex", n))
            return set(re.findall(rb"Lcom/halo/decomp/[A-Za-z0-9_$/]+;", dex))
        if classes(vr) != classes(flat):
            raise SystemExit("App classes differ between the Quest and Android APKs")
    print("Networking parity: same entries (but the OpenXR loader), networking strings and app classes in both APKs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vr", type=Path, required=True)
    parser.add_argument("--flat", type=Path, required=True)
    parser.add_argument("--build-tools", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", default="test17")
    parser.add_argument("--version-name", help="Internal APK version for a private candidate; does not authorize publication")
    parser.add_argument("--stable", action="store_true", help="Use semantic release identity; requires owner publication authorization")
    parser.add_argument("--runtime-source", help="Exact build commit when later commits change documentation only")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", args.label):
        parser.error("label must contain letters, digits, underscore or dash")
    if args.stable and not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.label):
        parser.error("stable label must be major.minor.patch")
    if args.version_name and (args.stable or not re.fullmatch(r"[A-Za-z0-9_.-]+",args.version_name)):
        parser.error("--version-name requires a private candidate and a simple version string")
    version_name=args.version_name or (args.label if args.stable else "1.0-"+args.label)
    release_tag="v"+args.label if args.stable else "halo-ce-quest-"+args.label
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT)
    if untracked.strip():
        raise SystemExit("Commit intended source files before packaging; untracked files remain")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    runtime_commit=subprocess.check_output(["git","rev-parse",args.runtime_source or "HEAD"],cwd=ROOT,text=True).strip()
    records = []
    networking_parity(args.vr, args.flat)
    for path, package, vr in [(args.vr, "com.halo.decomp.vr", True), (args.flat, "com.halo.decomp", False)]:
        signed = subprocess.check_output([str(args.build_tools / "apksigner"), "verify", "--print-certs", str(path)], text=True)
        if "certificate SHA-256 digest: " + CERTIFICATE not in signed:
            raise SystemExit("APK signing certificate differs from the user's test8 key")
        badging = subprocess.check_output([str(args.build_tools / "aapt"), "dump", "badging", str(path)], text=True)
        if f"package: name='{package}'" not in badging or "native-code: 'arm64-v8a'" not in badging:
            raise SystemExit("Wrong package or ABI: " + str(path))
        if f"versionName='{version_name}'" not in badging:
            raise SystemExit("Wrong candidate version: " + str(path))
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise SystemExit("APK ZIP checksum failure")
            names = archive.namelist()
            for guide in ["player-guide", "controls", "touch", "settings", "credits"]:
                if "assets/guide/"+guide+".txt" not in names:
                    raise SystemExit("Bundled guide missing: "+guide)
            guest = archive.read("assets/halo_guest.elf")
            host = archive.read("lib/arm64-v8a/libmain.so")
            dex = b"".join(archive.read(name) for name in names if re.fullmatch(r"classes\d*\.dex", name))
            for marker in [b"ServerBrowser;", b"ServerListing;", b"RunLog;", b"openGameLog", b"CoopLauncher;",
                           b"CoopLauncher;", b"prepareGameExit", b"PvpLauncher;", b"TouchLayout;", b"UpdatePolicy;",
                           b"upstreamVersion", b"compatibility.json", b"GamepadSupport;", b"GamepadNavigation;", b"GameDataLibrary;", b"GameDataManager;", b"ISO/revision versions", b"https://halo.milenko.org/v1/games.txt"]:
                if marker not in dex: raise SystemExit("Browser missing from APK: " + repr(marker))
            if not guest.startswith(b"\x7fELF") or not host.startswith(b"\x7fELF"):
                raise SystemExit("Missing native ELF payload")
            if b"/active-data.txt" not in host or b"/profile.properties" not in host:
                raise SystemExit("Native managed-data selection missing")
            if args.label=="test19":
                if b"UpstreamDownloads;" not in dex or b"browser: signed public discovery started" not in guest:
                    raise SystemExit("Test19 upstream downloads or native public browser missing")
                if b"safe ordered uploads; CPU index rebasing" not in guest:
                    raise SystemExit("Test19 ordered Safe geometry path missing")
            if candidate_at_least(args.label, 20):
                if b"UpstreamDownloads;" not in dex or b"browser: signed public discovery started" not in guest:
                    raise SystemExit("Test20 upstream downloads or native public browser missing")
                if b"safe streaming (fenced ring); CPU index rebasing" not in guest or b"[render-perf]" not in guest:
                    raise SystemExit("Test20 fenced Safe streaming or render diagnostics missing")
                if b"safe ordered uploads" in guest:
                    raise SystemExit("Test20 still contains the 1.0.1 ordered Safe upload path")
            if candidate_at_least(args.label, 22):
                for marker in [b"opence.milenko.org:1883", b"[game-ticks]"]:
                    if marker not in guest: raise SystemExit("Test22 broker or tick marker missing: " + repr(marker))
            if candidate_at_least(args.label, 22) and vr:
                for marker in [b"SCOPES", b"vr.scope_pistol_forward", b"vr.scope_sniper_scale", b"RESET SCOPES",
                               b"vr: shot (", b"adjustable scopes"]:
                    if marker not in guest: raise SystemExit("Test22 scope or diagnostic marker missing: " + repr(marker))
            if candidate_at_least(args.label, 23):
                if b"client dropped presentation" not in guest:
                    raise SystemExit("Test23 co-op cutscene diagnostic missing")
            if candidate_at_least(args.label, 30):
                # the co-op host's server name (format 3) in both; the menus' letters in the VR guest
                if b"co-op: lobby open: %s (%s), difficulty %d, up to %d players, %s, named %s" not in guest:
                    raise SystemExit("Test30 co-op server name missing")
                if b"Server name (optional, up to " not in dex:
                    raise SystemExit("Test30 launcher server name missing")
                if vr and b"test30 candidate 1.0.12" not in guest:
                    raise SystemExit("Test30 VR identity missing")
            if candidate_at_least(args.label, 29):
                # OpenCE build 144's network 21, and the held HUD tap's and PR #1's text
                expected_upstream = (b"OpenCE build 147 (network 23)" if candidate_at_least(args.label, 34) else
                                     b"OpenCE build 145 (network 22)" if candidate_at_least(args.label, 31) else
                                     b"OpenCE build 144 (network 21)")
                if expected_upstream not in dex:
                    raise SystemExit("Test29 upstream netcode text missing")
                if vr:
                    for marker in [b"OpenCE build 144 netcode, network 21", b"vr: HUD %s (VR settings)", b"WRIST ALONG", b"RESET WRIST",
                                   b"GLASSES 70X66", b"125% Q3", b"move with %s"]:
                        if marker not in guest:
                            raise SystemExit("Test29 VR marker missing: " + repr(marker))
            if candidate_at_least(args.label, 31):
                for marker in [b"display.menus", b"display.shadow_resolution", b"display.per_pixel_lighting",
                               b"display.anti_aliasing", b"audio.reverb", b"browser.show_empty",
                               b"browser.passwords", b"main_menu/multiplayer_type_select/join_game",
                               b"shadow maps: %ldx%ld", b"anti-aliasing:"]:
                    if marker not in guest:
                        raise SystemExit("Test31 menu/runtime marker missing: " + repr(marker))
                if vr:
                    for marker in [("HaloCE Quest " + args.label + " candidate " + version_name).encode("ascii"), b"HOG GLASS", b"vr.vehicle_warthog_hide_glass"]:
                        if marker not in guest:
                            raise SystemExit("Test31 VR marker missing: " + repr(marker))
            if candidate_at_least(args.label, 33):
                if b"menus: resetting network client in state" not in guest:
                    raise SystemExit("Test33 browser recovery marker missing")
                # The candidate identity banner is emitted by the VR startup
                # logger in vr_frame.c; flat Android shares the recovery code
                # but has no VR frame startup path.
                if vr and candidate_at_least(args.label, 34) is False and b"test33 candidate 1.0.14 code43" not in guest:
                    raise SystemExit("Test33 VR candidate identity marker missing")
            if candidate_at_least(args.label, 34):
                if vr:
                    for marker in [b"OpenCE Build 147 / network 23", b"test34 candidate 1.0.15 code44"]:
                        if marker not in guest:
                            raise SystemExit("Test34 OpenCE or candidate identity marker missing: " + repr(marker))
                    for marker in [b"scope display %s; zoom with the off-hand index trigger",
                                   b"zoom input %s from %s-hand index trigger", b"game zoom state %s",
                                   b"scope view gate: %s", b"scope render path %s"]:
                        if marker not in guest:
                            raise SystemExit("Test34 scope diagnosis marker missing: " + repr(marker))
                    if b"left trigger for right-handed play" not in archive.read("assets/guide/controls.txt"):
                        raise SystemExit("Test34 explicit scope zoom input missing from bundled control guide")
            if candidate_at_least(args.label, 28):
                # a release build (HALO_RELEASE, as OpenCE's): checks logged, play goes on
                if b"(release build)" not in guest:
                    raise SystemExit("Test28 release build marker missing")
                # gyro aim (flat option; the classes ship in both APKs)
                if b"GyroAim;" not in dex or b"GyroPolicy;" not in dex:
                    raise SystemExit("Test28 gyro aim missing from APK")
            if candidate_at_least(args.label, 27):
                for marker in [b"co-op: lobby open: ", b"(a newer OpenCE build)", b"This version plays co-op as OpenCE does"]:
                    if marker not in guest: raise SystemExit("Test27 OpenCE co-op hosting marker missing: " + repr(marker))
                for marker in [b"Co-op (network v", b"Directory classified for the ", b"Up to "]:
                    if marker not in dex: raise SystemExit("Test27 launcher co-op classification missing: " + repr(marker))
            if candidate_at_least(args.label, 26):
                # (test27 retired CE02: its gate names this app's old co-op hosts instead)
                for marker in [b"it is the host's to erase", b"This version plays co-op as OpenCE does"
                               if candidate_at_least(args.label, 27) else b"co-op protocol %X here, %X on the host"]:
                    if marker not in guest: raise SystemExit("Test26 co-op marker missing: " + repr(marker))
                if b"could not start on this device" not in host:
                    raise SystemExit("Test26 start failure message missing")
            if candidate_at_least(args.label, 26) and vr:
                for marker in [b"HUD + RETICLE", b"HEAD GESTURES", b"WRIST HUD", b"HUD TAP", b"vr.button_reticle",
                               b"vr.hud_tap_distance", b"vr.wrist_hud", b"vr: HUD %s (head tap)", b"the gun's end", b"L STICK CLICK",
                               b"right_stick_down"]:
                    if marker not in guest: raise SystemExit("Test26 HUD, gesture or button marker missing: " + repr(marker))
            if candidate_at_least(args.label, 25) and vr:
                for marker in [b"RESET OFFSETS", b"HORIZON", b"vr: recentre (", b"vr: seat: ", b"rows widened from",
                               b"vr: first-person seat: the vehicle draws see-through", b"vr.vehicle_tilt"]:
                    if marker not in guest: raise SystemExit("Test25 vehicle marker missing: " + repr(marker))
            if candidate_at_least(args.label, 24, "b") and vr:
                for marker in [b"COMFORT", b"VIGNETTE ON", b"SNAP ANGLE", b"SMOOTH SPEED", b"vr.vignette",
                               b"vr.snap_turn_amount", b"vr: comfort: turning"]:
                    if marker not in guest: raise SystemExit("Test24b comfort marker missing: " + repr(marker))
            if candidate_at_least(args.label, 24, "b") and b"not working yet" not in dex:
                raise SystemExit("Test24b SPV1 notice missing")
            if candidate_at_least(args.label, 24):
                if b"client follows the host's activating place" not in guest:
                    raise SystemExit("Test24 co-op cutscene activation missing")
            if candidate_at_least(args.label, 23) and vr:
                for marker in [b"BUTTONS", b"RESET BUTTONS", b"USE / RELOAD", b"NEXT GRENADE", b"vr.button_grenade",
                               b"vr.button_switch_grenade", b"that button does both"]:
                    if marker not in guest: raise SystemExit("Test23 button remapping marker missing: " + repr(marker))
            if candidate_at_least(args.label, 21) and vr:
                for marker in [b"FLOAT + ARMS", b"AUTO LOCK", b"SWING + ONLINE", b"support grip locked automatically",
                               b"vr.melee_multiplayer", b"vr.two_hand_auto_applied", b"physical melee",
                               b"AIM FOR", b"vr.aim_pistol_up", b"aim adjusted",
                               b"vr.aim_reset_applied", b"horn: stick clicked", b"reticle converges"]:
                    if marker not in guest: raise SystemExit("Test21 hand mode, two-hand or melee marker missing: " + repr(marker))
            if candidate_at_least(args.label, 20, "d") and vr:
                for marker in [b"HANDS + GUN", b"MIRROR CONTROLS", b"GUN GRIP", b"anchored to the controller",
                               b"sticks and face buttons", b"vr.gun_anchor", b"vr.mirror_controls"]:
                    if marker not in guest: raise SystemExit("Test20d gun anchor, handedness or menu marker missing: " + repr(marker))
            if b"vr pose: host negotiated visual avatars v1" not in guest:
                raise SystemExit("Negotiated avatar support missing")
            if vr and (b"HANDS ONLY" not in guest or b"NEXT PAGE (%ld/%ld)" not in guest):
                raise SystemExit("Body modes or paged settings missing")
            identity = ("HaloCE Quest " + args.label + (" release" if args.stable else " candidate")).encode("ascii")
            if (identity in guest) != vr:
                raise SystemExit("VR/flat guest identity mismatch")
            if ("lib/arm64-v8a/libopenxr_loader.so" in names) != vr:
                raise SystemExit("VR/flat OpenXR loader mismatch")
            if (b"Java_com_halo_decomp_TouchControls_nativeState" in host) == vr:
                raise SystemExit("VR/flat touch JNI separation mismatch")
            if (b"Java_com_halo_decomp_GamepadSupport_nativeSettings" in host) == vr:
                raise SystemExit("VR/flat gamepad settings JNI separation mismatch")
            for name in names:
                if name.lower().endswith((".map", ".yelo", ".jks", ".keystore")):
                    raise SystemExit("Unexpected game data or signing key in APK")
        records.append({"file": path.name, "package": package, "bytes": path.stat().st_size,
                        "version_code": int(re.search(r"versionCode='(\d+)'", badging)[1]),
                        "min_sdk": int(re.search(r"sdkVersion:'(\d+)'", badging)[1]),
                        "sha256": sha(path), "guest_sha256": hashlib.sha256(guest).hexdigest(),
                        "host_sha256": hashlib.sha256(host).hexdigest()})
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    for path in [args.vr, args.flat]: shutil.copy2(path, output / path.name)
    source = output / f"HaloCE-Quest-{args.label}-source.zip"
    subprocess.run(["git", "archive", "--format=zip", "--prefix=halo-ce-quest/", "-o", str(source), commit], cwd=ROOT, check=True)
    manifest = {"candidate": args.label, "created_utc": datetime.now(timezone.utc).isoformat(),
                "source_commit": commit, "runtime_source_commit": runtime_commit, "branch": branch, "runtime_accepted": args.stable,
                "publication": "owner-authorized 1.0 baseline" if args.stable else "held pending owner candidate testing and approval",
                "prior_device_report": "Public 1.0 preserves owner-authorized test18; current candidate requires separate device testing and publication approval",
                "certificate_sha256": CERTIFICATE, "apks": records,
                "source_zip": {"file": source.name, "sha256": sha(source)},
                "native_host_version": network_value("HALO_PORT_NETWORK_VERSION"), "accepted_host_versions": list(range(network_value("HALO_PORT_NETWORK_VERSION_MINIMUM"), network_value("HALO_PORT_NETWORK_VERSION_MAXIMUM")+1)),
                "coop": "opence-native", "campaign_runtime_verified": False,
                "avatar_protocol": 1, "avatar_message_ids": [37, 38], "avatar_prior_owner_report": "Owner confirmed earlier VR body movement was visible on flat Android; Test32 preserves avatar protocol v1 and native action handoff.",
                "directory": "https://halo.milenko.org/v1/games.txt"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    compatibility = {"schema": 1, "project": "moistman42069/HaloCE-Quest-VR",
        "tag": release_tag, "source_commit": commit, "minimum_app_code": 15,
        "save_policy": "preserve", "config_policy": "preserve", "vr_and_coop_integrated": True,
        "native_minimum": network_value("HALO_PORT_NETWORK_VERSION_MINIMUM"),
        "native_maximum": network_value("HALO_PORT_NETWORK_VERSION_MAXIMUM"), "coop": "opence-native",
        "editions": {record["package"]: {"apk": record["file"], "sha256": record["sha256"],
            "bytes": record["bytes"], "version_code": record["version_code"], "min_sdk": record["min_sdk"]} for record in records}}
    (output / "compatibility.json").write_text(json.dumps(compatibility, indent=2)+"\n")
    edition_docs=["RELEASE-"+args.label+".md", "RELEASE-PROVENANCE-"+args.label+".md"] if args.stable else [args.label.upper()+"-DELIVERY.md", args.label.upper()+"-PROGRESS.md"]
    # a lettered candidate (test21b) ships its base candidate's notes too
    base_label = re.sub(r"[a-z]$", "", args.label)
    if not args.stable and base_label != args.label:
        edition_docs += [base_label.upper()+"-DELIVERY.md", base_label.upper()+"-PROGRESS.md"]
    documents = edition_docs+["GAME-DATA-LIBRARY.md", "TEST15-DELIVERY.md", "TEST15-PROGRESS.md", "TEST15-UPSTREAM.md", "DATA-COMPATIBILITY.md", "CURRENT-STATE.md", "PLAYER-GUIDE.md", "CONTROLS-AND-OPTIONS.md", "COOP-COMPATIBILITY-AUDIT.md", "NETWORK-VR-AVATARS.md", "CAMPAIGN-PROTOCOL-WIP.md",
                 "ANDROID-TOUCH-CONTROLS.md", "ANDROID-GAMEPAD.md", "COOP-PLAYER-LIMITS.md", "MULTIPLAYER-BROWSER.md"]
    documents = list(dict.fromkeys(documents))
    if candidate_at_least(args.label, 31) and not args.stable:
        documents += ["TEST31-PLAYER-NOTES.md", "TEST31-MENU-SETTINGS-AUDIT.md",
                      "TEST31-UPSTREAM-DECISIONS.md", "VR-INTERACTION-REQUIREMENTS.md"]
    if candidate_at_least(args.label, 31, "b") and not args.stable:
        documents += ["TEST31B-PLAYER-NOTES.md"]
    if candidate_at_least(args.label, 31, "c") and not args.stable:
        documents += ["TEST31C-PLAYER-NOTES.md"]
    if candidate_at_least(args.label, 32) and not args.stable:
        documents += ["TEST32-PLAYER-NOTES.md"]
    if candidate_at_least(args.label, 34) and not args.stable:
        documents += ["TEST34-PLAYER-NOTES.md", "TEST34-UPSTREAM-INTEGRATION.md"]
    for doc in documents:
        shutil.copy2(ROOT / "docs" / doc, output / doc)
    for notice in ["CREDITS.md", "THIRD-PARTY-NOTICES.txt", "LICENSE.md"]:
        shutil.copy2(ROOT / notice, output / notice)
        documents.append(notice)
    build = output / f"HaloCE-Quest-{args.label}-build.zip"
    with zipfile.ZipFile(build, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in [args.vr.name, args.flat.name, "manifest.json", "compatibility.json"] + documents:
            archive.write(output / name, name)
    with zipfile.ZipFile(source) as archive:
        if archive.testzip() is not None: raise SystemExit("Source archive checksum failure")
    with zipfile.ZipFile(build) as archive:
        if archive.testzip() is not None: raise SystemExit("Build archive checksum failure")
    files = [output / record["file"] for record in records] + [source, build, output / "manifest.json", output / "compatibility.json"]
    (output / "SHA256SUMS.txt").write_text("".join(f"{sha(path)}  {path.name}\n" for path in files))
    print(json.dumps({"output": str(output), "source_commit": commit, "apks": records}, indent=2))


if __name__ == "__main__":
    main()
