# Test24b checkpoint: comfort settings, SPV1 notice

Updated 2026-10-05. Released build **test24b, version 1.0.6 / code 32**,
branch `test21-hands-body`, on top of test24 (1.0.6 / code 31; its co-op
cutscene fix, launcher join steps and default co-op listing are unchanged, see
[TEST24-PROGRESS.md](TEST24-PROGRESS.md)). Published as v1.0.6 with the
owner's approval; see [release notes](RELEASE-1.0.6.md).

## Requests

| Source | Request |
| --- | --- |
| A player, via the owner | "Would it be possible to add snap turn and vignetting as comfort settings please?" |
| Owner | A smooth turn speed and a snap turn amount to fine-tune them, maybe in a "comfort" section of the VR menu; title the pair 1.0.6. |
| Owner | SPV1 integration does not seem to work: warn in its section that it is not functioning and will be refined in a future release. |

## Changes

1. **COMFORT page (Quest).** VR Settings → COMFORT: **Turning** (Smooth or
   Snap), **Smooth Speed** (30–300 degrees a second in 12 steps), **Snap Angle**
   (10–90 degrees in 9 steps), **Vignette** (Off, Low, Medium, High) and
   **Vignette When** (Move + Turn, Turning Only, Always).
   - Snap turn already existed (Controls → Turning, 30/45/90). The game still
     turns by `vr.snap_turn` (0 = smooth) and `vr.smooth_turn_speed` exactly as
     before. The page keeps the chosen snap angle in `vr.snap_turn_amount`
     while you turn smoothly and takes it up again for Snap.
   - Controls → Turning keeps all its earlier choices and adds Snap 22.5 and
     60; its snap choices also set the kept angle.
2. **Comfort vignette (Quest).** A black edge is drawn into each gameplay eye
   just after it is copied to the headset image (`copy_to_swapchain`; the
   renderer retakes its GL state after each eye). The shader measures the
   angle from the eye's straight-ahead direction (tangent space from the eye's
   field of view), so the clear circle stays round in the Quest's skewed
   per-eye views.
   - At rest it starts from the eye's farthest corner, so nothing shows. At
     full motion the view is clear to about 39, 33 or 24 degrees from straight
     ahead (Low, Medium, High), then fades to black over a soft edge.
   - It eases in over 0.12 s and out over 0.35 s.
   - Motion is your own stick movement: the move stick (a vehicle's
     throttle), arm-swing running, smooth turning, a brief pulse on each snap
     turn, and stick steering in a seat.
   - It shows only while you are in control in stereo gameplay. Cutscenes, the
     3D screen and menus with the pointer never show it, and the amount
     resets there.
   - It uses only GL calls the game already imports, leaves the eye image's
     alpha untouched, and is drawn only when set on (default Off).
3. **SPV1 notice (both).** The launcher's SPV1 button reads "(not working
   yet)", and its panel opens with a warning that SPV1 support is currently not
   functioning and will be refined in a future release. Installing and
   restoring still work as before. The player guide says the same.
4. **Version 1.0.6 / code 32** (the code must rise above test24's 31).

## Status

| Item | Implemented | Automatically verified | Device |
| --- | --- | --- | --- |
| Comfort page, fine turning | Yes | Turning switches smooth/snap keeping the angle; Snap Angle steps 10–90, holds at the ends, moves a live snap turn and only keeps the angle while smooth; Controls' choices all kept; defaults unchanged | Try each row |
| Vignette | Yes | Eases in/out on time; turning-only ignores moving; always shows; one snap per push with a pulse; never in cutscenes, 3D screen, menus or when off; shape: nothing at rest (corners included), grows with motion, centre always clear; GL calls all imported | Look for the darkened edge while moving/turning at each strength |
| SPV1 notice | Yes | The button text, and the warning first in the panel | Open the launcher's SPV1 section |
