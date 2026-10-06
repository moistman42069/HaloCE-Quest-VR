# Test28 — v1.0.10 release delivery: co-op joined in progress, larger lobbies, gyro aim

Published as the new Latest release on 2026-10-06. The previous public v1.0.6
release and its assets remain intact. Test27 (1.0.9) was a candidate only. Details: [TEST28-PROGRESS.md](TEST28-PROGRESS.md),
[OpenCE co-op compatibility](OPENCE-COOP-COMPATIBILITY.md).

## Installation

- Android/flat: `HaloCE-Android-1.0.10.apk` (package `com.halo.decomp`)
- Quest/VR: `HaloCE-Quest-1.0.10.apk` (package `com.halo.decomp.vr`)

Both are **version 1.0.10 / code 36**, ARM64, API 28+, signed with the same
certificate as every release since v1.0.2. They install over v1.0.6 through
1.0.9 without uninstalling (`adb install -r <apk>`). Do not uninstall or
clear data. The network is unchanged from 1.0.9: OpenCE network version
**20** (OpenCE build 138).

## Changes

1. **Joining a co-op game in progress no longer stops with the blue screen.**
   A player who joins without a body yet watches the host from behind.
   OpenCE's camera for that went crooked when the host looked up or down,
   and this app halted on it.
   - The camera is now kept upright.
   - The APKs are now built the way OpenCE ships its own (release mode). If
     some other OpenCE check fails, it is written to the log and the game
     carries on.
2. **Co-op lobbies as big as OpenCE's.** Host campaign now offers 2, 4, 8,
   12, 16, 24, 32, 48, 64, 96 or 128 players, the sizes OpenCE's Server
   Setup offers. Before, 16 was the most. The default stays 4, because a full
   lobby starts by itself.
3. **Gyro aim on phones (Android APK only), off by default.** Turn the phone
   to aim. Options:
   - **Always on**, or **only while a finger is on LOOK or FIRE**;
   - horizontal and vertical sensitivity;
   - invert.

   Set it in the game (HUD → Options → Gyro aim, then Save) or in the
   launcher (Controller & touch settings). It works together with swipes and
   a controller.
4. Everything from 1.0.9 and earlier is kept.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Android-1.0.10.apk` | 26,253,876 | `70c712edb5a7b525a0f806ff6643e0ed6be61067022223dd45532ae60c0f28d8` |
| `HaloCE-Quest-1.0.10.apk` | 28,265,091 | `5e7beecb4ea9216b3f3d8268899fd210db1f4b8adfbe47bea3f714caa1f207ba` |

Runtime source `235c2f5b` on branch `test27-opence-netcode`; later commits
change only documentation. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. Built
serially from a clean tree; payload, signing and 16 KB alignment verified.

## Checks performed

- 30 regression suites pass, including the new `test_test28`:
  - the host-watching camera over 19,032 views, the logged one included;
  - release mode;
  - co-op sizes against OpenCE's list;
  - the gyro math and wiring.
- Cache formats pass. Both editions build in release mode without errors.
- The owner reports that co-op testing on this candidate works well. The exact
  device pairing, lobby size and mission coverage were not supplied, so this
  does not establish every cross-platform pairing or performance at 128 players.
- The new Android gyro option and maximum-size lobbies still need broader
  device/performance feedback.

## Please test (for each test, note the app version on every device, the OpenCE build if any, the devices, and Wi-Fi or mobile data)

1. **Join an OpenCE co-op game in VR (the one that failed):** on the Quest,
   open Multiplayer > System Link > Refresh and join a public co-op game that
   is already under way. Expected:
   - you watch the host for a moment, then get your own body;
   - play for a few minutes: fights, a door or two, a checkpoint.

   Send the log.
2. **The same on the phone**, if you can.
3. **Host a big co-op game:** launcher > Campaign co-op > Host campaign, then
   pick "Up to 24 players" or more and keep Public ticked. Check that it
   shows up in the browser with that size. If others join, note how smooth
   it stays.
4. **Gyro aim (phone):** HUD > Options > Gyro aim > Always on, then Save.
   - Turn the phone left and right and tilt it up and down: the view should
     follow, the right way round, with no drift when you hold still.
   - Try "only while a finger is on LOOK or FIRE": the view should turn only
     while touching.
   - Try the sensitivity and invert.
   - Turn it Off: the phone's turning should no longer aim.
   - Check the launcher's Controller & touch settings shows the same choice.
5. **Everything else:** a few minutes of single player in VR and on the
   phone, to confirm nothing else changed.

If something fails, note the time and send the logs from `Download/HaloCE`
(and OpenCE's `debug.txt` if a PC was in the game). Lines starting
`EXCEPTION … (release build)` are checks that failed and were let go. Please
send them even if the game kept running.
