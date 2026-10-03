> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Native Quest campaign co-op: evidence and implementation history

## Latest test12 source (2026-10-03)

Native host/join and the launcher are now connected. Campaign negotiation,
authoritative mission/AI logic, presentation/object/device/actor synchronization,
content hashes and coordinated loading/checkpoint/progression paths are implemented.
Opt-in public listing follows a live native host, with withdrawal and failure
reporting. Detailed behavior and limits are in CAMPAIGN-PROTOCOL-WIP.md; user
instructions are in TEST12-README.md. No paired-device campaign success is claimed.
The sections below preserve the investigation and earlier checkpoints; statements
such as "unwired" or "not exposed" describe their historical checkpoint only.

## User request (2026-10-02)

Host a VR campaign, list it in the launcher, and join it from another headset,
similar to the successful competitive browser. The user correctly points out
that the working online transport should be reused. This is an open feature
request, not rejected as impossible. Test10 does not implement online campaign
co-op and must not advertise otherwise.

## Last delivered build (test11) baseline

- `source/interface/ui_widget_event_handler_functions.c`: `coop_game_initialize`
  sets `player_spawn_count = 2`; `start_new_game` sets the local connection.
- `source/game/game.c`: `game_is_cooperative` means `player_spawn_count > 1`.
  That alone does not create a remote campaign session.
- `source/main/main.c`: `main_setup_connection` explicitly selects
  `_game_connection_local` for the solo/campaign loading path.
- `source/interface/player_ui.c`: `player_ui_fast_setup_network_server` starts
  the connected competitive pregame screen and game-engine playlist.
- Existing transport, invites, reliable messages, object replication, player
  prediction, damage authority and non-player bipeds ARE reusable. In
  `game_update`, `ai_update` already runs only on the host for distributed
  play. Do not repeat an unsupported claim that the port cannot replicate AI
  objects at all.
- `game_update` still calls `hs_update` on clients. The distributed message
  enum in `port/linux/game/network_distributed.h` has player/object/inventory,
  damage and competitive game-state messages; it has no campaign checkpoint,
  script-global, objective or campaign transition protocol. A campaign loaded
  on two independently ticking machines is not thereby synchronized.
- The reviewed Chupathingy directory describes competitive engine modes,
  maps, population and network version. No reviewed campaign capability or
  supported native campaign host/join path was found.

## Concrete next implementation phases

### Test12 source checkpoint (2026-10-03, not playable)

Current WIP now negotiates a separate campaign identity, suppresses client
scenario script threads, and replicates an allowlist of HUD/camera/control
presentation calls. Scenery and devices join the campaign object set; device
power/position/group values are replicated separately. Remote-player saved-unit
slots and host-owned respawn/BSP decisions no longer assume local controllers.
Persistent solo saves and last-solo resume paths are protected. Flat native and
both launcher Java compilations pass. See TEST12-PROGRESS.md for exact logs.

Further WIP now adds audio/custom animation, content hashes, transition barriers,
paired local checkpoints and native host/restart/next-level routes. Exact behavior
and remaining issues are in CAMPAIGN-PROTOCOL-WIP.md. Launcher host/join and public
publication are still unwired; native object/presentation coverage needs review.
The baseline findings below describe what needed adapting; they must not be
mistaken for the current WIP implementation or a playable accepted release.

### Additional audit, 2026-10-03

`network_game_create_game_objects` in `network_game_manager.c` builds options
from the network game's map, difficulty and seed, loads the map and spawns valid
network players into their slots. That is the candidate campaign load route.
It is not yet exposed as an online campaign session. The local campaign route
still forces `_game_connection_local` in `main_setup_connection`.

`hs_runtime_update` in `hs_runtime.c` executes eligible script threads on each
machine; `game_update`'s distributed-client AI guard does not guard `hs_update`.
The campaign work therefore requires auditing both host simulation effects and
client presentation effects. Disabling every client script without replicating
cinematics/objectives/transitions is insufficient. Copying an HS memory image
between machines is also insufficient because it contains local datum references.

The user has volunteered to try a two-client session, but their response did not
identify two Quests versus Quest/desktop. Plan matching Quest builds first. Test11
does not ship native campaign co-op. This remains a requested implementation task,
not a completed investigation or a cancelled feature.

### Implementation order

1. Negotiate a separate campaign capability between matching modified builds;
   retain competitive v9/v10 compatibility. Distinguish campaign sessions in
   discovery so stock clients cannot enter an unsupported campaign.
2. Route host-selected campaign map/difficulty and two remote player slots
   through the existing connection and loading handshake, instead of the
   local-only setup path. Require matching map content.
3. Keep AI and mission decisions authoritative on the host. Audit every
   script side effect: replicate objectives, script globals, device state,
   cinematics and BSP transitions; prevent clients running conflicting scripts.
4. Implement coordinated ready/start, respawn, both-dead checkpoint restore,
   restart, next-level load and disconnect behavior. Preserve local saves.
5. Exercise two actual clients from start through a checkpoint, death/reset,
   BSP transition and next-level load before calling it playable. Test VR pose
   independence and competitive cross-play regression separately.
6. Then expose launcher Host/Join and opt-in directory registration/heartbeat,
   with removal on exit and stale-listing expiry. Host must represent a live
   campaign session, not merely a published invite.

The web port's remote split-screen/streaming co-op is a different architecture;
it is not evidence that two native OpenXR clients already share campaign state.

## References

- [ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce): native online
  competitive hosting and public listings. Its account-based website can list
  a compatible OpenCE competitive host's invite.
- [Native netcode](../port/linux/NETCODE.md),
  [message definitions](../port/linux/game/network_distributed.h).

No new public server was created, account registered, or host session published
as part of this investigation.
