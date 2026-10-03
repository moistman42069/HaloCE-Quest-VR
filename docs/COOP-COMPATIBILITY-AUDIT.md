> **Subsequent acceptance, 2026-10-03:** the owner accepted the delivered test14 pair and explicitly authorized publication as the latest release. This supersedes the earlier release hold below. Original investigation/check results remain historical; no complete campaign playthrough or all-device certification is inferred. See [current state](CURRENT-STATE.md) and [release provenance](RELEASE-PROVENANCE.md).

# Co-op compatibility audit ? test14, 2026-10-03

This records a source audit and focused automated checks, not a full campaign playthrough. The owner has confirmed paired Quest/flat connectivity and VR body visibility. NPC animation/physics and the fixes below still need paired-device acceptance. **Public APK releases remain on hold.**

## Review matrix

| Area | Inspected implementation / result | Evidence still needed |
| --- | --- | --- |
| Discovery and join | `network_campaign.c`, native client/server advertisement and join-token gates; CE01, two players/two machines, campaign map marker and bounded mission/difficulty; normal v9/v10 path separate | Real public directory registration remains unverified; invites were used successfully |
| Directory parsing | `ServerListing`, `ServerBrowser`, `CoopLauncher`, `CoopPublisher`; bounded feed, malformed row/duplicate rejection, population sorting/paging, live-host opt-in listing and withdrawal | Directory service acceptance, NAT/router combinations |
| Content identity | `network_campaign_lifecycle.c`; both peers hash mission/shared resources, reject mismatches before release | Different legitimate/modded asset combinations |
| Clock, packet order and ownership | Epoch+tick gate; round/seed checks; sender direction, exact payload sizes, salted object existence; actors reject older ticks while allowing split batches from the same tick | Latency/loss extremes on physical devices |
| AI decisions and controls | Host-only `ai_update`; `network_campaign_actors.c`, `unit_control`, `unit_update`, `biped_update_moving`; FIX: remote control must mark NPC actively controlled | Visible NPC walking, turning, shooting in both host assignments |
| Stale controls and checkpoints | Bounded two-second input lease, death/rewind/ownership expiry, reset of borrowed flags; source-driven sanitizer harness | Long packet loss, restore while NPC moves/fires |
| Animation impulses | Host `unit_start_animation_impulse` was not captured by ordinary controls or script presentation; FIX: reliable event 39 with typed validation and graph bounds | Dodge/evade/other NPC one-shots, species/weapon-class variants. Native receiver may refuse an event while its animation state is incompatible; variants are selected locally |
| Grounding/deaths | `network_objects_handle_states`, `biped_update_moving/dead`; FIX: nearby snapshots must still apply velocity/rest; grounded-rest authority clears stale airborne state | Bodies settling, stairs/slopes/moving platforms and the reported stuck pose |
| Weapons, grenades, melee, damage | Existing inventory/actions and host damage authority; clients report their own hits; campaign expands scenery/device targets and forwards AI-versus-AI effects. No second client AI damage simulation | Both players shooting/melee/grenades, AI attacks, shields/death/respawn |
| Vehicles and seats | Host/client prediction retained; inventory records own seats; FIX: unarmed NPC passengers were excluded by inventory filtering | Entry/exit, driver swaps, passenger AI, turret firing, moving dropships |
| Devices and attachments | Reliable host power/position/group targets, health/regions, scale, visibility, generic parent-node transform; local device group mapping and bounds; inventories own seats/held weapons | Doors, elevators, switches, unusual/custom attachments |
| Mission scripts and presentation | Client scenario threads suppressed; bounded allowlist replay with typed tag/object/string/scenario validation; HUD, camera, fades, sound and scripted custom animations | All ten mission scripts/cinematics have NOT been played through; non-allowlisted script side effects may need further support |
| Save/restore/BSP | Barrier state machine pumps transport while holding ticks; matching resources, ACK, full object snapshot and ordered release; map/tick resets; pending effects survive saves/BSP, abandoned effects cleared on restore | Both-dead recovery, BSP transitions, moving/attached objects after restore |
| Respawn/mission progression | Host decisions; saved-unit slots keyed by network player; host teleports both players across BSP; restart/next mission through native lobby; final mission exits | Full progression/checkpoints, death/rejoin behavior across maps |
| Disconnect and late join | Partner loss ends host session; new late join is refused because prior cinematic/checkpoint history is not replayed | Abrupt connectivity loss, reconnect as a new session |
| Pause/settings | Log showed missing multiplayer pause widget in a campaign cache; FIX: select campaign widget using network toggle behavior; prevent local-only pause from desynchronizing peers | Quest pointer/settings and flat menu, resume/back, host restart, client leaving |
| Local saves | Campaign checkpoint path is separate from persistent solo-save export and last-solo resume writes | Solo resume after exiting a co-op session |
| VR avatars | Existing capability negotiation, 15 Hz visual-only nodes, player ownership and finite/bounds checks, expiry/interpolation and old-peer fallback retained | Owner confirmed VR movement on flat; verify test14 preserves it and check death/vehicle transitions |
| Flat/VR builds | Same shared network source, separate OpenXR/touch staging, package identities and matching signing identity | Phone-specific UI/performance and Quest runtime confirmation |

## Automated checks

Run under Linux/WSL from the repo (clang/JDK required):

```sh
python3 tools/test_campaign_actors.py
python3 tools/test_campaign_lifecycle.py
python3 tools/test_quest_browser.py
python3 tools/test_quest_vr_math.py
python3 tools/test_quest_render_targets.py
```

The actor and lifecycle harnesses compile production functions with small engine/transport mocks and AddressSanitizer/UndefinedBehaviorSanitizer. Native 32-bit wire longs are represented as 32-bit host ints; full Android builds independently compile the real ABI size assertions. These are behavioral checks of the included logic, not engine/network/headset emulation. Actor tests include the production uncontrolled-unit branch and the actual NPC rest-state block. Lifecycle checks exercise ready/ACK/release, incomplete snapshots, save/restore, deferred operations, bad sender/content, timeouts, generation limits, and non-campaign bypass. Browser checks execute the Java parser and native compatibility gate; an obsolete 128-row expectation and missing campaign harness declarations were updated to the current full-feed implementation. The older VR helper harness needed new support-grip fields added to its mock; runtime code was not changed for that test.

The general Linux tooling pytest suite requires pytest, absent in the current WSL environment; its results are not claimed here. Build/package outcomes and hashes are recorded separately in TEST14-DELIVERY.md. No automated result authorizes a public binary release.

## Test priorities for the owner

Use test14 on both peers; test Quest host/flat client and flat host/Quest client. Repeat the reported a10 scene, compare NPC gait and bodies settling, open/resume the campaign menu, then try a checkpoint/death recovery, a BSP transition and a vehicle sequence. Preserve both launch logs for discrepancies. Continue to regard complete mission/cinematic parity as pending until actual playthrough evidence exists.
