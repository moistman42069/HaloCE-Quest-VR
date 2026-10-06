# Test26 checkpoint: co-op crash and cutscenes, red text, first Quest start, HUD and gestures

Updated 2026-10-05. Private candidate **test26, version 1.0.8 / code 34**,
branch `test26-coop`, from test25 (`9bca3958`, 1.0.7 / code 33, delivered,
not yet tested by the owner), which it keeps whole. No release without
explicit owner approval.

## Evidence (kept private, `work/test26`)

| Source | What it shows |
| --- | --- |
| Owner's co-op logs 15:10:57 (launcher) and 15:11:02 (game), build 1.0.6, and two videos (15:12:40, 38 s; 15:17:32, 21 s) | The **phone hosted and the Quest joined** (the log: "our machine is #1"). "The phone looks right" is therefore host against client, not phone against VR code. On the client, cutscene characters stand where they were while the host's positions slide them, a crewman stands on top of a bridge console, and Cortana's hologram is on the floor. Thousands of "biped crewman fell outside world and was erased" lines every tick. |
| The same game log, crash | `EXCEPTION halt in units/unit_dialogue.c,#406` as a crewman was shot after the pistol pickup. Symbolized against 1.0.6's ELF: `network_campaign_script_receive → hs_campaign_replay → scripted_sound_new → unit_notify_impulse_sound`. |
| A Quest 2 report (multiplayer client) | Red text filling the screen: "playing in another's game: its host's rules…". |
| A player's first-Quest log (Android 10, build 1.0-test18) | The disc mounts, then "cannot reserve the Xbox memory window at 80000000 (No such file or directory)". |

## Causes and changes

1. **Co-op crash (fixed).** The host forwards every unit's speech, death screams included, as a scripted sound. When the death reached the client first, `unit_speak` correctly refused the dead unit scripted speech, and the assertion that it had taken it halted the game (these builds keep the original's assertions). The sound still plays; a dead unit now keeps no speech, as in the retail game. Weapon fire was not involved.
2. **Cutscene placement (fixed, general).** A script's teleport of a character standing still (`object_teleport`) is "at rest" again the same tick, and the host sent resting objects only in a slow round-robin. Characters therefore stood in the wrong place, then glided. The host now remembers where each resting object was when last sent and sends it at once when it moved more than 5 cm or turned (the client's own tolerances).
3. **Cutscene animation (fixed, general).** AI command lists (cutscenes' `animate`, alerts) start animations directly, which were never sent; script custom animations went as the script call, and each device picked its own random permutation. The host now sends every user animation as it played it (graph, animation, frame, interpolation) with the biped's absolute-movement and no-collision flags, in a new reliable message. The client plays exactly that; nothing walks into consoles, and nothing slides idle. Script custom animations are no longer also sent as calls.
4. **A client's fallen copy of a host biped** is reported once instead of every tick; the host's word decides.
5. **Co-op protocol CE02.** Two new campaign messages (animations; glass). 1.0.8 needs 1.0.8 on both devices; a 1.0.7 device is listed as "another app version" and refused with a plain message.
6. **Quest 2 red text (fixed).** The Quest 2's medium graphics preset turns shadows, reflections and lens flares off every frame; the multiplayer client's rule enforcer turned them back on every frame, warning each time. These are only cosmetic, so a client may keep them off. Water, grass, fog and the world itself are still drawn for everyone, and the preset now leaves those on in another's game. The warning appears once per game.
7. **First Quest start (fixed).** Kernels before 4.17 do not know `MAP_FIXED_NOREPLACE` and take the address as a hint, mapping elsewhere without an error. That was treated as a plain failure with a stale error code, so Android's idle space in the way was never reclaimed. It is now treated as "in use", which reclaims it; the remaining failure says plainly that the game files are fine and asks for a restart and the log.
8. **Upstream OpenCE Build 128** reviewed: engine speed-ups (`197c1994`, engine half), glass sync (`7a1ffca2`, adapted to CE02), a client never reverting alone (`b843156f`). See [UPSTREAM-REVIEW-2026-10-05.md](UPSTREAM-REVIEW-2026-10-05.md). The launcher still updates only to this project's releases.
9. **Controls (Quest).** Left stick click toggles the reticle (starts shown); crouch moved to the right stick held down (one-time migration of old configs; ducking still crouches). Controls → **L Stick Click: Crouch** restores the old layout exactly. Gun hand to its own temple toggles the HUD (on by default, reach 10 cm, adjustable or off). The flashlight tap's reach is adjustable (10–30 cm or off). Optional wrist HUD (off by default) on the back of the off-hand wrist, read like a watch. The new **HUD + Reticle** and **Head Gestures** pages; the **Reticle** row and **R Down** source on BUTTONS.
10. **Impact melee.** The gun strikes along its length (grip, middle, a long gun's far end) and a fast swing reaches up to 15 cm past the tracked hand, so swings that stopped against a character's collision now land. A hand carried inside a character counts; walls still stop the blow.
11. **Fingers.** Contact is searched continuously per finger (no jumps between a few poses), joint by joint (fingertips buckle from the tip; a pressed palm straightens from the knuckle), keeps its direction while in contact and eases out.
12. **Version 1.0.8 / code 34.**

## Defects found by the new tests before delivery

- The animation marks were cleared by the impulse flush, which runs just before the animation flush, so item 3 would never have sent anything. Fixed; `test_campaign_actors` now runs the messages end to end.
- The finger joints' pacing tables were swapped against their own description (the tip moved first when flattening). Fixed; `test_quest_vr_math` checks the order and continuity.
- The wrist panel faced out of the palm, not the back of the wrist (OpenXR's grip +x is out of a left palm), so it would not have appeared in the watch pose. Fixed; `test_test26` places it in a watch pose for either hand.

## Status

| Item | Implemented | Automatically verified | Device |
| --- | --- | --- | --- |
| Co-op crash | Yes | Guard placed after the speech attempt, before the assertion | Needed: co-op, crewmen killed near the client |
| Cutscene placement and animation | Yes | Resting teleports resent (tolerances, NaN, slot reuse); animations and flags sent, applied, validated; 1.0.4 reconciling unchanged | Needed: co-op a10 bridge and later cutscenes on the joining device |
| Glass sync | Yes | Host capture, refresh coverage, client validation | Needed: break glass in co-op |
| Quest 2 red text | Yes | 1.0.7 reproduced (98 of 98 frames fought); none now on any headset/setting/order | Needed: a Quest 2 joining multiplayer |
| First Quest start | Yes | Both kernel kinds simulated; 1.0.7's stale error reproduced | Needed: a first-generation Quest |
| Reticle, crouch, migration, L Stick Click | Yes | Mirror image for left-handed; migration cases; toggle restores 1.0.7 buttons; no button doubled | Needed |
| HUD tap, flashlight reach | Yes | Toggle, re-arm, head turn, false-trigger poses | Needed |
| Wrist HUD | Yes | Watch pose both hands, hidden cases | Needed: readability |
| Melee, fingers | Yes | Static wiring; finger curls continuous and bit-identical to 1.0.7 at one curl | Needed |
| Upstream | Yes | Markers in place | General play |
