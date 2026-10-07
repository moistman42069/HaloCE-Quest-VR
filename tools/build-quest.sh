#!/usr/bin/env bash
# Build in the checkout (including Gradle/temp caches), using an installed SDK.
set -euo pipefail
cd "$(dirname "$0")/.."
mode="${1:-vr}"
case "$mode" in
  vr) flags=(--vr --release) ;;
  flat) flags=(--release) ;;
  *) echo "Usage: bash tools/build-quest.sh [vr|flat]" >&2; exit 2 ;;
esac
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/Sdk}"
export ANDROID_NDK_HOME="${ANDROID_NDK_HOME:-$ANDROID_HOME/ndk/27.2.12479018}"
export GRADLE_USER_HOME="${GRADLE_USER_HOME:-$PWD/build/gradle-cache}"
export TMPDIR="$PWD/build/tmp"
mkdir -p "$TMPDIR" "$GRADLE_USER_HOME"
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Djava.io.tmpdir=$TMPDIR"
python3 tools/generate-field-guide.py
# Required for every candidate: includes full menu construction with the guest
# ABI/allocator and Android input lifecycle, not just compilation or XML parsing.
python3 tools/run-quest-checks.py
# (--release, as OpenCE ships its builds: a failed check is written to the
# log and play goes on, instead of halting the game: test28)
python3 configure.py "${flags[@]}"
ninja -j "${HALO_BUILD_JOBS:-6}" android_apk
# The upstream Ninja APK edge lists native staging inputs only. Always let
# Gradle check Java/resources too, including on launcher-only edits.
cd port/android
if [[ "$mode" == vr ]]; then
  ./gradlew --console=plain -q -PhaloVr assembleVrDebug
else
  ./gradlew --console=plain -q assembleDebug
fi
