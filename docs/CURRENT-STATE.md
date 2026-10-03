# Current development state

Updated 2026-10-03. Canonical public repository: [moistman42069/HaloCE-Quest-VR](https://github.com/moistman42069/HaloCE-Quest-VR), branch **main**. Main contains complete test14 runtime source plus current player/project documentation. The initial test13a import is historical; private identifying metadata remains excluded. Older private Git history remains a backup, not the continuation branch.

## Active candidate: test16 (unpublished)

Branch `test16-native-actions` continues the complete final test15 implementation.
Version 1.0-test16/code 17 adds VR Safe geometry defaults/upgrades and native action
arm ownership. Flat defaults to Normal. See [test16 checkpoint](TEST16-PROGRESS.md)
and [candidate delivery](TEST16-DELIVERY.md). The owner supplied test15 normal/Safe
bridge evidence and a weapon-action stretching video; test16 runtime acceptance
is pending. Test14 remains the public accepted pair; no new release is authorized.

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
| PvP browser | Full bounded feed, population sort then paging, four catalogs, invites/LAN, v9/v10 compatibility | Only ChupathingyCE preset verified; not retail PC/MCC/Xbox protocol |
| Campaign co-op | Separate host/join/browser/protocol, campaign authority/replication/transitions | Paired session and test14 release accepted; detailed full campaign coverage and public-directory announcement verification remain open |
| Remote avatars | Negotiated render-only snapshots, owner/bounds checks, interpolation/expiry, flat receiver | Owner confirmed VR body movement on flat partner; world skeleton has no separate fingers; old peers stock |
| Flat input | Multi-touch overlay, fire-drag aim, gamepad coexistence, lifecycle release | Phone layout/input validation and Type/Light profile labels pending |
| Logging/content | Per-launch Download/HaloCE logs with fallback; SPV1 original-map recovery | Custom content/dependencies remain experimental |

## Standing follow-up coverage

1. Reproduce reports with exact APK, settings, device, map and log; preserve the delivered binary/source.
2. Paired Quest/Quest and Quest/flat co-op: cinematic, AI/weapon/door behavior, checkpoints, both-dead recovery, BSP, restart/next mission, disconnect/reconnect.
3. Observe replicated VR head/arms/torso/legs and held weapons; check death/respawn and loss fallback. Test supporting PvP host with old/new peers.
4. Exercise flat touch movement+fire+aim, pointer cancellation/focus changes, gamepad coexistence, labels and screen sizes.
5. Diagnose any remaining menu/body/grip regressions from footage; maintain the approved Legs + Arms default and room-scale leg behavior.

Test14 is accepted for public release. Historical TEST9-TEST14 investigation/delivery documents retain their original test-time status; this file and release provenance take precedence. Source/privacy review must exclude personal author emails, workstation paths, signing keys and private evidence from public artifacts. Required third-party attribution remains intact.
