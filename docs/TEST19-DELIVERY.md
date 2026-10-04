# Test19 — 1.0.1 testing candidate

## Installation

- Android/flat: `HaloCE-Android-test19.apk`
- Quest/VR: `HaloCE-Quest-test19.apk`

Both use **1.0.1 / version code 20** and the established signing identity. Install
over the corresponding app; do not uninstall or clear data. Keep your game files,
saves and configuration backed up. Use this same candidate on both co-op peers.
No game maps are included. Public 1.0/test14 remain unchanged; this is not a release.

## Changes

1. Guard the invalid visibility-cluster replica state found after a successful
   populated PvP join; keep host object ownership and log the recovered condition.
2. Add signed OpenCE public discovery inside Multiplayer > System Link, with
   population sorting, stable paged rows, refresh and cancelable host resolution.
3. Correct updater handling of equal/older public version codes. Add separate
   verified official upstream ZIP downloads without replacing mod components.
4. Align VR reticle to the native firing ray and actual world-space collision point.
5. Restore renderer vertex-array state and use ordered Safe geometry uploads.
6. Improve valid deep-tree ISO/XISO import and incomplete/corrupt-image diagnostics.
7. Expand co-op setup help and update bundled controls, compatibility and credits.

Controls/defaults remain: Legs + Arms, deliberate support Grip, native action
handoff, third-person/right-hand vehicles, VR Safe and flat Normal geometry.
Network host 11, reviewed distributed clients 9–11, two-player CE01 campaign.

## Verification and limits

The final package manifest records source/runtime commits, certificate and hashes;
SHA256SUMS covers both APKs and matching source/build archives. Continuation and
check results are in TEST19-PROGRESS.md. Community triage and primary references are
in TEST19-COMMUNITY-REVIEW.md. The bundled player guide documents complete inputs,
settings, imports, multiplayer and co-op. No new headset/phone acceptance is implied.

## Please test before publication

- Replay the Autumn cryo-room/control-room path, watch each eye and compare Safe
  frame timing. Intermittent left-eye corruption has a candidate workaround,
  not a hardware-confirmed resolution.
- Shoot near/far walls with either hand, scopes, support grip and reload; compare
  impacts with the reticle offline and online (spread still applies).
- Browse System Link from a fresh launch, refresh/page/cancel, join a populated
  host, die/respawn and follow a map rotation. Empty/offline browsing must stay usable.
- Test matching Quest + flat co-op lobby, AI, checkpoints, transition and avatars;
  regular movement, gamepad/touch, grip/animation handoff and vehicles are regressions.
- Open Versions & updates while on this candidate; public code 19 must be reported
  as older, not installed as a downgrade. Check the separate upstream-download flow.
- Import source images/extracted maps without modifying existing sets or saves.
  On a failure, send exact file sizes/hashes and the new error; do not send game data.

Include the matching Download/HaloCE launch logs with each test result. Review
private invites/device/path details before sharing logs publicly.
