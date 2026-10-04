# Test20d checkpoint: gun anchored to the controller, left-handed controls, simpler settings

Updated 2026-10-04. Private candidate **1.0.2 / code 24**, branch
`test20-safe-upload-performance`. Background: [TEST20-PROGRESS.md](TEST20-PROGRESS.md)
(1.0.1 withdrawal and the performance fix), [TEST20C-PROGRESS.md](TEST20C-PROGRESS.md)
(hand/gun calibration split). No release without explicit owner approval.

## Evidence reviewed (owner, 2026-10-04; raw files kept private)

| Item | Build / setup | Findings |
| --- | --- | --- |
| Log 10:34 | test20c, Quest 3 | Migration ran as designed: both hands' −70 moved from controller calibration to hand orientation. Owner tried Gun Yaw 5/10 and back to 0, then set **Gun Pitch −15**. Tried every Body, Arms, Fingers and Hands combination. `[render-perf]`: 717–721 frames per 10 s (72 fps) in play, dips only around loads; 0 stream wraps; uploads 0.9–1.6 ms. |
| Video 10:37:16 (111 s) | same session, Floating | Side-by-side with passthrough at about 80/81 s, 90/93 s and 104/107 s: the virtual pistol sits **higher, further forward and more central** than the real controller. Turning the wrist swings the gun around a point behind the hand instead of turning it in the hand. Rough comparison only: different field of view and timestamps. |

## Cause (established in source)

The transform chain for a held gun was:

1. OpenXR aim pose (rotation) and grip pose (position) for the gun hand, after the
   controller correction (`vr.align_*`).
2. Gun calibration (`vr.weapon_pitch/yaw/roll`) on the aim rotation (`compute_aim_pose`).
3. `vr_weapon_view`: a **weapon camera** at the grip plus a fixed offset in the aim
   frame, from `vr.weapon_offset_*` (0.10 / −0.12 / −0.20): 20 cm behind, 12 cm
   above and 10 cm beside the grip; `hand_view` clamps it within 0.9 m of the head.
4. `weapon_out_of_walls` pulls the camera back along the barrel at walls.
5. Halo builds the first-person model **relative to that camera** from the weapon's
   own animation (`animation_graph_node_matrices_from_orientations`).
6. `vr_render_first_person_ik`: left-hand mirror, then arms, support grip, IK and
   native action blending.

Nothing ever measured where step 5 put the gun hand. Each weapon's animation holds
the hand at its own place in front of the camera, so the gun's position in the real
hand was the fixed offset plus a different animation offset for every weapon. The
camera sits behind the hand, so turning the controller swung the gun around it. The
mechanism is global, and the amount depends on the weapon, so a pistol-only fix
would have been wrong. Gun Pitch −15 partly hid the height error by tipping the gun
down around that same point behind the hand. The empty hand did not have the
problem because it is placed from the grip directly (`vr_hand_pose`).

## Changes

1. **Gun anchored to the controller** (`vr_gun_anchor.h`, `vr_anchor_gun`). The new
   step happens after step 6's left-hand mirror and before arms are hidden, animated
   or solved, and before the authored copy that action blending uses. The whole
   first-person model moves so that the gun arm's wrist bone lands where the empty
   hand's wrist goes (`vr_hand_pose` grip − 7.5 cm along the hand). Then come the
   player's gun position (`vr.gun_forward/up/out`, metres, 0 by default; Out is away
   from the body's middle and mirrors per hand), then the wall pullback from step 4.
   - The gap is kept in the weapon camera's axes, so the gun turns about the hand.
   - While Halo's animation owns the gun arm (ready, put away, reload, melee,
     throw, flashlight, overheat: the same mask as test16 action blending), the
     gap holds and the animation plays around the hand.
   - After an animation only the leftover difference eases out (τ 0.05 s), so the
     gun follows the controller at once even while settling. This matters with two
     hands, where the hands' line turns the camera.
   - Each weapon graph and hand remembers its last gap, so a weapon drawn again is
     anchored during its ready animation. A weapon's very first draw uses the old
     placement until the animation ends.
   - The gap is capped at 0.6 m as a guard. No allocation; one small fixed table.
   - Applies to every hand mode and to Animated and Gun Only arms. **Gun Grip:
     Classic** (`vr.gun_anchor false`) restores the old placement.
   - Shots and the reticle still come from the aim ray (unchanged), so they stay
     parallel to the barrel.
2. **Left-handed mode.** Controls → **Handedness** (`vr.left_handed`) with **Mirror
   Controls** (`vr.mirror_controls`, Auto by default):
   - When left-handed, the sticks swap jobs at frame acquisition, before anything
     reads them. The face buttons and stick clicks swap hands in `layout_controls`,
     as does the pointer's Back button.
   - Triggers, grips, zoom, flashlight, grenade grip, holsters (already
     symmetrical), two-handed aiming, the mirrored gun and the menu pointer already
     followed the gun hand.
   - Changing Handedness in the menu also mirrors Vehicle Steering and Move With
     when they named a hand.
   - One-time migration (`vr.handedness_applied`): a config already left-handed
     keeps standard sticks and buttons (Mirror Controls Off).
   - Advanced overrides: Mirror Controls Off, Steering and Move With rows, per-hand
     `vr.hand_left_*` in `config.toml`.
3. **Simpler settings** (12 categories → 9; one row per decision):
   - Turning includes the turn speed; Holsters includes the size; Weapons includes
     Physical + MP; Arm Run includes the effort.
   - Hands (Body IK / Floating / Animated / Gun Only) replaces the separate Arms and
     Hands rows.
   - Crosshair moved to **Gameplay** (formerly VR).
   - Left Hand, Right Hand and Gun became **Hands + Gun**, with both-hands rows (left
     mirrored) and Reset Hands / Reset Gun.
   - Combined rows use a new generic multi-setting row (`_vr_setting_multi`,
     `config_matches` / `config_write_text`). A hand-made combination shows CUSTOM.
4. **Floating merged.** `floating` now draws arms from the floating shoulder unless
   Body is Hands Only, which gives floating hands alone. A saved `floating_arms`
   migrates to `floating`. Same two looks as test20c, with one choice fewer.
5. Reset Gun also resets the new gun position and the legacy camera offsets.

Defaults kept: Legs + Arms, Body IK, hand −70/0/0, gun angle 0, two-hand Grip,
Physical weapons offline only, third-person/right-hand vehicles, VR Safe and flat
Normal geometry, 32 MB Safe slots, the test20 performance path. The owner's saved
Gun Pitch −15 is kept. Delivery asks for Reset Gun before judging the new grip.

## Status

| Item | Implemented | Automatically verified | Confirmed on device |
| --- | --- | --- | --- |
| 1.0.1 slowdown fix | test20 | Yes | **Yes** (test20b/c logs, 72 fps) |
| Gun anchored to controller | Yes | Yes (`test_test20d`: state machine, production function over 1,200 random frames, both hands, offsets, pullback) | No |
| Left-handed controls | Yes | Yes (24,000 random frames: left-handed output equals the mirrored right-handed output; migration) | No |
| Simplified settings | Yes | Yes (every combined row round-trips all value pairs; 26 menu choices show their defaults) | No |
| Floating merge | Yes | Yes (arms drawn unless Hands Only) | No |
| Hand/gun split, floating, cuff (test20c) | test20c | Yes | Partly (owner exercised all modes; looks not yet reported) |
| Left-eye corruption, co-op | No new change | — | Open |

## Device checks needed

1. With Gun Grip Anchored, after Reset Gun: hold pistol, rifle, shotgun, sniper and
   plasma weapons. In passthrough, the gun should sit in the real hand and turn about
   the wrist with no swing. Fine-tune with Gun Forward / Up / Out only if needed.
   Compare with Classic.
2. Reload, melee, throw a grenade, switch weapons, and drop and pick up weapons
   (Physical): the gun returns to the hand smoothly afterwards.
3. Two hands on a rifle, pressed against a wall: no jitter, and the wall pullback
   still works.
4. Handedness Left: sticks, face buttons, menu Back, holsters, two-handed grip,
   vehicles. Then Mirror Controls Off.
5. Every Hands mode with each Body choice; Floating with Hands Only is floating hands.
6. Settings pages: every row changes, saves and shows its value (no CUSTOM on a
   fresh config).

## Unresolved

- Left-eye corruption, co-op failures, populated-host crash guard: open
  (TEST19-COMMUNITY-REVIEW.md).
- Remote players still see body-IK arms; the anchored gun is local rendering only.
- The longest new menu line ("HAND PITCH: < -70 DEG >", "CROSSHAIR OPACITY: 100%",
  23 characters) is shorter than the shipped "PELICAN FORWARD: < 0 CM >" (25); still
  check for clipping on device.
