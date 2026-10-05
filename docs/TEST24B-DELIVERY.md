# Test24b — 1.0.6 candidate (private): comfort settings, SPV1 notice

Not a release. The public release is v1.0.3 (test21b, code 27). Do not
publish without explicit owner approval. Details:
[TEST24B-PROGRESS.md](TEST24B-PROGRESS.md). Everything in test24 (co-op
cutscene fix, launcher join steps, co-op listed by default) is included:
[TEST24-DELIVERY.md](TEST24-DELIVERY.md).

## Installation

- Quest/VR: `HaloCE-Quest-test24b.apk`
- Android/flat: `HaloCE-Android-test24b.apk`

Both are **version 1.0.6 / code 32**, ARM64, API 28+, signed with the same
certificate as v1.0.2 to 1.0.6 (code 31), so they install over any of them
without uninstalling (`adb install -r <apk>`). Do not uninstall or clear data.
Back up first. **Co-op needs the same build on every device.**

## Changes

1. **COMFORT page (Quest).** VR Settings → COMFORT: Turning (Smooth / Snap),
   Smooth Speed (30–300 degrees a second), Snap Angle (10–90 degrees), Vignette
   (Off / Low / Medium / High) and Vignette When (Move + Turn / Turning Only /
   Always). Controls → Turning still works and now also offers Snap 22.5 and 60.
2. **Comfort vignette (Quest).** When switched on, the edges of your view
   darken while you move or turn with the sticks (and while driving), fading
   in quickly and out when you stop. The centre always stays clear, and it
   never shows in menus or cutscenes. Off by default, so nothing changes until
   you turn it on.
3. **SPV1 notice (both).** The launcher's SPV1 button says "(not working yet)",
   and its section opens with a warning that SPV1 is not functioning and will
   be refined in a future release.

Unchanged: your turning settings (the game turns exactly as before until you
change them), buttons, co-op and everything else.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test24b.apk` | 28,154,499 | `18441ebf48a8485d35a4f7fe63c7b2f89f9e3ea34c5f0dbe18a71a312c3db2c9` |
| `HaloCE-Android-test24b.apk` | 26,081,844 | `13a9c827701585cbbb51f38ce41b5a6a899892eceed08c51b91093a1584f490b` |

Runtime source `d066d1e2` on branch `test21-hands-body`; later commits
change only documentation and packaging tooling. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, the same as
v1.0.2 to 1.0.6 (code 31). Built serially from a clean tree; payload, signing
and 16 KB alignment verified.

## Checks performed

- 26 runner suites pass, including new `test_test24b`:
  - the vignette's timing, triggers and limits (never in cutscenes, the 3D
    screen, menus, or when off);
  - its shape: nothing at rest, growing with motion, centre always clear;
  - its drawing uses only GL calls the game imports;
  - the Turning, Smooth Speed and Snap Angle rows behave as described;
  - the SPV1 notice is in place.
- `test_test20d`: the menu's defaults still read as choices, and every Controls
  → Turning choice round-trips.
- Cache formats: 127 passed, 4 missing-fixture skips.
- Both editions compile without warnings in the changed files; packaging checks
  pass.
- **Not done:** no phone or headset session. Your tests decide.

## Please test

1. **Comfort page:** VR Settings → COMFORT. Switch Turning between Smooth and
   Snap; change Smooth Speed and Snap Angle and turn with the right stick to
   feel each.
2. **Vignette:** set Vignette to Medium. Walk and turn: the edges should
   darken softly and clear when you stop. Try Low and High, Turning Only and
   Always, and drive a Warthog. Open the pause menu and watch a cutscene: no
   vignette there.
3. **Default:** with Vignette Off, everything looks exactly as before.
4. **SPV1:** in the launcher, the SPV1 button and section show the warning.
5. **Co-op (from test24, if not yet tried):** the a10 opening cutscene on the
   joining device; send both logs.
