# Test23 checkpoint: co-op cutscenes on joining devices, remappable Quest buttons

Updated 2026-10-04. Private candidate **test23, version 1.0.5 / code 30**, branch
`test21-hands-body` (after test22 = 1.0.4 / code 29 and the published v1.0.3 =
test21b, code 27). No release without explicit owner approval.

## Evidence (owner logs; kept private)

| Source | What it shows |
| --- | --- |
| Quest log 22:02:26 (1.0.4, joined co-op) and phone log 21:59:28 (1.0.4, hosting) | Co-op a10 now loads and plays on both (the test22 crash fix holds): lifecycle barriers complete, VR avatars are negotiated, a checkpoint restore goes through. In the opening cutscene the characters T-posed and slid on the Quest, while the phone was right. The host also warns that `cryotube_1` already exists (a host-side script note, unchanged). |
| Owner report | With **Locked** weapons the gun hand's grip threw grenades. The grenade should default to the left X button, the grip should be neutral, and every action should be remappable with a reset to defaults. |

## Causes and changes

1. **Co-op cutscenes on the joining device.** Only the host runs the
   cutscene. A joining device receives each character's position from the
   host and, as in gameplay, moves toward it half of the way each tick, and
   when the gap is large, jumps there but draws a short glide. A cutscene cuts
   between shots by teleporting its actors, so on the joining device they
   slid across the room instead, and a biped moved that way plays its falling
   (airborne) pose, which looks like a T-pose. The host was right because it
   sets them in place itself. On a campaign client during a cutscene
   (`cinematic_in_progress`, which clients replay from the host's
   `cinematic_start`/`cinematic_stop`), a character that no player controls
   and that is not seated in anything is now put exactly where the host has
   it, at once (`network_objects_reconcile`). Before and after a cutscene,
   players, vehicles and everything in gameplay keep the existing smoothing.
   The change applies to every campaign cutscene, not only a10's.
2. **Dropped cutscene cues logged.** A joining device skips a presentation cue
   it cannot apply (for example, an animation on an object it does not have).
   That was silent; it is now logged ("campaign: client dropped presentation
   ..."), eight times and then every hundredth, so a remaining cutscene
   problem can be traced from the next logs.
3. **Grenade on Left X; grip neutral (Quest).** On Touch controllers the
   grenade now defaults to the left X button in both weapon modes: a tap
   throws, a 0.4 second hold switches grenade type (as Physical weapons
   already did). With Locked weapons, X used to switch grenades at once and
   the grip threw; the grip now only switches weapons at a holster.
4. **Remappable buttons (Quest).** VR Settings → **BUTTONS**: Jump, Action /
   Reload, Melee, Crouch, Switch Weapon, Grenade and Switch Grenade, each on A,
   B, X, Y, R Stick, L Stick, Grip (Locked) or None (Switch Grenade also Hold
   Grenade), with **Reset Buttons**. A button another action already has is
   swapped to it, so no button does two actions; choosing Grip for the
   grenade moves Switch Grenade to the grenade's old button, giving back the
   1.0.4 Locked layout. A config edited by hand with two actions on one button
   does both and the log warns. Keys: `vr.button_*`.
   - "A"/"B" are the gun hand's lower/upper buttons and "X"/"Y" the other
     hand's, so left-handed play with Mirror Controls: Auto mirrors the layout
     exactly as before.
   - The grip source is the gun hand's grip, active only with Locked weapons
     and away from the holsters.
   - Not remappable, unchanged: triggers, zoom, flashlight, menu, recentre
     (both stick clicks), the off hand's grip (two hands, gun pass), the horn
     (raw stick clicks while driving), pointer menus, and every other
     controller's layout (Index, Steam Frame).
5. **Version 1.0.5 / code 30.**

## Status

| Item | Implemented | Automatically verified | Device |
| --- | --- | --- | --- |
| Co-op cutscenes | Yes | Wiring: applied only on a campaign client in a cutscene, to units no player controls and not seated, after the message is validated, with no drawn glide | Needs co-op a10 opening with the Quest joining; then roles swapped |
| Dropped-cue log | Yes | Wiring and rate limit | Next co-op logs |
| Grenade on X, grip neutral | Yes | Default layout equals 1.0.4 for every combination of A, B, Y and the sticks in both weapon modes; the locked grip throws nothing; X tap/hold timing | Needs both weapon modes |
| Remapping, reset, conflicts | Yes | Swap rules, grip-grenade layout and back, 20,000 random menu changes never leave a button with two actions; unknown values keep defaults | Needs the BUTTONS page |
| Left-handed | Unchanged | 24,000 random frames: left-handed output is the right-handed mirror image with the new layout | Optional check |
