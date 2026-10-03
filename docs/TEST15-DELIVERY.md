# Test15 candidate delivery

2026-10-03. **Unpublished; awaiting owner testing.** Test14 remains the accepted public release. This pair is `1.0-test15`, Android version code16, ARM64/API28+. VR package: `com.halo.decomp.vr`; flat: `com.halo.decomp`. Legs + Arms remains the default VR body mode and existing saved choices remain respected.

## Exact APKs

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test15.apk` | 27,814,461 | `0778545712c5502e1f449423e816bce3a43b3ebdad99c8d3cabb5ee5ebba6deb` |
| `HaloCE-Android-test15.apk` | 25,811,438 | `e8049e1fd8ed52679ceb5fd89e20781c6ab1c0a9f2ccebf0fcd00db1a33d9fa0` |

Certificate SHA256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, the established project identity. Runtime implementation is commit `b472918`; packaging verification/tooling is `c447e5f`. Subsequent delivery documentation does not change runtime payloads. The package manifest records the exact full source archive commit and hashes. Both flavors were built serially with `tools/build-quest.sh` and preserved before changing native staging. Compaction verified every non-signature payload hash and certificate, with 16KB native-library alignment.

## Changes to test

- Affected controller firmware: VR Settings > Align Left / Align Right, roll180 shortcut, pitch/yaw/roll and local position offsets, grip/native aiming and reset. No automatic firmware flip; zero defaults preserve normal tracking.
- Flat Android: HUD editor, drag/covered-control selection, save/cancel/reset, size/opacity/color, sensitivity/dead zone/floating MOVE, and swipe aiming (or held-stick mode).
- Native PvP: v11 match settings and v10 pings; explicit older v9/v10 settings conversion. Launcher hosting exposes map/variant/cap/name/score, time, team damage/balance, radar, vehicle respawn, grenade and custom-loadout choices. Capacity128 is not a Quest performance promise. Current upstream quit-slot reuse/next-map cleanup fixes included.
- Graphics: exact-size uploads, ordered static geometry mirrors, safe buffer/fence fallbacks; optional Safe geometry for affected devices. Original/Rev2 reports do not isolate a revision cause; Rev1 and a complete three-revision dataset remain unverified.
- Launcher: CE-inspired procedural presentation, scrollable help with161 native settings, per-map headers/fingerprints, network options, default automatic compatible-update checks, upstream protocol status and in-launcher installation path.

## Update behavior

Checks run on launcher open/resume at most every6hours (failed checks can retry after15minutes). Turn them off or check immediately under Versions & updates. Newer-protocol listings offer that same update path. Unknown upstream protocols report that integration is needed. Only this project's reviewed stable edition-matching APK can be offered; compatibility metadata, hash, package, version, minimum SDK, signing certificate and native/VR payload are verified. Current APK/config/touch settings are backed up, then Android asks for installation approval. No runtime component swap, silent uninstall, downgrade, save migration or background game restart. Offline play remains available. Future approved release assets must include generated `compatibility.json`.

## Checks completed before packaging

- Successful VR native+Java and flat native+Java builds; generated offline guide bundled in both.
- Seven targeted suites passed: campaign actor/control ownership; campaign barrier/checkpoint lifecycle; browser/invite parsing and native compatibility; VR pose/finger/weapon math; render-target stability; calibration/PvP parser/config/header fixtures; new input/wire/renderer/update-policy harnesses.
- Production settings sender/receiver tests cover native v11 and legacy CE01/v9/v10 record serialization, local-data tail preservation, fragmented assembly, mixed/invalid lengths and option bounds.
- Touch JNI tests cover quick taps, consumption, finite/bounded motion,250ms expiry, reset generation and32-byte ABI. Layout tests cover screen fractions, edges, dead zones and diagonals. Pure updater policy tests cover tags/flavors/URLs/digests/unknown and newer upstream protocol headers.
- Geometry exact-payload tests exercise512 size/mode combinations under ASAN/UBSAN.128 player-slot predicate cases cover live units, departed users, lobbies and invalid indices.
- Privacy/source review excludes local evidence, game maps, keys and personal metadata. Required third-party notices remain.

## What still requires the owner's devices

No agent installation, game launch, live match or update installation was performed. Check affected v78 orientation, indoor Adreno geometry, phone aiming/editor/cancellation/cutouts, real v9/v10/v11 hosts, public listing acceptance/NAT and repeated match/rejoin. Re-test both Quest/flat co-op peers together: NPC walking/falling, avatars, checkpoints, BSP/mission transitions, death/recovery and reconnect. CE01 serialization is retained, but this candidate has no new paired-device acceptance yet. Existing test14 acceptance is not a substitute.

Keep both peers on this candidate for testing and attach each launch's Download/HaloCE log if a problem occurs. Review logs for private invites before posting. Do not publish these APKs as a new release until the owner approves them.
