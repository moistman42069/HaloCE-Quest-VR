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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vr", type=Path, required=True)
    parser.add_argument("--flat", type=Path, required=True)
    parser.add_argument("--build-tools", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", default="test17")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.label):
        parser.error("label must contain letters, digits, underscore or dash")
    subprocess.run(["git", "diff", "--exit-code", "HEAD", "--"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT)
    if untracked.strip():
        raise SystemExit("Commit intended source files before packaging; untracked files remain")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    records = []
    for path, package, vr in [(args.vr, "com.halo.decomp.vr", True), (args.flat, "com.halo.decomp", False)]:
        signed = subprocess.check_output([str(args.build_tools / "apksigner"), "verify", "--print-certs", str(path)], text=True)
        if "certificate SHA-256 digest: " + CERTIFICATE not in signed:
            raise SystemExit("APK signing certificate differs from the user's test8 key")
        badging = subprocess.check_output([str(args.build_tools / "aapt"), "dump", "badging", str(path)], text=True)
        if f"package: name='{package}'" not in badging or "native-code: 'arm64-v8a'" not in badging:
            raise SystemExit("Wrong package or ABI: " + str(path))
        if f"versionName='1.0-{args.label}'" not in badging:
            raise SystemExit("Wrong candidate version: " + str(path))
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise SystemExit("APK ZIP checksum failure")
            names = archive.namelist()
            for guide in ["player-guide", "controls", "touch", "settings"]:
                if "assets/guide/"+guide+".txt" not in names:
                    raise SystemExit("Bundled guide missing: "+guide)
            guest = archive.read("assets/halo_guest.elf")
            host = archive.read("lib/arm64-v8a/libmain.so")
            dex = b"".join(archive.read(name) for name in names if re.fullmatch(r"classes\d*\.dex", name))
            for marker in [b"ServerBrowser;", b"ServerListing;", b"RunLog;", b"openGameLog", b"CoopLauncher;",
                           b"CoopPublisher;", b"prepareGameExit", b"PvpLauncher;", b"TouchLayout;", b"UpdatePolicy;",
                           b"upstreamVersion", b"compatibility.json", b"GamepadSupport;", b"GamepadNavigation;", b"GameDataLibrary;", b"GameDataManager;", b"ISO/revision versions", b"https://halo.milenko.org/v1/games.txt"]:
                if marker not in dex: raise SystemExit("Browser missing from APK: " + repr(marker))
            if not guest.startswith(b"\x7fELF") or not host.startswith(b"\x7fELF"):
                raise SystemExit("Missing native ELF payload")
            if b"/active-data.txt" not in host or b"/profile.properties" not in host:
                raise SystemExit("Native managed-data selection missing")
            if b"vr pose: host negotiated visual avatars v1" not in guest:
                raise SystemExit("Negotiated avatar support missing")
            if vr and (b"HANDS ONLY" not in guest or b"NEXT PAGE (%ld/%ld)" not in guest):
                raise SystemExit("Body modes or paged settings missing")
            identity = ("HaloCE Quest " + args.label + " candidate").encode("ascii")
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
                "source_commit": commit, "branch": branch, "runtime_accepted": False,
                "publication": "held pending owner candidate testing and approval",
                "prior_device_report": "test14 accepted for release; owner reports test16 action animations improved; test16 multiplayer log faults addressed in test17; candidate testing pending",
                "certificate_sha256": CERTIFICATE, "apks": records,
                "source_zip": {"file": source.name, "sha256": sha(source)},
                "native_host_version": network_value("HALO_PORT_NETWORK_VERSION"), "accepted_host_versions": list(range(network_value("HALO_PORT_NETWORK_VERSION_MINIMUM"), network_value("HALO_PORT_NETWORK_VERSION_MAXIMUM")+1)),
                "campaign_protocol": 0xCE01, "campaign_runtime_verified": False,
                "avatar_protocol": 1, "avatar_message_ids": [37, 38], "avatar_prior_owner_report": "VR body movement visible on flat Android in accepted test14; current action handoff regression pending",
                "directory": "https://halo.milenko.org/v1/games.txt"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    compatibility = {"schema": 1, "project": "moistman42069/HaloCE-Quest-VR",
        "tag": "halo-ce-quest-"+args.label, "source_commit": commit, "minimum_app_code": 15,
        "save_policy": "preserve", "config_policy": "preserve", "vr_and_coop_integrated": True,
        "native_minimum": network_value("HALO_PORT_NETWORK_VERSION_MINIMUM"),
        "native_maximum": network_value("HALO_PORT_NETWORK_VERSION_MAXIMUM"), "campaign_protocol": 0xCE01,
        "editions": {record["package"]: {"apk": record["file"], "sha256": record["sha256"],
            "bytes": record["bytes"], "version_code": record["version_code"], "min_sdk": record["min_sdk"]} for record in records}}
    (output / "compatibility.json").write_text(json.dumps(compatibility, indent=2)+"\n")
    documents = [args.label.upper()+"-DELIVERY.md", args.label.upper()+"-PROGRESS.md", "GAME-DATA-LIBRARY.md", "TEST15-DELIVERY.md", "TEST15-PROGRESS.md", "TEST15-UPSTREAM.md", "DATA-COMPATIBILITY.md", "CURRENT-STATE.md", "PLAYER-GUIDE.md", "CONTROLS-AND-OPTIONS.md", "COOP-COMPATIBILITY-AUDIT.md", "NETWORK-VR-AVATARS.md", "CAMPAIGN-PROTOCOL-WIP.md",
                 "ANDROID-TOUCH-CONTROLS.md", "ANDROID-GAMEPAD.md", "COOP-PLAYER-LIMITS.md", "MULTIPLAYER-BROWSER.md"]
    documents = list(dict.fromkeys(documents))
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
