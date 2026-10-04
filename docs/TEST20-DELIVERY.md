# Test20 — 1.0.2 performance-fix candidate (private)

Not a release. v1.0.1 was withdrawn by the owner; the public release is v1.0.0.
Do not publish this pair without explicit owner approval after device testing.

## Installation

- Quest/VR: `HaloCE-Quest-test20.apk`
- Android/flat: `HaloCE-Android-test20.apk`

Both are **1.0.2 / version code 21**, ARM64, API 28+, signed with the
established certificate, so they install over 1.0, test18 and the withdrawn
1.0.1 (`adb install -r <apk>`). Do not uninstall or clear data. Back up maps,
saves and settings first. No game data is included.

## Change

One focused runtime change plus diagnostics (details and evidence:
[TEST20-PROGRESS.md](TEST20-PROGRESS.md)):

1. Safe geometry (the VR default) streams vertex/index data through the
   fence-managed ring again, as in test18/1.0, instead of 1.0.1's per-draw
   `glBufferSubData` that stalled the Quest game thread for 44–248 ms a frame.
2. A `[render-perf]` line every 10 s reports draws, uploads, upload time,
   stream wraps and ring-fence wait, so a log can confirm the fix.

Everything else from 1.0.1 is kept: VAO restoration, native browser, PvP crash
guard, reticle, updater, imports. Defaults are unchanged: Legs + Arms, support
grip, native action handoff, third-person/right-hand vehicles, VR Safe and flat
Normal geometry. **Flat Android** uses Normal geometry by default, which never
took the 1.0.1 slow path; it only gains the diagnostic line (and the fix if
Safe was turned on manually).

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test20.apk` | 28,072,579 | `4e9f4a67490751e0a97b8659349c45696c3e82a76dd59626188e8369415cc5ee` |
| `HaloCE-Android-test20.apk` | 26,069,556 | `fe52eb50b2696716d84033adf8c331e8f3feb6e48f047ab32766a9b7e671b6d6` |

- Runtime source: `8dc8800fc9408a42e2e971072c20dff95d8ec95f` (branch
  `test20-safe-upload-performance`); later commits change documentation only.
- Certificate SHA-256 `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`
  (same key as every prior release; no new key).
- Built serially (VR, then flat) from a clean tree; compaction verified payload
  preservation, signing and 16 KB alignment for both. The flat APK's byte count
  equals test19's by alignment padding only; its hash and guest differ.

## Checks performed

- All 16 runner suites pass, including new `test_test20_render_perf`
  (ring-range invariant, no `glBufferSubData`/`glFinish` in Safe, diagnostic
  line, updater never offering v1.0.0 to code 20/21).
- Cache formats: 127 passed, 4 missing-fixture skips (same as test19).
- Package checks: versions, packages, ABI, certificate, guide/credits payloads,
  test20 identity, fenced-streaming and `[render-perf]` markers present, 1.0.1
  ordered-upload marker absent; SHA256SUMS over APKs and source/build ZIPs.
- **Not done:** no device install, headset session, phone session or live match.
  Compilation and tests do not show the regression is resolved on hardware.

## Please test

1. **Quest frame rate (main check):** launch, stay in the main menu ~20 s, play
   ~1 min of campaign, join a populated PvP server for ~1 min. It should feel
   smooth again, like 1.0. Send the launch log from `Download/HaloCE`.
   The log should show `[vr-perf]` near 72 frames/s and `[render-perf]` uploads
   of a few ms or less.
2. **Left eye:** replay the Autumn cryo/control-room path and watch each eye.
   Report any left-eye corruption with the log.
3. **Quick regression pass:** reticle vs. shot impacts, two-hand grip, reload
   and weapon actions, body/fingers, a vehicle, co-op if convenient.
4. **Flat Android:** short campaign or PvP session with touch or gamepad; send the log.
5. **Updates:** Launcher → Versions & updates must not offer 1.0.0 as an update.
