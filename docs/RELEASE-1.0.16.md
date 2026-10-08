# Halo CE Quest VR + Android 1.0.16

OpenCE Build 148 · network version 23 · Android version code 45

## 1. Installation

Download the APK for your device:

- **Android / flat:** [HaloCE-Android-1.0.16.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.16/HaloCE-Android-1.0.16.apk)
- **Meta Quest / VR:** [HaloCE-Quest-1.0.16.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.16/HaloCE-Quest-1.0.16.apk)

Both editions are ARM64 and require Android 9/API 28 or newer. Enable installation from your browser or file manager on Android. For Quest, enable Developer Mode, then sideload the Quest APK with SideQuest or ADB. Install over the existing project app; **do not uninstall or clear app data**, which would remove imported game files and local saves/settings. Back up important data before updating.

On first launch, open **Game files & versions** and import a supported Xbox Halo CE ISO/XISO or extracted game-data set. This project does not distribute game files. The launcher validates and stages an import before making it selectable.

## 2. New Features / Major Changes

- **OpenCE Build 148** is integrated for Android and Quest. It corrects negative or NaN particle collision radii/widths while tags load and clamps invalid computed radii before point physics can assert. Native halt screens identify the platform/build and show recent errors first.
- Build 148 retains **network version 23**; this update does not change the protocol. Android and Quest use the same multiplayer code and protocol.
- The OpenCE in-game menu includes server browsing and PvP/campaign hosting. Population sorting, native LAN/public discovery, direct invitations, and OpenCE co-op remain available.
- Retained fixes include server-row pointer selection, CE map/cache validation, co-op camera safeguards, VR scope diagnostics/alignment, and the established Android touch behavior and VR settings design.
- The launcher manages multiple imported game-data sets, updater checks, controller/touch settings, help, saved invites and per-launch logs.

## 3. Controls / Inputs

### Quest Touch controllers

Right-handed defaults are listed; **Controls → Handedness** and **VR Settings → Buttons** can change supported mappings.

| Input | Action |
| --- | --- |
| Left stick | Move/strafe |
| Right stick | Smooth or snap turn; hold down to crouch by default |
| Weapon-hand trigger / off-hand trigger | Fire / zoom |
| Right A / Right B | Jump or confirm / reload or use |
| Left Y / Left X | Switch weapon / throw grenade; hold X to switch grenade type |
| Weapon-hand grip | Hold or transfer a physical weapon; locked mode uses holster interactions |
| Off-hand grip near weapon support point | Lock the support hand when enabled |
| Left stick click | Toggle reticle visibility (starts visible) |
| Right stick click | Native melee |
| Both stick clicks | Recenter during gameplay |
| Left menu button | Pause/menu |
| Off hand near the left side of the head | Toggle flashlight when the gesture is enabled; reach is adjustable |
| Gun hand at its own temple | Toggle HUD when enabled |
| A while spectating / in a skippable co-op scene | Cycle teammate / vote to skip |

The native VR pointer selects menu items with the trigger; thumbstick/D-pad navigation is also available. Left-handed mode mirrors supported controls. To restore crouch to left-stick click, open **VR menu → Controls → Page 2 → L Stick Click → Crouch**. Reassign the reticle in **Buttons** if needed.

### Flat Android controller and touch

Common Xbox-style USB/Bluetooth gamepads use Android input through SDL3: left stick moves, right stick aims, RT fires, LT throws grenades, A jumps, B melees/cancels, X reloads/uses, Y switches weapons, LB toggles flashlight, RB switches grenade type, stick clicks crouch/zoom and Start pauses. D-pad/left-stick navigation and A/B confirmation/back are supported in launcher dialogs. Button labels can vary by controller; optional face-button swap is in **Controller & touch settings**.

Touch controls remain available: use **MOVE + swipe** to move and aim, or drag **FIRE** to move, aim and fire together. Tap **HUD** to reposition/resize controls or adjust opacity, color and response. Touch visibility can be **Auto**, **Always show** or **Always hide**. Optional gyro aim is off by default and supports sensitivity and inversion settings. See [Android gamepad](ANDROID-GAMEPAD.md) and [touch controls](ANDROID-TOUCH-CONTROLS.md).

## 4. VR Features and Settings

- Standalone OpenXR headset/controller tracking, room-scale movement, recentering, smooth/snap turns, native aiming and weapon-aligned scopes.
- **Safe geometry is the default** on Quest and Android for compatibility. Safe mode can cost performance; restart after changing the geometry setting.
- **Legs + Arms** is the default body representation. Full Body, Arms + Hands and Hands Only are available. Procedural IK estimates untracked joints; finger poses use controller sensors, not optical finger tracking. Hand/world contact and approximate held-weapon contact are supported.
- Weapon options include anchored alignment, physical/locked handling, protection until the first grip, configurable support-hand lock, holsters, per-gun aim and native animation handoff for reloads and other actions.
- HUD options include an optional wrist HUD and adjustable head gestures. The flashlight gesture remains separately configurable.
- Vehicle defaults are **Third Person + Right Hand steering**. Steering can use the right hand, left hand, head or stick. First-person vehicle view and its per-vehicle seat adjustments are available but remain experimental and are **not recommended** yet.
- Comfort, graphics, refresh requests, FOV, body/hand, weapon, scope, HUD and vehicle options are available in the VR settings pages. Higher render resolutions can reduce performance.

## 5. Android / Mobile Features and Settings

- Flat Android play with the existing editable touch HUD, multitouch movement/aim, swipe aim and fire-drag controls.
- Optional gyro aiming; Android-native/SDL3 gamepad support for common XInput-style and other controllers, hot-plugging/reconnect, analog triggers, dead zones, response, optional face-button swap and vibration where supported.
- Automatic touch hiding when a supported controller is ready, with manual **Always show** and **Always hide** choices. Auto restores touch input after controller disconnect.
- The launcher has **Game files & versions**, **Versions & updates**, **Controller & touch settings**, help and logs. It checks compatible project updates and offers official upstream downloads separately; upstream files do not blindly replace the integrated VR/co-op runtime.
- A detailed log is generated after each launch under **Download/HaloCE** when Android permits, with app-private fallback storage.

## 6. Multiplayer / Co-op / Server Compatibility

All peers must use **OpenCE network version 23** and compatible game content. The older public v1.0.12 release uses network 21; network-21 and network-22 peers cannot join network-23 sessions. A browser listing is not a relay or a guarantee that a host is reachable. NAT/firewall restrictions, passwords, full/closed lobbies, missing or modified maps, and game-data differences can prevent a join.

### Join a game

Open **Play → Multiplayer → Join Game → Server Browser**, refresh the listings, select a compatible server and join. Use the LAN list for nearby hosts. Direct invites can be pasted through the in-game invite flow. The server browser is in the game; the launcher retains help and saved-invite access, not the old host/browser workflow.

### Host PvP

Choose **Play → Multiplayer → Create Game → Internet or LAN → Multiplayer**, select a map and game type, configure **Server Setup**, then start the lobby. Make the server public for listing or share an invite for a private session.

### Host campaign co-op

Choose **Play → Multiplayer → Create Game → Internet or LAN → Singleplayer**, select mission and difficulty, set the player limit and other **Server Setup** options, then start the lobby and invite players or make it public. Joining in-progress missions and the native OpenCE campaign flow are supported. Player-limit choices reach 128, but this is an engine option, not a tested performance target; begin with a small group. Every player needs matching network 23 and compatible campaign maps/resources.

## 7. Game Revision / Version Compatibility

Use launcher **Game files & versions** to import, scan and switch among supported Xbox game-data sets. The port recognizes Xbox cache format 5 build identifiers including PAL `01.01.14.2342` and NTSC `01.10.12.2276` / `01.08.15.1749`. The launcher identifies observed cache builds and file fingerprints; filenames alone do not establish Original/Rev 1/Rev 2, and the manager does not claim full-disc integrity. Server advertisements do not provide authoritative revision hashes, so automatic per-server revision matching is not guaranteed.

Different ISO/XISO revisions or modified map files can explain some server incompatibilities. Network version, missing maps/resources, server state and NAT can also be the cause. Retail Halo PC/Custom Edition, MCC and original Xbox multiplayer use different networking protocols.

**SPV1 remains experimental and unverified.** Its ten listed maps are roughly 157–253 MiB, above the sometimes-quoted 128 MiB figure. The current Custom Edition reader has a 384 MiB ordinary limit (576 MiB with OpenSauce upgrades), so size alone does not rule these files out. That does not establish protected-map conversion, resource compatibility or a working campaign; those still require testing.

## 8. Known Issues / Important Notes

- No Android or Quest device session on this exact 1.0.16 APK pair is recorded. Builds and host-side checks do not establish device acceptance or compatibility with every server/map/setup.
- Co-op is OpenCE-native and available, but no exact-pair device session or exhaustive mission/player-count matrix is recorded. Report crashes, desyncs and failed joins with logs from all players.
- The 128-player choice is not a performance guarantee. NAT, firewalls, VPNs, mobile-data restrictions and Wi-Fi isolation can block direct connections; the directory does not relay traffic.
- First-person vehicles remain experimental and are not recommended; third-person/right-hand steering are the defaults.
- Safe geometry favors compatibility and may perform more slowly than Normal on some devices. Render resolution above 100% and high refresh requests can also affect performance.
- Disc revision recognition is based on supported cache evidence, not a guarantee that every ISO/XISO/extracted set is valid. Back up imported data and saves before experimenting.

## 9. Additional Technical Details / Credits

- APKs: `com.halo.decomp` (Android) and `com.halo.decomp.vr` (Quest), version 1.0.16 / code 45, ARM64, minimum API 28. Both retain the project's established signing certificate for in-place updates.
- OpenCE Build 148 / network 23. The Build 148 particle-radius and native error-screen changes do not alter the network protocol.
- Release asset order: Android APK, Quest APK, then required updater `compatibility.json`. GitHub supplies source ZIP/tar.gz automatically; no game assets, logs or duplicate archives are attached.
- OpenCE networking/co-op work is from [OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE). The glasses-FOV/resolution contribution by [Willem Horak, PR #1](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1) is included. See [CREDITS.md](../CREDITS.md) and [third-party notices](../THIRD-PARTY-NOTICES.txt) for further credits/licenses. This unofficial project contains no Halo game assets.

For help, DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord](https://discord.gg/S9uSCKxKx). Include device/model and OS, app/network version, game-data set and map/mission, connection type, steps to reproduce, and launch logs from all peers. Remove private invite/device details before sharing.
