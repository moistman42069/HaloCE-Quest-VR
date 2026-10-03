#!/usr/bin/env bash
# Installs and starts the VR build on a Steam Frame over USB.
#
#   tools/steam_frame/deploy.sh [--maps DIR] [--config KEY=VALUE ...] [--no-install] [--no-launch]
#
# The game's data, settings and saves live in the headset's Documents/HaloCE
# (Android's /sdcard/Documents/HaloCE in Lepton), which a Lepton reset keeps;
# --maps copies a maps folder there over SSH (tools/steam_frame/extract_maps.py
# makes one from your disc image). --config sets a [section] key in its
# config.toml, e.g. --config vr.dump_frame=200.
#
# Before running it, start "Lepton Development" from the Frame's Steam library.
#
# To play without the Mac, register the build once as a Lepton devkit title, which
# shows in the Steam library as HaloCEVR (docs/VR_ARCHITECTURE.md); deploy.sh then
# keeps its copy of the APK up to date.
# Set FRAME_HOST to the headset SSH endpoint before running this deployment helper.
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
apk="$root/port/android/app/build/outputs/apk/vr/debug/app-vr-debug.apk"
package="com.halo.decomp.vr"
frame_host="${FRAME_HOST:?Set FRAME_HOST to the headset SSH endpoint}"
adb_bin="${ADB:-${ANDROID_HOME:-$HOME/Library/Android/sdk}/platform-tools/adb}"
[[ -x "$adb_bin" ]] || adb_bin="$(command -v adb)"
maps=""
install=1
launch=1
settings=()

while (($#)); do
    case "$1" in
        --maps) maps="$2"; shift 2 ;;
        --config) settings+=("$2"); shift 2 ;;
        --no-install) install=0; shift ;;
        --no-launch) launch=0; shift ;;
        *) echo "unknown option $1" >&2; exit 2 ;;
    esac
done

# Android in Lepton: forward its adb port over the USB device's
"$adb_bin" start-server >/dev/null
"$adb_bin" -s frame forward tcp:5555 tcp:5555 >/dev/null
"$adb_bin" connect 127.0.0.1:5555 >/dev/null
device=127.0.0.1:5555
if ! "$adb_bin" -s "$device" shell true 2>/dev/null; then
    echo 'Start "Lepton Development" from the Frame'"'"'s Steam library, then retry.' >&2
    exit 1
fi

if [[ -n "$maps" ]]; then
    [[ -f "$maps/ui.map" ]] || { echo "$maps has no ui.map" >&2; exit 1; }
    ssh "$frame_host" 'mkdir -p ~/Documents/HaloCE/maps'
    rsync -a --partial "$maps/" "$frame_host:Documents/HaloCE/maps/"
fi

if ((${#settings[@]})); then
    # config.toml is written by the game on its first start; edit it in place
    for setting in "${settings[@]}"; do
        key="${setting%%=*}"
        value="${setting#*=}"
        section="${key%%.*}"
        name="${key#*.}"
        ssh "$frame_host" "python3 - ~/Documents/HaloCE/config.toml '$section' '$name' '$value'" <<'PY'
import re, sys
path, section, name, value = sys.argv[1:]
text = open(path).read() if __import__("os").path.exists(path) else ""
pattern = re.compile(r"(^\[%s\]\n(?:(?!^\[).*\n)*?)^%s = .*$" % (re.escape(section), re.escape(name)), re.M)
if pattern.search(text):
    text = pattern.sub(lambda m: m.group(1) + "%s = %s" % (name, value), text, count=1)
elif re.search(r"^\[%s\]$" % re.escape(section), text, re.M):
    text = re.sub(r"^\[%s\]$" % re.escape(section), "[%s]\n%s = %s" % (section, name, value), text, count=1, flags=re.M)
else:
    text += "\n[%s]\n%s = %s\n" % (section, name, value)
open(path, "w").write(text)
print("config.toml: %s.%s = %s" % (section, name, value))
PY
    done
fi

if ((install)); then
    "$adb_bin" -s "$device" install -r "$apk" | grep -i -E 'success|fail'
    # the Steam library's HaloCEVR title (a Lepton devkit game) runs its own copy
    if ssh "$frame_host" 'test -d ~/devkit-game/HaloCEVR'; then
        scp -q "$apk" "$frame_host:devkit-game/HaloCEVR/HaloCE-VR.apk" && echo "updated the HaloCEVR Steam title"
    fi
fi

if ((launch)); then
    "$adb_bin" -s "$device" shell am force-stop "$package"
    "$adb_bin" -s "$device" logcat -c
    "$adb_bin" -s "$device" shell am start -n "$package/com.halo.decomp.LauncherActivity" >/dev/null
    echo "started $package; logs: $adb_bin -s $device logcat -s halo"
fi
