# Agent and contributor continuation

The canonical repository is `moistman42069/HaloCE-Quest-VR`, default branch `main`.
Read `docs/CURRENT-STATE.md`, `docs/RELEASE-PROVENANCE.md`, `CONTRIBUTING.md`
and the relevant player/architecture/protocol documents before code changes.

Current accepted release pair: Quest VR and flat Android test14 (version code 15),
packaged from 696a7bbe9321565d90207042067658cb8814cad1; see docs/TEST14-DELIVERY.md.
Legs + Arms remains the VR default. Public main contains the full current source.
Historical TEST* files are dated evidence, not current instructions. Earlier
private history is retained as a backup and must not be pushed publicly.

Preserve working room-scale legs, grip/fingers/contact, logs, menus, touch,
browser and campaign/avatar implementations. The owner confirmed Quest-to-flat VR body movement on 2026-10-03; co-op NPC
walking/falling presentation failed on the earlier build. Test14 fixes were subsequently accepted for release; a full campaign playthrough is not documented. Physical reload remains deferred.
Record implementation, build checks and device evidence separately.

Keep all new local work/builds on D: on the maintainer's Windows machine; use a
writable clone on other systems. Check status/branch before edits. Build VR and
flat serially because native staging is shared; preserve each APK before switching.
Do not publish game assets, keys, private logs/invites, original source archives
containing personal paths, or commit emails. Use a GitHub noreply author.

On 2026-10-03 the owner accepted the delivered test14 pair and explicitly requested
publication as the latest public release. That supersedes the earlier co-op testing
hold for this exact pair. Preserve its APK/source hashes; do not rebuild or substitute
artifacts under the same tag. Future candidates require their own test result and
publication instruction. Installation, game launch and unrelated upstream pushes
require corresponding user instructions. Keep source/delivery
provenance exact and update CURRENT-STATE after substantive work. For runtime
bugs, obtain/read the actual reported build's log before theorizing.
