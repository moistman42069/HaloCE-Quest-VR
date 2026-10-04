# Test19 checkpoint: multiplayer crash, native browser, updater

Private candidate branch: `test19-network-browser`. Public 1.0/test18 and test14
remain unchanged. No new release approval. Working version: 1.0.1 / Android code
20; both final APKs built and package preflight verified. All work remains on D: on the maintainer's
machine. Read CURRENT-STATE and CLAUDE before continuing.

## Current implementation (2026-10-03)

- One supplied test18 log joins a network-v11 in-progress host with 37 players on
  Chiron TL-34 (`putput`), then hits `objects.c:369` (`cluster_index != NONE`).
  Exact shipped ELF stack resolves to `objects_update`. This is a PVS/object
  lifecycle assertion after a successful join, not a rejected network version.
- `object_activate` now honors the existing auto-deactivation rule for connected
  objects lacking a cluster. Reconnect deactivates out-of-PVS automatic objects;
  the PVS consumer bounds-checks and logs/deactivates an invalid active replica
  before any bit-vector access, retaining host ownership instead of deleting it.
  The log lacks an object ID, so the particular replicated object/producer that
  triggered the report is not proven. Detach/placement paths can violate the old
  invariant; focused tests exercise the recovered state. Headset reproduction
  remains required; do not claim the original server is validated.
- Upstream build-84 (`3304965653692fc2f4cbea84f1bea2bb7d0f2bdd`), including
  `c04765d7f49f49bda706a258826134ef41c566ca`, supplies signed MQTT public lobby
  discovery, Ed25519/X25519 binding and Monocypher notices. Campaign map hashing
  and the project's publisher invite API are retained. Its wholesale PC menu
  replacement is not imported. The existing System Link menu lists native public
  games and LAN hosts, population-first, with seven games per page, previous,
  next and refresh. It resolves the selected host to a real native advertisement
  before the existing protocol gate/join. Selection snapshots do not jump when
  population changes; refresh updates them. Pending joins cancel on navigation,
  selection movement or exit, and time out after 30 seconds. Native public
  listing remains opt-in; launcher PUBLIC applies per PvP session; CE01 campaign
  is excluded from the public PvP catalog. Existing launcher directories stay.
- Updater authenticates metadata before comparing Android version codes.
  Same-code release promotion and older public builds report already current or
  newer installed, rather than inconsistent metadata. Hash, edition, certificate,
  migration, SDK and downgrade guards remain. Project repository unchanged.
- Separate Official upstream section lists integrity-verified official Android,
  Windows and Linux ZIPs and exports them to Download/HaloCE/Upstream. It does not
  install them or replace the mod engine. Android package/signature conflicts and
  missing project integrations are explained before download.

## Evidence and verification so far

Six supplied test18 logs reviewed privately. One fatal cluster assertion above.
A second v11 host joined normally. Reliable-endpoint messages occur immediately
following the user's Back/server teardown; no independent runtime crash there.
One log rejects a persistent save checksum; no save file or corruption producer
is supplied. Do not bypass checksum validation or erase saves to hide that error.
No raw logs, invites, Discord DMs, media or private paths belong in public source.

Focused test19 checks pass: activation matrix; 256 browser results/page coverage,
population sorting, stable selection, exact host resolution, single deferred join,
cancel/timeout and refresh; version-code comparisons. Upstream RFC8032 vectors,
key binding, tampering, staleness, wrong slots and tombstones pass with ASan in a
host harness (platform include replaced only). Actual ILP32 layout compiles in the
APK build. First VR compile passed; subsequent UI polish and full regression run
are in progress. Flat and final source-identified pair still pending.

## Review scope (completed for the available reports)

Review the Halo decomp thread in Flat2VR and **all available DMs with the specified tester** for
reports. Read-only review is authorized; sending messages is not. Track every
distinct issue, including build/version context, duplicates, fixed historical
reports, evidence-backed fixes and unresolved reproduction needs. Keep private
message excerpts/evidence in the ignored private work folder, not Git. Carry all
current multiplayer/updater/browser work forward. Do not package until the review
and applicable fixes are complete. Then build both editions, rerun regressions,
update player/continuation docs and provide private APKs for owner testing.

## Community/media follow-through

Read [TEST19-COMMUNITY-REVIEW.md](TEST19-COMMUNITY-REVIEW.md) for complete distinct
report dispositions, the latest two-log/video correlation and primary sources.
Both latest videos plus the older orientation video were inspected. Current
changes add native-ray/world-point VR reticle placement, renderer VAO restoration,
ordered transient Safe uploads, iterative deep XDVDFS import, clearer import
errors and co-op help. Preserve accepted animation/grip/body/vehicle behavior.
The renderer workaround remains a hypothesis pending a headset reproduction.

The final 15-suite regression runner passes, including 680 reticle inverse
transforms, invalid-value rejection, compositor VAO restoration and ISO
layouts/deep-tree/large-offset/rejection cases. Cache-format checks: 127 passed, 4 absent real-fixture skips. Interim VR
compile passed, followed by both clean final builds and package preflight.
Final APK identity/hashes and follow-up cases are recorded in TEST19-DELIVERY.md. No device installation, live co-op match or public release occurred.

## Delivery / next action

Both flavors and package preflight passed from `ff93009e`. A final package review
found text encoding damage in bundled third-party notices and continuation docs.
Those texts were corrected without changing runtime code. Rebuild the pair from
the clean correction commit, then record its final hashes in TEST19-DELIVERY.md.
Use `--label test19 --version-name 1.0.1`. Preserve old preflight files privately;
do not deliver their superseded hashes. Device feedback and new publication
approval remain required.
