# Test31 — private candidate in progress

Target: 1.0.13 / Android code 39. Branch `test31-network-menus-vehicles`.
Based on test30 `fe725aff`. No publication, upload, tag, installation or game
launch is authorized for this candidate. Device results remain the acceptance test.

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
and local rest-state/camera checks. Full suite and both final APK builds remain
outstanding.

## Remaining test31 work

- Complete upstream take/skip review, map hardening and network delta proof.
- Bounded compatible NAT traversal, simulations and actionable failure guidance.
- Menu implementation awaits the owner's scope decision; see TEST31-MENU-PLAN.md.
- Warthog glass setting, left-hand AR counter, VR turret fire and actual-shot reticle.
- Focused regressions, full checks, docs/version identity, serial APK packaging,
  signing/hash verification and device checklist.

## Subsequent interaction work — queued after stable test31

The owner added a separate manual-reload and hand-contact workstream. Complete
test31 first. Then investigate and report a concrete plan and engine limits
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
