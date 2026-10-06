# Halo CE Quest VR + Android 1.0.10

[Latest release and downloads](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.10) · [Previous public release v1.0.6](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.6) · [Full release notes](docs/RELEASE-1.0.10.md) · [Controls and settings](docs/CONTROLS-AND-OPTIONS.md) · [Credits](CREDITS.md)

Halo: Combat Evolved for standalone Meta Quest VR and flat Android, built on the Halo CE decompilation. Version **1.0.10 / code 36** uses OpenCE Build 138's native network version 20 for PvP and campaign co-op.

## Downloads and installation

| Device | Download |
| --- | --- |
| Android phone/tablet — flat play | [HaloCE-Android-1.0.10.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.10/HaloCE-Android-1.0.10.apk) |
| Meta Quest — standalone VR | [HaloCE-Quest-1.0.10.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.10/HaloCE-Quest-1.0.10.apk) |

Both APKs are ARM64 and require Android 9/API 28 or newer. Quest requires Developer Mode and sideloading. Install over the existing project app; **do not uninstall or clear app data**. Back up saves and game data first. Import your own legally obtained Xbox Halo CE ISO/XISO or extracted game data through launcher **Game files & versions**. No game maps are distributed.

## What's new

- Direct OpenCE Build 138 netcode integration: network v20 for multiplayer and campaign co-op.
- Campaign co-op supports joining an active mission. Lobby-size choices now range from 2 to 128; 128 is an engine option, not a tested Quest/phone performance target.
- Fixed the join-in-progress blue-screen camera fault and build mode now matches OpenCE's release builds.
- Flat Android gyro aiming is optional and off by default, with Always / touch-to-aim modes, sensitivity and inversion.
- Includes earlier VR, gamepad/touch, revision manager, updater, vehicle, body and hand features.

## Quick inputs

**Quest VR:** left stick moves; right stick turns; triggers fire/zoom; right A jumps/confirms; right B reloads/uses; left Y switches weapons; left X throws or changes grenade type; left stick click toggles the reticle; hold the right stick down to crouch; right stick click melees; click both sticks to recenter. In co-op, **A** cycles the watched teammate and votes during a skippable cutscene.

**Flat Android gamepad:** left stick moves, right stick aims; RT fires, LT throws grenades; A jumps/confirms; B melees/cancels; X reloads/uses; Y switches weapons; LB flashlight; RB grenade type; stick clicks crouch/zoom; Start pauses. In co-op, A cycles the watched teammate or votes to skip a cutscene. Keyboard players press Space to vote.

**Android gyro aim:** HUD → Options → Gyro Aim, or launcher **Controller & touch settings**. It is off by default; choose Always or only while touching LOOK/FIRE, then adjust horizontal/vertical sensitivity and inversion. It works alongside touch and gamepad aiming.

## Multiplayer and campaign co-op

All peers must use **network version 20** (OpenCE Build 138 / this release). Older/newer network versions, including this project's 1.0.8 and earlier, are incompatible. Host from launcher **Campaign co-op → Host campaign**, select mission, difficulty and player limit, then start from the game lobby. Join from **Multiplayer → System Link → Refresh** or the launcher's co-op browser, then select the host in System Link. Public lobbies appear in native OpenCE discovery/community listings; LAN also works.

The owner tested co-op and reports it works well. Larger lobby options are available, but high player-count performance and every device/network combination have not been established. Use matching campaign maps. Strict NAT, passwords, modified content, missing maps or version mismatches can prevent joining.

## Support

DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord server](https://discord.gg/S9uSCKxKx). Include app/OpenCE version, device and OS, game-data revision/build, map, network type, steps and logs from all players. Android logs are under **Download/HaloCE** when permitted; remove private invite/device details before sharing.

See the [complete v1.0.10 release notes](docs/RELEASE-1.0.10.md) for installation, controls, VR/mobile settings, multiplayer/revision compatibility, known issues and credits. The GitHub About description is unchanged.
