# Current development state

## Current published release: v1.0.16 (2026-10-07)

Release **Halo CE Quest VR + Android 1.0.16** is published as Latest from
OpenCE Build 148 / network 23, version code 45. The release includes Android
and Quest APKs plus updater metadata; prior releases remain intact and the
GitHub About description is unchanged. Release notes, hashes and build
provenance are in [RELEASE-1.0.16.md](RELEASE-1.0.16.md) and
[RELEASE-PROVENANCE-1.0.16.md](RELEASE-PROVENANCE-1.0.16.md).

The exact v1.0.16 APK pair has no recorded Android or Quest device session.
Publication does not imply device acceptance. The most recent owner-confirmed
platform baselines remain Test31b VR and Test31c Android; Test35 carries those
settings/touch baselines forward. Continue using logs and device reports to
validate new runtime behavior.

## Test35 implementation summary (now released)

Test35 targets Android/Quest version 1.0.16/code45. It ports applicable
OpenCE Build148 changes while retaining network23: tag validation corrects
negative/NaN particle collision radii and widths in particle, particle-system,
contrail, weather, effect and breakable-surface records; point physics also
clamps any computed invalid radius before its assertion and reports it once.
The native halt screen identifies the platform/build and puts recent error
messages first. Build148 does not change network compatibility. Test34's CE
cache/BSP validation, map identity, capacity/co-op/camera fixes, server-row
pointer selection, scope diagnostics/alignment and the owner-accepted Android
touch / VR settings baselines remain. See [TEST35-PROGRESS.md](TEST35-PROGRESS.md),
[TEST35-UPSTREAM-INTEGRATION.md](TEST35-UPSTREAM-INTEGRATION.md), and
[TEST35-DELIVERY.md](TEST35-DELIVERY.md) for the engineering record.

SPV1 remains experimental. Its listed map files exceed 128 MiB but fit the
current Custom Edition parser's 384 MiB ordinary / 576 MiB upgraded file caps;
the launcher explains that size alone does not establish gameplay support.

Preserve the owner-confirmed baselines: Test31b Quest VR settings and Test31c
flat Android touch/gameplay. The prior v1.0.12 release remains archived at
network 21; it is not compatible with v1.0.16/network 23.

## Latest owner-accepted private result: Test31c Android; Test31b VR

On 2026-10-07 the owner reports the mobile port works great and requests leaving
its gameplay/touch implementation as-is. This applies to Test31c/code41,
runtime `173708ec068993a7256c7f0431b5d001ba46f8e6`; exact artifacts and hashes:
[TEST31C-DELIVERY.md](TEST31C-DELIVERY.md). The prior accepted VR settings design
remains a standing preference. This is not blanket acceptance of all VR vehicle
features: passenger tracking, recentering, turret controls and HUD gestures are
the next requested refinements. See [TEST32-PROGRESS.md](TEST32-PROGRESS.md).
The older pending Android entries below are superseded by this owner result.


## Private device result: Test31b VR accepted; Android UI correction pending

On 2026-10-07 the owner reported that Test31b **VR works great**, and specifically
requested that its **new VR settings design be preserved as a standing preference**.
Accepted Quest artifact: `HaloCE-Quest-test31b.apk`, 1.0.13/code40, runtime
`3399023ae8b7d0ec57e8c42c68c40ab6c33346af`, SHA-256
`d391f40a9bce4d127d5f91ceb34c84c96011ba5366db4cb99224d80c274de020`.
This is the owner's reported acceptance, not a claim that every feature was
individually tested. Preserve this APK and VR implementation.

The same candidate's Android UI is **not accepted**: its menu transition
replaced the familiar circular touch controls with a rectangular strip.
`test31c-flat-ui` restores that presentation while retaining direct menu taps
and making optional free look hide only LOOK. See `TEST31C-PROGRESS.md`.
Public GitHub v1.0.12 remains unchanged.

Follow-up before Test31c packaging: owner reports Warthog HOG GLASS does not
work and requests that specific VR fix plus both replacement APKs. Code40
remains the accepted VR comparison baseline, with this glass issue now noted.
Test31c/code41 device acceptance remains pending for both editions.

## Historical public release: v1.0.12 (test30 APKs)

**Published as Latest on 2026-10-07** from `D:\HaloQuest\builds\test30-20261007-v1.0.12`. Version **1.0.12 / code 38**, OpenCE Build 144/network 21. This incremental release fixes Quest face-button behavior in VR menus and adds an optional remembered name for campaign co-op hosts; prior release features remain. See [`RELEASE-1.0.12.md`](RELEASE-1.0.12.md), [`RELEASE-PROVENANCE-1.0.12.md`](RELEASE-PROVENANCE-1.0.12.md), and [`TEST30-DELIVERY.md`](TEST30-DELIVERY.md). Previous releases remain intact; the GitHub About description was not changed.

No device-session result for the exact v1.0.12 APK pair was supplied before publication. Automated tests and release hashes are recorded in test30 docs; they do not substitute for device acceptance. Network version remains 21, so v1.0.11 peers remain compatible. The 128-player capacity and resolution above 100% are not performance-certified.

The prior public release is v1.0.11. Historical progress and older release notes below are retained as records, not current compatibility guidance.

## Current release: test30 (1.0.12 / code 38)

**Published as Latest:** test30, version 1.0.12 / code 38, branch `test30-profiles-coopname`, on v1.0.11. The owner confirmed the prior build was in good shape and reported that X did nothing in the VR main menu when deleting a profile. Menus now map Quest A/X/Y to the on-screen labels, while B goes back once; gameplay bindings are unchanged. Campaign hosting has an optional remembered server name. See [TEST30-PROGRESS.md](TEST30-PROGRESS.md), [TEST30-DELIVERY.md](TEST30-DELIVERY.md), and [RELEASE-PROVENANCE-1.0.12.md](RELEASE-PROVENANCE-1.0.12.md). No device session on this exact pair is recorded yet.

## Post-release validation: test30

Validate VR menu profile deletion and navigation, ensure gameplay controls are unchanged, test named and unnamed co-op hosts and browser display, and check Android/Quest gameplay. Preserve logs from each peer for connection/desync/crash reports. See [TEST30-DELIVERY.md](TEST30-DELIVERY.md).

## Historical progress

The following entries preserve the state before test28. First-person vehicles remain experimental and opt-in. Test27 (1.0.9) introduced OpenCE Build 138's netcode and co-op at network 20; test26 and earlier records document the retired project-owned protocol. See [`TEST28-PROGRESS.md`](TEST28-PROGRESS.md), [`OPENCE-COOP-COMPATIBILITY.md`](OPENCE-COOP-COMPATIBILITY.md), and [`COOP-PLAYER-COUNT.md`](COOP-PLAYER-COUNT.md) for current details. The older OpenCE network 16 / project network 11 comparison below is historical and superseded.

**Historical test22–test24b campaign status:** co-op used the project's two-player protocol. This was replaced by OpenCE-native co-op in test27; use the current status at the top of this file.

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
