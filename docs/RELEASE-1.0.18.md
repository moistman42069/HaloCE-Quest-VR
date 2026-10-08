# Halo CE Quest VR + Android 1.0.18

**OpenCE Build 157 · network version 24 · Android version code 48**

## 1. Installation

Download the APK for the device:

- **Android / flat:** [HaloCE-Android-1.0.18.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.18/HaloCE-Android-1.0.18.apk)
- **Meta Quest / VR:** [HaloCE-Quest-1.0.18.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.18/HaloCE-Quest-1.0.18.apk)

Both apps are ARM64 and require Android 9 / API 28 or newer. On Android, allow installation from the browser or file manager. On Quest, enable Developer Mode and sideload the Quest APK with SideQuest or ADB. Install over the existing Halo CE port to keep its saves, settings and imported game data. **Do not uninstall the old app or clear its data.** Back up important data before updating.

On first launch, open **Game files & versions** and import your own supported Xbox Halo CE ISO/XISO or extracted game files. The APKs do not contain Halo game data. The launcher validates the import and lets you select among imported data sets.

## 2. New Features / Major Changes

- **Network-version selection with population information.** The launcher can combine its server listings across supported network versions, show reported server/player totals by version, and order versions and server rows busiest first. Choose an exact client target from 11–24 or **All compatible networks**. This changes native discovery and admission at the next launch; it is not just a visual filter. The setting is shared by the PvP and co-op browsers and imported game-data sets.
- **Network 24 hosting with backward-compatible client targets.** The app always hosts and advertises as network 24. Selecting an older target only changes which compatible hosts this client attempts to join; it does not make a new host impersonate an old protocol.
- **OpenCE Build 157 updates.** This integrates network 24 and applicable upstream changes: analog trigger pressure for weapons that use analog rate of fire; the PC vehicle-set option; authored facing for Custom Edition item spawns; Internet/LAN hosts can start alone and accept join-in-progress; and positional stereo world sounds receive directional panning, distance attenuation, obstruction/occlusion and room reverb. Unpositioned stereo music keeps its existing mix.
- **Build 148 safety fixes retained.** Invalid negative/NaN particle dimensions are corrected while tags load; invalid computed point-physics radii are clamped before assertion. Native halt screens identify platform/build and show recent errors first.
- **Launcher and diagnostics refinements retained.** The setup and Play screens have a selectable Halo-inspired font, standard-font fallback, original-XISO compatibility guidance and support contact. Network logs now identify the selected client target, broker readiness and rejected listing/admission cases. Per-launch logs are available under `Download/HaloCE` when Android permits, with app-private fallback.
- **Existing game and launcher features remain.** OpenCE's in-game server browser and PvP/co-op hosting, Android touch/controller support, VR full-body and hand options, game-file sets, updater, saved invites, help and settings are included.

## 3. Controls / Inputs

### Quest Touch controllers

The following are the right-handed defaults. **Controls → Handedness**, **Controls → Buttons** and **VR Settings → Buttons** change supported mappings.

| Input | Action |
| --- | --- |
| Left stick | Move and strafe |
| Right stick | Smooth/snap turn; hold down to crouch by default |
| Weapon-hand trigger | Fire |
| Off-hand index trigger | Zoom with a compatible weapon (left trigger for right-handed play) |
| Right A / Right B | Jump or confirm / reload or use |
| Left Y / Left X | Switch weapon / throw grenade; hold X to change grenade type |
| Weapon-hand grip | Hold/transfer a physical weapon; Locked mode uses holsters |
| Off-hand grip near the weapon support point | Attach the support hand when the selected two-hand mode permits it |
| Left stick click | Toggle reticle visibility; visible at game start |
| Right stick click | Native melee |
| Both stick clicks | Recenter during gameplay |
| Left menu button | Pause/menu |
| Off hand near the left side of the head | Flashlight gesture, when enabled |
| Gun hand held beside its own temple | HUD gesture, when enabled |
| A while spectating / in a skippable co-op scene | Cycle teammate / vote to skip |

Point at a menu item and press the trigger; thumbstick/D-pad navigation is also available. Left-handed mode mirrors supported mappings. To restore crouch to left-stick click, open **VR menu → Controls → Page 2 → L Stick Click → Crouch**. Reassign reticle toggle in **Buttons** if needed.

### Flat Android controls

Common Xbox-style USB/Bluetooth controllers use Android input through SDL3. The default gamepad profile maps left stick to movement, right stick to aim, RT to fire, LT to grenade, A to jump, B to melee/cancel, X to reload/use, Y to switch weapon, LB to flashlight, RB to next grenade, stick clicks to crouch/zoom, and Start to pause. D-pad/left-stick menu navigation and A/B confirm/back are supported. Labels can vary by controller profile; **Controller & touch settings** includes a face-button swap.

Touch controls retain the circular editable HUD and multitouch. Use **MOVE** with a screen swipe to move and aim, or drag **FIRE** to move, aim and shoot together. The HUD editor adjusts control position, size, opacity, color and response. Touch visibility can be **Auto**, **Always show** or **Always hide**; Auto hides it for a supported connected controller and restores it after disconnect. Optional gyro aim is off by default.

## 4. VR Features and Settings

- Standalone OpenXR, room-scale movement, recentering, smooth/snap turning, tracked hands and weapon-aligned aiming/scopes.
- **Safe geometry is the default** on Quest and Android for compatibility. Changing the geometry mode may require a restart; Safe mode can affect performance.
- **Legs + Arms** is the default body representation. Full Body, Arms + Hands and Hands Only are also available. IK estimates untracked joints; controller sensors animate finger poses, not optical finger tracking. Hand/world collision and approximate held-weapon contact are supported.
- Weapon settings cover physical or locked holding, protection until the first grip, support-hand behavior, holsters, per-gun aiming and temporary native animation handoff for reloads and similar actions.
- HUD settings include wrist HUD placement/size and adjustable head gestures. The left-temple flashlight gesture is configurable.
- Vehicle defaults are **Third Person + Right Hand steering**. Steering can instead follow the left hand, head or stick. Mounted turret aim can use right hand (default), left hand, head or stick.
- First-person vehicle seats have level-horizon and per-vehicle position adjustments, but first-person vehicle view remains experimental and **is not recommended yet**. Third person is the recommended view.
- Comfort, body, hands, buttons, weapons, scopes, HUD, vehicles, graphics and display options are in the in-game VR settings pages. Higher resolution/refresh choices can reduce performance.

## 5. Android / Mobile Features and Settings

- Flat Android gameplay with the existing circular touch HUD, direct menu taps, drag-anywhere look option, multitouch, adjustable layout and optional gyro aim.
- Android/SDL3 gamepad support for common XInput-style and other controllers, including hot-plug/reconnect, analog triggers, stick/trigger dead zones and response, vibration where supported, menu navigation and optional face-button swap.
- Touch can automatically hide while a supported controller is connected or be forced always visible/hidden; Auto restores it after disconnect.
- The launcher manages multiple game-data sets, revisions and updates, controls, saved invites, help, compatibility information and per-launch logs. It checks this project's updates and presents upstream downloads separately; upstream executables are not blindly substituted for the integrated VR/network runtime.

## 6. Multiplayer / Co-op / Server Compatibility

### Choosing a network

On the launcher, open **Browse multiplayer servers** or **Browse campaign co-op servers**, refresh, then choose **Network**. Choose an exact client version **11–24** or **All compatible networks**. The default is 24. Catalog-reported server/player counts are grouped by version and sorted busiest first; individual rows are also population ordered. Listings and counts can be stale or incomplete, and an empty/failed directory refresh is not proof that no games exist.

Close the game before changing the target: the running process keeps the target it started with. The selection is shared by PvP/co-op and imported data sets. It controls native discovery/admission as well as the launcher list. Hosting and signed advertisements always remain network 24.

The launcher HTTPS directory and the in-game signed OpenCE MQTT/LAN browser are separate sources, so results can differ. MQTT brokers are discovery mirrors, not distinct game protocols. The default ChupathingyCE/Delta HTTPS catalog is the only public cross-version catalog verified for this build; up to four compatible custom HTTPS catalogs can be configured. An entry is not a relay or a guarantee that a host is reachable.

### Join and host

In game, open **Play → Multiplayer → Join Game → Server Browser** for public games or **LAN** for nearby hosts. Use **Direct Link** for an invite. To host PvP, choose **Create Game → Internet or LAN → Multiplayer**, configure the match and **Server Setup**, then start the lobby. To host campaign co-op, choose **Create Game → Internet or LAN → Singleplayer**, select mission/difficulty, configure **Server Setup**, and start the lobby. Share the invite or make the lobby public.

### Compatibility limits

- **Network 11–22:** backward client targets are limited to original Xbox-map PvP. Custom Edition and campaign/co-op are not supported on these older targets.
- **Network 23–24:** PvP and campaign/co-op may be joined when game files, maps and session conditions match. Custom Edition requires host version 23 or 24 and matching map/checksum.
- **Hosting:** always network 24. Older clients that do not understand network24 cannot join this app's hosted games. Selecting an older target never downgrades a hosted game.
- **Unavailable:** versions below 11 and unknown future versions are not implemented by this selector. Retail Halo PC/Custom Edition, MCC and retail Xbox networking are separate protocols.

OpenCE-native campaign co-op and the native in-game browser/hosting flow are included. Server Setup offers co-op player-limit choices up to 128, but that is an engine option, not a certified performance target; start with a small group. The new backward-target matrix has not been gameplay-tested against every historical server or co-op setup.

Joins can still fail because of NAT/firewalls/VPNs, passwords, full/closed lobbies, stale invites, missing or modified maps, incompatible game-data revisions or other network conditions. If a join, crash or sync issue occurs, collect logs from both peers, identify their app/network versions and game-data set, and include the map, host/client roles, connection types and reproduction steps.

## 7. Game Revision / Version Compatibility

Use **Game files & versions** to import, scan and switch among supported game-data sets. The launcher reports supported cache build identifiers and fingerprints; filenames alone do not establish Original/Rev 1/Rev 2, and this is not a full-disc integrity certification. The browser cannot reliably infer the exact disc revision required by each server or automatically switch revisions when joining.

For the broadest compatibility, the launcher recommends the **original Xbox Halo CE XISO**. Rev 1 and Rev 2 can be imported where supported, but are not the recommended images. Different revisions or modified maps can cause a failed join; network protocol, missing content, server state and NAT are other possible causes. Original/Rev1/Rev2 image-matrix testing is not included in this release validation.

SPV1 is still experimental and unverified. Its listed maps exceed 128 MiB, but fit the current Custom Edition reader's 384 MiB standard / 576 MiB OpenSauce-upgraded cache limits. File size alone does not prove protected-map conversion, resource compatibility or campaign support.

## 8. Known Issues / Important Notes

- Hardware testing has not covered every Android/Quest model, historical network target, ISO revision, map, co-op mission or player count. Automated tests and directory parsing do not prove universal reachability or device gameplay.
- The per-version population is what compatible catalogs report; it can be stale and omits private/LAN games. Only the default HTTPS cross-version catalog was verified in this pass.
- Network targets 11–22 are PvP/original-Xbox-map client compatibility only. The app's host stays on network24; older clients cannot join it.
- Co-op player limits up to 128 are configurable, not a performance guarantee. Start small and report crashes, desyncs or join failures with both players' logs.
- First-person vehicle view remains experimental; use the default third-person view.
- Safe geometry favors compatibility and may cost performance. Higher render resolution/refresh can also affect frame rate.
- If no servers appear, distinguish a failed catalog refresh from a successful empty result, then check the in-game browser, connection type, selected network target and logs.

## 9. Technical Details / Credits

- App IDs: `com.halo.decomp` (Android) and `com.halo.decomp.vr` (Quest); version **1.0.18 / code 48**; ARM64; minimum API 28. The established project signing certificate is retained for in-place installation.
- Upstream baseline: [OpenCE Build 157](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-157), including the [network24 change](https://github.com/OpenCommunityEdition/OpenCE/commit/11117d7c287d519bf263db83273bc26295a87cb9) and [PC vehicle-set changes](https://github.com/OpenCommunityEdition/OpenCE/pull/173). The backward-client compatibility model was audited against pinned [ChupathingyCE source](https://github.com/ChupathingyCE/chupathingyce/tree/b78e6cfa00d007592a21b12363b2cbc1b5217997); this does not mean every historical gameplay combination was tested.
- The glasses-FOV and resolution contribution by [Willem Horak, PR #1](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1) is included. See [CREDITS.md](../CREDITS.md) and [third-party notices](../THIRD-PARTY-NOTICES.txt) for further credits and licenses. This unofficial project contains no Halo game assets.
- Automated validation: 62 registered Android/Quest regression suites passed; cache-format pytest reported 127 passed and 4 optional real-map fixture skips. APK signature/package/version/ABI, ZIP integrity, orphaned-payload, bundled-guide and Android/Quest networking-parity checks are recorded in [release provenance](RELEASE-PROVENANCE-1.0.18.md). No hardware test matrix is implied by these results.
- Custom GitHub release assets are only the Android APK, Quest APK and updater-required `compatibility.json`, in that order. GitHub provides source archives from the tag; no duplicate source/build ZIP, logs or game data are attached.

For help, DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord](https://discord.gg/S9uSCKxKx). Include the device/model and OS, app/network version, game-data set, map/mission, host/client role, connection type, reproduction steps and relevant logs from each peer. Remove private invite/device details before posting publicly.
