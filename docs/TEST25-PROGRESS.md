# Test25 checkpoint: vehicle report, first-person refinements, settings rows, upstream review

Updated 2026-10-05. Private candidate **test25, version 1.0.7 / code 33**,
branch `test25-vehicle-recenter`, from the released v1.0.6 (`f04f5612`; main
`90d775dc`). No release without explicit owner approval.

## Baseline accepted

The owner tested v1.0.6 (test24b, code 32) on device: "everything in the latest
build worked great (besides 1st person vehicles)". That covers co-op
cutscenes on the joining device, the comfort page, launcher join steps and the
default co-op listing. First-person vehicles remain experimental and opt-in.

## Evidence (kept private, `work/test25`)

| Source | What it shows |
| --- | --- |
| A player's 1.0.6 logs 09:20:36 (launcher) and 09:20:39 (game), Quest 3, from the Flat2VR thread | The report: after recentring while driving a Warthog the view faced sideways; getting out and in and switching views did not fix it; restarting the save did. This player is **left-handed with standard (unmirrored) sticks**, locked weapons, smooth turn 180. The log holds three recentres, all the system's (session start and resume), **no in-game recentre**, and no seat state (1.0.6 logged none). "cleared vehicle camera cache" lines show the player was seated when leaving levels (09:24:14, 09:26:45) and got out of a vehicle at 09:20:52 in first person. **The failing moment is not in this log; no cause is claimed.** |
| Owner's log 08:43:46 and video 08:48:14 (39 s, Silent Cartographer) | First-person Warthog (08:45–08:47, 08:48:23–08:48:43): the windshield glass is a bright white sheet from the driver's seat; the cockpit rocks hard against a level horizon; VR Settings rows are clipped at the right ("STEERING: RIGHT HAN", "ALL FORWARD: < 0 C", "HOG FORWARD: < 0 C"), which hides the right arrow of numeric rows. The "All Forward" row decrements with its left side, as the thread clarified. |
| Trever Spade's older logs | Historical (test18 / 1.0.2-era); he confirmed aiming fixed in 1.0.3. Not evidence of a 1.0.6 defect. |

## Code findings

- **Recentre in a seat.** In first-person view the eyes turn from the seat's heading plus the head's yaw in the room. A recentre (both sticks, View held, or the system regaining focus) makes the head's current direction "forward". Recentring while looking aside therefore leaves the vehicle's forward aside of the body, and stick turning is off in that view. That would last through getting out and in and through view switches, until the next recentre. It does not explain why a save restart fixed it, and the log contains no in-game recentre, so it stays a hypothesis. In third-person view a recentre re-takes the heading from the game's facing (where hand steering points), and the right stick still turns.
- **Vehicle defaults and adjustments** match the UI: Third Person, Right Hand, one-time migration kept; offsets step ±1 cm within ±50 cm (left side down, right side up). There was **no reset** for the offsets.
- **Clipped rows**: widget text is laid out and clipped to each cloned pause-menu button's bounds (`ui_widget.c`), about 199 menu units, while columns are 256 apart.

## Changes

1. **Diagnostics** (Quest): one log line per recentre (and its source), per seat entered or left, and per view switch while seated, with the heading before and after, head, aim, steering hand, game and seat angles. One line per seat entered gives the vehicle tag, seat, role and view. Nothing is logged per frame.
2. **First-person glass** (Quest, first person only): the seated vehicle's own `transparent_glass` shaders (and those of its attached parts) are not drawn from the seat. Each see-through shader kind on that vehicle is logged once, so the next log confirms which kind the white sheet was.
3. **Horizon option** (Quest, first person, driver only): Vehicles → HORIZON Level (default, unchanged) / Half / Vehicle (`vr.vehicle_tilt`). It tilts the eye cameras about the seat by the vehicle's pitch and roll (from its drawn root node), eased over 0.12 s, held at 60°. Gunners and passengers stay level.
4. **Settings rows fit**: setting buttons widened to their column (250 units; the original width is logged once), and rows over the budget renamed (see CONTROLS-AND-OPTIONS). Saved keys are unchanged.
5. **RESET OFFSETS** on the Vehicles page: all 18 seat offsets back to 0.
6. **Upstream fixes adopted** (no protocol change): `3d2c04d6` near-camera vertices, `fb1abedd` dead camera with no living player, `61623e68` texture binding order (adapted), `3ae09c3d` radar wedge art. See [UPSTREAM-REVIEW-2026-10-05.md](UPSTREAM-REVIEW-2026-10-05.md).
7. **Version 1.0.7 / code 33.**

## Notes written

- [UPSTREAM-REVIEW-2026-10-05.md](UPSTREAM-REVIEW-2026-10-05.md): OpenCE is at network 16 (exact match), DamnationCE 16, this project 11 (9–11). Current OpenCE/DamnationCE builds cannot play PvP with 1.0.x. PR #68 is merged, #69 and #85 open.
- [COOP-PLAYER-COUNT.md](COOP-PLAYER-COUNT.md): campaign co-op is two players; 128 is PvP capacity; what more would need.
- [PC-STEAM-FRAME-FEASIBILITY.md](PC-STEAM-FRAME-FEASIBILITY.md): flat desktop vs PC VR, the 32/64-bit boundary, a staged plan.

## Status

| Item | Implemented | Automatically verified | Device |
| --- | --- | --- | --- |
| Recentre/seat/view diagnostics | Yes | Logged once per event with the right source and states; nothing per frame | Needed: a session reproducing the sideways view |
| First-person glass | Yes | Only the seated vehicle's (and its parts') glass, only in first person; each kind logged once | Needed: Warthog in first person |
| Horizon option | Yes | Level unchanged; Vehicle matches the vehicle's tilt exactly; Half ~half; 60° limit; eased; drivers only | Needed: drive with each setting |
| Rows fit, renames | Yes | 107 rows within a width budget calibrated on the video (two Banshee/Pelican Right rows only at -10 to -50 cm may clip their last arrow) | Needed: look at the menus |
| Reset Offsets | Yes | 18 keys to 0, others untouched | Needed |
| Upstream fixes | Yes | Exact patches (files matched their parents) or the same change; PNG bytes verified | Needed: general play |
