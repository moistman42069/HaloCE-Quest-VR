# Halo CE Quest VR + Android

Native **Halo: Combat Evolved on standalone Meta Quest**, with a separate **flat Android APK** for touch/gamepad play. This community fork builds on the Halo CE decompilation, the native cross-platform port and astromaddie's OpenXR VR work. The reference headset is **Quest 3**.

**Latest release: test14, Quest VR + flat Android**, accepted for publication by the owner on 2026-10-03. These are the exact tested APKs, not rebuilt replacements. **Legs + Arms** remains the default for new VR settings; saved choices remain respected.

## Downloads

| Device / purpose | Download |
| --- | --- |
| Standalone Quest VR | [HaloCE-Quest-test14.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/halo-ce-quest-test14/HaloCE-Quest-test14.apk) |
| Flat Android, touch/gamepad | [HaloCE-Android-test14.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/halo-ce-quest-test14/HaloCE-Android-test14.apk) |
| Both APKs, current guides, credits and notices | [test14 bundle](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/halo-ce-quest-test14/HaloCE-Quest-Android-test14-bundle.zip) |
| Exact source used for both APKs | [test14 source ZIP](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/halo-ce-quest-test14/HaloCE-Quest-test14-source.zip) |

[Release notes and checksums](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/halo-ce-quest-test14) | [Always latest release](https://github.com/moistman42069/HaloCE-Quest-VR/releases/latest) | [VR controls](#vr-controls-quest-touch) | [All controls/options](docs/CONTROLS-AND-OPTIONS.md) | [Install/help](docs/PLAYER-GUIDE.md) | [Credits](CREDITS.md) | [Development checkpoint](docs/CURRENT-STATE.md)

Both APKs are `1.0-test14`, version code 15, ARM64. Supply your own Halo CE Xbox game data; maps are not included. Use test14 on both co-op peers.

## Development candidate

This work branch contains **test16**, held for owner testing. It adds VR Safe geometry defaults with a one-time config migration, and native action arm/hand playback that blends back to tracking. It preserves the complete test15 pass: configurable controller alignment, a flat touch HUD editor and swipe aim, Xbox-style Android gamepad settings/navigation and automatic touch hiding/recovery, native v11 PvP hosting/join support with legacy settings conversion, geometry upload fixes, bundled help, and signed project update handling. The download links above remain the accepted test14 release. [Candidate details and limits](docs/TEST16-PROGRESS.md).

## What's new in test14

Co-op fixes preserve host-controlled NPC movement inputs on the client, apply resting/velocity updates even inside position tolerance, transmit optional one-shot AI animation events, replicate unarmed NPC vehicle seats, and open the campaign pause/settings menu without pausing only one peer. Existing VR body/finger/grip, flat touch, launcher and avatar features are preserved. [Investigation and checks](docs/TEST14-PROGRESS.md).

The owner previously confirmed Quest gameplay, multiplayer, settings, Downloads logging, room-scale legs and full VR body movement visible on a flat Android partner, and has now accepted this replacement pair for release. This is not a documented playthrough of every mission, device or network condition. [Evidence and remaining coverage](docs/CURRENT-STATE.md).

## VR features

- Native OpenXR stereo rendering and tracked headset/controllers; the Quest runs the game locally.
- Hand aiming, either weapon hand, head- or controller-relative movement, smooth/snap turning, room-scale walking and recentering.
- Procedural **full-body IK** using Halo's biped hierarchy, tracked head/hands and inferred torso/legs. Includes room-scale foot following/planting, bounded shoulders, elbow-plane smoothing, continuous wrist twist and crouch clearance. Additional hip/foot trackers are not required or implemented.
- Four local views: **Full**, **Arms + Hands**, **Legs + Arms** (torso hidden, default), **Hands Only**. Separate arm choices: IK, hidden and authored animation.
- Articulated local finger poses driven by controller touch/trigger/grip input, finger smoothing, palm/finger contacts and haptics. This is controller-driven posing, not controller-free optical hand tracking. Held-gun contact is an approximation rather than a fully simulated rigid-body hand.
- Deliberate two-hand support grip by default: squeeze near the weapon support region to attach at a fixed point until release. **Auto** restores proximity attachment; **Off** disables it.
- Physical weapon hold/drop/transfer/pickup/holster behavior and first-grip protection for guns supplied on load/pickup. **Locked** holding is available. Physical weapons in network play are separately opt-in and have replication limitations.
- Impact-sweep or swing-triggered physical melee with a speed threshold. Network clients use native swing melee; contact does not make indestructible scenery destructible.
- Optional arm-swing movement and up to 1.5x offline sprint speed. Network speed stays stock; deliberate stick input takes priority, including reverse movement.
- Physical crouch, flashlight gesture, shoulder/hip holsters, haptics, weapon scope, vehicle view/steering choices and immersive/3D-screen/flat cutscenes.
- Native weapon crosshair artwork with size/opacity controls; independent menu pointer.
- Paged VR settings covering graphics, effects, resolution and refresh requests. Actual frame rate depends on device/runtime and scene load.

## VR controls (Quest Touch)

Use **Controls = VR** with the standard native controller profile. "Weapon hand" is the right hand by default; select Left in VR Settings to swap weapon/zoom trigger roles. Face-button sides are not all mirrored.

| Input | Action |
| --- | --- |
| Left stick | Move/strafe relative to Head, Left Hand or Right Hand setting |
| Right stick | Smooth or Snap 30/45 turn; vertical input also serves native look prompts |
| Weapon-hand trigger | Fire |
| Other-hand trigger | Zoom; Scope enables the weapon-aligned zoomed view |
| Right A | Jump / confirm |
| Right B | Reload/use; hold for native interaction/pickup prompts; Back in pointer menus |
| Left Y | Switch weapons |
| Left X, Physical weapons | Tap and release to throw grenade; hold 0.4 seconds to change grenade type |
| Left X, Locked weapons | Change grenade type |
| Weapon-hand grip, Physical | Hold the gun; release after the first grip to drop/holster/transfer |
| Weapon-hand grip, Locked | Throw grenade away from holsters; switch weapon at a holster |
| Other-hand grip near support area | Attach support hand at a fixed point; release to detach |
| Left stick click | Crouch |
| Right stick click | Melee |
| Both stick clicks together | Recenter during gameplay; stand at normal height first |
| Left menu button | Open pause/menu; online co-op keeps the shared world running |
| Weapon pointer + trigger | Select menu item; right B goes back |

**Weapon holding and two-hand grip:** Physical is the offline default. A weapon supplied on load/pickup stays supported until your first grip action, then grip/release controls holding. **Two Hands = Grip** is the default: proximity alone does not attach the support hand. **Auto** enables proximity attachment; **Off** disables it. Bring palms together and grip with the other hand to transfer handedness. Reload uses the button; physical magazine reloading is not implemented.

**Multiplayer difference:** **MP Physical defaults Off**, so online play uses Locked holding even when Weapons is set to Physical. Use the Locked grenade inputs above in that case. Enabling MP Physical opts into physical holding/drop behavior, whose replication has limitations. This setting does not disable remote VR body visibility.

**Gestures and body:** duck physically (default 35 cm below recentered height), bring the off hand near your head for the flashlight (default 20 cm), and use shoulder/hip holsters with entry haptics. Swing/contact melee uses the configured speed threshold; stick-click melee remains available. Optional Arm Run uses arm motion with a neutral stick, reaching up to 1.5x speed offline; online speed stays stock and stick movement takes priority. Fingers follow controller sensors, not optical hand tracking. **Legs + Arms** is the default body view; Full, Arms + Hands and Hands Only are also available.

**Changing options:** campaign pause > **VR Settings**. A/right increases or advances; left decreases. Next Page exposes more settings; Back returns through pages/categories. Settings save to `config.toml`; existing choices survive updates. Body, hand, movement, turn, scope, vehicle, cutscene, graphics, refresh and crosshair options are covered in the [complete controls and options guide](docs/CONTROLS-AND-OPTIONS.md), including flat touch/gamepad inputs and all menu ranges.

## Flat Android features

- Separate ARM64 app with multi-touch movement, rate-based look, fire-and-drag aim, combat/menu buttons and a saved overlay visibility toggle.
- Physical gamepads remain supported; touch merges into player one without creating another controller slot.
- Shared launcher/data import, population-sorted PvP directory, experimental campaign host/join, per-launch logs and remote VR-avatar receiver.
- Android 9/API 28+, ARM64 and compatible OpenGL ES graphics are required. Comprehensive phone testing remains pending.

## Multiplayer, co-op and remote avatars

The launcher reads the **ChupathingyCE native-port directory**, displaying names, maps, populations and versions. All retained listings sort by reported population before paging in groups of 50. Up to four compatible HTTPS catalogs can be merged; saved invites and LAN discovery cover hosts outside public listings. No second compatible preset provider was verified during this release's research.

PvP accepts reviewed native distributed host versions **9/10**, subject to matching content/rules. The owner confirmed multiplayer play. Compatibility concerns native decompilation-port clients: retail Halo PC/Custom Edition, original Xbox, MCC and arbitrary browser/WebRTC rooms use different protocols. A listing is a host report, not a measured ping or reachability guarantee.

**Campaign co-op is experimental.** A separate browser, host/join, host-controlled campaign replication and transition handling are implemented. Both players need this campaign implementation and matching mission/resource files. Public directory acceptance of its separate `0xCE01` protocol remains unverified; private invite/LAN is the fallback. Joining in progress is disabled and disconnects require a new lobby. [Instructions and limits](docs/PLAYER-GUIDE.md#campaign-co-op-experimental).

**Remote VR avatars are experimental.** Supporting hosts/observers negotiate visual skeletal snapshots at 15 Hz, with interpolation and expiry fallback. Flat observers can receive them. Local body hiding is not transmitted; peers can see the complete body. The stock world biped lacks individual finger bones, so local articulated finger detail is not replicated. The extension changes rendering, not hitboxes/shot origins. Older hosts/clients keep stock animation. [Protocol details](docs/NETWORK-VR-AVATARS.md).

## Install and play

1. Download the APK for your device. Sideload the VR APK using your authorized Quest developer-mode installer, or install the flat APK through Android's installer.
2. Supply your own legally obtained **Halo CE Xbox game data**. The launcher extracts `maps/` from a compatible `.iso`/`.xiso`; allow around 1.8 GB for extracted maps plus cache/saves and temporary image space. No Halo maps are included in the APKs.
3. Import the data and choose Play. Existing Quest data in `Documents/HaloCE/maps` is recognized when `ui.map` exists there.
4. Recenter at normal standing height. In the stock campaign pause menu, open **VR Settings** to adjust body, controls and graphics.
5. Keep the matching `Download/HaloCE/halo_log_...txt` when reporting an issue.

Updates are manual APK installs over the existing app, retaining the project signing certificate. A differently signed fork with the same package ID cannot update in place: back up maps/config/saves before considering removal. VR/flat apps have separate data and do not automatically share saves. [Full player guide](docs/PLAYER-GUIDE.md).

## Relationship to other projects

[LivingFray's HaloCEVR](https://github.com/LivingFray/HaloCEVR) converts the original 2003 PC edition to PC VR. This repository follows the native Xbox-decompilation/Android route and builds on [astromaddie's HaloCE-VR](https://github.com/astromaddie/HaloCE-VR) OpenXR foundation. Its focus is standalone Quest, the body/finger/contact systems above and a flat Android companion. It is separate from our [MCC VR project](https://github.com/moistman42069/MCCVR-Halo-Build). [Full credits and licensing](CREDITS.md).

## Known limits and feedback

- Body quality depends on rig/pose; there is no universal clipping-free guarantee. Three tracked devices infer the remaining joints.
- Campaign co-op, avatar transitions and flat touch require the device checks in [CURRENT-STATE.md](docs/CURRENT-STATE.md).
- Public listing/NAT traversal can fail; the existing transport has no relay fallback for restrictive/symmetric NAT.
- Physical reload is deferred; button reload is implemented. Network physical drops/pickups may look different on peers and are off by default.
- Custom Edition/OpenSauce/SPV1 support is experimental and has separate content dependencies. SPV1 install/uninstall recovery is present; broad retail PC mod/rig compatibility is not established.
- Custom pause-menu tags may not support the generated menu; config-file settings remain available.

Use [Issues](https://github.com/moistman42069/HaloCE-Quest-VR/issues) with APK version, device/OS, map/mission, settings, host/client role, peers' versions, exact steps and launch logs. Review logs for private invites/device information before sharing. Recordings help with IK/grip/menu issues.

## Continuing development

`main` contains the complete test14 runtime source and current documentation. The release tag and matching source ZIP point to build commit `696a7bbe9321565d90207042067658cb8814cad1`; later documentation commits do not change the tested APKs. Earlier private history remains private because it contains personal commit metadata. [Provenance](docs/RELEASE-PROVENANCE.md) and [CONTRIBUTING.md](CONTRIBUTING.md) explain source identity, build checks and continuation.

Build in Linux/WSL using Python, Ninja, clang with `arm64_32`, JDK 17, Android SDK 35 and NDK 27.2.12479018:

```sh
bash tools/build-quest.sh vr
# Preserve the VR APK before changing the shared native staging directory.
bash tools/build-quest.sh flat
```

Never run the two flavors concurrently. The original update signing key stays private; local/CI keys generally cannot update an installed project APK. Read [CURRENT-STATE.md](docs/CURRENT-STATE.md) and [architecture](docs/VR_ARCHITECTURE.md) before editing. Current-state/provenance take precedence over dated checkpoint documents. The inherited desktop/flat workflow is manual and does not publish these Quest releases automatically.

The inherited root license is [CC0](LICENSE.md); third-party code/fonts retain their own terms. That source license grants no Halo game-data rights. Halo and its assets belong to their respective owners. This is an unofficial community project.
