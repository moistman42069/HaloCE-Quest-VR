# Test22 — 1.0.4 candidate (private): co-op crash, vehicle view, ammo display, scopes

Not a release. The public release is v1.0.3 (test21b, code 27). Do not
publish without explicit owner approval. Evidence, causes and status:
[TEST22-PROGRESS.md](TEST22-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test22.apk`
- Android/flat: `HaloCE-Android-test22.apk`

Both are **version 1.0.4 / code 29** (the launcher now shows 1.0.4; the first test22 pair was 1.0.2 / code 28), ARM64, API 28+, signed with the same
certificate as v1.0.2 and v1.0.3, so they install over either (and over the first test22 pair) without
uninstalling (`adb install -r <apk>`). Do not uninstall or clear data. Back up
first. **Co-op needs the same version on every device.**

## Changes

1. **Co-op crash fixed (both).** An Android host crashed the moment a Quest
   joined and the mission started (every co-op campaign mission, on any pair of
   devices). It was the bug upstream fixed in its PR #73; that fix is applied.
2. **Steadier first-person vehicle view (Quest).** The view now turns with the
   vehicle exactly as it is drawn, and stays anchored to the vehicle instead
   of following the driver's steering and bump animations. The vehicle's own
   turns and bounce stay; the interior no longer shakes against your view.
3. **Left-hand ammo counter (Quest).** Holding the assault rifle left-handed,
   its counter now reads the right way round, as in the right hand.
4. **Adjustable scopes (Quest).** VR Settings → **SCOPES**: pistol and sniper
   scopes each move forward/up/right and change size; Reset Scopes restores
   them. Untouched, they are exactly as before.
5. **Upstream fixes (both).** Reviewed the 16 newest upstream decomp commits (no
   protocol change): no grenades from vehicle seats with no weapon, a menu crash
   guard, upstream's own server-browser/invite broker added first, and the
   shotgun's HUD ammo meter alignment.
6. **Diagnostics.** The log now notes where shots went against the aim and the
   reticle (Quest), and frames that had to catch up game ticks (both).

Not changed: aiming (a player's report came from v1.0.2; v1.0.3 already has
the fix), vehicle mechanics, third-person vehicle view, performance settings.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test22.apk` | 28,084,867 | `2dbd82756ab4a69c4cd614a56d258ea89093db48c288a772275835f43c078637` |
| `HaloCE-Android-test22.apk` | 26,077,748 | `402d3dd879c1ced7020d6f68c7dedec45bad2cedc7ff3db19a0ace13f8726254` |

Runtime source `afeed66d3ef537cea2552570fc8747070733ac5d` on branch `test21-hands-body`; later commits
change only documentation and packaging tooling. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, the same as
v1.0.2 and v1.0.3. Built serially from a clean tree; payload, signing and 16 KB
alignment verified.

## Checks performed

- 23 runner suites pass, including new `test_test22`:
  - an unarmed blow on a campaign map never reads the empty weapon list;
    multiplayer and bipeds with their own blow unchanged;
  - the vehicle seat anchor follows a moving, turning, pitching vehicle exactly
    over 2,000 frames, cuts a 5 cm head bob to 11%, snaps on a new seat; the
    view's heading follows the drawn vehicle, across the ±180° wrap;
  - scopes with nothing set are placed and sized exactly as before (pistol,
    sniper, rocket, either hand); adjustments apply to their own scope only;
  - wiring for the upstream fixes, broker migration, left-hand display,
    diagnostics (the Android weapon code is unchanged).
- Cache formats: 127 passed, 4 missing-fixture skips.
- Both editions compile without warnings in the changed files; packaging checks
  pass.
- **Not done:** no phone or headset session. Your tests decide.

## Please test

1. **Co-op (most important):** host co-op on the phone (a10 and a30), join from
   the Quest. Both should load in and play. Try shooting, melee, a vehicle, a
   checkpoint, dying and respawning, and an area change. Then host on the Quest
   and join from the phone. Send both logs either way.
2. **First-person vehicle:** VR Settings → Vehicles → View: First Person. Drive
   the Warthog over bumps and through turns. The dashboard should stay still in
   your view; only the outside should move.
3. **Left hand:** Controls → Handedness: Left, hold the assault rifle: the ammo
   counter should read correctly. Check it still looks right in the right hand.
4. **Scopes:** zoom with the pistol and the sniper: they should look as before.
   Then open VR Settings → SCOPES, move and resize each, zoom again, then Reset
   Scopes.
5. **Server browser and invites:** public games should still list and join.
6. **Phone performance:** if frames drop in a big server again, send the log
   (look for "[game-ticks]").
