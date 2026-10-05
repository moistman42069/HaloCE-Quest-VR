# Test24 checkpoint: co-op cutscenes animate on joining devices

Updated 2026-10-04. Private candidate **test24, version 1.0.6 / code 31**,
branch `test21-hands-body` (after test23 = 1.0.5 / code 30). No release without
explicit owner approval.

## Evidence (owner log; kept private)

| Source | What it shows |
| --- | --- |
| Quest log 23:14:32 (1.0.5, joined a10 co-op hosted by the phone) | The mission loads; barriers 1 to 4 complete (the opening cutscene runs between tick 2 and tick 1307); avatars are negotiated; host actor controls arrive (1,433, none expired). The owner still saw the cutscene's characters T-pose and slide on the Quest. **No "client dropped presentation" line**: every cutscene cue the host sent was replayed, so test23's suspicion (cues dropped, or smoothing turning cuts into slides) was not the cause. |

## Cause

Halo updates (animates and thinks for) only objects in **active** parts of
the map. The active parts are what each player's cluster can see plus one
extra place a script names, "the special place that activates everything it
sees" (`object_pvs_set_object`, `object_pvs_set_camera`, `object_pvs_activate`,
cleared by `object_pvs_clear`; read by `objects_get_activating_cluster_index` in
`players_compute_combined_pvs`). Cutscenes use it to wake the area they film,
often far from the players (a10's opening).

In co-op only the host runs scripts. Clients replay a list of presentation
calls, and these four were not on it. On the joining device the cutscene's
area therefore stayed inactive: its characters were never updated, so they
never ran their animations (a character created there stays in its default
T-pose; one with a cue holds its first frame). Their positions, however, come
from the host's object stream, so they moved anyway: the slide. On the host
everything played, and with the phone hosting it looked right, which made the
problem look VR-specific. Any joining device (Quest or phone) is affected the
same way, and any campaign cutscene that films an area away from the players.

## Changes

1. **The host's activating place is followed.** `object_pvs_set_object`,
   `object_pvs_set_camera`, `object_pvs_activate` and `object_pvs_clear` are
   appended to the presentation stream (reliable, ordered, after the tick's
   object creations, so a named object always exists on the client first).
   The joining device now wakes the same area as the host, for cutscenes and
   for any scripted moment that uses it. Earlier wire IDs are unchanged.
2. **Seat postures.** `unit_set_seat` (the posture a character's idle
   animations are chosen for, such as sitting at a console) is replayed too.
3. **Diagnostics.** The joining device logs each activating place it follows
   ("campaign: client follows the host's activating place: ... (cluster N)"),
   so the next log proves the cutscene area woke up.
4. **test23's cutscene change withdrawn.** Its smoothing bypass addressed the
   wrong cause; `network_objects.c` is byte-identical to 1.0.4 again, so normal
   co-op movement is exactly as accepted.
5. **Launcher: how to join (owner request).** A new main-menu button, **How
   to join co-op & find servers** (also first in the Field guide), gives
   plain steps to host and join co-op and to open the in-game server browser
   (Multiplayer > System Link > Refresh). The Campaign co-op dialog, the host
   dialog and the server lists repeat the short version.
6. **Co-op listed by default (owner request).** In Host campaign, **List this
   game in the co-op server browser** is now ticked by default; unticking it
   still keeps a game private.
7. **Version 1.0.6 / code 31.** The test23 button changes (grenade on X,
   BUTTONS page) are kept unchanged.

## Status

| Item | Implemented | Automatically verified | Device |
| --- | --- | --- | --- |
| Cutscene activation followed | Yes | The real host capture, wire and client replay code: the four calls and `unit_set_seat` go out in order and replay with the host's arguments (strings decoded); another game's cues refused; argument types accepted by the validator; earlier wire IDs unchanged; the engine's activation reads the place | Needs a10 co-op, Quest joining, then roles swapped |
| test23 snap withdrawn | Yes | `network_objects.c` byte-identical to 1.0.4 | Normal co-op play |
| Launcher join steps, listing on by default | Yes | Wiring: steps name the real buttons and menus; the box starts ticked and still decides the listing | Read the new page; host co-op |
| Buttons (test23) | Unchanged | test23 and test20d suites | As in 1.0.5 |
