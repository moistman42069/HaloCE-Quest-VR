> **Current release candidate: v1.0.10 (test28, 2026-10-06).** OpenCE Build 138/network 20 co-op is integrated. The host selector offers 2–128 players, default 4. The owner reports co-op works well; exact player count/device pairing was not provided. Maximum-count stability is not certified. The old test15 audit below concerns a retired project-owned protocol, not the current OpenCE implementation. See [OpenCE compatibility](OPENCE-COOP-COMPATIBILITY.md).

# Campaign player-count audit — test15

## Decision for this candidate

**Campaign remains two players on two machines.** This is the highest implemented
capacity backed by the owner's paired-session result; it is not a claim that all
missions or every two-player edge case have passed. Native PvP still exposes
2–128 slots. No evidence establishes stable 4-, 8- or 128-player campaign support.
An unsupported capacity selector would create sessions the current protocol
cannot load. The launcher explains the limit and blocks known CE01 directory
entries advertising another capacity. Unknown saved invites still undergo the
native handshake; compatible PvP listings remain available and population-sorted.

The 128-player transport/table expansion is reusable infrastructure. It does
not expand campaign lifecycle state, player recovery storage or authored mission
behavior. This audit does **not** conclude that a future expanded co-op
implementation is impossible; it identifies the work required before enabling it.

## Source findings

| System | Current evidence | Consequence for expansion |
| --- | --- | --- |
| Transport / player slots | `halo_port_limits.h` allocates 128 network players/machines, using signed-byte indices with NONE. The distributed transport already sends to multiple clients. | Reuse this infrastructure; 128 is a representable network ceiling, not a tested campaign capacity. |
| Session identity | `network_campaign_game` requires minimum=maximum=2. `network_campaign_prepare` writes 2. `network_game_manager` rejects a campaign marker with invalid campaign settings. | Raising only a launcher option fails the native settings gate. |
| Lobby / admission / disconnect | `network_campaign_session_update` starts only with player_count=2 and machine_count=2; any other in-game player count aborts. Campaign late join is refused. | Needs roster and start policy, participant-aware disconnect handling and explicit late-join policy. |
| Loading / resources / BSP | `network_campaign_lifecycle.c` stores one `peer_ack` and one `peer_machine`. ACK validation requires exactly one remote. | With 2+ remotes ACKs are refused; simply raising the cap makes transitions stall and time out. A multi-peer readiness/digest/timeout state machine is required. |
| Checkpoints / snapshots | Save/restore shares that barrier. `network_distributed_campaign_snapshot(machine)` targets the one ACKed peer before release is broadcast. | Every participant needs an ordered, complete snapshot and matching generation before release; a first-ACK release would be unsafe. |
| Spawn / death / recovery | `player_saved_unit_slot` maps network indices into `MAXIMUM_LOCAL_PLAYERS` (4). `players_globals.dead_units` has 4 entries. Indices 4–127 return NONE. Spawn equipment uses primary/secondary campaign sets. | 128 network slots cannot retain campaign saved-unit state. Expand separate campaign recovery storage with save-layout/version handling; do not enlarge local split-screen arrays indiscriminately. Four storage slots do not prove four-player campaign works. |
| Respawn / all-dead | Host owns campaign respawn/death decisions; clients do not independently restore. Saved-unit handling is bounded as above. | Validate partial deaths, all dead, remaining living partners, checkpoint state and roster churn at each proposed cap. |
| BSP placement | Host iterates network players and calls `player_teleport_on_bsp_switch` around one source/teleport position. | Iteration can include more players, but it does not demonstrate collision-safe placement for a crowd. Need bounded free-space placement and tests in small transition areas. |
| AI / NPC animation | Decisions are host-owned; captured NPC controls are batched and sent to all clients; impulses use reliable batches. Object tables remain bounded. | Replication can fan out, but host cost, reliable queue growth, visibility/object limits and packet loss need measurements. No 128-player campaign/AI load measurement exists. |
| Scripts / cutscenes | Host runs scenario scripts; clients replay a bounded allowlist. Presentation has a 256-entry pending queue. Actual mission scripts and seat/spawn authoring reside in map resources. | Neither a larger transport nor an allowlist proves arbitrary mission scripts handle larger rosters. Audit real maps and play all missions/cinematics before acceptance; no such 128-player evidence is available. |
| Vehicles | Existing authoritative inventory/seat replication is retained; unarmed NPC seats were fixed in test14. Seats are defined by unit tags. | Additional players do not create additional seats or scripted transport capacity. Validate boarding, overflow participants, driver/passenger changes and mission-critical vehicle sequences. |
| Level progression | Restart/next mission resets to the normal lobby and returns through the two-player start gate. Final mission closes the session. | Expanded sessions need the same negotiated roster/cap across restart, next mission and final exit. |
| Avatars / VR | Negotiated render-only avatar snapshots coexist with campaign/PvP. Their prior two-peer acceptance is preserved. | Do not infer 128 visible VR bodies perform acceptably from two-peer video. Measure CPU, bandwidth and frame timing. |

## Executed checks

- `test_campaign_capacity.py`: production campaign identity/preparation and saved-unit
  slot functions. Capacities 1–128 are checked: only 2 is accepted as CE01;
  recovery indices 0–3 exist and 4–127 are explicitly rejected. Invalid maps and
  difficulty stay rejected.
- `test_campaign_lifecycle.py`: production barrier with one, two and 127 mocked
  remotes. Multiple-remotes ACKs do not release; the one-remote path completes.
  Existing digest/epoch/timeout, checkpoint and snapshot checks remain.
- `test_quest_browser.py`: CE01 capacity validation across 1–128, unknown saved
  invite handling, and PvP capacity independence; existing parser/version checks.
- Existing actor, VR, renderer, input/controller, update and networking suites
  remain part of this candidate's regression pass.

These are automated source/behavior checks. No extra physical clients, mission
playthrough, many-player simulation, live server or headset session was run.

## Required next implementation and acceptance stages

This is a roadmap, not shipped expanded co-op:

1. Add a distinct negotiated expanded campaign capability/version, explicit
   roster and host-selected target count. Keep CE01 two-player behavior intact.
2. Replace the single-peer barrier with per-machine readiness, digest, applied
   snapshot and release tracking; test missing/duplicate/late ACKs, dropped peers,
   old epochs, restore during transition and mixed-version rejection.
3. Add bounded per-network-player campaign recovery state with compatible save
   handling, collision-aware spawns and BSP relocation. Cover every proposed slot.
4. Validate authored scripts, cinematics and vehicles using legal installed map
   data and real multi-client progression. Define overflow and disconnect behavior.
5. Start device trials at four; test eight and higher only after prior stages
   pass. Measure per-peer bandwidth, reliable backlog, tick/frame time, AI/object
   limits, repeated checkpoints, all-dead recovery and all ten mission transitions.
6. Expose only accepted limits in the launcher and compatible directory metadata.
   Retain two as the default until larger sessions have their own acceptance.

No practical stable ceiling above two can be honestly reported from the current
evidence. A public 128-player PvP event is evidence for that upstream PvP event,
not for campaign synchronization, scripts or Quest campaign performance.
