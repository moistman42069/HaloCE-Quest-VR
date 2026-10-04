# Test21b checkpoint: reticle on the shots, horn, left-hand ammo counter

Updated 2026-10-04. Private candidate **test21b, 1.0.2 / code 27**, branch
`test21-hands-body`; it replaces the first test21 pair (code 26). Everything
else in test21 is unchanged: see [TEST21-PROGRESS.md](TEST21-PROGRESS.md)
(causes 1–12, changes, headset checks). Delivery:
[TEST21B-DELIVERY.md](TEST21B-DELIVERY.md). No release without explicit owner
approval.

## Owner result for the first test21 pair

- Full Body, two-hand grip and the rest work ("everything else seems to be
  working great now").
- The bullets no longer matched the reticle: in the video starting 15:33:34
  (log 15:30:41, b30) the impacts land above and left of the reticle on the
  assault rifle and the pistol.
- The Warthog horn is still silent.
- In the left hand the ammo counter reads the wrong way.

## Causes and changes

1. **Reticle.** The first test21 reticle was shifted by each trigger's
   `first_person_weapon_offset`. The engine then turns every player shot, in
   `player_aim_projectile`, toward where the camera's line hits (from the
   unit's camera along its aim), within the weapon's deviation cone (the larger
   of its deviation and autoaim angles). So the offset never shows in the
   impacts, and the shift moved the reticle off them. The camera trace is now
   factored out of `player_aim_projectile` unchanged
   (`aim_assist_collision_direction`, both builds), and the VR reticle turns its
   ray through it (`vr_aim_assist_converge`; render only, no autoaim pull toward
   targets). A test compiles both from the source: the reticle's direction equals
   the shot's bit for bit over 20,000 aims. Per-gun aim values set while testing
   the first build reset to 0 once (`vr.aim_reset_applied`).
2. **Horn.** The engine chain (crouch control → driver → vehicle flag 2 → the
   horn function) is intact. `vr_horn_held` read the VR pad, where the right
   thumb is the zoom (off-hand trigger), so a stick click with that trigger held
   counted as the both-sticks recentre. It now reads the controllers' own stick
   clicks. Each press is logged ("vr: horn: ..."), including whether the vehicle
   received the crouch control. This is not proven to be the whole cause.
3. **Ammo counter in the left hand.** The left hand's gun is the right-handed
   first-person model mirrored, so its display reads backwards on every gun that
   has one. Fixing only the display needs a per-part winding decision in the
   renderer. Known issue; not changed.

## Status

| Item | Implemented | Automatically verified | Headset |
| --- | --- | --- | --- |
| Shots on the reticle | Yes | Engine-identical direction (20,000 aims) | No |
| Horn | Partial (recentre test, logging) | Button logic | No |
| Left-hand ammo counter | No | — | Reversed |
