# Test15 community refinement work - 2026-10-03

## Delivery contract

Accepted baseline: test14, source 696a7bb, public docs 983a6ae. Work branch: test15-community-refinements. Build both VR and flat APKs for owner testing; DO NOT publish a new release/binaries before subsequent approval. Preserve test14 release and working co-op/body/input. Work and private evidence stay on D:.

## Requested scope

- Read entire Flat2VR announcement thread and relevant upstream sources; retrieve available logs/videos/images directly.
- Investigate upside-down controller/weapon orientation reported on Quest OS v78. Add persisted per-hand pose alignment adjustments and reset with clear in-game help, preserving zero-offset behavior.
- Verify upstream 128-player support and protocol differences; expose regular PvP hosting, map/type/player/name/network choices safely.
- Investigate original/Rev1/Rev2 game data without assuming revision causes graphics faults. Identify available evidence, record fingerprints, distinguish data formats from network protocols.
- Explain every blocked join accurately, retain all compatible listings and population sorting.
- Polish launcher with readable CE-inspired presentation and first-run/settings/tutorial explanations.
- Review regressions/edge cases; focused automated checks, serial builds, exact hashes/signature/source archives; no device acceptance claims without evidence.

## Evidence acquired so far (private media/logs not in repository)

Flat2VR thread 1555959498349215774 read from opening announcement through 15:03 EDT on October 3. Relevant reports:
- v78 user: guns inverted with hand aim, upright with head aim. 20.1-second video reviewed as frames: inverted weapon/hand, stretched scenery/texture artifacts. No v78 log uploaded at that point.
- Another Quest 3 user reports identical graphical faults with original and Rev2 data; screenshot shows stretched terrain strips. Three test14 logs downloaded (two gameplay, one launcher). Logs identify Adreno 740, GLES 3.2, persistent stream buffers; one transparent geometry group overflow. This does NOT establish a disc-revision cause.
- Rev2 user reports successful populated PvP and no graphics fault on Blood Gulch. No confirmed Rev1 report in thread.
- Owner's 13.2-second Quest/flat co-op clip downloaded. Voice feedback attachment identified for review.
- Upstream OpenCE FAQ identifies PAL debug build 2342 as decomp target because of symbols, not an exclusive requirement on player's data. Repos channel points to bnunu/halo-1 and cybersecurity/halo-ce-universal. 128-player playtest instructions use Direct Link after invite; protocol/build audit ongoing.
- Local source already has 128-player and 128-machine limits. Upstream bnunu/halo-ce-universal cloned at c3e55ba8131140838a294eb9fd38f73481d10f4b for read-only comparison.

## Status

Implementation and validation are in progress; see the current checkpoint below. Original pasted requests are retained privately. This work log overrides old test14 publication instructions for the NEXT build only.

## Additive request (2026-10-03, active)

Owner explicitly kept all prior work and added a substantial flat Android pass: in-game draggable touch layout editor with saved layouts, size/opacity/color/scale, sensitivity/dead-zone/response improvements, aspect-ratio safety and defaults; refreshed Discord/upstream audit; integrated build/version display and controlled compatible project updates rather than unsafe replacement with an upstream engine APK. Still deliver both APKs privately for owner testing; no test15 GitHub release.

Implemented so far (uncommitted): controller-local calibration + roll flip/reset; production PvP bootstrap and launcher configuration/public listing; upstream v10 ping wire support/advertisement retaining v9 acceptance; exact-byte stream uploads, per-slot persistence fallback, fence fallback and ordered static mirror writes; optional safe geometry; launcher theme/help/data report/fingerprinting/network preferences. Six focused suites passed, first VR native compile completed. Packaging and device validation not yet done. Flat controls and managed updates are now in progress.

Additional evidence: voice attachment transcribed locally (no external audio upload) describes mostly clean multiplayer geometry with a minor distance-related artifact, not universal campaign success. Co-op clip reviewed: remote VR avatar arm/stance movement visible on flat. Primary upstream cybersecurity/halo-ce-universal pinned at 23b542601f2ca505c7a0143703e92fbda6075e18; latest unarmed-melee/infinite-grenade changes are under review. Ordered mirror-upload fix adapted from Andiweli/HaloCE-Android-AAOS a88f25763b8a51335554ef02e613127ee92677d4, whose report describes nonzero CPU geometry paired with zero GPU pages. This is supporting evidence, not a Quest confirmation. Do not adopt that fork's global 30 FPS/interpolation-off policy in VR.

## Current checkpoint

Implemented in the active candidate:

- Per-controller local pitch/yaw/roll, position, native/grip aim choice, flip180 and reset; zero defaults preserve tracking. Settings changes clear gesture velocity and rearm melee.
- Flat HUD editor: 19 independently movable controls, covered-control selector, individual/global size and opacity, five colors, axis sensitivity, dead zone, floating MOVE, default relative swipe aim, saved/reset/cancel behavior and cutout-aware placement. Input ownership, quick taps, cancellation and stale-motion guards retained/extended.
- Production PvP launcher host bootstrap; map, variant, name, 2-128 player cap, score and v11 match options; public listing is explicit opt-in, private invites supported. Network preferences preserve advanced settings.
- Native v11 match-option layout/gameplay; v10 pings; v9/v10 settings conversion; CE01 legacy campaign serialization. Latest reviewed upstream fixes free quit PvP slots and unload menu maps before another game. See TEST15-UPSTREAM.md for exact pins and limits.
- Renderer exact-byte uploads, per-ring persistence fallback, ordered static mirrors, fence recovery; optional Safe geometry. No global VR30FPS/interpolation change.
- Launcher procedural CE-inspired theme, responsive scrolling, offline player/control/settings guides generated from source, map-header/fingerprint report and controlled signed project APK updater with backups.

Evidence: Flat2VR thread rechecked and still ended with the15:03 logs; upstream event channel reviewed through16:37 and image showed128/128 in an invite. This is upstream evidence, not our candidate's load test. No second verified native directory was found. Event invites are supported without pretending they form a permanent directory. Original/Rev2 reports disagree on graphics by environment; no verified Rev1 report or local three-revision stock dataset. See DATA-COMPATIBILITY.md.

Checks already passed: campaign actors and lifecycle, VR math, stable render targets, browser parser/native version gate, calibration/PvP parser/config/header tests, touch JNI/layout/update-policy tests, v11 and legacy settings assembly/validation, exact-sized geometry writes under ASAN/UBSAN. Java and the VR native build have compiled; final matched packaging is still pending at this checkpoint. The final delivery record/manifest will identify exact source, APK hashes, signatures and completed flavor builds.

Device acceptance remains pending: upside-down-controller calibration on affected firmware, indoor geometry on affected Adreno devices, touch layout/swipe feel and focus/rotation, real v9/v10/v11 joins/public host publication, crowded sessions, repeated match/quit/rejoin and paired Quest/flat campaign regression. No headset/phone game was installed or launched here. Prior test14 acceptance does not certify these candidate changes. APK publication stays on hold.

## Latest additive request: automatic update management

Implemented launcher-start/resume checks (six-hour interval, on by default, optional opt-out), cached visible status, upstream protocol detection from the public primary header, and a newer-protocol server-row update entry. Project release metadata must explicitly describe supported editions/protocols and preserved data before the signed APK can be installed. Unknown upstream versions report integration pending; this never replaces VR/co-op with upstream engine files. Candidate publication remains held. Updater Java compilation and protocol-header parser tests passed after this addition. Release process must upload generated compatibility.json with future approved APKs.

## Build completion

Both final VR and flat builds completed successfully and were preserved separately. Seven targeted suites passed. Both APKs were compacted/aligned/re-signed with exact non-signature payload and signing-certificate equivalence verified. See TEST15-DELIVERY.md for APK hashes and the device test matrix; the package manifest/checksums record the final full source archive. No release publication or device installation.

## Added Android controller pass

The owner added full Xbox-style Android gamepad support before delivery. Prior candidate APK hashes are superseded; final pair must be rebuilt. Retained SDL3/native Xbox mapping, added full-pad readiness detection, flat-only response/trigger/rumble settings, focus neutralization and recycled disconnect handles. Auto/Show/Hide touch policy and controller navigation across launcher dialogs are included. Corrected touch Type/Light mappings against the native default profile. See ANDROID-GAMEPAD.md. Adapter and UI-policy tests pass; hardware controller acceptance remains pending. Preserve all earlier test15 scope and release hold.

## Added campaign capacity investigation

Audited the 128-player transport against campaign identity/lobby/lifecycle, spawning/recovery, scripts/AI, vehicles, checkpoints/BSP and mission progression. Current CE01 cannot support more than two: the barrier validates exactly one remote, and recovery stores four slots despite 128 network indices. No higher stable campaign capacity is established. Retained two-player operation, added clear launcher/browser capacity explanations and saved-listing capacity preservation; known unsupported CE01 capacities cannot be joined. Added production capacity and multi-peer barrier rejection tests. See COOP-PLAYER-LIMITS.md for findings, limits and staged expansion work. This is an investigation result, not a shipped 128-player co-op feature.
