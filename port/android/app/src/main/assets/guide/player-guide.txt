# Halo CE Quest VR + Android 1.0.2

## 1. Installation

**Current release: 1.0.2 / version code 25.** This update restores the Quest Safe-geometry upload path changed in withdrawn 1.0.1, adds render-performance diagnostics, improves multiplayer join explanations and adds the in-game public PvP browser. It also includes controller-anchored weapon alignment, left-handed controls and simpler VR settings from test20d. Version 1.0.1 was withdrawn for severe Quest performance regression. This release installs over it using the established signing certificate; earlier releases remain available.

| Your device | Download |
| --- | --- |
| Android phone/tablet — flat, touch or gamepad | **[HaloCE-Android-1.0.2.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.2/HaloCE-Android-1.0.2.apk)** |
| Meta Quest — immersive standalone VR | **[HaloCE-Quest-1.0.2.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/v1.0.2/HaloCE-Quest-1.0.2.apk)** |

1. **Install the appropriate APK.** On Quest, enable developer mode and sideload with SideQuest or your existing installer; open it from **Unknown Sources**. On Android, open the downloaded APK and allow installation from that source when prompted. Both require ARM64, Android 9/API 28 or newer and compatible graphics. **Quest 3 is the reference headset**; other devices are not equally verified.
2. **Updating this project? Install over it.** Both APKs retain their package IDs and signing certificate. Do not uninstall or clear app data. Optional ADB command: `adb install -r <apk-file>`. Back up your maps, saves and settings first. Another fork using the same package ID but a different key cannot update in place.
3. **Supply your own legally obtained Xbox Halo: Combat Evolved data.** No game maps are included. Copy your `.iso`/`.xiso` or extracted game folder to the device. MCC and retail PC installation files are not substitutes for the supported Xbox base data.
4. **Open the launcher → Game files & versions.** Import an ISO/XISO or select an extracted `maps` folder/game root. Wait for validation, then select **Use** beside the imported set. Allow roughly 1.8 GB for the usual maps, plus the source image, saves and import space. Multiple sets require additional storage.
5. **Choose Play.** Existing installations remain available as **Existing game data**. In VR, stand normally and press both stick clicks together to recenter. Open the campaign pause menu → **VR Settings** to customize your experience.

The launcher includes an offline **Field guide** with controls, settings and credits. Existing Quest data under `/sdcard/Documents/HaloCE/maps` is recognized when `ui.map` is present; otherwise each app uses its own external-files storage. VR and flat can coexist and have separate app data.

**Updating:** install this APK over the existing app. Code 25 supports updating public 1.0 (code 19), withdrawn 1.0.1 (code 20) and test20 through code 24. Do not uninstall or clear data; back up maps, saves and settings first. Android may ask you to confirm installation.

## 2. New Features / Major Changes

This release carries forward the project features and adds performance recovery, diagnostics, Quest/Android network parity checks, join-stage feedback and a per-frame VR crosshair update. The v1.0.1 release was withdrawn; its inefficient Safe streaming upload path is not used here.

- **In-game public server browser:** Multiplayer > System Link combines signed OpenCE public listings and native LAN games, most populated first. Seven games per page, Previous/Next and Refresh. The launcher browser remains available.
- **Multiplayer crash guard:** safely deactivates invalid automatic object replicas outside a valid visibility cluster instead of asserting after joining a populated match.
- **Updater correction:** same-code public promotions and an older public build no longer trigger the reported inconsistent-edition error. Integrity, signature and downgrade checks remain.
- **Official upstream downloads:** Versions & updates > Official upstream exports verified OpenCE ZIPs separately. They do not replace this mod's VR/co-op engine.
- **VR reticle alignment:** the world-space target follows the native pre-spread firing ray, including the offline guarded hand origin and online native camera origin. Handedness, weapon alignment and native action handoff remain unchanged.
- **Safe geometry refinement:** restoration of the renderer's vertex-array state after compositor work. The 1.0.1 ordered upload path caused the severe Quest slowdown; 1.0.2 restores the fenced streaming path. The reported intermittent left-eye corruption still needs device confirmation.
- **ISO/XISO import:** handles deeply unbalanced valid directory trees and provides clearer damaged-image, incomplete-transfer and unsupported-container errors. Revisions still use actual cache build IDs/fingerprints, not guessed disc labels.
- **Clearer co-op instructions** in the launcher and guide. Existing two-player campaign, body sharing, touch/gamepad, vehicle controls and per-launch logging remain.

## 3. Controls / Inputs

### Quest Touch — default VR layout

Use **Controls = VR** and the standard native controller profile. Right is the default weapon hand. **Controls → Handedness: Left**  mirrors the whole layout: gun, triggers, sticks (move on the right, turn on the left) and face buttons (jump on X, reload on Y, grenades on A, switch weapons on B); Mirror Controls Off keeps the standard buttons.

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

**Online holding differs:** **Weapons: Physical** (the default) applies offline only, so multiplayer uses **Locked** holding unless you choose **Physical + MP**, with the Locked grenade inputs above. Body sharing remains available. A newly supplied weapon stays held until the first grip action in Physical mode. **Two Hands** defaults to **Auto Lock**: resting the off hand at the support grip locks it; pulling away releases (Squeeze restores the old way). Physical melee is off in network games unless Body → Melee is set to Impact + Online or Swing + Online; the melee button always works.

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
- **Calibration and handedness :** the held gun is **anchored to the controller**: the gun hand's wrist sits where your empty hand's wrist would, for every weapon, and the gun turns about your hand (Hands + Gun → Gun Grip: Anchored; Classic restores the old placement). **Hands + Gun** sets both visible hands at once (default pitch -70, left mirrored), the gun's angle (shots and reticle follow it) and its place in the hand (Gun Forward / Up / Out). **Controls → Handedness: Left** puts the gun in the left hand and, with Mirror Controls Auto, mirrors the sticks and face buttons too; vehicle Steering and Move With follow when they used a hand. **Controller Left/Right** is an advanced tracking correction that moves hand and gun together; normally leave it at zero. **Body → Hands** chooses Body IK (default), Floating (hands only), Float + Arms, Animated or Gun Only. While driving, either stick click sounds the horn. **Hands + Gun → Aim Up / Aim Right** fine-tune the held gun's shots and reticle (each gun separately; Reset Aim clears it).

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

Open **Multiplayer → System Link** in-game, then choose **Refresh**. The page combines OpenCE public games and native LAN hosts, removes duplicate hosts, sorts by reported population (highest first) and shows seven games. Use **Next/Previous** to page. Select a public listing to resolve its current native host advertisement, which can take up to 30 seconds, then join. Move the selection or press **B** to cancel a pending resolve. If you chose a community-directory listing in the launcher, use its **Join** action first, then return to System Link and select that host after the invite tunnel connects. Empty results remain in the list so you can refresh or page again.

For community catalogs, open launcher **Multiplayer servers → Refresh → Join**. After the invite tunnel connects, use **Multiplayer → System Link** in-game to select the host; other native ports may call it Direct Link. Saved invites and LAN discovery support unlisted hosts.

The launcher browser reads the ChupathingyCE native-port directory and can merge up to four compatible HTTPS catalogs. It sorts compatible listings by reported population before paging. Full/incompatible hosts show their status; a listing does not prove reachability or measure ping. The in-game OpenCE signed native discovery is a separate source and format; do not paste its broker address into launcher Directory settings. Private/unadvertised games cannot all be enumerated.

**Host multiplayer** offers installed map, game type, name, score/time, friendly fire, radar, team balance, vehicle respawn, loadout/grenade options and **2–128 PvP slots**. Public listing is opt-in; private invites are available. Start with modest limits: 128 is protocol capacity, not a verified Quest-host performance target. Network settings expose Internet/LAN, UPnP, clipboard invites and tunnel port.

This build hosts native **Network 11** and accepts reviewed distributed hosts **9–11**, subject to content/rules and connectivity. Supported native Windows/macOS/Linux/Android ports can cross-play when compatible. **Retail Halo PC/Custom Edition, original Xbox and MCC use different network protocols.** Older clients that insist on an older version need an update.

### Campaign co-op and avatars

Campaign sessions use a separate two-player flow and do not appear in the PvP browser. Use matching 1.0.2 project builds and matching campaign/resource files on both devices. Two Quests or Quest plus flat Android are intended pairings.

1. **Host:** open launcher **Campaign co-op → Host campaign**, choose a mission and difficulty, and enable **List publicly** if you want the community co-op catalog to show the session. Create the session and enter the System Link lobby. Keep the app in the foreground.
2. **Join:** the other player opens **Campaign co-op → Browse / join**, refreshes and selects the host, or enters a private invite. After connection, launch the game and open **Multiplayer → System Link**; select the host and join their lobby.
3. **Start:** wait until both players are in the lobby before the host starts the mission. Keep both apps in the foreground. If public co-op discovery fails, use a private invite or LAN.

The launcher's campaign directory is separate from the OpenCE PvP directory; the latter does not advertise this campaign protocol. The host controls campaign scripts, AI, checkpoints and transitions. **Campaign supports two players**, not 128; joining mid-mission is disabled. Disconnects require a new lobby. Public campaign directory acceptance remains unverified; private invite/LAN is the fallback.

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

- **Device follow-up:** the populated-server crash guard, native browser, reticle alignment and intermittent left-eye workaround still need broader real-device confirmation. A build/test pass is not a campaign playthrough or proof that every server works.
- **Co-op remains experimental:** not every mission, checkpoint, vehicle, cinematic, transition or device/network combination has a documented full playthrough. The 1.0 baseline is not universal certification.
- Inferred body joints can still clip in extreme poses/custom rigs. Physical weapon drops/pickups online remain limited, so **Physical + MP** is not the default.
- Safe geometry can reduce performance. Refresh requests do not guarantee that frame rate; simulation remains 30 Hz with interpolated rendering.
- Controller mappings/rumble depend on Android, driver, connection type and model. Other headsets/phones have less testing than Quest 3.
- NAT/firewall/Wi-Fi isolation can block multiplayer; the native transport has no general relay fallback. Keep the app foregrounded during a match. **Mobile data is the usual cause when one device joins a server and another does not:** carrier networks give each connection its own public port (the log says "this network's NAT gives each destination its own port"), so hosts whose routers are also strict cannot be reached. Use Wi-Fi for multiplayer. The Quest and Android builds share the same multiplayer code; the log names the stage that failed (1 asking the host, 2 opening the direct connection, 3 connected) and the network type ("Network: Wi-Fi" or "mobile data").
- Custom Edition/SPV1/custom rigs/resources remain experimental; custom cache support does not add retail Custom Edition network compatibility.
- **Logs:** each launch writes to `Download/HaloCE`, with app-storage fallback if needed. Include the matching log, build, map, device/OS and reproduction steps in a report. Review logs before posting: they may contain invites and device/path details.
- Back up the whole data root, including `game-versions`, for all imported sets and saves. Uninstalling or clearing app data can remove app-specific files. Switching sets intentionally keeps progress separate.

## 9. Additional Technical Details / Credits

Both release APKs are ARM64, **version 1.0.2 / code 25**, using package IDs `com.halo.decomp` and `com.halo.decomp.vr` and the established signing certificate. GitHub provides tagged source archives; compatibility.json is the small metadata asset required by the updater. Earlier releases are preserved.

Validation includes both flavor builds, signatures/versions, 16 KB ZIP alignment, payload integrity, targeted regressions and synthetic cache/import checks. These checks do not substitute for testing the test20e join diagnostics and crosshair on a phone/headset or a full campaign playthrough. Performance recovery was confirmed on device with test20b; test20e networking still needs device checks. See [1.0.2 provenance](RELEASE-PROVENANCE-1.0.2.md), [withdrawn 1.0.1 record](RELEASE-PROVENANCE-1.0.1.md), [test20 investigation](TEST20-PROGRESS.md) and [test20e delivery](TEST20E-DELIVERY.md).

Credits: **Bungie/Microsoft and the original Halo team**; **punpckhdq/halo and bnunu/halo-1 contributors** for the decompilation; **bnunu/cybersecurity halo-ce-universal contributors** for the native port/networking; **astromaddie/Madison** for the OpenXR VR foundation; **ChupathingyCE and halo.milenko.org maintainers** for the directory; **moistman42069 and project contributors/testers** for this integration and refinements. Thanks also to LivingFray/HaloCEVR and the documented IK references, Andiweli's Android rendering work, and SnowyMouse's cache-format documentation.

SDL3, OpenXR, Monocypher, musl, KCP, miniupnpc, Mbed TLS, tomlc17, stb, extract-xiso and other inherited dependencies retain their licenses. **This product includes software developed by in &lt;in@fishtank.com&gt;.** Full credits and notices are included inside each APK under **Field guide → Credits & licenses**, and in the tagged repository. This is an unofficial community project; supply your own game data.

## Storage reference

| Data | Location |
| --- | --- |
| Quest shared game root, when present | `/sdcard/Documents/HaloCE` |
| Quest app external root | `/sdcard/Android/data/com.halo.decomp.vr/files` |
| Flat app external root | `/sdcard/Android/data/com.halo.decomp/files` |
| Maps/config | `maps/`, `config.toml` under the active root |
| Saves | Preserve app `save/` and any shared-root save data; consult startup log/config for active save root |
| Public launch logs | `Download/HaloCE/halo_log_<date>_<time>_<pid>.txt` |

Only VR selects the shared root, and only when `maps/ui.map` exists. Editing an inactive config has no effect. Android file-manager restrictions may require the system picker or authorized ADB access.

Managed sets and their saves live under `game-versions/p-<id>` beneath the selected base. Quit before editing configuration manually.
