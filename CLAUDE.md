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

Active work: test15-community-refinements, see docs/TEST15-PROGRESS.md. Preserve the test14 public release; test15 APKs are private testing candidates until the owner approves publication. New controller alignment, touch layout, protocol adapters and update checks require targeted regression coverage.

Test15 also includes the added Android controller pass (docs/ANDROID-GAMEPAD.md): SDL/Xbox mappings, reviewed digital-trigger patch, launcher/dialog navigation, response settings, reconnect cleanup and Auto/Show/Hide touch. Earlier pre-controller test15 artifact hashes are superseded by the final delivery record. Hardware gamepad/phone/Quest regression evidence remains pending.

Campaign expansion investigation is recorded in docs/COOP-PLAYER-LIMITS.md. CE01 remains two-player: do not expose larger capacities by changing a constant. Multi-peer transition ACK/snapshot state and recovery storage are concrete blockers; larger mission/vehicle/script performance remains unverified. The test15 browser rejects known unsupported campaign capacities without hiding compatible PvP rows.

Active continuation is now `test16-native-actions`; read docs/TEST16-PROGRESS.md
and docs/TEST16-DELIVERY.md. Preserve the complete test15 scope. VR Safe geometry
migrates once; flat stays Normal. Native action ownership is driven by real FP
states, preserves the gun subtree and grip latch, and blends back to tracking.
Do not publish test16 until owner testing/approval; headset validation is pending.


Current continuation: **test17-network-data-profiles**. Read docs/TEST17-PROGRESS.md,
docs/TEST17-DELIVERY.md and docs/GAME-DATA-LIBRARY.md. Owner confirmed improved
test16 native animations; preserve action/IK/grip and native online melee. Six
test16 logs identified the PvP in-progress/campaign flag collision and unmasked
player action bit 15. Test17 addresses these and reviewed upstream departure
fixes, and adds managed data sets. Both APKs must be built serially and delivered
privately with source/build ZIPs. No new release/install/launch is authorized.
Do not infer Original/Rev1/Rev2 identity from filenames or promise revision-based
server matching without advertised fingerprints. The launcher includes the
owner-requested note that differing ISO/revision map files may affect joins.
