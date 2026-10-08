# Halo CE Quest VR + Android

**Latest release: [v1.0.18](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.18)** · OpenCE Build 157 · network 24

Halo CE for standalone Meta Quest VR and flat Android. The release includes an in-game OpenCE server browser and campaign co-op, tracked VR body and hands, customizable Android touch/gamepad controls, and a launcher for game-data management and updates. It does not include Halo game data; provide your own supported Xbox game files.

## Downloads and installation

| Device | Download |
| --- | --- |
| Android phone/tablet — flat play | [HaloCE-Android-1.0.18.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.18/HaloCE-Android-1.0.18.apk) |
| Meta Quest — standalone VR | [HaloCE-Quest-1.0.18.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.18/HaloCE-Quest-1.0.18.apk) |

Both APKs are ARM64 and require Android 9/API 28 or later. Enable app installation from your browser/file manager on Android. For Quest, enable Developer Mode and sideload the Quest APK with SideQuest or ADB. Install over the existing project app to preserve saves, settings and imported game data. **Do not uninstall the old app or clear its data.** Back up important data before updating.

On first launch, use **Game files & versions** to import your own legally obtained Xbox Halo CE ISO/XISO or extracted game files. See the [complete v1.0.18 release notes](docs/RELEASE-1.0.18.md) for setup, controls, network selector, compatibility and known issues.

## Highlights

- OpenCE Build 157 / network 24 with native in-game server browsing and campaign co-op. The launcher adds a population-sorted client target selector for compatible networks 11–24; hosting remains network 24.
- Build 157 analog trigger pressure, PC vehicle-set support, Custom Edition spawn facing, host-alone lobby start and spatial stereo world audio. Build 148 particle-radius validation and clearer native halt-screen details remain.
- Quest OpenXR rendering, full set of VR body/hand modes, controller-driven fingers, weapon alignment, Safe geometry by default and adjustable comfort/vehicle/HUD settings.
- Android touch HUD editor, swipe/fire-drag controls, optional gyro aiming, Xbox-style USB/Bluetooth gamepads and controller-aware touch visibility.
- Launcher game-data/revision manager, updater, settings, help and per-launch logs.

## In-game multiplayer and co-op

Open **Play → Multiplayer**. Join through the in-game server browser or LAN list. To host PvP, choose **Create Game → Internet or LAN → Multiplayer**, configure the match and server, then start the lobby. To host campaign co-op, choose **Create Game → Internet or LAN → Singleplayer**, select a mission and difficulty, configure **Server Setup**, and start the lobby. Share the invite or make the lobby public. Hosting is network 24. Client targets 11–22 are limited to original Xbox-map PvP; co-op and Custom Edition need host version 23 or 24. The selectable co-op limit up to 128 is an engine option, not a performance guarantee.

For detailed paths and controls, use the [player guide](docs/PLAYER-GUIDE.md) and [controls/settings reference](docs/CONTROLS-AND-OPTIONS.md). The launcher’s **Multiplayer & co-op guide** also has offline instructions.

## Game revisions and support

Import multiple supported game-data sets and switch them in **Game files & versions**. The manager recognizes supported Xbox cache build identifiers, but it does not reliably infer every Original/Rev 1/Rev 2 disc label or guarantee full-disc integrity. Different map files or revisions can prevent a multiplayer join.

For best game-data compatibility, the launcher recommends the original Xbox Halo CE XISO. Rev 1 and Rev 2 can be imported where supported, but are not recommended; the browser cannot automatically match a server to every disc revision. For crashes, failed joins, desync or compatibility reports, include the device/OS, app and network versions, selected game-data set, map/mission, connection type, reproduction steps and logs from each player. Android logs are saved under **Download/HaloCE** when permitted. Contact **@MeWhenINameMyself** by DM or report in the [Halo CE Decomp Discord](https://discord.gg/S9uSCKxKx). Remove private invite and device details before sharing.

## Project

This is an unofficial community port and contains no Halo game assets. OpenCE networking and campaign co-op are from [OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE). The glasses-FOV and resolution contribution by [Willem Horak, PR #1](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1) is included. Additional contributors and licenses are in [CREDITS.md](CREDITS.md) and [THIRD-PARTY-NOTICES.txt](THIRD-PARTY-NOTICES.txt).
