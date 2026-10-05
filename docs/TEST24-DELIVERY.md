# Test24 — 1.0.6 candidate (private): co-op cutscenes on joining devices

Not a release. The public release is v1.0.3 (test21b, code 27). Do not
publish without explicit owner approval. Evidence, cause and status:
[TEST24-PROGRESS.md](TEST24-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test24.apk`
- Android/flat: `HaloCE-Android-test24.apk`

Both are **version 1.0.6 / code 31**, ARM64, API 28+, signed with the same
certificate as v1.0.2 to 1.0.5, so they install over any of them without
uninstalling (`adb install -r <apk>`). Do not uninstall or clear data. Back up
first. **Co-op needs 1.0.6 on every device.**

## Changes

1. **Co-op cutscenes (both).** Cutscene characters on the device that joined
   now animate as on the host. The cause: only the host runs the mission
   script, and the script "wakes up" the part of the map a cutscene plays in.
   The joining device was never told, so that area stayed asleep there: its
   characters never animated (T-pose) while the host's positions still moved
   them (sliding). The joining device now wakes the same area. This applies to
   every campaign cutscene, on Quest and phone alike.
2. **Seat postures (both).** Characters a cutscene sits or stands in a seat
   take that posture on the joining device too.
3. **1.0.5's cutscene change removed (both).** It addressed the wrong cause;
   normal co-op movement is exactly as in 1.0.4.
4. **Diagnostics (both).** The joining device logs each time it follows the
   host's cutscene area.
5. **How to join (both).** New launcher button **How to join co-op & find
   servers** (also first in the Field guide) with step-by-step hosting,
   joining and in-game server browser instructions; the co-op dialogs and
   server lists show the short version.
6. **Co-op listed by default (both).** In Host campaign, **List this game in
   the co-op server browser** starts ticked. Untick it for a private game.

Unchanged from 1.0.5: grenade on Left X, the BUTTONS page, and everything else.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test24.apk` | 28,084,867 | `48b9a7a8c13db7f975d3763d7005621da77e7b6251a2e7498211ccce86ddac8b` |
| `HaloCE-Android-test24.apk` | 26,073,652 | `b0767f78a604f4b973224c14630832d87f9e4ed63223b43664621e79b03de3d1` |

Runtime source `47a178dc` (cutscene fix `7700fdc9`, launcher `f3532d28`) on branch `test21-hands-body`; later commits
change only documentation and packaging tooling. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, the same as
v1.0.2 to 1.0.5. Built serially from a clean tree; payload, signing and 16 KB
alignment verified.

## Checks performed

- 25 runner suites pass, including new `test_test24`: the real host capture,
  network and client replay code sends the four cutscene-area calls and the
  seat call in order and replays them with the host's exact arguments;
  another game's calls are refused; the engine's activation reads that area;
  earlier message IDs are unchanged; the 1.0.4 movement code is restored
  byte for byte; the launcher steps name the real buttons and the listing box
  starts ticked.
- Cache formats: 127 passed, 4 missing-fixture skips.
- Both editions compile without warnings in the changed files; packaging checks
  pass.
- **Not done:** no phone or headset session. Your tests decide.

## Please test

1. **Co-op cutscene (most important):** put 1.0.6 on both devices. Host a10
   co-op on the phone and join from the Quest. Watch the opening cutscene on
   the Quest: characters should walk and animate as on the phone. Then swap
   (host on the Quest, join from the phone) and watch it on the phone. If you
   can, also try a later mission's cutscene. Send both logs either way.
2. **Normal co-op:** play a few minutes after the cutscene (move, fight, a
   vehicle) to confirm nothing else changed.
3. **Launcher:** open **How to join co-op & find servers** and check the steps
   read clearly. Open Campaign co-op > Host campaign: the server browser box
   should already be ticked, and your partner should find the game under
   Browse / join.
