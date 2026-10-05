# Test25 — 1.0.7 candidate (private): vehicles, settings rows, upstream fixes

Not a release. The public release is v1.0.6 (code 32), which the owner has
tested on device. Do not publish without explicit owner approval. Details:
[TEST25-PROGRESS.md](TEST25-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test25.apk` (package `com.halo.decomp.vr`)
- Android/flat: `HaloCE-Android-test25.apk` (package `com.halo.decomp`)

Both are **version 1.0.7 / code 33**, ARM64, API 28+, signed with the same
certificate as every release since v1.0.2, so they install over v1.0.6
without uninstalling (`adb install -r <apk>`). Do not uninstall or clear data.
Back up first. **Co-op needs the same build on both devices.**

Edition-specific: the vehicle, glass, horizon, menu and diagnostics changes are
VR only (the flat edition has no VR menu or seat view). The four upstream fixes
and the launcher are shared.

## Changes

1. **Settings rows fit (Quest).** Rows are wider and some names shorter, so
   values and their **<** **>** arrows are no longer cut off. Renamed:
   FORWARD → **FWD** on the Vehicles and Scopes pages; Crosshair Opacity →
   **OPACITY**; Action / Reload → **USE / RELOAD**; Switch Weapon/Grenade →
   **NEXT WEAPON/GRENADE** (values **GRIP**, **HOLD**); Vignette When →
   **VIGNETTE ON: MOVING / TURNING / ALWAYS**. Your saved settings are kept.
2. **Vehicles → RESET OFFSETS (Quest)** puts all seat Up/Fwd/Right offsets
   back to 0.
3. **First-person vehicles (Quest, still experimental and off by default):**
   - **HORIZON: Level** (as before), **Half** or **Vehicle**. Vehicle keeps
     the cockpit still and tilts the world instead, for the driver's seat.
   - The glass of the vehicle you sit in is no longer drawn from inside (the
     white windshield).
4. **Vehicle report diagnostics (Quest):** the log now records every recenter,
   getting in or out of a seat, and view switches while seated.
5. **Upstream fixes (both):** no more streaks from geometry touching the
   camera; a death-camera bug when nobody is alive (co-op); a one-draw wrong
   texture after a texture loads; the radar wedge fades out fully.

Unchanged: third-person vehicles and right-hand steering as defaults,
co-op (still two players), comfort settings, buttons, network version 11.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test25.apk` | VR_BYTES | `VR_SHA` |
| `HaloCE-Android-test25.apk` | FLAT_BYTES | `FLAT_SHA` |

Runtime source `RUNTIME_COMMIT` on branch `test25-vehicle-recenter`; later
commits change only documentation and packaging tooling. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, as every
release since v1.0.2. Built serially from a clean tree; payload, signing and
16 KB alignment verified.

## Checks performed

- 27 runner suites pass, including new `test_test25`: settings rows fit;
  Reset Offsets; the horizon's tilt; the seat glass; the diagnostics; adopted
  upstream fixes in place; defaults kept.
- Cache formats: 127 passed, 4 missing-fixture skips.
- Both editions compile without warnings in the changed files; packaging checks
  pass.
- **Not done:** no phone or headset session. Your tests decide.

## Please test

1. **Menus:** open VR Settings and look through every page: no row should be
   cut off. On Vehicles, step **ALL FWD** left and right, then **RESET
   OFFSETS**.
2. **Vehicle report:** in a Warthog (third person and first person), recenter
   with both sticks while driving, once looking straight ahead and once
   looking to the side; get out and back in; switch the view. Send the log.
   It now records what the view was doing at each step.
3. **First person (if you want to try it):** Vehicles → View: First Person.
   The windshield should be clear. Drive with **HORIZON** Level, then Half,
   then Vehicle, and say which feels best.
4. **Normal play and co-op:** a few minutes on foot, in co-op and in
   multiplayer, to confirm nothing else changed.
