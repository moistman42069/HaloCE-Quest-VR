# Test27 checkpoint: OpenCE's netcode and co-op (network 20)

Updated 2026-10-06. Private candidate **test27, version 1.0.9 / code 35**,
branch `test27-opence-netcode`, from test26 (`a537c4b6`, 1.0.8 / code 34). Not
released: the GitHub Latest release is still v1.0.6, and no v1.0.8 release or
tag exists.

## Request

Make this app work with OpenCE's recent co-op and server browser: VR and
Android players finding and creating co-op lobbies of more than two players,
with the same function as the recent OpenCE build. Integrate OpenCE's newest
updates before packaging. Do not fake support, do not just change a version
number, and keep the existing features.

## Decision

OpenCE's co-op is not a separate protocol. It is the native netcode at
OpenCE's version (exact match), and versions 12–20 changed the wire for every
game. The owner chose (2026-10-06) to **switch this app to OpenCE's netcode**
rather than run two netcodes. Consequences:
- this app's own CE01/CE02 two-player co-op is retired;
- the v9–11 multiplayer window is retired;
- 1.0.8 and older devices need 1.0.9 to play with 1.0.9.

## Work

1. **Investigation** (see [OPENCE-COOP-COMPATIBILITY.md](OPENCE-COOP-COMPATIBILITY.md)):
   - discovery is signed listings over MQTT brokers, mirrored by the community directory;
   - co-op hosts are engine 0 on a campaign map;
   - the native version must match exactly;
   - the directory's 12-column format;
   - the live population.
2. **Merge to build 129**: a classified 3-way merge from OpenCE `7e00135d`, this tree's last v11 review point. 45 files taken whole, 11 added, 60 merged by hand (66 conflicts); the PC menus were left out except the co-op server set-up.
3. **Builds 130–138**: `62fa7e13` (v19 co-op collisions), `6112dcfc` (v20 password lobbies) and `76addf66` (second hardening round, with its zlib). Renderer, audio, PC menu and Windows commits were left out.
4. **Parity pass**: every networking file was compared with build 138.
   - Found: the merge had kept gaps where this tree predated OpenCE's v11 baseline, and this app's receive filter dropped all of OpenCE's co-op messages.
   - Result: the networking files are now build 138's plus only this app's additions (listed in the compatibility doc).
   - Restored OpenCE online gameplay: picked-up weapons readied, weapon swap, team from unit, unarmed melee, second-weapon pickup.
5. **Launcher**:
   - co-op hosting opens an OpenCE co-op lobby (2–16 players, public through the signed lobby);
   - the co-op browser lists the directory's co-op games, joinable at network 20, and marks this app's old co-op;
   - the multiplayer browser no longer shows co-op;
   - help, dialog and updater texts are updated;
   - the HTTP co-op announcer is removed.
6. **Game**: locked (password) lobbies are marked in Multiplayer > System Link. The join gate names this app's old co-op hosts and newer OpenCE builds.

## Status

| Item | Implemented | Automatically verified | Device |
| --- | --- | --- | --- |
| Network 20, OpenCE's netcode | Yes | Version, message numbers, 15 files byte for byte, receive path | Needed |
| Join an OpenCE co-op game | Yes | Gate cases; directory classification against the live list | **Needed: a real session** |
| Host co-op from the launcher (2–16, public) | Yes | Request parser; set-up wiring | Needed: Quest and Android host |
| An OpenCE player joins a 1.0.9 host | Yes (same code as OpenCE's) | — | **Needed** |
| Multiplayer with OpenCE build 138 | Yes | Gate, settings record | Needed |
| Locked lobbies marked | Yes | Static | Needed |
| VR avatars between 1.0.9 devices | Kept (messages 37/38) | Message numbers | Needed |
| Earlier features (VR, controls, vehicles, test25/26) | Kept | 29 suites | Needed |

Cross-play with OpenCE is **not yet claimed**; see the test checklist in
[TEST27-DELIVERY.md](TEST27-DELIVERY.md).
