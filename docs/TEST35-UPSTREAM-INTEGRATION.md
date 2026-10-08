# Test35 OpenCE Build 148 integration audit

## Upstream identity

The official [OpenCE Build 148 release](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-148)
identifies commit [`ff47e47ad6f54bc533cee2a0fe57232c8f63d614`](https://github.com/OpenCommunityEdition/OpenCE/commit/ff47e47ad6f54bc533cee2a0fe57232c8f63d614)
and is marked Latest. The release note is “Correct negative particle radii as
maps load.” The tag range from Build 147 includes the native build/error-screen
diagnostic change and point-physics runtime guard as well. The Test35 port
adapts the Android/Quest-relevant behavior to this app's CE cache validation
and native guest build; it is not a byte-for-byte desktop port.

## Behavior carried forward

- **Tag-load repair:** `tag_validate_non_negative` uses `!(value >= 0.0f)` so
  both negative values and NaN are corrected to zero and reported through the
  existing correction path. All radius/width fields listed by the upstream
  Build 148 commit are wired into their matching render/effect schemas.
- **Runtime defense:** point physics uses the same comparison before its
  existing nonnegative assertion. A once-only silent error message records
  this fallback if an invalid radius reaches runtime despite tag checks.
- **Native halt details:** the engine version output and halt screen identify
  the native platform/build flavor. Recent nonempty errors are shown newest
  first, with bounded line count and length; the full log remains available in
  the game data folder. Android guest compilation uses the upstream
  `updater_defines` configuration for its release/debug flavor.

## Compatibility and limits

Build 148 does not change network compatibility: Test35 remains on OpenCE
network **23**, so network-23 peers remain protocol-compatible, subject to
game content, game state, server availability and network reachability. The
protocol-21 public v1.0.12 release remains unchanged and cannot join network-23
games.

Only invalid negative/NaN collision-size inputs are changed. Valid nonnegative
tag values and the current VR/mobile input, camera, scope, touch and menu paths
are not intentionally modified. The runtime clamp is a final safety net, not
a guarantee that every malformed custom map is otherwise valid. Automated
source checks do not certify every map or device.

## Excluded upstream build tooling

Build 148's `tools/linux_build.py` and `tools/windows_build.py` changes apply
to upstream desktop build graphs. This app builds the Quest and Android guest
through its own shared Android build graph, so only the corresponding native
main-file compile defines were applied there. Upstream desktop binaries and
assets are not bundled in the APKs.
