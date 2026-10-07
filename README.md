# Halo CE Quest VR + Android 1.0.12

[Latest release and downloads](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.12) · [Previous release v1.0.11](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.11) · [Full release notes](docs/RELEASE-1.0.12.md) · [Controls and settings](docs/CONTROLS-AND-OPTIONS.md) · [Credits](CREDITS.md)

Halo: Combat Evolved for standalone Meta Quest VR and flat Android, built on the Halo CE decompilation. Version **1.0.12 / code 38** uses OpenCE Build 144's native network version 21 for PvP and campaign co-op.

## Downloads and installation

| Device | Download |
| --- | --- |
| Android phone/tablet — flat play | [HaloCE-Android-1.0.12.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.12/HaloCE-Android-1.0.12.apk) |
| Meta Quest — standalone VR | [HaloCE-Quest-1.0.12.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.12/HaloCE-Quest-1.0.12.apk) |

Both APKs are ARM64 and require Android 9/API 28 or newer. Quest requires Developer Mode and sideloading. Install over the existing project app; **do not uninstall or clear app data**. Back up saves and game data first. Import your own legally obtained Xbox Halo CE ISO/XISO or extracted game data through launcher **Game files & versions**. No game maps are distributed.

## What's new

- VR menus now map Quest A/X/Y to the matching on-screen button labels; X deletes the selected profile and B backs out once. Gameplay bindings are unchanged.
- Campaign co-op hosting now accepts an optional, remembered server name (up to 15 printable ASCII characters); blank keeps the device name. It appears in lobbies and server browsers.
- This is a small update: OpenCE Build 144/network 21 and all v1.0.11 features remain unchanged.
- OpenCE Build 144 netcode, network v21, plus upstream co-op replication and area-transition fixes.
- Fixed HUD head tap behavior; added HUD visibility and head-tap settings, wrist HUD placement/size controls, and two-hand movement alignment.
- Added glasses FOV and resolution options through 200% (125% Q3 approximates Quest 3 panels).
- Co-op lobby-size choices range from 2 to 128; 128 is an engine option, not a tested Quest/phone performance target.
- VR options include the optional wrist HUD, flashlight/HUD gestures, configurable body and finger modes, weapon grip/aim tuning, close-contact movement, melee and vehicle adjustments. **Legs + Arms** and **Third Person + Right Hand steering** are the defaults; first-person vehicles remain experimental.
- Flat Android gyro aiming is optional and off by default; controller/touch settings and per-launch logging remain available.
- Android includes the controller/touch adjustment guide below, game-data revision manager, updater and per-launch logging.

## Quick inputs

**Quest VR:** left stick moves; right stick turns; triggers fire/zoom; right A jumps/confirms; right B reloads/uses; left Y switches weapons; left X throws or changes grenade type; left stick click hides/shows the reticle (starts visible); hold the right stick down to crouch; right stick click melees; click both sticks to recenter. In menus, A/X/Y perform the matching on-screen action (X deletes the selected profile); B backs out once. Gameplay bindings are unchanged. Crouch moved from the old left-stick-click binding: restore it in **VR menu → Controls → Page 2 → L Stick Click → Crouch**. In co-op, **A** cycles the watched teammate and votes during a skippable cutscene.

**Flat Android gamepad:** left stick moves, right stick aims; RT fires, LT throws grenades; A jumps/confirms; B melees/cancels; X reloads/uses; Y switches weapons; LB flashlight; RB grenade type; stick clicks crouch/zoom; Start pauses. In co-op, A cycles the watched teammate or votes to skip a cutscene. Keyboard players press Space to vote.

**Android gyro aim:** HUD → Options → Gyro Aim, or launcher **Controller & touch settings**. It is off by default; choose Always or only while touching LOOK/FIRE, then adjust horizontal/vertical sensitivity and inversion. It works alongside touch and gamepad aiming.

### Android control setup

- **Gamepad:** connect by USB or Bluetooth. Defaults use Xbox-style positions: left stick move, right stick aim, RT fire, LT grenade, A jump, B melee, X reload/use, Y switch weapon, LB flashlight, RB grenade type. Adjust stick/trigger dead zones, response, vibration, face-button swap and touch visibility in launcher **Controller & touch settings**.
- **Touch:** tap **HUD** in game to move or resize buttons and adjust opacity, color and response. Use **MOVE + swipe** for movement and aiming, or drag **FIRE** to combine move/aim/fire. Touch visibility can be Auto, Always show or Always hide.
- Detailed guides: [Android gamepad](docs/ANDROID-GAMEPAD.md) · [touch controls and HUD editor](docs/ANDROID-TOUCH-CONTROLS.md).

## Multiplayer and campaign co-op

All peers must use **network version 21** (OpenCE Build 144 / this release); v1.0.11 peers remain compatible, while v1.0.10/network-20 and other versions are incompatible. Host from launcher **Campaign co-op → Host campaign**, select mission, difficulty and player limit, and optionally enter a remembered server name (up to 15 printable ASCII characters; blank uses the device name). Start from the game lobby. Join from **Multiplayer → System Link → Refresh** or the launcher's co-op browser, then select the host in System Link. Public lobbies appear in native OpenCE discovery/community listings; LAN also works.

No device session on this exact v1.0.12 APK pair was recorded before publication. Prior co-op functionality remains and network v21 is unchanged; please verify hosting/joining after updating. Larger lobby options are available, but high player-count performance and every device/network combination have not been established. Use matching campaign maps. Strict NAT, passwords, modified content, missing maps or version mismatches can prevent joining.

## Support

DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord server](https://discord.gg/S9uSCKxKx). Include app/OpenCE version, device and OS, game-data revision/build, map, network type, steps and logs from all players. Android logs are under **Download/HaloCE** when permitted; remove private invite/device details before sharing.

See the [complete v1.0.12 release notes](docs/RELEASE-1.0.12.md) for installation, controls, VR/mobile settings, multiplayer/revision compatibility, known issues and credits. The GitHub About description is unchanged.
