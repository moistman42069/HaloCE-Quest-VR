# Test15 candidate delivery

2026-10-03. **Unpublished; awaiting owner testing.** Test14 remains the accepted public release. This pair is `1.0-test15`, Android version code 16, ARM64/API28+. VR package: `com.halo.decomp.vr`; flat: `com.halo.decomp`. Legs + Arms remains the default VR body mode and existing saved choices remain respected.

This final pair supersedes the earlier pre-controller test15 candidates. Use the hashes below; earlier test15 APKs are not this delivery.

## Exact APKs

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test15.apk` | 27,834,941 | `75a6b88c731b1a122e3e9c4d14b2d9d6b8d8d1b449832b5f7409775c3a0815f3` |
| `HaloCE-Android-test15.apk` | 25,827,822 | `4aaa6416ca2e5341a346738c473bb84910ba33bc80b4f826bade4b79e4919a42` |

Certificate SHA256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, the established project identity. Final runtime/launcher source is `f9a9e166b8605fbc5de024c0e1386fc0b74d8d29`, including controller commit `d949612` and the prior test15 implementation. SDL 3.4.16 is pinned at `fa2c02bb6e21974a89ea9824bc53c9932abe5f9c` with the recorded clipboard and digital-trigger patches. Subsequent delivery documentation does not change runtime payloads. The package manifest records the exact full source archive commit and hashes. Both flavors were built serially with `tools/build-quest.sh` and preserved before changing native staging. Compaction verified every non-signature payload hash and certificate, with 16KB native-library alignment.

## Changes to test

- Affected controller firmware: VR Settings > Align Left / Align Right, roll180 shortcut, pitch/yaw/roll and local position offsets, grip/native aiming and reset. No automatic firmware flip; zero defaults preserve normal tracking.
- Flat Android: HUD editor, drag/covered-control selection, save/cancel/reset, size/opacity/color, sensitivity/dead zone/floating MOVE, and swipe aiming (or held-stick mode).
- Android gamepad: Xbox-style USB/Bluetooth mappings, analog and digital-only triggers, launcher/dialog navigation, separate stick response/dead zones, trigger threshold, face-button swap, supported rumble, device input check, disconnect cleanup and Auto / Always show / Always hide touch. Default native profile: LB flashlight, RB grenade type; touch labels corrected accordingly. [Controller guide](ANDROID-GAMEPAD.md).
- Co-op capacity audit: two players remains the supported CE01 limit. Single-peer ACK/snapshot state and four-slot campaign recovery block a safe cap increase. Unsupported known directory capacities are blocked with an explanation; PvP listing capacity is unchanged. [Findings and required expansion work](COOP-PLAYER-LIMITS.md).
- Native PvP: v11 match settings and v10 pings; explicit older v9/v10 settings conversion. Launcher hosting exposes map/variant/cap/name/score, time, team damage/balance, radar, vehicle respawn, grenade and custom-loadout choices. Capacity 128 is not a Quest performance promise. Current upstream quit-slot reuse/next-map cleanup fixes included.
- Graphics: exact-size uploads, ordered static geometry mirrors, safe buffer/fence fallbacks; optional Safe geometry for affected devices. Original/Rev2 reports do not isolate a revision cause; Rev1 and a complete three-revision dataset remain unverified.
- Launcher: CE-inspired procedural presentation, scrollable help with 161 native settings, per-map headers/fingerprints, network options, default automatic compatible-update checks, upstream protocol status and in-launcher installation path.

## Update behavior

Checks run on launcher open/resume at most every six hours (failed checks can retry after 15 minutes). Turn them off or check immediately under Versions & updates. Newer-protocol listings offer that same update path. Unknown upstream protocols report that integration is needed. Only this project's reviewed stable edition-matching APK can be offered; compatibility metadata, hash, package, version, minimum SDK, signing certificate and native/VR payload are verified. Current APK/config/touch settings are backed up, then Android asks for installation approval. No runtime component swap, silent uninstall, downgrade, save migration or background game restart. Offline play remains available. Future approved release assets must include generated `compatibility.json`.

## Checks completed before packaging

- Successful VR native+Java and flat native+Java builds; generated offline guide bundled in both.
- Nine targeted suites passed: campaign actor/control ownership; campaign barrier/checkpoint lifecycle; browser/invite parsing and native compatibility; VR pose/finger/weapon math; render-target stability; calibration/PvP parser/config/header fixtures; new input/wire/renderer/update-policy harnesses; Android controller mapping/capability/lifecycle checks; campaign capacity checks.
- Production settings sender/receiver tests cover native v11 and legacy CE01/v9/v10 record serialization, local-data tail preservation, fragmented assembly, mixed/invalid lengths and option bounds.
- Touch JNI tests cover quick taps, consumption, finite/bounded motion,250ms expiry, reset generation and32-byte ABI. Layout tests cover screen fractions, edges, dead zones and diagonals. Pure updater policy tests cover tags/flavors/URLs/digests/unknown and newer upstream protocol headers.
- Geometry exact-payload tests exercise 512 size/mode combinations under ASAN/UBSAN. 128 player-slot predicate cases cover live units, departed users, lobbies and invalid indices.
- Controller tests execute the production Xbox mapper, flat host adapter and patched SDL Java/C trigger mapping; all 65,536 raw stick values, 600 reconnects, independent triggers, focus/rumble gates and visibility policies pass. Campaign capacity checks cover 1-128 limits, 40 mission/difficulty identities, saved-slot bounds and refusal of multi-peer barrier ACKs.
- Privacy/source review excludes local evidence, game maps, keys and personal metadata. Required third-party notices remain.

## What still requires the owner's devices

No agent installation, game launch, physical USB/Bluetooth controller session, live match or update installation was performed. Test controller mappings in gameplay/menus, vibration, hot-plug/reconnect, focus loss, dead zones, swapped layouts and all three touch policies. Higher-player campaign support is not enabled or claimed. Check affected v78 orientation, indoor Adreno geometry, phone aiming/editor/cancellation/cutouts, real v9/v10/v11 hosts, public listing acceptance/NAT and repeated match/rejoin. Re-test both Quest/flat co-op peers together: NPC walking/falling, avatars, checkpoints, BSP/mission transitions, death/recovery and reconnect. CE01 serialization is retained, but this candidate has no new paired-device acceptance yet. Existing test14 acceptance is not a substitute.

Keep both peers on this candidate for testing and attach each launch's Download/HaloCE log if a problem occurs. Review logs for private invites before posting. Do not publish these APKs as a new release until the owner approves them.
