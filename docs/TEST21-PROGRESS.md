# Test21 checkpoint: hand modes, body turns, Full Body, two-hand lock, horn, online melee

Updated 2026-10-04. Private candidate **1.0.2 / code 26**, branch
`test21-hands-body` from `main` (`dae77ab1`). The accepted release is v1.0.2
(the exact test20e pair, code 25); see
[RELEASE-PROVENANCE-1.0.2.md](RELEASE-PROVENANCE-1.0.2.md). No release without
explicit owner approval.

## Evidence reconciled (owner files kept private)

The recording starts at 12:45:58 in the session logged from 12:42:16. That
session ran test20e (code 25, the public v1.0.2 binary) on a freshly written
default config in the default data root. Video time + 12:45:58 lines up with
every logged setting change:

| Video | Log | State |
| --- | --- | --- |
| 0–7 s | 12:45:53 | Body Arms + Hands, Hands Body IK |
| 8 s | 12:46:06 | Hands **Floating** (the overlay the report describes) |
| 13–57 s | 12:46:11 | Hands Animated |
| 58 s | 12:46:56 | Body IK; 59 s Floating again |
| 74 s / 76 s | 12:47:11 / 12:47:13 | Body Full, then Legs + Arms (Floating) |
| 93 s | 12:47:31 | Body **Hands Only** + Floating |
| 95–96 s | 12:47:33–34 | Animated, Gun Only |

The `body legs` snapshots are earlier moments of the same session, not stale
state or a migration. The 12:36 log is a test20d runtime on a managed data set.
The local signing key's certificate matches v1.0.2
(`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`), and the
local copy of the release APK has the published SHA-256.

## Causes (established in source)

1. **Floating kept attached arms** (owner: "the floating hands toggle didn't
   really work"). Test20d merged Floating with Float + Arms, so Floating drew arms
   from a floating shoulder whenever Body showed arms (59–61 s, 76–84 s).
2. **Cut, slivered wrists** (Hands Only + Floating, 93–95 s). A floating hand is
   moved to the controller without an arm solve. `vr_hide_forearms` then gathered
   the hidden forearm 3.5 cm toward the forearm bone's old animated position, an
   arbitrary direction, which flattened the cuff into slivers.
3. **Arms don't follow body turns.** Without a drawn body (Arms + Hands, Hands
   Only) the IK shoulders faced `vr.heading`, the stick-turn heading, not the
   torso. With a body, the torso yaw followed the head only beyond a 25° cone.
4. **Full Body clipping and snapping.** The neck target was a fixed 14 cm behind
   (along the torso yaw) and 20 cm below the eyes, ignoring head pitch. Room-scale
   moves the character with the eyes, so looking down carried the chest into the
   camera. The torso yaw came from the flattened head forward, which is unstable
   looking straight down.
5. **No horn while driving.** The horn is the driver's crouch control
   (`vehicles.c`). `player_control` passes crouch only while the move stick is
   below 98%, and the Warthog's throttle is that stick.
6. **Melee too easy online.** Swing melee fires on any hand moving faster than
   2 m/s vertically, in every game type.
8. **Quest OS v78 report, last step (gun upside down again in two hands).**
   `compute_aim_pose` built the two-handed gun's orientation from the raw
   controller's up (`vr.frame.aim`), dropping the gun calibration
   (`vr.weapon_*`, applied only to one-handed aim). A gun turned upright with Gun
   Roll 180 stayed upright in one hand and flipped back in two. The earlier steps
   (hands 180° off on v78; the hand option fixing hands but not guns) fit the
   design: Hand rotation is hand-only by design (test20c). Controller → Flip Roll
   180 corrects the raw pose for hand, gun and two hands together and was not
   affected. The v78 cause itself is still unconfirmed.
9. **Pistol reticle low and a bit left** (tester, after the first test21
   report: "most other weapons compensate with wider spread"). In
   `trigger_create_projectiles` a trigger flagged *uses weapon origin* takes its
   shot's start from the weapon's own marker, after the hand origin has been
   applied, so in VR the shot left from the unseen third-person gun (where the
   body animation holds it) and flew parallel to, but off, the hand's reticle
   ray. Separately, every aimed shot is shifted by its trigger's
   `first_person_weapon_offset` (along the aim, Halo's left and up), which the
   VR reticle never included. The pistol-class weapon in the campaign maps on this
   PC (SPV1 Custom Edition maps; protected names; latched, 5 shots/s) carries the
   *uses weapon origin* flag; stock tag values could not be read here, so the
   stock pistol is expected, not proven, to match. A precise gun shows the
   difference; spread hides it on others.
10. **First test21 reticle off the shots** (owner video 15:33:34 with log
    15:30:41, b30: impacts above and left of the reticle on the assault rifle
    and the pistol; "beforehand it was aligned"). The reticle had been shifted
    by the trigger's `first_person_weapon_offset`, but every player shot is then
    turned by `player_aim_projectile` toward where the camera's line hits (from
    the unit's camera along its aim), within the weapon's deviation cone (the
    larger of its deviation and autoaim angles), so that offset never shows in
    the impacts; the shift moved the reticle away from them. The hand's own line
    was never exactly the shots' either: they converge on the camera line's hit.
11. **Horn still silent** (owner, 15:37 session). The chain (crouch control →
    driver → vehicle flag 2 → the horn function) is intact in the engine. One
    defect in `vr_horn_held`: its "both sticks = recentre" test read the VR pad,
    where the right thumb is the zoom (off-hand trigger), so a stick click with
    the off-hand trigger held counted as a recentre. Not proven to be the whole
    cause; a log of the chain was added.
12. **Ammo counter reversed in the left hand** (owner). The left hand's
    first-person gun is the right-handed model mirrored, so its display reads
    backwards on every gun with one. Un-mirroring only the display needs a
    per-part winding decision in the renderer; not changed in this candidate.
7. **Two-hand auto grip "removed".** "Auto" was a magnet: two-handed aim only
   while the off hand stayed within a narrow cone; it never locked. The default was
   Grip (squeeze).

## Changes

- `vr.hand_tracking`:
  - `floating` = hands only (any Body);
  - `floating_arms` = Float + Arms;
  - Hands row: Body IK / Floating / Float + Arms / Animated / Gun Only.
- The hidden-arm cuff (Hands Only, Floating) closes along the hand's own axis
  (`vr_hand_back_axis`: finger bases to wrist), with the forearm direction as a
  fallback.
- One torso heading (`vr_body_heading`) for the IK shoulders in every Body mode,
  for the body, and for the published avatar:
  - pitch-safe head yaw (`vr_head_yaw_vector`);
  - pulled halfway toward both tracked hands ahead, within 45°
    (`vr_body_wanted_yaw`);
  - 15° comfort cone, rate 10/s, wrapped.
- Full Body neck pivot (`vr_neck_pivot`):
  - eye − (0.14 f′ + 0.20 u′), with pitch limited to −60..+30°;
  - horizontal follow cap 45 cm (was 30);
  - Legs + Arms stays the default.
- Two Hands **Auto Lock** (new default `auto`):
  - locks after the off hand rests 0.12 s at the support grip;
  - releases on a 20 cm distance change or leaving a 60° cone;
  - re-arms only after the hand leaves the grip;
  - Squeeze (`grip`) and Off remain;
  - one-time migration from the old Grip default (`vr.two_hand_auto_applied`);
  - two-handed aim now always uses the lock (the old magnet is gone).
- Online melee:
  - `vr.melee_multiplayer` (off by default) gates impact and swing melee in any
    network game (`vr_set_network_game`); the button is unaffected;
  - Melee row: Impact / Swing / Impact + Online / Swing + Online.
- Horn: seated, either stick click sets the crouch control whatever the throttle
  (`vr_horn_held` via `vr_take_actions`); a lowered head no longer crouches while
  seated.
- Two-handed aim takes the gun's up from its calibrated one-handed aim, so Gun
  Roll (and the rest of the gun angle's roll) survives two-hand grip.
- Shots and reticle per gun:
  - offline, with the hand aiming, a *uses weapon origin* gun now fires from the
    hand like every other gun (`weapons.c`, VR build only; the hand origin
    exists only in local games, so network play and the flat build are
    unchanged);
  - the reticle follows the shot exactly as the engine aims it: the trigger's
    offset, then the turn toward the camera line's hit within the weapon's cone,
    through the engine's own code (`aim_assist_collision_direction`, factored
    out of `player_aim_projectile` unchanged and shared by the reticle via
    `vr_aim_assist_converge`; render only, no autoaim pull toward targets);
  - per-gun aim values set while testing the first build reset to 0 once
    (`vr.aim_reset_applied`);
  - new per-gun **Aim Up / Aim Right** (Hands + Gun page, half-degree steps,
    ±10°, `vr.aim_<gun>_up/_right`, default 0) turn the held gun's shots, reticle
    and scope together, never the drawn gun. Eleven kinds by tag name (pistol,
    plasma pistol, assault rifle, plasma rifle, shotgun, sniper, rocket, needler,
    fuel rod, flamethrower, other). At 0 the aim is bit-identical to before.
- Packaging recognises test21 labels and checks its markers.

Kept: Legs + Arms default, gun anchoring, hand/gun calibration, fingers,
action-animation handoff, Safe geometry, avatar publishing, left-handed mode,
and Quest/Android networking parity. The Quest OS v78 orientation report
remains separate (FUTURE-RELEASE-FOLLOWUPS.md); nothing here links to it.

## Status

| Item | Implemented | Automatically verified | Headset |
| --- | --- | --- | --- |
| Floating hands only / Float + Arms | Yes | Yes (test21, test20c/d updated) | No |
| Wrist cuff along the hand | Yes | Yes (2,000 hands, forearm bone anywhere) | No |
| Arms follow body turns | Yes | Yaw math, all pitches, hands ahead/behind, wrap | No |
| Full Body neck pivot | Yes | Pivot math across pitch | No: needs looking-down, turning, crouch and room-scale walking checks |
| Auto two-hand lock | Yes | Static wiring and migration | No |
| Horn | Yes | Button logic | No |
| Online melee off | Yes | Gate logic | No |
| Shots on the reticle (every gun) | Yes (engine convergence shared, pistol from the hand offline, per-gun aim) | Yes (reticle direction equals `player_aim_projectile` bit for bit over 20,000 aims; per-gun turn exact; zero = bit-identical) | First build failed (owner video); rebuilt candidate needs the owner and the tester |
| Horn | Recentre test fixed; chain logged | Button logic | No: still silent in the first build; send the log after honking |
| Ammo counter in the left hand | No (known issue) | — | Reversed (owner) |
| v78: gun re-inverted in two hands | Yes (gun roll kept) | Yes (2,000 poses, both hands) | No: needs the reporter (Quest 3S, v78) |

## Headset checks needed

1. Hands: Floating (no arms, closed wrists) and Float + Arms with each Body choice.
2. With hands still, turn the body slowly through 180°+ and back (Arms + Hands,
   Legs + Arms, Full): the shoulders follow and the arms don't twist across.
   Repeat while moving the hands, reaching across the body, and after a recenter.
3. Full Body: look straight down at the torso and turn the head side to side;
   crouch; walk in room-scale. The chest must stay visible below and never clip,
   snap or vanish. Then switch back to Legs + Arms.
4. Two hands: bring the off hand to a rifle's support grip without squeezing; it
   locks. Pull away; it releases. Also try Squeeze and Off, and left-handed.
5. Warthog: honk with either stick click while driving at full throttle.
7. v78 tester: if hands are 180° off, use Controller Left/Right → Flip Roll 180
   (fixes hand and gun together). If they used Hand Roll plus Gun Roll instead,
   two-hand grip must now keep the gun upright.
6. Multiplayer: quick hand movements don't melee, the melee button does; Melee →
   Impact + Online re-enables physical melee.
8. Pistol (offline campaign): shoot a wall at about 5 m and 20 m; the impacts
   land on the reticle. Online, report whether it still differs. Hands + Gun →
   Aim For shows the held gun; Aim Up/Right fine-tune it, Reset Aim clears it.
   Other guns must behave as before.

## Multiplayer VR avatars

The owner asked for co-op's visible VR body movement in normal multiplayer
and later sent Android logs of a game joined in VR where the phone saw a flat
player. It is already one shared path: `network_vr_pose.c` runs in every
`network_distributed_tick`, campaign or PvP (see NETWORK-VR-AVATARS.md), but
the host must run this build: poses go client → host → viewers, and a host on
another build never offers the capability. The logs show exactly that:

| Log | Device / build | Game | Outcome |
| --- | --- | --- | --- |
| 11:42:41 | Quest, test20d | "the BIG CTF", bloodgulch, host 122f9b1c2e16, network v11, 35 players | Joined as machine #11; no avatar offer (no `vr pose` line) |
| 11:39:53 | Android 1.0.2 (code 24) | same host | Joined at 11:41:29, left at 11:41:41, then could not reconnect (NAT) |
| 11:43:27 | Android 1.0.2 | same host | Could not connect (NAT); ended up hosting its own empty carousel game |
| 12:22:17 | Android | hangemhigh, host 96600ed501d8, network v11, 19 players | Joined; no avatar offer |
| 21:20:20 (10-03) | Android test17 | — | Launch only |

Both hosts were public games on another build, so neither device was offered
avatars and the phone drew the Quest player with stock animation, as designed
for compatibility. Clients have no link to each other, so this cannot work
without the host. Change: a client now logs once, 10 s into a game whose host
offered no avatars, "vr pose: this host offered no VR avatars ... Host the game
from this build". To see VR movement, one player on this build hosts (Quest or
phone) and the others join that game.
