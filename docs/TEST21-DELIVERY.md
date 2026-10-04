# Test21 — 1.0.2 candidate (private): hands, body turns, Full Body, two-hand lock, horn, online melee, pistol aim

Not a release. The public release stays v1.0.2 (test20e, code 25). Do not
publish without explicit owner approval. Evidence, causes and status:
[TEST21-PROGRESS.md](TEST21-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test21.apk`
- Android/flat: `HaloCE-Android-test21.apk`

Both are **1.0.2 / version code 26**, ARM64, API 28+. They are signed with the
same certificate as v1.0.2 (checked against the published APK before building),
so they install over v1.0.2 without uninstalling (`adb install -r <apk>`). Do
not uninstall or clear data. Back up first.

## Changes (Quest; the Android build shares the guide text, the packaging checks and item 9's multiplayer log line)

1. **Floating means hands only again.** Body → Hands: Body IK / **Floating**
   (hands, no arms) / **Float + Arms** / Animated / Gun Only. The wrists of hidden
   arms close neatly instead of looking cut or slivered.
2. **Arms follow your body.** The shoulders face your torso in every Body mode.
   The torso turns with your head beyond 15° and is pulled toward where your hands
   are, so turning your body turns it. It no longer snaps when you look straight
   down.
3. **Full Body looking down.** The body hangs from a neck point behind and below
   your eyes, so looking down shows your chest below you instead of clipping into
   the camera. Legs + Arms stays the default until you confirm Full Body.
4. **Two Hands: Auto Lock (new default).** Rest your off hand on the gun's front
   grip: it locks without squeezing. Pull it away to let go. Squeeze and Off are
   still available. Configs on the old default switch once.
5. **Warthog horn.** While seated, click either stick to honk, even at full
   throttle.
6. **Melee online.** Physical melee is off in multiplayer by default; the melee
   button still works. Body → Melee: Impact + Online / Swing + Online turns it on.

7. **Upside-down gun in two hands (Quest OS v78 report).** If a gun was
   turned upright with Hands + Gun → Gun Roll, two-hand grip now keeps it
   upright (it flipped back before). For hands 180° off, the one-step fix is
   Controller Left/Right → Flip Roll 180 (hand and gun together).

8. **Pistol reticle.** Offline, guns that started their shots at the unseen
   body's gun (the pistol) now fire from your hand, so shots land on the
   reticle. The reticle also includes each gun's built-in shot offset. New
   Hands + Gun → **Aim For / Aim Up / Aim Right / Reset Aim** fine-tune the gun
   you hold (each gun separately, half-degree steps); the gun model doesn't move.
   All guns start at 0, which changes nothing.

9. **Multiplayer VR avatars.** Normal multiplayer already shares VR movement
   like co-op, but only through a host running this build. Your logs show
   games hosted by others on another build (no avatar offer), so the phone
   saw stock animation. A log line now says when that happens.

Kept: Legs + Arms default, gun anchoring, hand/gun calibration, fingers,
reload/grenade/melee animations, left-handed mode, Safe geometry, avatar
movement for other players, Quest/Android networking parity.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test21.apk` | 28,084,867 | `bad2bb564bb200636bc2c1202def673fcd3b3fc1b506a583c35ceff859982553` |
| `HaloCE-Android-test21.apk` | 26,077,748 | `fa9f09aa476f4fa98bc056c67c0fbbd8f44fa94ac43fc0e186a04fe0b743fcb6` |

Runtime source `d0a8e476f9da9b3947eae4cb05b360cb1c1b296e` on branch `test21-hands-body`; later commits are
documentation only. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, the same as
v1.0.2. Built serially from a clean tree; payload, signing and 16 KB alignment
verified.

## Checks performed

- 22 runner suites pass, including new `test_test21`:
  - head yaw stays exact at any pitch (20,000 poses);
  - torso yaw follows the hands ahead and ignores hands behind;
  - the neck pivot keeps the upright offset and stays put as the head pitches;
  - the cuff closes along the hand for 2,000 random hands;
  - online melee gate, horn buttons and the two-hand migration;
  - two-handed aim keeps the gun's roll (2,000 poses, both hands);
  - the reticle's shot offset equals the engine's own shift (5,000 aims);
  - per-gun aim: tag names map to the right gun, the held gun turns exactly up
    and right, and at 0 the aim is bit-for-bit unchanged (4,000 poses);
  - the flat build's weapon code is unchanged, and the hand shot is offline only.
- `test_test20c_hands` and `test_test20d` were updated for the restored modes.
- Cache formats: 127 passed, 4 missing-fixture skips.
- Packaging checks: versions, certificate, Quest/Android networking parity, and
  the new menu and log markers.
- **Not done:** no headset or phone session. Automated checks cannot show how
  hands, arms or Full Body look. Your headset test decides.

## Please test (Quest)

1. **Hands:** Body → Hands → Floating: hands only, with closed wrists. Then
   Float + Arms. Try each Body choice.
2. **Turning:** hold your hands still and turn your whole body slowly through
   half a turn and back, in Arms + Hands, Legs + Arms and Full. The shoulders
   should come with you and the arms shouldn't twist across. Do it again while
   moving your hands, after recentering, and reaching across your body.
3. **Full Body:** look straight down at your chest, turn your head left and
   right, crouch, and walk around the room. Report any clipping, snapping or
   disappearing. Then switch back to Legs + Arms.
4. **Two hands:** with a rifle, move your off hand to the front grip without
   squeezing; it should lock. Pull away; it should let go. Try Squeeze too, and
   left-handed if you use it.
5. **Warthog:** drive at full speed and click either stick to honk.
6. **Multiplayer:** quick hand movements shouldn't melee; the melee button
   should. Send the log.
7. **For the v78 tester:** with Gun Roll 180 (or Flip Roll 180), grip a rifle
   with both hands: it must stay upright.
8. **Pistol (offline campaign):** shoot a wall from about 5 m and 20 m. The
   bullet marks should land on the reticle. If it's still off, open Hands +
   Gun (second screen) while holding the pistol: Aim For should say PISTOL;
   step Aim Up / Aim Right until it lines up (Reset Aim undoes it). Check
   another gun still behaves as before. Online, say whether it still differs.
9. **Multiplayer avatars:** host a game from the Quest or the phone with this
   build, and join it from the other. The phone should show the Quest player's
   head, arms and body moving. Your earlier logs joined public games run by
   someone else ("the BIG CTF", a Hang 'Em High game); those hosts run another
   build and pass no VR movement, so everyone looked like a flat player there.
   The log now says so after 10 seconds in such a game.
