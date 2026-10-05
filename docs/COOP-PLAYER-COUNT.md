# Campaign co-op player count: status and feasibility (2026-10-05)

## Correction

**Campaign co-op in v1.0.6 (and the 1.0.7 candidate) is two players.** The
128 figure is the PvP/System Link capacity of the native builds and of this
project's **Host multiplayer** slots (`HALO_PORT_MAXIMUM_NETWORK_PLAYERS`). It
is protocol capacity, not a tested Quest-host target, and it does not apply to
campaign. No higher campaign count is selectable.

The repository's player-facing text already says this: README and the player
guide ("Campaign supports two players, not 128") and the launcher's co-op
guide ("co-op is for two players"). No document in the tree claims more.

## Where two is fixed in code

`port/linux/game/network_campaign_session.c`:

- the host starts the mission when `player_count == 2 && machine_count == 2`;
- once playing, any other count ends the session ("partner disconnected"),
  because a reconnect would need cutscene and checkpoint history (no join in
  progress);
- the launcher's listing reports the session open while fewer than two have
  joined.

Everything else in the campaign protocol (presentation stream, host actor
controls, object poses, device states, lifecycle barriers) is written per
object or per machine rather than per player pair. The fixed points are the
session rules above and the game's own campaign assumptions below.

## What more players would need

| Area | Evidence | Work |
| --- | --- | --- |
| Engine arrays | Players/machines sized for 128 (`halo_port_limits.h`); per-tick player update for 128 is 3,857 bytes | None for counts up to 16 |
| Spawning | Campaign scenarios place few player starting locations | Place extra players near a teammate (DamnationCE "big team" overflow) |
| Scripts | Missions name `(player0)`/`(player1)`, `(players)` lists, cutscene teleports | Survey per mission; players beyond two may be left behind by teleports |
| Checkpoints | A save needs every player safe; restore barriers wait for every machine | Barrier rules generalised from "the other machine" to all; test failure cases |
| Respawn | Co-op respawn at a living teammate | Choose a teammate; timing in ticks (upstream `cd345aac`) |
| Loading zones/BSP | This project follows the host's BSP via lifecycle barriers | Team-wide zones with waiting/rescue (upstream/DamnationCE ideas) |
| Vehicles/seats | Seat ownership per machine | More riders per vehicle; seat races |
| Cutscenes | test24 activation stream is per machine | Already per machine; verify with 3+ |
| Bandwidth | Host actor controls and object poses go to every client | Scales with clients; measure on a phone/Quest host |
| Quest host CPU | A phone dropped to ~27 fps in a 56-player PvP server (test22 logs) | A Quest/phone host for more than 2–4 co-op players is unproven |
| Join in progress | Refused (no history replay) | Needed for more than two to be practical |

## Recommendation

Keep the released default and limit at **two**. A higher cap is not offered,
not even as an experimental setting, because the session logic aborts on any
count other than two and no 3+ session has ever run. A future experimental step
would be a config-only cap of 3–4 behind a clear WIP label. That needs the
session rules generalised, barrier and respawn tests for N machines, and a
3-device test. The upstream co-op (16 players by default) is a different
protocol (network 12–16); see
[UPSTREAM-REVIEW-2026-10-05.md](UPSTREAM-REVIEW-2026-10-05.md).
