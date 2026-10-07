# Halo CE Quest VR + Android 1.0.11 — Release Notes

## 1. Installation

Choose the APK for your device. Both are **version 1.0.11 / code 37**, ARM64, and require Android 9 / API 28 or newer.

| Device | Download |
| --- | --- |
| Android phone/tablet — flat play | **[HaloCE-Android-1.0.11.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.11/HaloCE-Android-1.0.11.apk)** |
| Meta Quest — standalone VR | **[HaloCE-Quest-1.0.11.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.11/HaloCE-Quest-1.0.11.apk)** |

Quest installation requires Developer Mode and sideloading; open the installed app from Unknown Sources. On Android, allow APK installation from the selected source if prompted. Install over the existing project app using its established signing certificate. **Do not uninstall or clear app data**; back up game data and saves first. The project does not distribute Halo game files. Import your own legally obtained Xbox Halo CE ISO/XISO or extracted data in launcher **Game files & versions**; see [the game-data guide](https://github.com/moistman42069/HaloCE-Quest-VR/blob/v1.0.11/docs/GAME-DATA-LIBRARY.md).

## 2. New Features / Major Changes

- **OpenCE Build 144 / network version 21:** the current upstream networking and co-op implementation is integrated. OpenCE moved to network 21 in Build 141; this release can join matching network-21 games. It cannot join v1.0.10 / network-20 sessions.
- **Campaign co-op updates:** includes upstream replication and transition fixes for bodies settling on remote screens, killing blows, team BSP/gate transitions, respawning near a teammate, and co-op garbage throttling. Lobby options remain 2–128 (default 4); the maximum is not a tested Quest/phone performance target.
- **HUD head tap fixed:** hold the gun hand beside its own temple briefly to hide or restore the HUD; a short haptic confirms the action. A hand passing by or reaching for the shoulder holster no longer toggles it accidentally.
- **VR HUD controls:** menu rows can show/hide the HUD, disable/configure Head Tap, and move/resize/reset the Wrist HUD. The Wrist HUD now sits on the wrist rather than the back of the hand.
- **Two-hand movement fix:** when **Move With** is set to a hand and both hands hold the weapon, forward movement follows the gun's direction instead of gradually turning into a strafe. **Move With: Head** remains the default.
- **Graphics options:** adds **FOV: Glasses 70×66** and resolution steps through **200%**. **125% Q3** approximates Quest 3 panel resolution. Auto and resolution settings through 100% keep the existing recommended eye images; higher settings render more detail and may cost performance.
- **Pull request #1:** includes the glasses FOV and higher-resolution work, with Quest eye-size and layout fixes. Contributor credit is in section 9.

## 3. Controls / Inputs

### Quest Touch controllers

Standard right-handed controls are shown. **Controls → Handedness** mirrors supported controls. **VR Settings → BUTTONS** remaps actions.

| Input | Action |
| --- | --- |
| Left stick | Move / strafe |
| Right stick | Smooth/snap turn; hold straight down to crouch on foot |
| Weapon-hand trigger / other-hand trigger | Fire / zoom |
| Right A / right B | Jump or confirm / reload or use |
| Left Y / left X | Switch weapon / throw grenade; hold X to change grenade type |
| Weapon-hand grip | Hold, switch or holster according to Weapons mode |
| Other-hand grip near support point | Attach support hand according to Two Hands setting |
| Left stick click | Hide/show reticle; it starts visible each game start |
| Right stick click | Native melee |
| Both stick clicks | Recenter during gameplay |
| Left menu button | Pause/menu |
| Off-hand near head | Flashlight gesture when enabled |
| Gun hand held at its own temple | Toggle HUD after the hold/haptic when enabled |
| Dead-player co-op view | A cycles the teammate being watched |
| Skippable co-op cutscene | A votes to skip; host counts votes |

Crouch moved from the older left-stick-click binding to holding the right stick down. To restore the old binding, open **VR menu → Controls → Page 2 → L Stick Click → Crouch**. Left stick click then crouches instead of toggling the reticle; assign Reticle to another button on the Buttons page if desired. In co-op, pause does not stop the shared game.

### Flat Android gamepad and keyboard

The default profile uses common Xbox-style positions; Halo's native controller layout options remain available.

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
| Co-op spectating / cutscene | A cycles teammates / votes to skip |
| Keyboard | Space votes to skip a skippable co-op cutscene |

### Android touch and gyro

Use **MOVE + swipe** to move and aim, or drag from **FIRE** to combine movement, aiming and firing. Tap **HUD** in-game to edit control position, size, opacity, color and response. Gyro aim is off by default; enable it under **HUD → Options → Gyro Aim** or launcher **Controller & touch settings**, then choose Always or only while touching LOOK/FIRE and set sensitivity/inversion.

## 4. VR Features and Settings

- Standalone OpenXR rendering, tracked headset/controllers, room-scale movement, recentering, smooth/snap turning, hand/head aim and weapon-aligned scopes.
- **Legs + Arms** remains the default body representation. Full Body, Arms + Hands, Hands Only and other modes are available. Procedural IK estimates untracked joints; finger poses use controller touch/trigger sensors, not optical finger tracking. Hand/world contact, approximate held-weapon contact and haptics are supported.
- **Wrist HUD:** optional and off by default. It places health/shields, ammo, grenades and the motion tracker on the back of the off-hand wrist. **HUD → Wrist HUD** enables it. **Wrist Along, Across and Height** move it in 1 cm steps (±20 cm); **Wrist Size** scales it from 50–200%; **Reset Wrist** restores defaults. Turn the wrist toward your face to read it. The forward HUD returns in vehicles or if off-hand tracking is lost; the panel hides while both hands hold the gun or a menu is open.
- **HUD menu:** **HUD: Shown/Hidden** changes the HUD for the current session. **Head Tap** turns the gesture off or adjusts how near the hand must be (6–15 cm, 10 cm default). Hold the gun hand by its own temple briefly to toggle; a haptic confirms. The flashlight head gesture remains separately adjustable.
- **Move With:** Head remains the default; Left Hand and Right Hand are alternatives. When both hands grip a weapon, movement follows the gun's direction.
- Gun handling includes controller-anchored placement, per-weapon aim tuning, physical/locked holding, first-grip protection, two-hand support grip (Auto Lock / Squeeze / Off), holsters and native reload/grenade animation handoff. Impact/swing melee options remain; online melee retains native events as required.
- VR Safe geometry remains enabled by default for compatibility. Comfort options include smooth/snap turn, turn speed, snap angle and vignette.
- Vehicle default is **Third Person + Right Hand steering**. Steering can use the left hand, head or stick. First-person vehicle mode remains experimental and is not recommended; supported seats have adjustable offsets.
- **FOV: Glasses 70×66** draws a narrower 70°×66° view with black around it, simulating lower-FOV glasses. **Resolution** ranges through 200%; 125% Q3 approximates Quest 3 panels. Keep Full/Auto or values through 100% for v1.0.10's recommended eye sizes; higher values may reduce performance.
- Opening gaze calibration follows the tracked headset direction, not eye tracking. VR avatar presentation is available between compatible project peers; other OpenCE players see the regular Halo character.

## 5. Android / Mobile Features and Settings

- Flat-play APK with multitouch movement, swipe aiming, fire-drag and an editable touch HUD.
- Optional gyro aiming: Off, Always or only while touching LOOK/FIRE, with horizontal/vertical sensitivity and inversion.
- Common USB/Bluetooth Xbox-style gamepads use Android input and SDL3. Hot-plug/reconnect, analog and supported digital triggers, dead zones, response, face-button swap and vibration where supported are included.
- Launcher **Controller & touch settings** adjusts dead zones/response, trigger threshold, vibration, face-button swap, touch visibility and gyro. Touch policy is Auto, Always show or Always hide; Auto restores touch after a supported controller disconnects.
- Each launch writes a detailed log under **Download/HaloCE** when Android permits, with app-private storage as fallback. Review logs for private information before sharing.
- See the [Android gamepad guide](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/docs/ANDROID-GAMEPAD.md) and [touch/HUD guide](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/docs/ANDROID-TOUCH-CONTROLS.md) for adjustment steps.

## 6. Multiplayer / Co-op / Server Compatibility

### Network version and servers

This release uses **OpenCE Build 144, network version 21**. All peers must use exactly matching network version 21, compatible maps and game data. OpenCE Build 141 and newer use network 21; v1.0.10 / Build 138 uses network 20 and cannot join these sessions. Network versions before or after 21 are not accepted by this build. Retail Halo PC/Custom Edition, original Xbox and MCC use different network protocols.

Browse in-game through **Multiplayer → System Link → Refresh** for signed OpenCE public listings and LAN sessions, sorted by population. The launcher also has multiplayer and campaign co-op browsers backed by community listings. A listing is not a relay and cannot bypass NAT/firewall, a closed/full/passworded lobby, network-version mismatch or missing/incompatible content. Password-locked games require an invite.

### Hosting and joining campaign co-op

Open launcher **Campaign co-op → Host campaign**; select mission, difficulty, maximum players and Public/Private. Host limits are **2, 4, 8, 12, 16, 24, 32, 48, 64, 96 or 128** (4 by default). The host starts from the in-game lobby; players may join in progress when allowed and spectate a teammate after death. **The campaign implementation is OpenCE-native, but no device session on this exact v1.0.11 APK pair was recorded before publication.** v1.0.10 co-op had owner confirmation; this network-21 update and its latest co-op fixes still need user device validation. The selectable 128-player capacity does not establish stable Quest/phone performance.

The test29 automated browser check against the live directory saw 4 co-op and 10 multiplayer games at network 21 as joinable by version. This is a listing/protocol compatibility check, not proof that every game, map, network path or mission succeeds on a device.

## 7. Game Revision / Version Compatibility

The launcher detects supported Xbox cache build identifiers and map/resource fingerprints. A disc filename alone cannot reliably identify Original, Revision 1 or Revision 2.

| Cache build identifier | Region/family |
| --- | --- |
| 01.01.14.2342 | PAL |
| 01.10.12.2276 | NTSC |
| 01.08.15.1749 | NTSC |

Use matching maps/resources when playing together. A server listing does not verify a peer's disc revision or exact per-map hashes. Modified/missing content, incompatible revisions and network-version mismatch can prevent joining/loading. Retail PC/MCC files are not substitutes for the supported Xbox game data.

## 8. Known Issues / Important Notes

- **Network compatibility changed:** v1.0.10/network 20 peers cannot join v1.0.11/network 21 sessions. Update all peers to v1.0.11 or another compatible network-21 build.
- No physical-device session on the exact v1.0.11 APKs was recorded before publication. Verify Quest and Android play, hosting/joining co-op, HUD gestures, wrist placement and graphics options on your devices; send logs for failures.
- 128-player lobby choice is available, but Quest/phone performance at high player counts is unverified. Begin with small lobbies on mobile.
- Resolution above 100% and Glasses FOV may affect frame rate/visual comfort. Restore **Full** FOV and **Auto** resolution to use the established defaults.
- Strict/symmetric NAT, mobile-data restrictions or firewall rules can block direct UDP joining; the directory is not a traffic relay. Maps, revisions, password settings and game versions must also match.
- First-person vehicle view remains experimental and is not recommended. Third Person + Right Hand steering are the defaults.
- SPV1 support is not currently functional. Mods/Custom Edition content are not promised compatible with the Xbox-data build.
- Report crashes, desyncs, failed joins or `EXCEPTION ... (release build)` messages. Include exact app/OpenCE version, device/OS, cache build, map/mission, connection type, reproduction steps and logs from all peers.

## 9. Additional Technical Details / Credits

- Packages: flat Android **com.halo.decomp**; Quest VR **com.halo.decomp.vr**. Version **1.0.11 / code 37**, ARM64, minimum API 28.
- Network: OpenCE Build 144 / version 21. The release-mode APKs are signed with the same certificate as v1.0.10 and earlier project releases.
- Automated validation: 32 regression suites and cache-format checks passed; both Android/Quest builds and the host build use release mode. The network/browser check matched 21 OpenCE files and found 4 co-op / 10 multiplayer live listings compatible by version. These checks do not replace the device testing noted above.
- OpenCE networking/co-op work is from [OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE). The glasses FOV and resolution contribution by [Willem Horak (PR #1)](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1) is included in this build. VR foundation, other contributors and third-party licenses are in [CREDITS.md](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/CREDITS.md) and the included notices. This unofficial project contains no Halo game assets.
- GitHub provides tagged source ZIP/tarball. Release assets are the two APKs and updater `compatibility.json`; candidate ZIPs, logs, manifests and temporary artifacts are not attached.

**Support:** DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord server](https://discord.gg/S9uSCKxKx). For multiplayer/co-op issues, include matching logs from every peer. Remove private invite/device details before sharing.
