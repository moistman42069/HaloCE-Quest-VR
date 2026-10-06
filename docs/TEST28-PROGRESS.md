# Test28 checkpoint: co-op joined in progress, OpenCE-sized co-op hosting, gyro aim

Updated 2026-10-06. Private candidate **test28, version 1.0.10 / code 36**,
branch `test27-opence-netcode`, on top of test27 (1.0.9 / code 35). Not
released: GitHub's Latest is still v1.0.6.

## Reports and requests

1. The owner (Quest 3, 1.0.9) joined a public OpenCE co-op game (128-player
   lobby, 18 players on The Maw, d40) and got the blue halt screen right after
   the map loaded. Request: find the cause, review any misses, fix.
2. Add gyro aiming to the Android (flat) port, as an option.

## What the 1.0.9 log proves

The log (kept private) shows OpenCE cross-play working as far as the halt:
- the signed lobby found;
- join stages 1/3 to 3/3 connected;
- "joining a host of network version 20";
- the game joined in progress at tick 20227;
- d40 loaded.

This is the first real cross-build session. Joining and loading an OpenCE
build 138 co-op game work. Play after the load is still to be confirmed.

## The halt and its fix

- **Symptom:** `EXCEPTION halt in camera_scripting.c #370` one tick after the load. The camera's forward was (-0.990, -0.060, -0.126) and its up was (0, 0, 1).
- **Cause (symbolized):** the call chain is `network_coop_client_tick` → the camera watching the host → `director_update` → `scripted_camera_update`.
  - A player who joins in progress has no unit yet, so they watch the host from behind.
  - OpenCE's `client_watch_host_from_behind` sets up to the world's and keeps it whenever `distributed_axes_make_valid` refuses it. That happens when the host looks more than about 6 degrees up or down.
  - So the camera's axes were not square, and the scripted camera's check failed.
- **Why OpenCE players don't see it:** OpenCE ships release builds (`--release`, HALO_RELEASE), where a failed check is written to `debug.txt` and play goes on. This app built without `--release`, so the same check halted.
- **Fix, part 1:** up is made square to forward (`network_coop.c`; the only change to that OpenCE file).
- **Fix, part 2:** the APKs now build with `--release` as OpenCE's do. Any other upstream check that fails is logged as `EXCEPTION … (release build)` in the game log, and the game carries on instead of halting.

## Review of other misses

- **Co-op lobby size:** OpenCE's Server Setup offers co-op games of 2, 4, 8, 12, 16, 24, 32, 48, 64, 96 or 128 players (16 by default; `menu_functions.c`). This app hosted 16 at most. Now:
  - the launcher offers the same sizes (4 by default, since a full lobby starts by itself);
  - the game takes them (`network_campaign_session.c`, `network_server_manager.c`);
  - 1.0.8's request format still means 16.

  Every per-player table, VR avatars included, was already sized for 128.
- **Joining large games:** nothing limits joining by size. The joined game had 18 players.
- **Upstream:** OpenCE `main` is still `76addf66` (build 138); nothing newer to integrate.
- **Release mode logging:** release-mode failures reach the same game log the owner sends (Download/HaloCE).

## Gyro aim (flat Android)

- **Option:** off by default. Choices are Off, Always on, or Only while a finger is on LOOK or FIRE (lift your thumb to re-center, like lifting a mouse). Horizontal and vertical sensitivity run from 0.25 to 4, where 1 is the phone's own turn; vertical can be inverted.
- **Where:** the in-game touch Options (HUD → Options) and the launcher's Controller & touch settings. Both share the same settings.
- **How:**
  - `GyroAim` reads the gyroscope at game rate and sends the turn the same way a swipe does (`nativeLook`). The game already takes swipe turns for player one, drops them in menus, and turns off aim magnetism while they are in use, as it does for a mouse.
  - With the gravity sensor, a turn of the body turns the view however far the phone is tilted back ("player space").
  - Very slow turns are eased off, so a phone held still does not creep.
  - It listens only while the game is resumed and focused and the option is on. Nothing is sent while the HUD is being edited.
  - The gyroscope is an optional feature: phones without one still install, and the option says so.
- **Not changed:** native code, VR, swipe/stick aim, controllers.

## Evidence

`tools/test_test28.py`:
- runs `client_watch_host_from_behind` over 19,032 views, the logged one included;
- checks the `--release` flags;
- checks the co-op sizes against OpenCE's list;
- runs the gyro math (`GyroPolicy`): every display rotation, upright, tilted back 0–80 degrees, flat, sensitivity, invert, a still phone, bad samples and stalls;
- checks the gyro wiring: flat only, stopped when paused, unfocused, off or editing, and the settings shared with the launcher.

`test_test27` now reads the co-op limits from the source. 30 regression suites and the cache-format tests pass. Both editions build in release mode.

## Next

The owner's device tests ([TEST28-DELIVERY.md](TEST28-DELIVERY.md)):
- join an OpenCE co-op game in progress (VR) and play on;
- host a co-op game larger than 16;
- gyro aim on a phone.
