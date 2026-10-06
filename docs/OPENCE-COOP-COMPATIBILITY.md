# OpenCE co-op and browser compatibility (test27/test28, 1.0.9/1.0.10 candidates)

Updated 2026-10-06. Candidate **test27, version 1.0.9 / code 35**, branch
`test27-opence-netcode`. Not released.

**Status (1.0.10, test28): partly verified on a device.** On 2026-10-06 a
Quest 3 on 1.0.9 found a public OpenCE co-op game (18 players on d40) through
the signed lobby, connected (join stages 1/3 to 3/3, network 20), joined in
progress and loaded the map. It then halted on an upstream camera check that
OpenCE's release builds only log; 1.0.10 fixes that
([TEST28-PROGRESS.md](TEST28-PROGRESS.md)). Still to confirm: play after
joining, an OpenCE player joining a Quest or Android host, and games of three
or more mixed players. Do not call cross-play fully working until those logs
are in.

## What OpenCE's "co-op server browser update" is

Checked against OpenCE's source (tags `build-128` = `2b0327bc`, `build-129`,
`build-138` = `76addf66`) and the live community directory.

| Question | Finding |
| --- | --- |
| Which discovery service? | OpenCE hosts publish **signed listings** (Ed25519, format `HL` 1) through **public MQTT brokers**, `opence.milenko.org:1883` first (`port/assets/network/brokers.txt`; `p2p_lobby.c`, topics `hceu/3/lobby/...`). OpenCE has no HTTP announce. The community directory `https://halo.milenko.org/v1/games.txt` mirrors these listings. |
| How do co-op hosts advertise? | As an ordinary network game: **game engine 0 on a campaign map** (a10 … d40). There is no separate co-op protocol or listing type. |
| Do listings carry a type and version? | The native **network version** (17 for build 128, 18 for 129, 20 for 138), the engine, map, players, and since build 138 a **password (locked) flag**. The directory adds age, score limit, teams and a roster (12 tab-separated columns, 2026-10-05). |
| Join and handshake | The listing's invite → signalling over the brokers → a direct UDP connection → the native join, which requires an **exact network-version match**. |
| Gameplay messages | OpenCE's distributed netcode at that version. Its co-op adds messages 64–77 (`network_coop.c`, `network_actors.c`): host-run scripts, cinematics, devices, BSP switches, allegiances, AI units, spectating, extra enemies, glass. |
| Same service as this app's directory? | The same directory, yes. But until 1.0.8 this app published its own co-op over HTTP with version 0xCE02 (52738) and joined only 0xCE02 hosts: a different protocol, two players. |

On 2026-10-05 the directory held 46 games (versions 11, 15, 16, 17, 18), six of them OpenCE co-op on a10, a30, b40 and c40, up to 32 players. On 2026-10-06 it held 29, one co-op game on network 20.

## Why the fix is a netcode change, not a version number

Network versions 12–20 changed the wire format for every game, multiplayer included: unit states, player input (the BSP each client has loaded), game settings, damage, and the co-op messages. Accepting v17 or v20 at the join gate without speaking it would desync or crash. So 1.0.9 **runs OpenCE build 138's netcode** (network 20, exact match, as every OpenCE build does). The owner chose this direction over a dual-netcode design on 2026-10-06.

## Compatibility matrix (1.0.9 against each peer)

| Peer | Listing / discovery | Join / handshake | Gameplay sync | Game data |
| --- | --- | --- | --- | --- |
| OpenCE build 138 (network 20), co-op | Listed: in-game System Link list and launcher co-op browser (seen on a Quest, 2026-10-06) | **Seen working** (Quest 3, 1.0.9: connected, joined in progress, map loaded) | Expected: OpenCE's co-op modules byte for byte | Same campaign maps; Xbox caches, PAL as NTSC |
| OpenCE build 138, multiplayer | Listed | Expected | Expected: OpenCE's netcode | Same map files |
| OpenCE builds 128–136 (network 17–19) | Listed, marked as another version | Refused by name ("the host is on version N") | n/a | n/a |
| Newer OpenCE (network 21+) | Listed, marked | Refused: "update this app when a version for it is out" | n/a | n/a |
| This app 1.0.9 (Quest or Android) | Listed (signed lobby; directory mirror) | Expected (same code as OpenCE's path) | Expected; VR avatars between 1.0.9 devices (messages 37/38, negotiated) | Same campaign maps |
| This app 1.0.8 or older (CE01/CE02 co-op, network 11 multiplayer) | Co-op listed as "Co-op of this app 1.0.8 or older"; network 11 games marked | Refused by name; the host must update | n/a | n/a |

"Expected" means implemented and covered by the automated checks below, but not yet observed in a real session.

## What changed in 1.0.9

- **Netcode = OpenCE build 138.** The co-op and lobby modules (`network_coop.c`, `network_actors.c`, `coop_*.c`, `p2p_lobby.c`, `network_damage.c`, three `source/networking` files) are byte for byte build 138's. `network_objects.c`, `network_distributed.c/.h` and the rest of `source/networking` are build 138's plus only this app's additions:
  - test26's resting-teleport resend;
  - the VR avatar messages (37/38, sent only to machines that said they draw them; OpenCE drops kinds it doesn't know);
  - the launcher's PvP and co-op hosts;
  - the join gate's messages;
  - gametype-default options (no PC menus).
- **Bugs found and fixed while merging:**
  - The 3-way merge had kept gaps where this tree predated OpenCE's v11 baseline: the picked-up weapon, the in-progress flag, name cleaning, weapon swap, unarmed melee and team assignment.
  - This app's receive filter dropped every message after `pings` except its own CE02 ones, which would have discarded all of OpenCE's co-op traffic.
- **Hosting.** Campaign co-op > Host campaign writes `coop_host.txt` with mission, difficulty, public/private and the most players: OpenCE's Server Setup sizes, 2 to 128 (1.0.9: 16 at most). The game opens an OpenCE co-op lobby, set up exactly as OpenCE's Create Game does: a campaign map with no game engine. A public game is listed through the signed lobby. The host starts it from the lobby, or it starts when the lobby fills; players may join while it's under way.
- **Joining.** In the game, Multiplayer > System Link lists public co-op and multiplayer games (and Wi-Fi ones). The launcher's browsers list the same directory, co-op apart from multiplayer, joinable only at network 20. Locked (password) games are marked and not joined; their invite still works.
- **Retired:** the CE01/CE02 co-op protocol, its HTTP announcer (`CoopPublisher`), its join path, and the v9–11 multiplayer window. The old code is still compiled but never activates (`network_campaign_game` is always false).
- **Not taken from builds 130–138:** renderer features (anti-aliasing, per-pixel lighting, shadow maps), the audio overhaul, the PC menus, PC scoreboard and volumes, Windows crash reports. None changes the wire, and the renderer and audio changes risk VR regressions.

## What changed in 1.0.10 (test28)

- **Joining a game in progress no longer halts.** A player who joins without a unit watches the host from behind. OpenCE's camera for that kept "up" pointing at the sky even when the host looked up or down, which left the camera skewed. 1.0.10 squares it.
- **Release builds, as OpenCE ships.** A failed upstream check is written to the game log as `EXCEPTION … (release build)` and play goes on, as on OpenCE. Before, it halted with the blue screen.
- **Co-op hosts of 2 to 128 players**, the sizes OpenCE's Server Setup offers.

## Automated evidence

- `tools/test_test27.py`:
  - network 20 exactly;
  - the 15 OpenCE files by hash;
  - every message number against OpenCE's (compiled);
  - the receive path decodes every OpenCE kind;
  - restored gameplay;
  - the join gate;
  - the launcher's host request (runs the parser);
  - locked-lobby marking.
- `tools/test_quest_browser.py`: directory parsing (12 columns, rosters, future columns), the three kinds, browser placement and joinability, plus the native join gate compiled and run over 112 cases. Run against the live directory: 29 games, one co-op game joinable at network 20, 10 multiplayer games joinable.
- 29 regression suites pass; VR and flat game code and the host build without errors.

## Limits

- **Versions:** network 20 exactly. OpenCE moves fast (17 → 20 in a day); when it moves on, this app needs a new release.
- **Game data:** the same campaign maps (Xbox caches; PAL is played as NTSC). Modified maps or other revisions can fail to load.
- **Network:** direct UDP connections; strict NAT on both sides (common on mobile data) can block joining; there is no relay.
- **Devices:** OpenCE's co-op defaults to 16 players and offers up to 128; how many a Quest or phone host can keep smooth is not measured. Hosting on Wi-Fi is recommended; for big games a PC host is the safer choice.
- **Not in this app:** setting a lobby password (no PC menus); joining a locked game from the list (use its invite); OpenCE's in-game co-op server settings (extra enemies and friendly fire use `config.toml` defaults: `network.coop_*`).

## How to report a failure

Send **both logs of the same session** (host and joiner): the game logs from `Download/HaloCE` (Android/Quest) or OpenCE's `debug.txt`, plus the launcher log, with:
- the app version on each device (1.0.9 / code 35) or OpenCE build number;
- the device and OS;
- Wi-Fi or mobile data;
- the mission and the time it failed.

The logs record each join stage ("stage 1/3 … 3/3"), the network version, NAT class and refusals.
