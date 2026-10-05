# Current development state

## Current GitHub latest release: v1.0.6 (test24b APKs)

The owner authorized v1.0.6 as a new Latest release on 2026-10-05. Exact test24b APK bytes use standard `HaloCE-Android-1.0.6.apk` and `HaloCE-Quest-1.0.6.apk` filenames, internal version **1.0.6 / code 32**, plus updater `compatibility.json`. Prior releases are preserved. See [`RELEASE-1.0.6.md`](RELEASE-1.0.6.md) and [`RELEASE-PROVENANCE-1.0.6.md`](RELEASE-PROVENANCE-1.0.6.md).

**Owner device acceptance (2026-10-05):** "everything in the latest build worked great (besides 1st person vehicles)". First-person vehicles stay experimental and opt-in. **Next candidate: test25 (1.0.7 / code 33)**, see [`TEST25-PROGRESS.md`](TEST25-PROGRESS.md): vehicle recentre diagnostics, first-person glass and horizon option, settings rows that fit, Reset Offsets, four reviewed upstream fixes. Upstream OpenCE/DamnationCE are now network 16 (exact match) and cannot play PvP with this project's 11: [`UPSTREAM-REVIEW-2026-10-05.md`](UPSTREAM-REVIEW-2026-10-05.md). Co-op player count: [`COOP-PLAYER-COUNT.md`](COOP-PLAYER-COUNT.md). PC/Steam Frame: [`PC-STEAM-FRAME-FEASIBILITY.md`](PC-STEAM-FRAME-FEASIBILITY.md).

**Campaign co-op is working again per the owner's latest report.** This release includes the campaign host-crash fix and the joining-client cutscene activation/animation fix. It remains two-player; the whole campaign and every device/network combination have not been exhaustively tested.

The released build is test24b (comfort page, configurable smooth/snap turning and vignette, SPV1 status notice) on top of test24 (co-op client cutscene activation, host/join instructions and public listing by default), test23 (Quest button remapping and grenade controls) and test22 (campaign host-crash fix). Detailed records: [`TEST24B-PROGRESS.md`](TEST24B-PROGRESS.md), [`TEST24-PROGRESS.md`](TEST24-PROGRESS.md), [`TEST23-PROGRESS.md`](TEST23-PROGRESS.md), [`TEST22-PROGRESS.md`](TEST22-PROGRESS.md). The earlier hand/IK report is historical, not the active release handoff.

## Historical 1.0.1 withdrawal and original 1.0.0 release notes

The withdrawn 1.0.1 record is `docs/RELEASE-PROVENANCE-1.0.1.md`. The 1.0/code-19 statements below remain historical context; the release status above supersedes them.



The following entries record the earlier release-1.0 state as of 2026-10-03. They are historical and superseded by the test20e / v1.0.2 baseline at the top of this file. Canonical public repository: [moistman42069/HaloCE-Quest-VR](https://github.com/moistman42069/HaloCE-Quest-VR), branch **main**. Release 1.0 advanced main to the complete code and public documentation at that time. The initial test13a import is historical; private identifying metadata remains excluded. Older private Git history remains a backup, not the continuation branch.

## Historical release: 1.0.0 (exact delivered test18 APKs)

The owner stated “go ahead and NOW proceed with the 1.0 release instructions
using these recent apks”. This supersedes the publication hold for the exact
pair in TEST18-DELIVERY.md. Release `v1.0.0` uses professional 1.0 filenames but
preserves **1.0-test18 / code 19** inside both APKs. No rebuild or re-sign occurs.
Public test14 remains unchanged. [Release notes](RELEASE-1.0.0.md),
[exact provenance](RELEASE-PROVENANCE-1.0.0.md).

The runtime includes test17 networking/data fixes plus test18 vehicle-camera map
lifecycle cleanup, headset-based tutorial gaze, explicit vehicle steering and
seat adjustments. **Third Person + Right Hand** are the vehicle defaults;
**Legs + Arms** remains the body default. Prior animation/grip behavior remains.
[Source evidence and tests](TEST18-PROGRESS.md).

All 13 targeted suites, both builds and packaging checks passed. Cache checks:
127 passed, 4 missing-fixture skips. Publication approval is not a new detailed
headset/phone/full-campaign test result; retain the device follow-up checklist.

### Continuation

- Future APKs need code >19 and a consistent semantic version; separate release
  approval is required. Preserve both public releases and their exact assets.
- The preserved code-19 updater can call the 1.0 promotion inconsistent because
  it has the same version code. Documented workaround: test18 users already have
  these binaries. In the next build, handle same-code promotions using version-code
  metadata before offering an update; keep downgrade/signature/hash guards.
- Bundled test18 guide/candidate wording is preserved inside the exact APKs;
  current web docs explain public 1.0 status. A future rebuild regenerates guides.
- Runtime source is `f45e32dd73b15280a5db4e5d4a4b2643f2c28379`; tag source adds
  publication documents only. Historical holds below are superseded for this pair.

## Historical candidate: test17 (basis of 1.0)

Branch `test17-network-data-profiles`, version 1.0-test17/code 18. The owner reports
test16 animations significantly improved and requests preserving native online
melee. Six test16 logs identify two networking defects now addressed: running PvP
hosts rejected by the campaign flag collision, and action-only bit 15 reaching
unit controls. Reviewed upstream departure/rejoin guards and v11 option semantics
are included. Both launchers add managed ISO/extracted data sets, detected build
and fingerprint labels, and explicit ISO/revision compatibility guidance.
[Findings, preserved scope and tests](TEST17-PROGRESS.md),
[data library](GAME-DATA-LIBRARY.md), [delivery](TEST17-DELIVERY.md).
The owner subsequently authorized 1.0 from this baseline; test14 stays available unchanged.

## Prior candidate: test16 (unpublished)

Branch `test16-native-actions` continues the complete final test15 implementation.
Version 1.0-test16/code 17 adds VR Safe geometry defaults/upgrades and native action
arm ownership. Flat defaults to Normal. See [test16 checkpoint](TEST16-PROGRESS.md)
and [candidate delivery](TEST16-DELIVERY.md). The owner supplied test15 normal/Safe
bridge evidence and a weapon-action stretching video. The follow-up confirms
improved action animation but reports the multiplayer faults addressed in test17. Test14 remains the public accepted pair; no new release is authorized.

## Prior candidate: test15 (unpublished)

Campaign capacity was audited: CE01 remains two-player; [findings and expansion requirements](COOP-PLAYER-LIMITS.md).

The added flat Android controller pass is included; see [gamepad support](ANDROID-GAMEPAD.md).

Branch `test15-community-refinements` carries the next VR/flat pair, version 1.0-test15/code 16. See [test15 checkpoint](TEST15-PROGRESS.md) for implementation, evidence, tests and remaining device validation. [Candidate delivery record](TEST15-DELIVERY.md) identifies the new APK pair and completed checks. Test14 remains the accepted public pair. No test15 release publication is authorized before owner testing.

## Accepted release: test14

On 2026-10-03, after receiving the replacement pair, the owner stated "this is it" and explicitly requested these APKs as the latest public release. This lifts the earlier release hold **for the exact delivered test14 pair**. [Release](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/halo-ce-quest-test14).

Both Quest VR and flat Android are `1.0-test14`, code 15, ARM64, built from `696a7bbe9321565d90207042067658cb8814cad1`. Subsequent commits update documentation only. Client NPC control ownership/resting state, one-shot AI animation events, unarmed vehicle-seat replication and campaign pause-menu routing are corrected. Both builds, all five targeted suites and signature/version/integrity/privacy checks passed before delivery. Exact hashes: [release provenance](RELEASE-PROVENANCE.md). The original [delivery record](TEST14-DELIVERY.md) preserves pre-acceptance evidence.

The owner accepted the pair for publication; no detailed new mission/device matrix was supplied. Do not turn that acceptance into a claim that all campaign transitions, ten missions, phones or networks have passed. Preserve the exact APKs; future changes need their own candidate result.

## Historical versions

Test13a VR/code 14 changed the body default to Legs + Arms; flat test13/code 13 retained touch and avatar reception. The initial public release was withdrawn when co-op NPC issues were reported. Test14 replaces both. `SOURCE-IDENTITY.json` describes only the initial public import. Earlier private source history stays private.

## Observed device evidence

The owner reported improved gameplay, working multiplayer/settings/Downloads logs, good room-scale legs and then that Legs + Arms works great. Earlier Quest 3 baseline observations included immersive launch and approximately 72 Hz play. These are specific reports, not an all-device/all-feature certification. The supplied test12 log ended through normal cleanup/exit; footage showed menu overlap and chest/shoulder crowding that motivated test13.

The 2026-10-03 follow-up reports successful Quest/flat co-op connectivity and full VR body movement visible on flat Android. The supplied Quest log identifies **test13**, not test13a, and records avatar negotiation. Footage/report show sliding NPCs and a stuck falling character. This narrows the failure to NPC presentation; it does not establish full campaign/checkpoint acceptance. Private media and logs stay outside Git.

## Current implementation

| Area | Included | Remaining evidence/limits |
| --- | --- | --- |
| Quest render/input | Native OpenXR, tracked headset/Touch, hand aiming, room-scale, scope, menu pointer, vehicle/cinematic options | Other headsets and all performance settings not accepted |
| Body | Four views, inferred full-body rig, room-scale feet, bounded shoulder reach, smooth elbows/twist, local torso hiding | Extreme/cross-body/overhead poses and custom rigs can still clip; no hip/foot trackers |
| Hands | Controller-driven finger poses, smoothing, palm/finger/world and approximate held-gun contact | Not optical hand tracking/full hand rigid-body simulation |
| Grip | Deliberate support grip default, fixed support anchor, first-grip protection, physical/locked weapons and holsters | Paired network physical weapon behavior unverified; off by default online |
| Movement/melee | Offline arm-run sprint and close contact, stock network speed/collision, impact or swing melee | Physical reload deferred; button reload works |
| Settings | Generated pages/dynamic storage, directional stepping, body and graphics options | Custom pause tags may not provide same menu |
| PvP browser | Full bounded feed, population sort then paging, four catalogs, invites/LAN, reviewed v9-v11 compatibility | Only ChupathingyCE preset verified; not retail PC/MCC/Xbox protocol |
| Campaign co-op | Separate host/join/browser/protocol, campaign authority/replication/transitions | Paired session and test14 release accepted; detailed full campaign coverage and public-directory announcement verification remain open |
| Remote avatars | Negotiated render-only snapshots, owner/bounds checks, interpolation/expiry, flat receiver | Owner confirmed VR body movement on flat partner; world skeleton has no separate fingers; old peers stock |
| Flat input | Customizable multi-touch overlay, swipe/fire-drag aim, Xbox-style gamepad settings, lifecycle release | Phone layout/input validation and Type/Light profile labels pending |
| Managed data | ISO/XISO/extracted imports, inbox, cache-build/fingerprint detection, atomic set selection, isolated saves | Exact disc-revision hash matrix and per-server content fingerprints unavailable |
| Logging/content | Per-launch Download/HaloCE logs with fallback; SPV1 original-map recovery | Custom content/dependencies remain experimental |

## Standing follow-up coverage

1. Reproduce reports with exact APK, settings, device, map and log; preserve the delivered binary/source.
2. Paired Quest/Quest and Quest/flat co-op: cinematic, AI/weapon/door behavior, checkpoints, both-dead recovery, BSP, restart/next mission, disconnect/reconnect.
3. Observe replicated VR head/arms/torso/legs and held weapons; check death/respawn and loss fallback. Test supporting PvP host with old/new peers.
4. Exercise flat touch movement+fire+aim, pointer cancellation/focus changes, gamepad coexistence, labels and screen sizes.
5. Diagnose any remaining menu/body/grip regressions from footage; maintain the approved Legs + Arms default and room-scale leg behavior.

Test14 is accepted for public release. Historical TEST9-TEST14 investigation/delivery documents retain their original test-time status; this file and release provenance take precedence. Source/privacy review must exclude personal author emails, workstation paths, signing keys and private evidence from public artifacts. Required third-party attribution remains intact.
