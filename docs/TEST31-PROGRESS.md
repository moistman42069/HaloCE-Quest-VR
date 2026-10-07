# Test31 — private candidate in progress

Target: 1.0.13 / Android code 39. Branch `test31-network-menus-vehicles`.
Based on test30 `fe725aff`. No publication, upload, tag, installation or game
launch is authorized for this candidate. Device results remain the acceptance test.

## Packaging gate (owner clarification, 2026-10-07)

**No packaging until every item across all three task prompts has been worked
through.** Finish test31, manual reload/finger/palm interaction, then world
interaction/NPC handling in order, validating available source/build behavior
between subsystems. A test31-only APK pair is no longer the delivery plan.
The indexed follow-on requirements and dependencies are in
[VR-INTERACTION-REQUIREMENTS.md](VR-INTERACTION-REQUIREMENTS.md). A queued or
acknowledged item is not complete. Eventual device results are still required
for acceptance, but are not a reason to skip the remaining pre-package work.

## Current evidence and outstanding work

| Work | Current status | Remaining proof / action |
|---|---|---|
| Build 145 / exact network 22 | Integrated; three-way delta audit; 28 files identical and 8 preserve app-only deltas | Real mixed OpenCE/Quest/Android sessions; no cross-play claim yet |
| CE namespace / missing-map preflight | Implemented, compiled and regression checked | Device missing-map dialog and CE/PAL/.yelo regression checks |
| Portable script/tag/resource bounds | Integrated selected upstream fixes; range helper tested with sanitizers | Broad tag validator and desktop CE loader explicitly deferred in upstream decisions |
| LTE / VPN traversal | Bounded standard pings, current IP+port STUN classification and failure guidance implemented | Real LTE/VPN tests; random/unadvertised endpoints remain unsupported without relay design |
| OpenCE menus | Proposal written; owner scope question pending | Required explicit scope go-ahead, implementation and full input/navigation checks |
| First-person Warthog glass | Persisted setting; prior hidden default; relevant view only | Headset visibility checks for Warthog variants and other views |
| Left-hand AR display | Per-part winding uses actual vertex influences; bounded CPU work | Headset visibility/orientation/counter updates, right-hand and other-weapon checks |
| Seated VR trigger | Physical empty-hand suppression no longer blocks seated fire | Actual mounted/stationary turrets and primary/secondary input checks |
| Turret reticle | Native muzzle/aim preview without writing aim-assist targeting state | Both VR and Xbox layouts; shot alignment and frame-time checks |
| Manual reload / hand contact | All M1–M29 recorded; not implemented | Investigation/plan after baseline and approved menus, then sequential work |
| World interaction / NPCs | All W1–W66 recorded; not implemented | Prior interaction dependencies, investigation/plan, sequential viability/implementation work |
| Version / guides / packaging identity | Pending final content | Update to 1.0.13/code39, guides, package checks only after scope is resolved |

All 32 suites in `tools/run-quest-checks.py` passed during the current pass;
cache-format pytest: **127 passed, 4 skipped**. VR and flat guest release
compile/link checks and the Android VR host library compiled successfully.
Build configuration reports no PGO because installed clang 18 does not match
the clang 22 profiles. No performance acceptance is inferred from compilation.
The subsequent STUN refresh review added an actual packet-parser test covering
same-response classification, XOR/legacy replies, wrong source/transaction,
truncation, multiple egress IPs and repeated route changes; focused test31 passes.
Final full checks must run again after all source changes are complete.

No test31 APKs have been packaged, signed, installed or published.

## Network target and integration

On 2026-10-07 the fetched OpenCE **build-145** tag and main both resolve to
`4e8ed2f196e0edd1f2830a4de9841686aabbf466`, network **22**. The earlier
handoff's untagged-main warning is superseded by that tag. The actual browser
parser accepted 3 co-op and 5 multiplayer listings from the saved directory
snapshot at version 22 (29 total listings). These counts are transient and
are not connection/session evidence.

Three-way staging compares build 144 `76b1898e` to build 145 and the test30
tree. Network 22's changed client manager is merged, including missing-map
preflight. CE map selection advertises `custom_maps\name`; a missing map in
that namespace cannot fall through to an Xbox map with the same basename.
Missing-map text uses upstream's deferred in-game error dialog and wrapping,
adapted to the launcher's active game-set folder. The app's existing CE/.yelo
loader, PAL conversion and co-op pause handling remain in place.

Initial evidence: the VR release guest compiles and links. The new test31
suite pins 28 unchanged networking files to upstream build 145 SHA-256 values.
The browser suite passes against the downloaded feed. Earlier test29 protocol
checks now allow the exact current version while preserving their file hashes
and local rest-state/camera checks. The later validation results are above;
final APK builds remain held by the owner's all-tasks packaging gate.

## Test31 completion order

- Complete independent source review of current fixes and resolve its findings.
- Menu implementation awaits the owner's scope decision; see TEST31-MENU-PLAN.md.
- Finish approved menu scope, focused regressions, full checks and guides.
- Work through both added interaction prompts before packaging, then finalize
  version identity, signing/hash verification and the combined device checklist.

## Subsequent interaction work — queued after stable test31

The owner added a separate manual-reload and hand-contact workstream. Complete
test31 source work and available validation first, without packaging. Then investigate and report a concrete plan and engine limits
before committing to architecture changes. Manual reload must default OFF and
retain classic reload fallback. Start with authentic AR magazine geometry;
expand to pistol only after the first weapon is sound. Cover grip-only left
shoulder AND hip retrieval, both weapon hands, spatial/oriented insertion,
magazine removal, charging components, bounded object lifetime, distinct
haptics, and real engine ammo with cancellation/death/switch/vehicle/pause/
checkpoint/network/level reset safety. No visual-only ammo or duplication.

The related hand work requires continuous independent finger contact, joint
and palm probes, bounded visual hand compliance, contact/release hysteresis,
held-object filtering and poses, stable support-hand interaction priorities,
subtle contact haptics, opt-in diagnostics, and a measured Quest CPU budget.
Investigate current reload/ammo/model-node/animation, hand/grab, collision,
haptic, two-hand and replication paths before selecting the architecture.
Automated logic coverage and the owner's detailed physical checklist are
required; neither substitutes for device testing. The complete request is
preserved privately with the test31 work records.
