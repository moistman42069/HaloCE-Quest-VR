# Agent and contributor continuation

## Current GitHub latest release: v1.0.3 (test21b APKs)

The owner authorized publishing the signed test21b APK bytes as the new GitHub Latest under semantic tag `v1.0.3`, with standard 1.0.3 asset names so GitHub sorts it correctly and the updater resolves the files. APK internals remain version name **1.0.2 / code 27**; code 27 installs over prior v1.0.2/code 25. Both earlier releases (`v1.0.2` and `halo-ce-quest-test21b`) remain intact. This is not headset acceptance: no phone/headset session was performed for test21b. See `docs/RELEASE-1.0.3.md`, `docs/RELEASE-PROVENANCE-1.0.3.md` and the preserved `docs/RELEASE-PROVENANCE-TEST21B.md`.

**Active candidate: test28 (version 1.0.10 / code 36): test27 plus the fix for the halt on joining an OpenCE co-op game in progress (camera squared; APKs built --release as OpenCE's), co-op hosts of 2-128 players as OpenCE's Server Setup, optional gyro aim on phones. See docs/TEST28-PROGRESS.md, docs/TEST28-DELIVERY.md; not released. A Quest on 1.0.9 joined and loaded an OpenCE co-op game (first cross-play evidence); play after the load not yet confirmed.** Before it: test27 (version 1.0.9 / code 35): OpenCE build 138's netcode (network 20), its co-op, with OpenCE players; this app's CE01/CE02 co-op and v9-11 retired. See docs/TEST27-PROGRESS.md, docs/OPENCE-COOP-COMPATIBILITY.md, docs/TEST27-DELIVERY.md. Before it: test26 (1.0.8 / code 34) and test25 (1.0.7 / code 33), delivered, not released (GitHub Latest remains v1.0.6). Released and accepted on the owner's devices: v1.0.6 (test24b, code 32), except first-person vehicles (experimental). Notes: docs/UPSTREAM-REVIEW-2026-10-05.md (network 11 vs upstream 16), docs/COOP-PLAYER-COUNT.md (co-op is two players), docs/PC-STEAM-FRAME-FEASIBILITY.md.

**Published latest build: v1.0.3 (test21b runtime, internal 1.0.2 / code 27; test21 was code 26), branch `test21-hands-body`; see `docs/TEST21B-PROGRESS.md`, `docs/TEST21B-DELIVERY.md` and `docs/TEST21-PROGRESS.md`. It still awaits headset tests.** **Current active handoff (2026-10-04):** read `docs/ACTIVE-WORK-CHECKPOINT.md` and `docs/REPORT-2026-10-04-HANDS-IK-REGRESSION.md` before starting new work. The owner reports cut-off/floating hands returning and arm IK not following body turns. Do not presume v1.0.2 caused this: supplied logs include test20d and test20e runtime banners, while only the latter's launcher log explicitly confirms installed code 25; verify installed APK hash/version/source. Keep all raw logs/video private. The release is published; preserve the regression investigation and do not claim test21b headset acceptance until the owner reports results.

## Historical 1.0.1 and 1.0 notes

The withdrawn 1.0.1 record is `docs/RELEASE-PROVENANCE-1.0.1.md`. The 1.0/code-19 statements below remain historical context; the release status above supersedes them.



Canonical repository: `moistman42069/HaloCE-Quest-VR`, default branch `main`.
Read docs/CURRENT-STATE.md, docs/RELEASE-PROVENANCE-1.0.0.md, CONTRIBUTING.md,
and relevant player/architecture/protocol documents before changes.

Current public baseline: **release 1.0**, tag `v1.0.0`. The owner explicitly
re-authorized publication using the exact delivered test18 APKs. This supersedes
the test18 publication hold. Both APKs retain **1.0-test18 / code 19** internally;
only release filenames change. Do not rebuild, re-sign or replace them. Public
test14 stays unchanged. See RELEASE-PROVENANCE-1.0.0.md for hashes/build source.
Publication authorization is not a newly reported headset/campaign playthrough.
Future APK updates must use code >19 and need separate publication approval.

Preserve accepted VR animation handoff, Legs + Arms, room-scale legs, fingers,
contact/grip, online native melee, Safe VR geometry and Normal flat geometry.
Keep the flat touch/controller, co-op/NPC/avatar, logging, browser and managed
set implementations. Co-op is two-player for concrete lifecycle/recovery reasons;
128 PvP slots do not establish 128-player campaign or Quest hosting performance.
Do not invent disc-revision labels, verified content matching, directories or
headset acceptance. Record code, automated checks and device evidence separately.

Keep all new local work/builds on D: on the maintainer's Windows machine. Other
systems use a writable clone. Check status and read continuation docs first.
Build VR/flat serially; native staging is shared. Preserve each APK before a
flavor switch. No game install/launch or unrelated upstream push without a
corresponding instruction. Use GitHub noreply authors; never publish private
history, personal paths/emails, keys, game assets, raw logs/media or invitations.
Required third-party license notices remain intact.

Every future release must have self-contained notes in the nine-section order
in docs/RELEASE-TEMPLATE.md, installation and APK download links first. Upload
only the two APKs plus updater compatibility metadata unless another asset has
a concrete purpose. Preserve existing releases. Future version names, increasing Android codes, stable tags, APK names and
UpdatePolicy must agree. The exact-byte test18-to-1.0 promotion is a documented
owner-directed exception, including the same-code updater message.
Older test updaters require one manual install of 1.0; do not disguise that
limitation with fake compatibility metadata or duplicate legacy releases.
