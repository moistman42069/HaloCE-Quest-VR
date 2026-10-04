# Test20c checkpoint: hand/gun calibration split, floating hands and arms

Updated 2026-10-04. Private candidate **1.0.2 / code 23**, branch
`test20-safe-upload-performance`. Background, the 1.0.1 withdrawal and the
performance fix: [TEST20-PROGRESS.md](TEST20-PROGRESS.md). No release without
explicit owner approval.

## Evidence reviewed (owner, 2026-10-04; raw files kept private)

| Item | Build / setup | Findings |
| --- | --- | --- |
| Log 09:44 | test20b, Quest 3, default data root | PvP Blood Gulch 15 players and campaign: 68–72 fps, game frame 9–13 ms, `[render-perf]` uploads 0.3–1.9 ms, 0 wraps. Owner set both controllers to pitch −70, roll −25. Tried every Body/Arms mode. |
| Log 09:51 | test20b, managed data set `game-versions/p-…` | That set has its **own** config: defaults written, calibration back to 0. a10 (Autumn) and a30 at 68–72 fps; game frame 11–14 ms; Safe streamed **up to 15.6 MB/frame into a 16 MB ring** (0 wraps). Owner set both pitches to −70. |
| Video 09:56:18 (99 s) | same session | 0–12 s (zero calibration): empty hands point fingers up/forward, unlike real hands on Touch controllers (14–16 s passthrough). 26–34 s: rifle correct at zero. 38–76 s: pitch −70 set on both hands. 76–82 s: hands natural (palms down, fingers forward). 84–96 s: pistol/rifle point well below the controller: the reported gun-angle problem. |
| Log 02:43 | public 1.0 (test18) | 58–72 fps baseline; nothing new. |

Performance is confirmed fixed on device: test20b holds 68–72 fps where 1.0.1
fell to 4–22 fps.

## Cause of the gun-angle problem (established in source)

The empty hand is posed from the controller's **grip** pose (`vr_hand_world` →
free-hand IK → `vr_orient_hand`); the held gun from the **aim** pose
(`compute_aim_pose` → `vr_weapon_view`, shots via `vr_hand_ray`). The only
adjustment available was the controller correction (`vr.align_*`), which since
test20b deliberately moves both together. The hand model sits about 70° off
the real hand at zero, while the gun is right at zero, so one value could
never fit both.

## Changes

1. **Hand orientation** `vr.hand_<side>_pitch/yaw/roll` (default −70/0/0):
   applied by new `vr_hand_pose` to the free/empty hand (orientation, wrist
   target, fingers, contact) and to the network avatar's hands. Never reaches the gun.
2. **Gun calibration** `vr.weapon_pitch/yaw/roll` (default 0), applied to
   the one-handed aim pose, so the gun model, shots and reticle turn together;
   mirrored for the left hand; two-handed aim still follows the hands' line.
   Existing `vr.weapon_offset_*` now live-reload and are on the GUN page.
3. **Migration** (`vr.calibration_split_applied`, once per config): a nonzero
   controller rotation with |roll| < 135° moves to the hand page and is cleared
   from the controller; roll flips stay; a failed save retries next launch.
4. **Hand tracking** `vr.hand_tracking` = `ik` (default, unchanged),
   `floating` (free hand placed exactly at the controller, no arm solve,
   arms hidden), `floating_arms` (exact hands; arms solved from a shoulder
   that slides to stay within 97% reach; only body IK uses body shoulders).
   Independent of `vr.body`. Applies with Arms = IK.
5. **Hands Only / floating presentation**: hidden arm bones gather 3.5 cm
   behind each wrist instead of collapsing onto their own origin, which
   dragged shared wrist vertices toward the elbow.
6. **Safe stream slots 32 MB** (Normal 16 MB) after the 15.6 MB/frame Autumn
   measurement, so a heavy frame does not orphan mid-frame. Memory +48 MB.
7. Menu: Body → HANDS; new LEFT HAND, RIGHT HAND, GUN pages with resets
   (defaults read from the config table); Calibrate pages renamed CONTROLLER
   LEFT/RIGHT.

## Status

| Item | Implemented | Automatically verified | Confirmed on device |
| --- | --- | --- | --- |
| 1.0.1 slowdown fix | test20 | Yes | **Yes** (test20b logs, 68–72 fps) |
| Hand vs gun calibration split | Yes | Yes (`test_test20c_hands`) | No |
| −70° hand default | Yes (from video) | Config default checked | No |
| Calibration migration | Yes | Yes | No |
| Floating / Float + Arms | Yes | Shoulder reach, wiring | No |
| Hands-only cuff | Yes | Collapse geometry | No — needs a look |
| 32 MB Safe slots | Yes | Static check | No |
| Left-eye corruption, co-op | No new change | — | Open |

## Device checks needed

1. Empty hands at default: natural, like 76–82 s of the video, with no menu changes.
2. Pick up pistol and rifle: barrel and shots follow the controller as at 26–34 s;
   adjust GUN only if wanted.
3. Hands: Floating, then Float + Arms. Reach far, cross hands, grip a rifle with
   both hands, reload, throw a grenade, melee; switch modes mid-play.
4. Body Hands Only: wrist cuff closed, not cut off.
5. Body IK with Legs + Arms unchanged from test20b.
6. Autumn: `[render-perf]` stream wraps stay 0; watch the left eye.

## Unresolved

- Left-eye corruption, co-op failures, populated-host crash guard: open
  (TEST19-COMMUNITY-REVIEW.md).
- "the game's sound work" count spikes during map loads (seen again 09:45:46);
  frame pacing unaffected; not investigated further.
- Floating arms are cosmetic for remote players: network avatars still use
  body IK arms (with the calibrated hand orientation).
