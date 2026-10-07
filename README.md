# Halo CE Quest VR + Android 1.0.12

Development branch: **test34 / 1.0.15 private OpenCE Build 147 and menu-pointer candidate**.
It adds hover selection for server rows, adopts network 23 with CE map-checksum
matching, integrates OpenCE's tag schemas and validator into the Quest CE cache
loader, and adapts the applicable Build 146/147 safety and capacity changes.
The owner-accepted VR settings and Android touch behavior remain the baseline.
[Current evidence and scope](docs/TEST34-PROGRESS.md).
The public download links below remain v1.0.12 until a release is authorized.

[Latest release and downloads](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.12) · [Previous release v1.0.11](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.11) · [Full release notes](docs/RELEASE-1.0.12.md) · [Controls and settings](docs/CONTROLS-AND-OPTIONS.md) · [Credits](CREDITS.md)

The latest public download from this project remains **v1.0.12 / code 38**. The private Test34 candidate is **1.0.15 / code 44**, adapted to OpenCE Build 147 / network 23. OpenCE's direct Build 147 release page marks it Latest; the general releases listing may still show stale Build 145 metadata. Private candidates are not public downloads.

## Current private candidate: Test34

Test34 updates the native game to OpenCE Build 147 behavior where applicable: network 23 with Custom Edition map-header checksum matching, the upstream tag-schema validator adapted to the Quest cache, Build 147 capacity/co-op/camera safeguards, and pointer hover selection for server rows. It preserves the owner-accepted Android touch behavior and VR settings design. The source-level and APK checks are recorded in [Test34 progress](docs/TEST34-PROGRESS.md) and [delivery](docs/TEST34-DELIVERY.md). These APKs remain private test candidates and have not received device acceptance.

## Downloads and installation

| Device | Download |
| --- | --- |
| Android phone/tablet — flat play | [HaloCE-Android-1.0.12.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.12/HaloCE-Android-1.0.12.apk) |
| Meta Quest — standalone VR | [HaloCE-Quest-1.0.12.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.12/HaloCE-Quest-1.0.12.apk) |

Both APKs are ARM64 and require Android 9/API 28 or newer. Quest requires Developer Mode and sideloading. Install over the existing project app; **do not uninstall or clear app data**. Back up saves and game data first. Import your own legally obtained Xbox Halo CE ISO/XISO or extracted game data through launcher **Game files & versions**. No game maps are distributed.

## What's new in this project's latest published release (v1.0.12)

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

## Multiplayer and campaign co-op in v1.0.12

All peers must use **network version 21** (OpenCE Build 144 / this release); v1.0.11 peers remain compatible, while v1.0.10/network-20 and other versions are incompatible. Host from launcher **Campaign co-op → Host campaign**, select mission, difficulty and player limit, and optionally enter a remembered server name (up to 15 printable ASCII characters; blank uses the device name). Start from the game lobby. Join from **Multiplayer → System Link → Refresh** or the launcher's co-op browser, then select the host in System Link. Public lobbies appear in native OpenCE discovery/community listings; LAN also works.

No device session on this exact v1.0.12 APK pair was recorded before publication. Prior co-op functionality remains and network v21 is unchanged; please verify hosting/joining after updating. Larger lobby options are available, but high player-count performance and every device/network combination have not been established. Use matching campaign maps. Strict NAT, passwords, modified content, missing maps or version mismatches can prevent joining.

## Support

DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord server](https://discord.gg/S9uSCKxKx). Include app/OpenCE version, device and OS, game-data revision/build, map, network type, steps and logs from all players. Android logs are under **Download/HaloCE** when permitted; remove private invite/device details before sharing.

See the [complete v1.0.12 release notes](docs/RELEASE-1.0.12.md) for installation, controls, VR/mobile settings, multiplayer/revision compatibility, known issues and credits. The GitHub About description is unchanged.
