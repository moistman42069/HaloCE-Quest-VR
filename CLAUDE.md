# Agent and contributor continuation

## Current GitHub latest release: test21b (APK 1.0.2 / code 27)

The owner authorized publishing the exact test21b APK pair as the new GitHub Latest release under `halo-ce-quest-test21b`. APK version name remains **1.0.2**, Android version code is **27**; the previous v1.0.2/code-25 release and assets remain unchanged. These signed artifacts install over code 25. This authorization is not headset acceptance: no phone/headset session was performed for test21b. See `docs/RELEASE-TEST21B.md` and `docs/RELEASE-PROVENANCE-TEST21B.md`; earlier release provenance is preserved.

**Published latest build: test21b (1.0.2 / code 27; test21 was code 26), branch `test21-hands-body`; see `docs/TEST21B-PROGRESS.md`, `docs/TEST21B-DELIVERY.md` and `docs/TEST21-PROGRESS.md`. It still awaits headset tests.** **Current active handoff (2026-10-04):** read `docs/ACTIVE-WORK-CHECKPOINT.md` and `docs/REPORT-2026-10-04-HANDS-IK-REGRESSION.md` before starting new work. The owner reports cut-off/floating hands returning and arm IK not following body turns. Do not presume v1.0.2 caused this: supplied logs include test20d and test20e runtime banners, while only the latter's launcher log explicitly confirms installed code 25; verify installed APK hash/version/source. Keep all raw logs/video private. The release is published; preserve the regression investigation and do not claim test21b headset acceptance until the owner reports results.

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
