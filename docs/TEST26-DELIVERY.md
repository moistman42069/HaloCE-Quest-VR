# Test26 — 1.0.8 candidate (private): co-op fixes, controls, upstream Build 128

Not a release. The public release is v1.0.6 (code 32). Test25 (1.0.7) was
delivered but not yet tested; test26 contains all of it. Do not publish
without explicit owner approval. Details: [TEST26-PROGRESS.md](TEST26-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test26.apk` (package `com.halo.decomp.vr`)
- Android/flat: `HaloCE-Android-test26.apk` (package `com.halo.decomp`)

Both are **version 1.0.8 / code 34**, ARM64, API 28+, signed with the same
certificate as every release since v1.0.2, so they install over v1.0.6 or
test25 without uninstalling (`adb install -r <apk>`). Do not uninstall or
clear data. Back up first.

**Co-op needs 1.0.8 on both devices.** The co-op protocol changed (CE02). A
1.0.7 or older device is listed as "another app version" and refused with a
plain message. PvP multiplayer is unchanged (network 11).

Edition-specific: the controls, HUD, wrist, melee and finger changes are VR
only. The co-op fixes, glass, the red-text fix, the start fix, the upstream
engine speed-ups and the launcher text are shared.

## Changes

1. **Co-op crash fixed (both).** The joining device halted ("blue screen")
   when a crewman was shot. The cause was not the pistol: the host replays
   every character's speech on the joining device, and a death scream that
   arrived after the death tripped a safety check. That no longer stops the
   game.
2. **Co-op cutscenes on the joining device (both).** Characters are now put
   where the host puts them at once (no wrong places, no gliding), play the
   exact animation the host chose, and pass through consoles as on the host.
   This is general, not a10-specific. The log no longer fills with "fell
   outside world" lines.
3. **Glass breaks for both players (both)**, from OpenCE.
4. **Quest 2 red text in multiplayer fixed.** The Quest 2's graphics preset
   and the host's rules fought every frame. Cosmetic effects stay off for
   speed; anything that matters for fairness is still drawn. The warning
   appears once per game at most.
5. **First Quest start fixed (both).** On the original Quest's older Android,
   the game could not reserve its memory after the disc mounted. It now
   reclaims the space as newer Android versions do; if it still fails, the
   message says the files are fine and to restart and send the log.
6. **Reticle toggle (Quest):** click the **left stick** to hide or show the
   reticle (it starts shown). **Crouch moved** to pushing the **right stick
   straight down and holding**. Ducking still crouches.
   **Controls → L Stick Click: Crouch** puts crouch back on the click, exactly
   as before.
7. **HUD tap (Quest):** bring the **gun hand to the side of your head** to
   hide or show the HUD (on by default). The reach is adjustable on the new
   **Head Gestures** page, which also sets the flashlight tap's reach.
8. **Wrist HUD (Quest, optional, off by default):** HUD + Reticle →
   **Wrist HUD: On** puts shields/health, ammo/grenades and the motion
   tracker on the back of your off-hand wrist; look at it like a watch.
9. **Settings grouped (Quest):** new **HUD + Reticle** and **Head Gestures**
   pages; **Reticle** and **R Down** on Buttons. Saved settings are kept.
10. **Impact melee (Quest):** the whole gun hits, not just its middle, and
    fast swings follow through a little, so swings that stopped just short of
    an enemy now land. Walls still block.
11. **Fingers (Quest):** fingers bend smoothly joint by joint against
    surfaces, without snapping or twisting.
12. **Upstream OpenCE Build 128 (both):** engine speed-ups with many enemies,
    glass sync, and a joining device never reverting on its own.

Unchanged: everything in test25 (vehicle diagnostics, first-person glass and
horizon, settings rows, Reset Offsets), third-person vehicles and right-hand
steering as defaults, comfort settings, PvP network version 11, the
launcher's updater (it only installs this project's releases).

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test26.apk` | 28,162,691 | `794b6576c3b98c591cc34d0162a8ab5a148fa81304cfbbcbdb4e0425ab5aa08c` |
| `HaloCE-Android-test26.apk` | 26,085,940 | `cd150f786e04c8996ef1345bb72561256a1f706e5f06c11bf8ac65bfcb25655d` |

Runtime source `2bd5cb12` on branch `test26-coop`; later commits change
only documentation. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, as every
release since v1.0.2. Built serially from a clean tree; payload, signing and
16 KB alignment verified.

## Checks performed

- 28 runner suites pass, including the new `test_test26`, which runs the
  production code for each fix and reproduces two of the 1.0.7 faults (the
  Quest 2 fight; the first Quest's stale error). Three defects were caught by
  the new tests and fixed before this build (see TEST26-PROGRESS).
- Cache formats: 127 passed, 4 missing-fixture skips.
- Both editions compile without warnings in the changed files; packaging
  checks pass.
- **Not done:** no phone or headset session. Your tests decide.

## Please test

1. **Co-op (most important):** install 1.0.8 on both devices. Host on the
   phone, join with the Quest, and play the first level through the bridge
   cutscene and the first fights. On the Quest, check that characters stand
   and move where they do on the phone, and that shooting crewmen no longer
   stops the game. Break some glass. Send both logs.
2. **Quest 2 (if you have one):** join a multiplayer game. There should be
   no wall of red text.
3. **Original Quest (if available):** start the game after the disc mounts.
4. **Controls:** click the left stick (reticle hides and shows); push the
   right stick down (crouch); try Controls → L Stick Click: Crouch and back.
   Touch your gun hand to the side of your head (HUD hides and shows). Try
   the Head Gestures distances.
5. **Wrist HUD:** turn it on (HUD + Reticle), look at your off-hand wrist like
   a watch, and say whether it is readable and placed well.
6. **Melee and fingers:** swing the gun at an enemy at close range; press
   your free hand's fingers against a wall and slide them.
