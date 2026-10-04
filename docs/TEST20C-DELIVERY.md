# Test20c — 1.0.2 candidate (private): hand/gun calibration and floating hands

> **Superseded by [test20d](TEST20D-DELIVERY.md)** (code 24). Owner tested this pair on 2026-10-04: migration worked; the held pistol sat ahead of and above the real controller and swung around a point behind the hand, addressed in test20d.

Not a release. v1.0.1 was withdrawn; the public release is v1.0.0. Supersedes
test20b (code 22). Do not publish without explicit owner approval. Full
evidence and status: [TEST20C-PROGRESS.md](TEST20C-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test20c.apk`
- Android/flat: `HaloCE-Android-test20c.apk`

Both are **1.0.2 / version code 23**, ARM64, API 28+, signed with the
established certificate; they install over 1.0, 1.0.1, test20 and test20b
(`adb install -r <apk>`). Do not uninstall or clear data. Back up first.

## Changes

1. **Hands and gun calibrate separately.** VR Settings → **Left Hand / Right
   Hand** turn only the visible hand (default pitch −70, from the owner's
   video). **Gun** sets the gun's own angle and grip position; shots and
   reticle follow it. **Controller Left/Right** (formerly Calibrate) remains a
   tracking fix moving both. Rotations saved on the old pages move to the Hand
   pages once, so the gun points with the controller again.
2. **Hand tracking** on the Body page → **Hands**: Body IK (default,
   unchanged), **Floating** (hands exactly at the controllers, arms hidden),
   **Float + Arms** (hands exactly at the controllers, arms drawn from a
   floating shoulder). Independent of the Body visibility choice.
3. **Hands Only** no longer looks cut off: hidden arms gather just behind
   the wrist.
4. Safe geometry stream slots grow to 32 MB (Autumn measured 15.6 MB/frame).

Kept: test20 performance fix (device-confirmed with test20b), Legs + Arms,
support grip, native action handoff, third-person/right-hand vehicles, VR Safe
and flat Normal geometry. Flat Android changes are diagnostic/settings text
only; hand features are VR-only.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test20c.apk` | 28,076,675 | `c1cd52d021d83aeab22cb08813bec6e41da03819889435abd099c240a02d40ed` |
| `HaloCE-Android-test20c.apk` | 26,069,556 | `60fd6cdc50cdc90933ed052b5c7d1368743763cd7f70b5f670663a5aad4a84e7` |

Runtime source `7b9de936ae1a7fc22b91d97f8161e2dfa9357854`; later commits are
documentation only. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. Built
serially from a clean tree; payload, signing and 16 KB alignment verified.

## Checks performed

- 18 runner suites pass, including new `test_test20c_hands` (500 gun
  calibrations for both hands with left mirroring; two-handed override; hand
  rotation never reaches the gun; migration cases; 5,000 floating-shoulder
  reach cases; wrist-side arm collapse; 32 MB Safe slots).
- Cache formats: 127 passed, 4 missing-fixture skips.
- Package checks: versions, certificate, guides, test20c identity, new menu
  labels and settings text.
- **Not done:** no headset/phone session. Hand look, floating feel and the
  cuff need your eyes.

## Please test

1. **Default hands:** without touching any setting, empty hands should look
   like the end of your video (palms down, fingers forward). If you saved
   values before, they were moved to the Hand pages; check them there.
2. **Gun:** pick up the pistol and the rifle. The barrel and shots should go
   where the controller points, as in your video at zero calibration. Only if
   you want a different angle, use VR Settings → Gun.
3. **Floating:** Body → Hands → Floating, then Float + Arms. Reach far, cross
   your hands, grip a rifle with both hands, reload, throw a grenade, melee,
   and switch modes during play. Report any stretched arms, doubled hands or a
   wrong gun angle.
4. **Hands Only:** Body → Hands Only; check that the wrists look closed.
5. **Body IK** with Legs + Arms should feel exactly like test20b.
6. Autumn cryo room: watch the left eye; send the log either way.
