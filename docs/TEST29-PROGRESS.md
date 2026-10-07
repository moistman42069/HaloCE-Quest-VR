# Test29 checkpoint: OpenCE build 144 (network 21), HUD tap fix and settings, wrist HUD placement, two-hand movement, PR #1

Updated 2026-10-07. Private candidate **test29, version 1.0.11 / code 37**,
branch `test29-opence-144`, on top of the published v1.0.10. Not released.

## Requests

1. Check for recent OpenCE/upstream updates and integrate them, without
   missing anything for multiplayer and co-op compatibility.
2. HUD head tap: tapping the right side of the head hid the HUD, and tapping
   again did not bring it back, so players were stuck without a HUD. The
   owner asked for three things:
   - a simple HUD on/off in the HUD settings;
   - an option to turn the head gesture off (on by default);
   - a thorough fix of the gesture itself.
3. Wrist HUD: a little off-centre and not on top of the wrist. Adjust it, and
   add position options to the menu.
4. A player's report: with the gun held in both hands, the left stick's
   forward slowly turned into a strafe, and letting go reset it. Fix only if
   the cause is conclusive.
5. Pull request #1 (glasses field of view and resolution steps): add it
   without regressions.

## 1. OpenCE build 144 (network 21)

- **What OpenCE changed:** builds 140–144 came out on 2026-10-07. Build 141
  moved to **network 21** with the co-op garbage throttle. The live directory
  that day listed its co-op games (a30, a50) on network 21, which 1.0.10
  (network 20) refuses.
- **How it was merged:** the 148 files changed between builds 138 and 144
  were merged three ways (scripts in `work/test29`):
  - 93 files this app had unchanged from OpenCE took build 144's version;
  - 27 merged cleanly;
  - 11 conflicts were resolved by hand.
- **Taken from OpenCE:**
  - a body come to rest is sent three times; test26's resend of an object moved while at rest is kept too;
  - killing blows reach every client;
  - the host's BSP crossing brings the team along;
  - a gate one player passes brings the team;
  - a respawn starts behind a teammate;
  - the co-op garbage throttle;
  - multiplayer scores start at zero for a player joining in progress;
  - both hardening rounds.
- **Not taken:**
  - the PC scoreboard (display only, now also used in co-op), as in test27;
  - the desktop-GL renderer changes and multisampling;
  - map tag validation, a new loader check rather than a network change, which could refuse this app's Custom Edition and PAL handling.
- **Verified:**
  - 21 co-op, lobby and message files are build 144's byte for byte (`network_coop.c` differs only by test28's camera fix).
  - 13 more differ from 144 only by this app's earlier additions, exactly as they differed from 138.
  - Message numbers are unchanged.
  - Against the live directory: 4 of 4 co-op games and 10 multiplayer games are joinable at network 21.

## 2. HUD head tap

- **Cause:** the 1.0.10 log hid the HUD half a second after a gun went into
  the right shoulder's holster. On its way there the hand passes the temple.
  The tap point sat at the skin (8 cm out), but a controller's middle stays
  some way off the head, so a deliberate tap often missed.
- **Fix:**
  - The point is now 11 cm out and 3 cm back.
  - The hand has to be held there, slowed (under 0.6 m/s), for 0.15 s, and not in a holster.
  - A hand passing by does nothing.
- **VR SETTINGS > HUD, new rows:**
  - **HUD: SHOWN/HIDDEN** works for the session, like the tap, and every start shows the HUD.
  - **HEAD TAP:** Off or 6–15 cm, on (10 cm) by default. It is the same setting as HEAD GESTURES > HUD TAP.

## 3. Wrist HUD

- **Default placement:** now on the wrist itself, 10 cm behind the grip and
  4.5 cm out. In 1.0.10 it was 7.5 cm behind, on the back of the hand.
- **New HUD page rows:**
  - WRIST ALONG, ACROSS and HEIGHT (±20 cm in 1 cm steps);
  - WRIST SIZE (50–200%);
  - RESET WRIST.

## 4. Two hands and MOVE WITH

The report fits **MOVE WITH: LEFT HAND**: forward followed the left controller, so looking around or pointing the gun hand didn't change it. A hand on a gun's front grip is turned to hold it rather than pointed where you walk. While both hands hold the gun, the gun's line now stands in for that hand. The head mode (the default) is unchanged. The settings log line now names MOVE WITH, so the next report can confirm the setting.

## 5. Pull request #1 (glasses FOV and resolution, by willemhorak)

- **Merge fixes:** the PR was written against 1.0.6.
  - Its layer flag moved to 0x400 (0x200 is the wrist HUD's).
  - `eye_fov` now follows the wrist fields (`halo_xr_layers` is 180 bytes).
- **Changes found in review:**
  - The PR also shrank the eye images for AUTO's 85% and 70% on the Quest 2 and the first Quest. The full view at 100% or less now keeps the recommended images, exactly as 1.0.10 did.
  - A failed resize of the second eye returned before describing the first, which had already been remade. Both eyes are now always described.
  - "125% Q3 NATIVE" overran its menu row, so it is now "125% Q3".

## Evidence

- `tools/test_test29.py` runs:
  - the rest sends;
  - the held HUD tap (hide, then show again; passing by, holsters, the cheek, off);
  - the wrist placement;
  - MOVE WITH under a two-hand hold;
  - the layer layout;
  - the eye sizes against 1.0.10's.
- `test_quest_browser` now judges games at the header's network version, including against the live directory.
- 32 regression suites and the cache-format tests pass. Both editions and the host build in release mode.

## Next

The owner's device tests ([TEST29-DELIVERY.md](TEST29-DELIVERY.md)).
