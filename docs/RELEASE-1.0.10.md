# Halo CE Quest VR + Android 1.0.10 — Release Notes

## 1. Installation

Download the APK for your device. Both packages are **version 1.0.10 / code 36**, ARM64, and require Android 9/API 28 or newer.

| Device | Download |
| --- | --- |
| Android phone/tablet — flat play | **[HaloCE-Android-1.0.10.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.10/HaloCE-Android-1.0.10.apk)** |
| Meta Quest — standalone VR | **[HaloCE-Quest-1.0.10.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.10/HaloCE-Quest-1.0.10.apk)** |

Quest installation requires Developer Mode and sideloading; launch the app from Unknown Sources. On Android, allow APK installation from the selected source if prompted. Install over an existing project build using its established signing key. **Do not uninstall or clear app data**; back up game data and saves first.

The project does not distribute Halo game files. In launcher **Game files & versions**, import your own legally obtained Xbox Halo CE ISO/XISO or select an extracted game-data folder, wait for validation, then choose **Use**. See [Game files & versions](https://github.com/moistman42069/HaloCE-Quest-VR/blob/v1.0.10/docs/GAME-DATA-LIBRARY.md).

## 2. New Features / Major Changes

Version 1.0.10 updates the co-op integration based on owner testing and adds optional gyro aiming for flat Android.

- **OpenCE-native network and co-op:** retained OpenCE Build 138 network v20. The camera fault that caused a blue halt screen when joining a campaign already in progress is fixed; the watch-host camera stays upright.
- **Release build behavior:** Android/Quest builds now use OpenCE's release configuration. Assertion-style checks that would halt a debug build are logged as release-build exceptions. If one appears in a log, please report it even if play continues.
- **Larger co-op lobby sizes:** campaign hosting offers OpenCE's choices of 2, 4, 8, 12, 16, 24, 32, 48, 64, 96 and 128 players. Default is 4. These are supported engine/session options; 128-player performance is not verified on Quest or phone.
- **Android gyro aiming:** optional, off by default. Turn the phone to aim; select Always or only while touching LOOK/FIRE; adjust horizontal/vertical sensitivity and inversion. Works with touch swipes and gamepad input.
- The earlier OpenCE networking/co-op integration, Android/Quest port, VR avatars, body/hand features, controller/touch support, vehicle and comfort options, and game-data manager remain.

The OpenCE base is [Build 138](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-138), network v20. This port adds Android/Quest VR and launcher integration.

## 3. Controls / Inputs

### Quest Touch controllers

Standard right-handed controls are listed below; **Controls → Handedness** mirrors supported controls. **VR Settings → BUTTONS** allows action remapping.

| Input | Action |
| --- | --- |
| Left stick | Move and strafe |
| Right stick | Smooth/snap turn; push straight down to crouch on foot |
| Weapon-hand trigger / other-hand trigger | Fire / zoom |
| Right A / right B | Jump or confirm / reload or use |
| Left Y / left X | Switch weapon / throw grenade; hold X to change grenade type |
| Weapon-hand grip | Hold, switch or holster according to Weapons mode |
| Other-hand grip near weapon support point | Attach support hand according to Two Hands setting |
| Left stick click | Toggle reticle |
| Right stick click | Native melee |
| Both stick clicks | Recenter during gameplay |
| Left menu button | Pause/menu |
| Dead-player co-op view | Press **A** to cycle the teammate being watched |
| Skippable co-op cutscene | Press **A** to vote to skip; the host counts votes |
| Off-hand near head | Flashlight gesture when enabled |
| Gun hand at its own temple | Toggle HUD when enabled |

In co-op, the pause screen does not pause the shared world. A cutscene skip is a vote, not an immediate skip; the host acts when enough players vote.

### Flat Android gamepad and keyboard

The Android gamepad profile uses common Xbox-style positions. Controls can also follow Halo's native controller layout options.

| Input | Default action |
| --- | --- |
| Left / right stick | Move / aim |
| RT / LT | Fire / throw selected grenade |
| A / B | Jump-confirm / melee-cancel |
| X / Y | Reload/use / switch weapon |
| LB / RB | Flashlight / switch grenade type |
| Left / right stick click | Crouch / zoom |
| Start / Back or View | Pause / Halo Back or score display |
| D-pad or left stick | Menu navigation |
| Dead-player co-op view | A cycles the teammate being watched |
| Skippable co-op cutscene | A votes to skip |
| Keyboard | Space votes to skip a skippable co-op cutscene |

### Android gyro and touch

Open touch **HUD → Options → Gyro Aim**, or launcher **Controller & touch settings**. Gyro aim is **Off by default**. Select **Always** or **Only while a finger is on LOOK or FIRE**, then set horizontal/vertical sensitivity and inversion. A phone without a gyroscope remains fully usable with touch or a gamepad.

For touch gameplay, use MOVE and swipe aiming, or drag from FIRE to move, aim and shoot together. The HUD editor changes control position, size, opacity, color and response. Touch visibility can be Auto, Always show or Always hide.

## 4. VR Features and Settings

- Standalone OpenXR stereo rendering, tracked headset/controllers, room-scale movement, recentering, smooth/snap turning, hand/head aim and weapon-aligned scopes.
- **Legs + Arms** remains the default body representation. Full body, Arms + Hands, Hands Only and other modes remain available. Procedural IK estimates untracked joints; finger contact uses controller sensors, not optical finger tracking.
- Weapon alignment, physical/locked holding, first-grip protection, two-hand support grip, holsters, native reload/grenade animation handoff and melee options remain.
- VR Safe geometry remains enabled by default for compatibility; it may reduce performance. Flat Android continues to default to Normal geometry.
- Comfort options include smooth/snap turn, turn speed, snap angle and vignette.
- Vehicle defaults remain **Third Person + Right Hand steering**. First-person vehicle mode is still experimental and not recommended.
- The opening gaze calibration uses tracked headset direction, not eye tracking.
- Networked VR avatar presentation remains available to compatible 1.0.9/1.0.10 peers. Other OpenCE players see the regular Halo character model.

## 5. Android / Mobile Features and Settings

- Flat-play APK with multitouch movement, swipe aiming, fire-drag and an editable touch HUD.
- Optional phone gyroscope aiming: Off, Always, or only while touching LOOK/FIRE, with horizontal/vertical sensitivity and inversion. Settings are shared between the in-game HUD options and launcher controller/touch settings.
- Android handles common USB/Bluetooth Xbox-style gamepads through Android input and SDL3. Hot-plug/reconnect, analog and supported digital triggers, dead zones, response, face-button swap and vibration where supported are included.
- Touch controls can Auto-hide for a fully mapped connected controller and return after disconnect, or be set to Always show / Always hide.
- The launcher scans/manages multiple supported ISO/XISO and extracted game-data sets, validates actual cache headers, displays map fingerprints and lets users switch sets without overwriting the others.
- Each launch writes a detailed log under **Download/HaloCE** when Android permits; app-private storage is the fallback. Review logs for private information before sharing.

## 6. Multiplayer / Co-op / Server Compatibility

### Network compatibility

This release uses **OpenCE Build 138's network version 20** directly for both multiplayer and campaign co-op. All peers must use an exactly matching network version. OpenCE peers on network v20 can cross-play with this release when their maps and game data are compatible. Other network versions are rejected with an explanatory message.

The prior app's network 9–11 window and CE01/CE02 two-player campaign protocol are retired. A build using those older protocols cannot join this release's sessions. Retail Halo PC/Custom Edition, original Xbox and MCC use different network protocols.

### Browsing and joining

1. In game, open **Multiplayer → System Link → Refresh** to browse signed public OpenCE listings and LAN sessions, sorted by population.
2. The launcher also has separate campaign co-op and multiplayer browsers backed by community listings. A listed game may still be unreachable due to NAT, a closed lobby, incompatible version or content.
3. To join a campaign session, select it in System Link and join the lobby. Campaign hosts may allow joining after the mission has started.
4. A password-locked (**LOCK**) lobby requires an invite. The launcher does not set every OpenCE PC lobby option.

### Hosting campaign co-op

Open launcher **Campaign co-op → Host campaign**. Select mission, difficulty, maximum players and whether the session is Public. The selectable sizes are **2, 4, 8, 12, 16, 24, 32, 48, 64, 96 and 128**; default is 4. The host enters the in-game lobby and starts the mission; a full lobby may start automatically. Players can join a mission in progress and can spectate a teammate after dying, returning when game conditions allow.

The owner tested co-op on this candidate and reports that it works well. Automated network/browser checks and upstream parity checks also passed. This confirms the reported setup; it does not certify every map, revision, player count, device, OS or NAT configuration. **The 128-player lobby choice is available, but high-count performance on Quest/phone is not established.** Begin with a smaller group on mobile.

## 7. Game Revision / Version Compatibility

The launcher reads supported Xbox cache build IDs and hashes map/resource files. It does not identify every Original/Revision 1/Revision 2 disc from its filename.

| Cache build identifier | Region/family |
| --- | --- |
| 01.01.14.2342 | PAL |
| 01.10.12.2276 | NTSC |
| 01.08.15.1749 | NTSC |

Use matching maps and resources when playing together. A server listing does not certify a peer's disc revision or per-map hashes. Modified/missing content, incompatible revisions and network-version mismatch may prevent joining or loading. Retail PC/MCC files are not substitutes for the supported Xbox game data.

## 8. Known Issues / Important Notes

- Network version 20 is exact-match only. A future OpenCE network change will need an integrated, reviewed update before those newer hosts work.
- Lobby choices include up to 128 players, but Quest and Android performance at that size is unmeasured. Default to a small lobby on mobile.
- Strict/symmetric NAT, mobile-data restrictions or firewall rules can block direct UDP joining; the listing directory is not a traffic relay.
- Password-locked lobbies require a host invite. Some server configuration is available only from OpenCE's desktop menus/configuration.
- Different game revisions, modified maps/resources, missing maps, expired invites, closed/full games or version mismatch can independently prevent a join.
- First-person vehicle view remains experimental and is not recommended. Third Person and Right Hand steering remain the defaults.
- SPV1 support is not currently functional. Mods and Custom Edition content are not promised compatible with this Xbox-data build.
- Report crashes, desyncs, failed joins and unexpected release-build exceptions. Include exact app/OpenCE version, device and OS, game cache build, map/mission, connection type, reproduction steps and logs from all peers.

## 9. Additional Technical Details / Credits

- Packages: flat Android **com.halo.decomp**; Quest VR **com.halo.decomp.vr**.
- Version **1.0.10 / code 36**, ARM64, minimum Android API 28.
- Netcode: OpenCE Build 138, version 20. Campaign lobby choices up to 128; runtime performance at maximum capacity is unverified.
- Candidate validation: 30 regression suites pass, including the join-camera fix, release configuration, lobby-size options and gyro math/wiring. Cache-format checks and both release builds pass. These checks complement, but do not replace, user testing.
- OpenCE networking/co-op work is credited to [OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE). VR foundation and dependencies/third-party licenses are listed in [CREDITS.md](https://github.com/moistman42069/HaloCE-Quest-VR/blob/v1.0.10/docs/CREDITS.md) and the packaged notices. The project is unofficial and contains no Halo game assets.
- GitHub provides the source ZIP/tarball from the tag. Release assets are limited to the Android APK, Quest APK and updater compatibility metadata; candidate archives, logs and temporary build files are omitted.

**Support:** DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord server](https://discord.gg/S9uSCKxKx). For co-op issues include matching logs from every peer. Remove private invite/device details before posting.
