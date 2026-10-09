<p align="center">
  <img src=".github/decomplogo.png" alt="Halo Combat Evolved VR — OpenCE port" width="460" />
</p>

<h1 align="center">Halo CE Quest VR + Android</h1>

<p align="center"><strong>Halo: Combat Evolved on standalone Meta Quest VR and Android</strong><br />An unofficial community port built on OpenCE.</p>

<p align="center">
  <a href="https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.18"><strong>Download latest release · v1.0.18</strong></a>
  &nbsp;·&nbsp;
  <a href="docs/RELEASE-1.0.18.md">Release notes</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/OpenCommunityEdition/OpenCE">OpenCE upstream</a>
</p>

---

## Download and install

**v1.0.18 · OpenCE Build 157 · network version 24**

| Device | Download |
| --- | --- |
| **Meta Quest** · standalone VR | [HaloCE-Quest-1.0.18.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.18/HaloCE-Quest-1.0.18.apk) |
| **Android phone or tablet** · flat play | [HaloCE-Android-1.0.18.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.18/HaloCE-Android-1.0.18.apk) |

Both APKs are ARM64 and require Android 9 / API 28 or newer. On Quest, enable Developer Mode and sideload the Quest APK with SideQuest or ADB. On Android, allow installation from your browser or file manager.

When updating, install over the existing app to keep your saves, settings and imported game data. **Do not uninstall the old app or clear its data.** Back up important data before updating.

The app does not contain Halo game data. On first launch, open **Game files & versions** and import your own supported Xbox Halo CE ISO/XISO or extracted game files. For best compatibility, use the original Xbox Halo CE XISO. Rev 1 and Rev 2 images are supported where recognized but are not recommended.

## What’s included

- **Quest VR:** standalone OpenXR rendering, room-scale play, tracked body and hands, weapon-aligned aiming, configurable comfort and controls, and multiple body/hand modes. Safe geometry is the default.
- **Android:** editable touch HUD, multitouch, swipe/fire-drag controls, optional gyro aiming, and USB/Bluetooth gamepad support with controller-aware touch visibility.
- **OpenCE multiplayer and co-op:** native in-game server browser, PvP hosting and campaign co-op, with network 24 hosting and a launcher selector for compatible client targets 11–24.
- **Game and launcher tools:** multiple game-data sets and revisions, updates, settings, saved invites, help and per-launch logs.

### Network compatibility

The app always hosts on network 24. Selecting an older client target changes which compatible games this client can join; it does not downgrade hosted games. Targets 11–22 are limited to original Xbox-map PvP. Custom Edition and campaign co-op require network 23 or 24, with matching game files, maps and session conditions. The selectable co-op limit up to 128 is an engine setting, not a tested performance guarantee. See the [release notes](docs/RELEASE-1.0.18.md) for limitations and troubleshooting.

## Join or host a game

Join public games from **Play → Multiplayer → Join Game → Server Browser**, or nearby games from **LAN**. Use **Direct Link** to join by invite. To host PvP, choose **Create Game → Internet or LAN → Multiplayer**. To host campaign co-op, choose **Create Game → Internet or LAN → Singleplayer**, select a mission and difficulty, then configure **Server Setup**. Share the invite or make the lobby public. Hosting remains on network 24.
## Guides and support

- [Player guide](docs/PLAYER-GUIDE.md)
- [Controls and settings reference](docs/CONTROLS-AND-OPTIONS.md)
- [Complete v1.0.18 release notes](docs/RELEASE-1.0.18.md)

For help or a bug report, include the device and OS, app and network versions, selected game-data set, map or mission, connection type, reproduction steps, and relevant logs from each player. Android logs are saved under **Download/HaloCE** when permitted. Contact **@MeWhenINameMyself** or visit the [Halo CE Decomp Discord](https://discord.gg/S9uSCKxKx). Remove private invites and device details before posting publicly.

## Project and upstream status

This repository publishes the Halo CE Quest VR and Android app source, documentation and releases. It is an unofficial community project based on [OpenCE](https://github.com/OpenCommunityEdition/OpenCE), includes OpenCE networking and campaign co-op, and contains no Halo game data or other Halo game assets.

The separate [OpenCE-VR fork](https://github.com/moistman42069/OpenCE-VR) holds the dedicated upstream integration branch. The Quest implementation is under review in [OpenCE PR #217](https://github.com/OpenCommunityEdition/OpenCE/pull/217); it remains open and has not been merged into upstream. The fork’s current Quest/Android release is also [available there](https://github.com/moistman42069/OpenCE-VR/releases/tag/quest-v1.0.18).

The glasses-FOV and resolution contribution by [Willem Horak, PR #1](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1) is included. See [CREDITS.md](CREDITS.md) and [THIRD-PARTY-NOTICES.txt](THIRD-PARTY-NOTICES.txt) for additional contributors and licenses. This project is not affiliated with or endorsed by Microsoft or 343 Industries.
