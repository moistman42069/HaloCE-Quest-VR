# Agent and contributor continuation

## Current public baseline: 1.0 — 1.0.1 withdrawn (2026-10-03)

The owner **deleted the v1.0.1 GitHub release** because its Quest VR build had a severe performance regression. Its source (runtime `bc1f04465f68e3b14f1bf7de306854ae8cb36dc1`) remains on `main` but is **not an accepted or working baseline**; never republish it. The current public release is **v1.0.0** (exact test18 APKs, 1.0-test18 / code 19). Preserve v1.0.0 and test14 unchanged. 1.0.1 installs carry code 20, so every future APK needs code >20; never offer v1.0.0 to them as an update.

Active continuation: `docs/TEST20-PROGRESS.md` (measured regression, cause, fix, armed/unarmed calibration finding, status table) and `docs/TEST20E-PROGRESS.md` / `docs/TEST20E-DELIVERY.md` (current candidate **test20e, 1.0.2 / code 25**: Quest/Android multiplayer parity audit, join-stage diagnostics and parity guards, on top of test20d's gun anchoring, left-handed controls and simplified settings — `docs/TEST20D-PROGRESS.md`; supersedes test20d code 24, test20c code 23 — see `docs/TEST20C-PROGRESS.md` for the hand/gun calibration split — test20b code 22 and test20 code 21). Performance fix confirmed on device with test20b. Private candidates; publication needs explicit owner approval after device testing. Unresolved test19 device cases remain in `docs/TEST19-COMMUNITY-REVIEW.md`.

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
