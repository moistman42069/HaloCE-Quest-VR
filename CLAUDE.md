# Agent and contributor continuation

## Active private work / packaging hold (2026-10-07)

Read `docs/ACTIVE-WORK-CHECKPOINT.md` and `docs/TEST31-PROGRESS.md` first.
The current branch is `test31-network-menus-vehicles`; the target is
1.0.13/code39. **Latest owner override:** finish and validate the full OpenCE
menus, turret fixes, Warthog window setting and upstream/network upgrade, then
package the Quest and flat APKs for testing BEFORE the manual reload/hand
contact and world/NPC interaction phase. Those later requirements remain queued
and must not be marked complete. Track all requirements in
`docs/VR-INTERACTION-REQUIREMENTS.md`. The owner now requires ALL OpenCE in-game
menu functionality, superseding the narrower browser/setup approval; see
`docs/TEST31-MENU-PLAN.md`. No publication, push, tag,
installation or game launch is authorized. Public release pointers below are
historical/public state, not permission to release this work.

## Current GitHub latest release: v1.0.12 (test30 APKs)

**Published release: test30 (version 1.0.12 / code 38),** branch `test30-profiles-coopname`, on v1.0.11. Quest A/X/Y now match the button labels in VR menus (X deletes a profile; B backs out once), with gameplay mappings unchanged. Campaign hosting accepts an optional remembered server name. The network remains OpenCE Build 144 / version 21. The exact APK pair has no recorded device session at publication. See `docs/RELEASE-1.0.12.md`, `docs/RELEASE-PROVENANCE-1.0.12.md`, `docs/TEST30-PROGRESS.md` and `docs/TEST30-DELIVERY.md`.

**Published release: test29 (version 1.0.11 / code 37).** OpenCE Build 144/network 21, HUD tap and wrist-HUD refinements, two-hand movement alignment, glasses FOV and higher resolution options. The exact v1.0.11 APK pair had no owner device-session validation at publication; the owner-confirmed co-op result applies to v1.0.10/network 20. Preserve all prior releases and do not alter the repository About description. See `docs/RELEASE-1.0.11.md`, `docs/RELEASE-PROVENANCE-1.0.11.md`, `docs/TEST29-PROGRESS.md`, and `docs/OPENCE-COOP-COMPATIBILITY.md`.

**Published release: test28 (version 1.0.10 / code 36).** The user supplied `D:\HaloQuest\builds\test28-20261006-v1.0.10` and reports campaign co-op works well in testing. Test28 uses OpenCE Build 138/network 20, fixes the join-in-progress camera halt, offers co-op lobby sizes up to 128, and adds optional phone gyro aiming. High-count performance and gyro behavior were not reported as tested. See `docs/RELEASE-1.0.10.md`, `docs/RELEASE-PROVENANCE-1.0.10.md`, `docs/TEST28-PROGRESS.md` and `docs/OPENCE-COOP-COMPATIBILITY.md`. The release is Latest at https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.10. Preserve all prior releases and do not alter the repository About description.

**Published from candidate:** test29, version 1.0.11 / code 37, branch `test29-opence-144`, built on v1.0.10:
- OpenCE build 144 netcode (network 21). Current OpenCE co-op and multiplayer games are on 21, which 1.0.10 cannot join.
- The HUD head tap must now be held by the temple for a moment, so a hand passing by no longer hides the HUD.
- New HUD rows: HUD Shown/Hidden and Head Tap.
- The wrist HUD sits on the wrist and can be moved and resized.
- MOVE WITH a hand follows the gun while both hands hold it.
- [Willem Horak's PR #1](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1) contributes the glasses FOV option and resolution steps up to 200%; defaults are as in 1.0.10.

See [TEST29-PROGRESS.md](docs/TEST29-PROGRESS.md) and [TEST29-DELIVERY.md](docs/TEST29-DELIVERY.md).

Test27 (version 1.0.9 / code 35) integrated OpenCE build 138's netcode (network 20) and co-op; project CE01/CE02 and network 9–11 are retired. Test26 (1.0.8 / code 34) and earlier co-op reports are historical. v1.0.6 (test24b, code 32) is the preceding public release.

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
