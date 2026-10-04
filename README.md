# Halo CE Quest VR + Android

[Release 1.0](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.0) | [Full controls/options](docs/CONTROLS-AND-OPTIONS.md) | [Development state](docs/CURRENT-STATE.md) | [Contributing/builds](CONTRIBUTING.md) | [Credits](CREDITS.md)

## 1. Installation

**Halo CE Quest VR + Android 1.0** is the first stable baseline for this project: standalone Quest VR and a separate flat Android edition. Release **1.0** publishes the exact delivered test18 APKs: Android internally reports **1.0-test18 / code 19**. Already installed test18? You already have these binaries; no reinstall is needed.

| Your device | Download |
| --- | --- |
| Android phone/tablet — flat, touch or gamepad | **[HaloCE-Android-1.0.0.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.0/HaloCE-Android-1.0.0.apk)** |
| Meta Quest — immersive standalone VR | **[HaloCE-Quest-1.0.0.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.0/HaloCE-Quest-1.0.0.apk)** |

1. **Install the appropriate APK.** On Quest, enable developer mode and sideload with SideQuest or your existing installer; open it from **Unknown Sources**. On Android, open the downloaded APK and allow installation from that source when prompted. Both require ARM64, Android 9/API 28 or newer and compatible graphics. **Quest 3 is the reference headset**; other devices are not equally verified.
2. **Updating this project? Install over it.** Both APKs retain their package IDs and signing certificate. Do not uninstall or clear app data. Optional ADB command: `adb install -r <apk-file>`. Back up your maps, saves and settings first. Another fork using the same package ID but a different key cannot update in place.
3. **Supply your own legally obtained Xbox Halo: Combat Evolved data.** No game maps are included. Copy your `.iso`/`.xiso` or extracted game folder to the device. MCC and retail PC installation files are not substitutes for the supported Xbox base data.
4. **Open the launcher → Game files & versions.** Import an ISO/XISO or select an extracted `maps` folder/game root. Wait for validation, then select **Use** beside the imported set. Allow roughly 1.8 GB for the usual maps, plus the source image, saves and import space. Multiple sets require additional storage.
5. **Choose Play.** Existing installations remain available as **Existing game data**. In VR, stand normally and press both stick clicks together to recenter. Open the campaign pause menu → **VR Settings** to customize your experience.

The launcher includes an offline **Field guide** with controls, settings and credits. Existing Quest data under `/sdcard/Documents/HaloCE/maps` is recognized when `ui.map` is present; otherwise each app uses its own external-files storage. VR and flat can coexist and have separate app data.

**Coming from a test build:** install 1.0 manually once. Older test updaters do not recognize the new stable release names. From 1.0 onward, **Versions & updates** supports normal release versions. The previous test14 release remains available unchanged.

## 2. New Features / Major Changes

This release brings the refinements since public test14 together into the 1.0 baseline:

- **Campaign transition fix:** clears and validates cached vehicle-camera references across map changes, addressing the reported Pelican transition crash.
- **Head-look tutorial and vehicle controls:** headset-based light detection; third-person/right-controller defaults, four steering modes and adjustable first-person seats.
- **Multiplayer compatibility fixes:** running native PvP matches are no longer falsely rejected by the shared advertisement flag; the action-control bit responsible for the reported assertion is handled correctly. Includes reviewed upstream player departure/rejoin safeguards and Network 11 options, while accepting reviewed v9/v10 hosts.
- **Managed game-data sets:** import multiple ISO/XISO or extracted installations, scan an import inbox, view detected builds/fingerprints, rename sets and switch without replacing the original installation. Saves remain separate per set.
- **Smoother native weapon actions in VR:** reloads, grenade throws, melee, weapon swaps and other affected animations temporarily own the appropriate arm/hand, then blend back to tracking. Existing support grip is preserved through the action.
- **Safe geometry by default in VR**, including a one-time migration of older settings. Flat Android retains Normal by default. Explicit later choices are preserved.
- **Per-controller alignment controls** for unusual tracking/firmware orientation, plus a customizable flat touch HUD and expanded Xbox-style gamepad settings.
- **Launcher PvP hosting**, population-sorted browsing, compatibility explanations, bundled help, detailed per-launch logs and verified project updates.

Gameplay retains the test17 baseline plus test18 campaign vehicle-cache cleanup, headset-based tutorial checks and vehicle camera/control options. Existing body, grip and native action behavior is preserved. The release also includes stable-version update handling and bundled license information.

## 3. Controls / Inputs

### Quest Touch — default VR layout

Use **Controls = VR** and the standard native controller profile. Right is the default weapon hand. Left-handed mode changes weapon/off-hand trigger roles; face-button sides are not all mirrored.

| Input | Action |
| --- | --- |
| Left stick | Move/strafe; relative to the selected head/hand orientation |
| Right stick | Smooth or snap turn; vertical input also serves native look prompts |
| Weapon-hand trigger / other-hand trigger | Fire / zoom |
| Right A / Right B | Jump or confirm / reload-use; hold B for interaction prompts; B returns in pointer menus |
| Left Y | Switch weapons |
| Left X, Physical weapons | Tap/release to throw a grenade; hold 0.4 seconds to switch grenade type |
| Left X, Locked weapons | Switch grenade type |
| Weapon-hand grip, Physical | Hold the gun; release after the first grip to drop/holster/transfer |
| Weapon-hand grip, Locked | Throw grenade away from holsters; switch weapon at a holster |
| Other-hand grip near the support region | Lock the support hand; release to detach |
| Left / right stick click | Crouch / native melee |
| Both stick clicks together | Recenter during gameplay |
| Left menu button | Pause/menu; online co-op continues running |
| Weapon pointer + trigger | Select menu item; right B returns |

**Online holding differs:** **MP Physical defaults Off**, so multiplayer uses **Locked** holding and the Locked grenade inputs above. Body sharing remains available. A newly supplied weapon stays held until the first grip action in Physical mode. Two Hands defaults to **Grip**: proximity alone does not attach it.

### Flat Android — Xbox-style gamepad defaults

| Input | Action |
| --- | --- |
| Left / right stick | Move / aim |
| RT / LT | Fire / throw grenade |
| A / B | Jump-confirm / melee-cancel |
| X | Reload; hold for use, pickups and vehicle interaction |
| Y | Switch weapons |
| LB / RB | Flashlight / switch grenade type |
| Left / right stick click | Crouch / zoom |
| Start-Menu / Back-View | Pause / Halo Back input or multiplayer scores |
| D-pad or left stick in launcher | Navigate; A confirms, B returns |

PlayStation/Nintendo-style pads use equivalent button positions; an optional face-button swap is available. Native Halo Options retains alternate layouts, sensitivity and inverted aim. System file pickers/keyboards follow Android's own input support.

### Flat touch

Use **MOVE** plus swipe aiming or **FIRE-and-drag** to move, fire and aim together. Labeled buttons provide jump, crouch, melee, reload/use, weapon/grenade switching, grenade, zoom, flashlight and menu navigation. Tap **HUD** during play to edit the layout. Editing does not pause an online match.

## 4. VR Features and Settings

- **Native standalone OpenXR:** stereo rendering, tracked headset/controllers, hand or head aim, room-scale movement, recentering, smooth/snap turning and weapon-aligned scope.
- **Body modes:** **Legs + Arms is the default**. Full, Arms + Hands and Hands Only are also available. The procedural IK rig infers torso/legs from headset/controllers, with room-scale foot following, bounded shoulders and smoothed elbows/wrist twist. Arm modes include IK, hidden and authored animation.
- **Hands and contact:** controller-driven finger poses and smoothing, palm/finger/world contact, approximate held-weapon contact and haptics. These are controller sensors, not optical finger tracking or fully simulated rigid-body hands.
- **Weapons:** deliberate support grip at a fixed anchor, optional Auto proximity grip or Off, physical/locked holding, first-grip protection, hand transfer and shoulder/hip holsters. Reload uses native animations and the button; physical magazine reloading is not implemented.
- **Movement and gestures:** physical crouch, off-hand-near-head flashlight, impact or swing melee, optional arm-run effort and up to 1.5× offline sprint. Online movement speed/collision remain stock; network clients use native swing melee.
- **Vehicles:** third-person chase and right-controller steering default. **VR Settings > Vehicles** selects Third Person / First Person and Right Hand / Left Hand / Head / Stick steering. Left stick supplies movement/throttle; the selected physical controller points the driving direction independently of weapon handedness or support grip. Tracking loss holds native facing. Gunners retain head aiming.
- **First-person seats:** level horizon with head leaning; Up, Forward and Right adjustments in 1 cm steps, ±50 cm. Global offsets plus Warthog, Ghost, Banshee, Scorpion and Pelican profiles; custom vehicles use global values. Combined offsets clamp to ±50 cm per axis and are shortened at map collision. Zero restores the native seat location. Offsets affect First Person only. First-person heading follows the vehicle; chase steering uses the world heading with normal stick turns.
- **Upgrade defaults:** the first launch of this VR build applies chase/right once and backs up the prior settings as `config.toml.pre-vehicle-defaults`. Your subsequent vehicle choices persist. Other body, grip, action and graphics preferences are retained.
- **Other views:** immersive, 3D-screen or flat cinematics; native crosshair artwork with size/opacity or Off.
- **Opening look tutorial:** look toward the lights with your headset. Script gaze and head-movement checks use the tracked head, independently of the weapon reticle. This is headset direction, not eye tracking.
- **Graphics:** Auto/Low/Medium/High/Max presets; render resolution; shadows, lights, specular, reflections, bump maps, grass, fog, decals, particles, contrails, weather, lens flares and camouflage. Refresh choices are 72/80/90/120 Hz requests, not guaranteed frame rates.
- **Calibration:** Align Left/Right provides controller-local pitch/yaw/roll, position offsets, Flip Roll 180, Native/Grip aim source and separate resets. Correct only the affected hand; no automatic firmware-based flip is applied.

In VR Settings, **A/right increases or advances; left decreases**. Next Page exposes more options; Back returns through pages/categories. Settings persist. **Safe geometry** can be changed in the launcher; restart afterward. It can trade performance for compatibility. Existing body preferences are retained when updating.

## 5. Android / Mobile Features and Settings

- Separate flat APK with multi-touch movement, relative swipe aim, fire-drag aiming and controller coexistence.
- **HUD editor:** drag individual controls; choose covered controls from a selector; adjust individual/global size and opacity, spacing through placement, overall scale, color, horizontal/vertical sensitivity, dead zone, floating movement and swipe/stick aim. Save, Cancel and Reset are provided; placement accounts for screen edges/cutouts.
- **USB/Bluetooth gamepads:** Android input through SDL3, targeting Xbox/XInput-style controllers without requiring a Windows XInput layer. Includes analog and supported digital trigger mappings, hot-plug/reconnect cleanup, independent dead zones/response, optional face-button swap and vibration where the device/driver supports it.
- **Touch visibility:** Auto hides the HUD when a fully mapped controller is ready and restores it after disconnection. Always show and Always hide are manual choices. In Always hide, touch stays hidden after disconnect until you change the setting.
- **Controller input check** and controller navigation across launcher/browser dialogs; gameplay uses Halo's native controller mapping.
- Shared launcher, game-data manager, offline help, server browsing/hosting, co-op, update checks and remote VR-avatar reception. Flat geometry remains Normal by default.

## 6. Multiplayer / Co-op / Server Compatibility

### Regular PvP

Open **Multiplayer servers → Refresh → Join**. After the invite tunnel connects, use **Multiplayer → System Link** in-game to select the host; other native ports may call it Direct Link. Saved invites and LAN discovery support unlisted hosts.

The browser reads the ChupathingyCE native-port directory, retains valid listings and sorts by reported population before paging. Directory settings can merge up to four compatible HTTPS catalogs. Full/incompatible hosts show their status; a listing does not prove reachability or measure ping. No second independent compatible preset directory has been verified, and private/unadvertised games cannot all be enumerated.

**Host multiplayer** offers installed map, game type, name, score/time, friendly fire, radar, team balance, vehicle respawn, loadout/grenade options and **2–128 PvP slots**. Public listing is opt-in; private invites are available. Start with modest limits: 128 is protocol capacity, not a verified Quest-host performance target. Network settings expose Internet/LAN, UPnP, clipboard invites and tunnel port.

This build hosts native **Network 11** and accepts reviewed distributed hosts **9–11**, subject to content/rules and connectivity. Supported native Windows/macOS/Linux/Android ports can cross-play when compatible. **Retail Halo PC/Custom Edition, original Xbox and MCC use different network protocols.** Older clients that insist on an older version need an update.

### Campaign co-op and avatars

**Campaign co-op → Host campaign / Browse or join** is separate from PvP. Use **matching 1.0 builds and matching campaign/resource files** on both peers. Two Quests or Quest plus flat Android are the intended pairings; Quest-to-flat connectivity and remote VR body movement have prior owner confirmation.

Both players join the lobby before starting. The host controls campaign scripts, AI, checkpoints and transitions. **Campaign supports two players**, not 128; joining mid-mission is disabled. Disconnects require a new lobby. Public campaign directory acceptance remains unverified; private invite/LAN is the fallback.

Supporting hosts/clients negotiate VR head/arms/body/leg presentation, including the flat receiver. Local torso hiding does not hide the remote body. Older peers use stock presentation; remote world skeletons do not replicate the local individual finger rig. Avatar extensions also operate in supporting PvP sessions.

## 7. Game Revision / Version Compatibility

**Some server incompatibilities may result from different ISO/revision map files or modified game data.** Network versions, missing maps, NAT, full/closed servers and expired invites are other possible causes; an ISO revision is not automatically the explanation for a failed join.

The manager recognizes Xbox cache format 5 with these actual build strings:

| Detected build | Region |
| --- | --- |
| `01.01.14.2342` | PAL |
| `01.10.12.2276`, `01.08.15.1749` | NTSC |

PAL normalization is automatic. **Original/Rev1/Rev2 disc labels are not conclusively identified from filenames or these headers**; no verified disc-revision hash database is bundled. Imported sets show detected cache builds and import-time SHA-256 fingerprints. You can rename your set without altering its detected identity. Header recognition is not a full-disc integrity guarantee.

Use **Game files & versions** to import/switch, or place images/extracted roots in the displayed `game-versions/inbox` and scan. Imports validate in staging before becoming selectable. The original installation is retained; new sets copy current settings once and keep separate saves. The browser can offer an installed set containing a missing map, but servers do not advertise authoritative revision/content fingerprints, so it cannot guarantee automatic revision matching.

**Versions & updates** checks compatible project releases and upstream network changes. Complete signed APKs are checked against compatibility metadata, hashes, edition, version and certificate; the current APK/config/touch preferences are backed up before Android asks to install. Maps/saves are preserved. New upstream protocols require reviewed integration rather than blindly replacing VR/co-op components. Automatic checks are optional; offline play remains available.

## 8. Known Issues or Important Notes

- **Version labels/update check:** these preserved APKs and their bundled guide retain test18/candidate wording. This release page records their public 1.0 approval. On code 19, the updater can report “Release edition metadata is inconsistent” when comparing this same-code promotion; you already have the release, so no update is needed. Future APK updates must have a higher code. Older test builds need one manual install from the links above.
- **Co-op remains experimental:** not every mission, checkpoint, vehicle, cinematic, transition or device/network combination has a documented full playthrough. The 1.0 baseline is not universal certification.
- Inferred body joints can still clip in extreme poses/custom rigs. Physical weapon drops/pickups online remain limited and **MP Physical defaults Off**.
- Safe geometry can reduce performance. Refresh requests do not guarantee that frame rate; simulation remains 30 Hz with interpolated rendering.
- Controller mappings/rumble depend on Android, driver, connection type and model. Other headsets/phones have less testing than Quest 3.
- NAT/firewall/Wi-Fi isolation can block multiplayer; the native transport has no general relay fallback. Keep the app foregrounded during a match.
- Custom Edition/SPV1/custom rigs/resources remain experimental; custom cache support does not add retail Custom Edition network compatibility.
- **Logs:** each launch writes to `Download/HaloCE`, with app-storage fallback if needed. Include the matching log, build, map, device/OS and reproduction steps in a report. Review logs before posting: they may contain invites and device/path details.
- Back up the whole data root, including `game-versions`, for all imported sets and saves. Uninstalling or clearing app data can remove app-specific files. Switching sets intentionally keeps progress separate.

## 9. Additional Technical Details / Credits

Both APKs are ARM64, **internal version 1.0-test18 / version code 19**, using package IDs `com.halo.decomp` and `com.halo.decomp.vr` with the established signing certificate. Only the download filenames change for this release; APK bytes and signatures are unchanged. Runtime build source is `f45e32dd73b15280a5db4e5d4a4b2643f2c28379`; **v1.0.0** contains that code plus finalized public documentation; GitHub's source ZIP/tar.gz downloads are sufficient. `compatibility.json` is the small metadata file required by the launcher updater; players do not need to install or edit it.

Validation covers both flavor builds, package/version/signature checks, 16 KB ZIP alignment, payload/ZIP integrity and targeted networking, imports, animation, co-op, controller/touch and updater tests. The owner authorized these exact APKs for release; no new complete device playthrough was reported. These checks complement earlier device feedback; they do not substitute for real multiplayer or headset testing. Exact hashes/build provenance live in the tagged source documentation.

Credits: **Bungie/Microsoft and the original Halo team**; **punpckhdq/halo and bnunu/halo-1 contributors** for the decompilation; **bnunu/cybersecurity halo-ce-universal contributors** for the native port/networking; **astromaddie/Madison** for the OpenXR VR foundation; **ChupathingyCE and halo.milenko.org maintainers** for the directory; **moistman42069 and project contributors/testers** for this integration and refinements. Thanks also to LivingFray/HaloCEVR and the documented IK references, Andiweli's Android rendering work, and SnowyMouse's cache-format documentation.

SDL3, OpenXR, musl, KCP, miniupnpc, Mbed TLS, tomlc17, stb, extract-xiso and other inherited dependencies retain their licenses. **This product includes software developed by in &lt;in@fishtank.com&gt;.** Full credits and notices are included inside each APK under **Field guide → Credits & licenses**, and in the tagged repository. This is an unofficial community project; supply your own game data.
