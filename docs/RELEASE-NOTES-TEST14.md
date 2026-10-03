# Test14 - standalone Quest VR + flat Android

The accepted test14 pair is now available for standalone Quest VR and flat Android. These are the exact APKs supplied for testing, with no rebuild or re-signing during publication. Both are `1.0-test14`, version code 15, ARM64.

## Downloads

- **HaloCE-Quest-test14.apk**: immersive Quest VR, package `com.halo.decomp.vr`.
- **HaloCE-Android-test14.apk**: flat Android touch/gamepad, package `com.halo.decomp`.
- **HaloCE-Quest-Android-test14-bundle.zip**: both APKs, current player/control guides, credits, dependency notices and release manifest.
- **HaloCE-Quest-test14-source.zip**: exact source commit for both APKs. Its build-time docs retain the historical testing hold; current documentation records the subsequent acceptance.
- **SHA256SUMS.txt / release-manifest.json**: file integrity, source identity and acceptance record.

[Installation and troubleshooting](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/docs/PLAYER-GUIDE.md) | [Quest VR controls in the README](https://github.com/moistman42069/HaloCE-Quest-VR#vr-controls-quest-touch) | [Complete controls and settings](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/docs/CONTROLS-AND-OPTIONS.md)

## Co-op fixes in this build

- Preserve valid host NPC movement/aim/fire inputs through the client unit update, with bounded expiry and death/checkpoint cleanup. This addresses the control-state loss that caused NPC sliding.
- Apply NPC velocity and resting-state updates even when transforms are within correction tolerance; clear stale airborne presentation for grounded rest.
- Send optional reliable one-shot AI animation events with object, enum, alignment and graph guards. Native animation eligibility still applies and variants are selected locally.
- Replicate vehicle seats for unarmed campaign NPC passengers.
- Route co-op pause/settings through the campaign menu while keeping the shared simulation running.

Use **test14 on both co-op peers**, with matching mission/resource files. Existing CE01 layouts and avatar IDs are retained; optional animation event 39 extends presentation. Campaign remains experimental: acceptance of this pair does not establish a complete mission/transition/device test matrix. Public co-op directory registration remains unverified; private invites/LAN are available. No joining in progress; a disconnected session needs a new lobby.

## Included VR, Android and multiplayer features

- Native standalone OpenXR, tracked hand aiming, smooth/snap turning, room-scale movement, scopes and vehicle/cutscene choices.
- Inferred full-body IK with **Legs + Arms default**, plus Full, Arms + Hands and Hands Only; room-scale feet and controller-driven articulated fingers/contact feedback.
- Deliberate support-hand grip at a fixed attachment point, optional proximity attachment, first-grip weapon protection, physical/locked holding, holsters and motion melee.
- Physical crouch/flashlight gestures and optional arm-run movement with offline sprint. Network movement speed remains stock.
- Paged VR settings and native crosshair controls. Existing saved choices survive updates.
- Flat Android multitouch movement/look, fire-and-drag aim, combat/menu buttons, gamepad coexistence and overlay visibility control.
- Population-sorted native-port PvP directory with paging, compatible custom feed slots, saved invites and LAN. ChupathingyCE is the verified preset; retail PC/Custom Edition, MCC and original Xbox servers use other protocols.
- Campaign host/join and negotiated remote VR body snapshots visible to supporting VR/flat peers. Visual extension does not change hitboxes; remote individual fingers are not replicated.
- Per-launch diagnostics in `Download/HaloCE`.

## Start here

1. Install the appropriate APK over the existing project app to preserve data; the signing identity is unchanged.
2. Import your own legally obtained Halo CE **Xbox ISO/XISO** using the launcher. No game maps/data are included. Allow roughly 1.8 GB for maps plus cache/saves and extraction space.
3. On Quest, recenter with **both stick clicks** at normal standing height. Open campaign pause > **VR Settings**.
4. Default Physical holding: weapon grip holds, support grip near the gun attaches; left X tap/release throws a grenade and hold changes type. **MP Physical is Off by default**, so online Locked holding uses weapon grip for grenade (away from a holster), and left X changes type.
5. Consult the full input tables above for every button, gesture and option, including left-handed and flat controls.

Quest 3 is the reference headset. Flat requires Android 9/API 28+, ARM64 and compatible OpenGL ES. Physical reload is not implemented; button reload works. Bodies infer untracked joints, so extreme poses/custom rigs may clip. Online physical weapon drops are opt-in with replication limitations. Logs may contain invites/device details; review them before posting an issue.

## Source, verification and credits

Build/tag commit: `696a7bbe9321565d90207042067658cb8814cad1`. The owner accepted this delivered pair and authorized publication on 2026-10-03. Serial builds, five targeted suites, signatures, version/ABI, payload and archive/privacy checks passed before delivery. Publication checks preserve the tested hashes. This is not an all-device/full-campaign certification.

[Release provenance](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/docs/RELEASE-PROVENANCE.md) | [Development checkpoint](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/docs/CURRENT-STATE.md) | [Full credits and licensing](https://github.com/moistman42069/HaloCE-Quest-VR/blob/main/CREDITS.md)

Thanks to Bungie and the original Halo team; punpckhdq/halo and bnunu/halo-1; bnunu/cybersecurity's universal port contributors; astromaddie/Madison's OpenXR foundation; ChupathingyCE/service maintainers; the dependency authors; and players providing testing and feedback. LivingFray's separate PC VR project and the documented IK references are credited in the full guide. This product includes software developed by in <in@fishtank.com>. Required third-party notices accompany the release. Unofficial community project; Halo game-data rights remain with their respective owners.
