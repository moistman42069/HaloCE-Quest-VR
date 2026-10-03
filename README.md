# Halo CE Quest VR + Android

Native **Halo: Combat Evolved on standalone Meta Quest**, with a separate **flat Android APK** for touch/gamepad play. This community fork builds on the Halo CE decompilation, the native cross-platform port and astromaddie's OpenXR VR work. The reference headset is **Quest 3**.

**Current release: Quest VR test13a + flat Android test13.** Test13a makes **Legs + Arms** the VR body default. Saved choices remain respected. The flat companion already contains the matching campaign/avatar implementation and does not need that local visibility change.

## Downloads

| Device / purpose | Download | Identity |
| --- | --- | --- |
| Standalone Quest VR | [HaloCE-Quest-test13a.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/halo-ce-quest-test13a/HaloCE-Quest-test13a.apk) | `1.0-test13a`, code 14; `com.halo.decomp.vr` |
| Flat Android phone/tablet | [HaloCE-Android-test13.apk](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/halo-ce-quest-test13a/HaloCE-Android-test13.apk) | `1.0-test13`, code 13; `com.halo.decomp` |
| Both APKs, guides, notices and hashes | [Download bundle](https://github.com/moistman42069/HaloCE-Quest-VR/releases/download/halo-ce-quest-test13a/HaloCE-Quest-Android-test13a-bundle.zip) | Same binaries as above |

[Release notes and source](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/halo-ce-quest-test13a) · [Controls/options](docs/CONTROLS-AND-OPTIONS.md) · [Install/help](docs/PLAYER-GUIDE.md) · [Credits](CREDITS.md) · [Development checkpoint](docs/CURRENT-STATE.md)

These are **experimental community builds**. Quest gameplay, multiplayer, settings, Downloads logging and room-scale legs have received positive owner reports; the owner specifically approved Legs + Arms. Campaign co-op, remote avatar replication and flat touch still need documented paired-device/phone acceptance. Build checks do not establish those results.

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

`main` contains the complete current test13a source plus current public documentation. Earlier private history is retained privately because it contains personal commit metadata. Privacy-clean source downloads preserve each shipped APK's runtime source files byte for byte; documentation/publishing metadata is refreshed. [Provenance](docs/RELEASE-PROVENANCE.md) and [CONTRIBUTING.md](CONTRIBUTING.md) explain the two APK revisions.

Build in Linux/WSL using Python, Ninja, clang with `arm64_32`, JDK 17, Android SDK 35 and NDK 27.2.12479018:

```sh
bash tools/build-quest.sh vr
# Preserve the VR APK before changing the shared native staging directory.
bash tools/build-quest.sh flat
```

Never run the two flavors concurrently. The original update signing key stays private; local/CI keys generally cannot update an installed project APK. Read [CURRENT-STATE.md](docs/CURRENT-STATE.md) and [architecture](docs/VR_ARCHITECTURE.md) before editing. Current-state/provenance take precedence over dated checkpoint documents. The inherited desktop/flat workflow is manual and does not publish these Quest releases automatically.

The inherited root license is [CC0](LICENSE.md); third-party code/fonts retain their own terms. That source license grants no Halo game-data rights. Halo and its assets belong to their respective owners. This is an unofficial community project.
