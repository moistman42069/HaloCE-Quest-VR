# Test20b — 1.0.2 candidate (private): performance fix + controller calibration

> **Superseded by [test20c](TEST20C-DELIVERY.md)** (code 23). Owner tested this pair on 2026-10-04: performance fixed; hand-comfort calibration tilted the gun, addressed in test20c.

Not a release. v1.0.1 was withdrawn by the owner; the public release is v1.0.0.
Supersedes the untested test20 pair (code 21). Do not publish without explicit
owner approval after device testing.

## Installation

- Quest/VR: `HaloCE-Quest-test20b.apk`
- Android/flat: `HaloCE-Android-test20b.apk`

Both are **1.0.2 / version code 22**, ARM64, API 28+, signed with the
established certificate. They install over 1.0, test18, the withdrawn 1.0.1 and
test20 (`adb install -r <apk>`). Do not uninstall or clear data. Back up maps,
saves and settings first. No game data is included.

## Changes

1. **1.0.1 Quest slowdown (from test20, unchanged):** Safe geometry streams
   through the fenced ring again instead of per-draw `glBufferSubData`; a
   `[render-perf]` log line every 10 s shows upload cost.
2. **Armed vs. empty-hand alignment (new):** controller calibration is one
   rigid correction per controller, so the held weapon and the empty hand move
   together. Saved calibrations are kept and leave the held weapon unchanged.
   Menu pages are renamed **Calibrate Left / Calibrate Right**; "Aim Pose" is
   now **Aim Source**. Config keys are unchanged; no migration.

Defaults unchanged: Legs + Arms, support grip, native action handoff,
third-person/right-hand vehicles, VR Safe and flat Normal geometry. Flat Android
gets the diagnostic line; calibration is VR-only.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test20b.apk` | 28,072,579 | `a7b7e2745867038164efa86b178f8eee64594b6fbcffd85e436508116eab3311` |
| `HaloCE-Android-test20b.apk` | 26,069,556 | `1020fed8448f9cef62e4397a4cf6739641f835ebfbd7c417eceb02c04c9c9e87` |

- Runtime source `daf23a34e0d7b04b74f4cc75bd8f66437b29b45e`; later commits are
  documentation only. Certificate SHA-256
  `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4` (no new key).
- Built serially (VR, then flat) from a clean tree; payload preservation,
  signing and 16 KB alignment verified. Equal byte counts to test20 come from
  alignment padding; hashes and payloads differ.

## Checks performed

- 17 runner suites pass, including `test_test20_render_perf` and new
  `test_test20_alignment` (2,000 random calibrations keep hand and weapon rigid;
  the old path broke all 2,000; held weapon bit-identical for saved values;
  empty → pistol → rifle → empty in both handedness modes; zero no-op; Aim
  Source Grip; invalid poses; menu/reset/reload key agreement).
- Cache formats: 127 passed, 4 missing-fixture skips.
- Package checks: versions, certificate, guides, test20b identity, fenced
  streaming and `[render-perf]` markers, new calibration labels.
- **Not done:** no device install, headset, phone or live-match session.

## Please test

1. **Quest frame rate (top priority):** main menu ~20 s, ~1 min campaign, ~1 min
   on a populated PvP server. It should feel like 1.0. Send the launch log.
2. **Hand/weapon alignment:** in VR Settings → Calibrate Right (or Left), set a
   noticeable Yaw or Roll. Then go empty hand → pistol → another weapon → empty
   hand. The hand and the gun should both follow the controller the same way.
   Try with support grip, a reload, and Gun Hand set to Left. Reset afterwards
   if you don't need calibration. A short video helps if it still looks wrong.
3. **Left eye:** Autumn cryo/control room; report corruption with the log.
4. **Regression pass:** reticle vs. impacts, grip, animations, body/fingers,
   vehicles, co-op if possible; flat touch/gamepad session.
5. **Updates:** Versions & updates must not offer 1.0.0.
