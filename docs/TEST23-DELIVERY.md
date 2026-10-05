# Test23 — 1.0.5 candidate (private): co-op cutscenes, remappable Quest buttons

Not a release. The public release is v1.0.3 (test21b, code 27). Do not
publish without explicit owner approval. Evidence, causes and status:
[TEST23-PROGRESS.md](TEST23-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test23.apk`
- Android/flat: `HaloCE-Android-test23.apk`

Both are **version 1.0.5 / code 30**, ARM64, API 28+, signed with the same
certificate as v1.0.2, v1.0.3 and 1.0.4, so they install over any of them
without uninstalling (`adb install -r <apk>`). Do not uninstall or clear data.
Back up first. **Co-op needs the same version on every device.**

## Changes

1. **Co-op cutscenes (both).** On the device that joined, cutscene characters
   now stand where the host has them at every cut instead of sliding there in
   a falling (T-pose-like) pose. Gameplay, players and vehicles are unchanged.
2. **Grenade on Left X (Quest).** In both weapon modes a tap of X throws a
   grenade and a 0.4 second hold switches grenade type. With Locked weapons
   the grip no longer throws; it only switches weapons at a holster.
3. **BUTTONS page (Quest).** VR Settings → BUTTONS remaps Jump, Action /
   Reload, Melee, Crouch, Switch Weapon, Grenade and Switch Grenade. A button
   already in use is swapped, so no button does two things. **Reset Buttons**
   restores the defaults. Setting Grenade to Grip (Locked) restores the old
   Locked layout.
4. **Diagnostics (both).** The joining device logs cutscene cues it had to
   skip.

Not changed: weapon handling, two hands, melee, reload, holsters, triggers,
left-handed mirroring, other controllers' layouts, vehicles, aiming.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test23.apk` | 28,088,963 | `3900b31fbd422d0e15fb865fc5c4c0dec4ab8f8901ba392bd6231b4bbe0e93b6` |
| `HaloCE-Android-test23.apk` | 26,077,748 | `87b01c2cc3c1258f6287f30017ced6688de620430b21b6a90b2d670f43788974` |

Runtime source `fb1d094b` (runtime changes in `dc0d9d88`) on branch `test21-hands-body`; later commits
change only documentation and packaging tooling. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, the same as
v1.0.2, v1.0.3 and 1.0.4. Built serially from a clean tree; payload, signing
and 16 KB alignment verified.

## Checks performed

- 24 runner suites pass, including new `test_test23`:
  - the default Quest layout matches 1.0.4 for every combination of A, B, Y
    and the stick clicks in both weapon modes; the locked grip throws nothing;
    an X tap throws once and a hold switches grenades once;
  - a grenade on the grip throws only with Locked weapons, away from the
    holsters, and X then switches grenades;
  - menu swaps, the grip-grenade layout and back, and 20,000 random menu
    changes never leave one button doing two actions;
  - the cutscene placement applies only on a joining device during a
    cutscene, to characters no player controls.
- `test_test20d`: 24,000 random frames confirm left-handed play is still the
  exact mirror of right-handed play.
- Cache formats: 127 passed, 4 missing-fixture skips.
- Both editions compile without warnings in the changed files; packaging checks
  pass.
- **Not done:** no phone or headset session. Your tests decide.

## Please test

1. **Co-op cutscenes (most important):** host co-op a10 on the phone and join
   from the Quest. Watch the opening cutscene on the Quest: the characters
   should stand, walk and animate as on the phone, with no T-pose or sliding.
   Then swap roles (host on the Quest, join from the phone) and watch it on the
   phone. Send both logs either way.
2. **Grenade:** with Weapons: Locked, tap X to throw, hold X to switch grenade
   type, and squeeze the gun hand's grip: nothing should happen (at a holster
   it still switches weapons). Repeat with Weapons: Physical.
3. **BUTTONS page:** set Jump to X: Grenade should move to A by itself. Try a
   few changes, then Reset Buttons and check A jumps, B reloads, Y switches
   weapons and X throws again.
4. **Nothing else changed:** reload, melee, two-hand grip, holsters, picking
   up and dropping guns (Physical), and left-handed mode.
