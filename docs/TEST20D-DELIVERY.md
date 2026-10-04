# Test20d — 1.0.2 candidate (private): gun anchored to the controller, left-handed mode, simpler settings

Not a release. v1.0.1 was withdrawn; the public release is v1.0.0. Supersedes
test20c (code 23). Do not publish without explicit owner approval. Full
evidence, cause and status: [TEST20D-PROGRESS.md](TEST20D-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test20d.apk`
- Android/flat: `HaloCE-Android-test20d.apk`

Both are **1.0.2 / version code 24**, ARM64, API 28+, signed with the
established certificate; they install over 1.0, 1.0.1, test20, test20b and
test20c (`adb install -r <apk>`). Do not uninstall or clear data. Back up first.

## Changes

1. **The held gun is anchored to the controller.** Every frame the gun, hands
   and arms move together so the gun hand's wrist sits exactly where your empty
   hand's wrist is, for every weapon, and the gun turns about your hand instead
   of swinging around a point behind it. Reload, melee, grenade and weapon-draw
   animations still play and return to the hand. VR Settings → **Hands + Gun**:
   Gun Forward / Up / Out to fine-tune; **Gun Grip: Classic** for the old
   placement.
2. **Left-handed mode.** Controls → **Handedness: Left** puts the gun in the
   left hand. It also mirrors the sticks (move right, turn left) and the face
   buttons (jump X, reload Y, grenades A, switch weapons B, menu Back Y), and
   moves vehicle steering and Move With to the left hand. **Mirror Controls:
   Off** keeps the standard buttons. A config that was already left-handed keeps
   its old layout until you change it.
3. **Simpler settings.** Nine categories instead of twelve, one row per
   decision: Turning includes the speed; Holsters the size; Weapons the
   multiplayer choice; Arm Run the effort; Body → Hands covers Body IK /
   Floating / Animated / Gun Only. **Hands + Gun** replaces the Left Hand, Right
   Hand and Gun pages (hand rows turn both hands, the left mirrored). Crosshair
   rows moved to **Gameplay**. Floating draws arms unless Body is Hands Only.

Kept: every saved setting (including your Gun Pitch, −15 in your last log), the test20
performance fix, Legs + Arms, Body IK, the −70 hand default, two-hand Grip,
action animations, third-person/right-hand vehicles, VR Safe and flat Normal
geometry. Flat Android changes are guide text only.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test20d.apk` | 28,076,675 | `f2eb7f7235bf4d28d4b80b8dc7ff3ca72cdc90681bb9b642885604833049aebf` |
| `HaloCE-Android-test20d.apk` | 26,073,652 | `6e41bf1f3e58305e49647151a3770f24712225e665f593757adaac83fb21c0c0` |

Runtime source `346b0c074f5ed9ae2627de7bb8dfd19019eb7610`; later commits are documentation only.
Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. Built
serially from a clean tree; payload, signing and 16 KB alignment verified.

## Checks performed

- 19 runner suites pass, including new `test_test20d`:
  - the anchor's state machine over 2,000 random poses, including holds,
    settling, weapon memory, the cap and bad input;
  - the production anchor over 1,200 checked random frames with both hands,
    gun offsets and wall pullback (wrist exact, whole model moves rigidly);
  - 24,000 random input frames where left-handed output equals the mirrored
    right-handed output;
  - every combined menu row round-trips all value pairs, and 26 menu choices
    show their defaults;
  - migrations.
- Cache formats: 127 passed, 4 missing-fixture skips.
- Package checks: versions, certificate, guides, test20d identity, new menu
  rows present, retired rows absent.
- **Not done:** no headset/phone session. The anchored grip, left-handed
  layout and menu text need your eyes.

## Please test

1. **Reset Gun first** (Hands + Gun → Reset Gun): your saved −15 pitch was tuned
   while the gun sat in the wrong place.
2. **Gun in the hand:** with passthrough or by feel, hold the pistol, then an
   assault rifle, shotgun, sniper and a plasma weapon. The grip should sit in
   your palm, and turning your wrist should turn the gun in place. Fine-tune with
   Gun Forward / Up / Out (and Gun Pitch) only if needed. Switch Gun Grip to
   Classic and back to compare.
3. **Animations:** reload, melee, throw a grenade, switch weapons, and drop
   and pick up a gun. The gun should come back to your hand smoothly.
4. **Two hands and walls:** grip a rifle with both hands, then push it into a
   wall. There should be no jitter, and the gun should still pull back.
5. **Left-handed:** Controls → Handedness: Left. Try moving, turning, jump,
   reload, grenades, weapon switch, holsters, two-handed grip, a vehicle and
   the pause-menu pointer/Back. Then try Mirror Controls: Off. Switch back to
   Right afterwards.
6. **Settings pages:** open every category; each row should change, save and
   show a value (not CUSTOM) on your config. Report any clipped text.
7. Body → Hands: Body IK, Floating (with Legs + Arms, then Hands Only),
   Animated, Gun Only. Send the log either way.
