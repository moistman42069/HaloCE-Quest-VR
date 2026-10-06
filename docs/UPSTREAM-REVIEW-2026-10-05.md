# Upstream and network review, 2026-10-05

> **Current status (2026-10-06):** This review records the earlier test25 decision
> and is historical. Test27/test28 subsequently integrated OpenCE Build 138
> directly, including network 20 and campaign co-op; project-specific network 11
> and CE01/CE02 paths are retired. v1.0.10 owner testing reports co-op works
> well. See [current compatibility notes](OPENCE-COOP-COMPATIBILITY.md).

Reviewed for test25 (1.0.7 candidate) against this tree (`test25-vehicle-recenter`,
from v1.0.6 `f04f5612`). Sources: the local upstream clone
(`cybersecurity/halo-ce-universal`, whose tags and history match
OpenCommunityEdition/OpenCE: `build-121` to `build-125` are the same commits);
GitHub pages for OpenCE releases, tags and PRs #68, #69 and #85; DamnationCE
releases. Checked on 2026-10-05; upstream moved several builds that day.

## Where the two projects stand

| | This project (v1.0.6, test25) | OpenCE (Build 125, `13c14df9`) | DamnationCE (v0.3.18) |
| --- | --- | --- | --- |
| Native network version | **11**; joins hosts 9–11 | **16**; exact match required | **16**; all players must match |
| Campaign co-op | Own two-player protocol (CE01, a separate launcher flow) | Its own online co-op since `8194c5a0` (defaults to 16 players, private) | Same family as OpenCE's (its author's PRs #89–#101 merged into OpenCE) |
| AI in co-op | Host actor controls replayed on the client (this project's design) | PR #68 "host-authoritative AI sync" **merged** (not open) | As OpenCE |

Network version history upstream since this project's last review (`7e00135d`,
still version 11):

| Commit | Version | What |
| --- | --- | --- |
| `7d0e587c` | 12 | Co-op review fixes (after the native co-op merge `01586cfe`, PR #89) |
| `a38ede07` | 13 | Co-op extra enemies per player |
| `91e838e2` | 14 | Build 123 |
| `24957ff6` | 15 | Build 124 |
| `b525bf85` | 16 | A client's input says which structure BSP it has loaded (co-op), Build 125 |

**Consequence:** every OpenCE release still published (Builds 121–125, versions
13–16) and DamnationCE 0.3.12+ (16) are network-incompatible with this
project's 1.0.6/1.0.7 in both directions. The client refuses with the game's
own "the host is newer/older" message; nothing crashes. The in-game browser
can list such public hosts, but joining them is refused. Cross-play with OpenCE
works only with its builds from before `7d0e587c`. This is a protocol boundary,
not a bug, and it is **not** changed in test25.

## Adopted in test25 (unchanged code, no protocol change)

| Upstream | Why it applies | How |
| --- | --- | --- |
| `3d2c04d6` vertices at the camera plane | Our `nv2a_vsh.c` was byte-identical to its parent. A vertex with clip w = 0/NaN streaked to the screen centre: in VR, from geometry at the camera plane (first-person weapon, a first-person vehicle's interior). | Applied exactly |
| `fb1abedd` dead camera with no living player | Original-game bug: a stray pointer taken as the next unit to watch. Co-op with both players dead reaches it. Our file matched its parent. | Applied exactly |
| `61623e68` texture bindings after first upload | Our `bind_textures` has the same order; our upload binds on the active unit (then invalidates the state cache), so an earlier stage could draw with the new texture for one draw. Samplers are objects, not affected. | Adapted (same change) |
| `3ae09c3d` radar wedge fades fully | HUD art; our two PNGs matched its parent. | Applied exactly (bytes verified) |

## Needs adaptation (not adopted now)

| Upstream | Why it waits |
| --- | --- |
| `39ece781`/`fc7271fd`/`2853a422` antenna stepped per tick and drawn between ticks | Touches `game.c`, `game_time.c`, `objects.c`, which differ here (render interpolation, VR). Needs a port onto this tree's interpolation. |
| `cd345aac` death/respawn delays in ticks | `main.c` differs here; relevant to co-op respawn, worth porting with a co-op test. |
| `de520606` host takes grenade damage only from grenades thrown | Touches `network_damage.c`/`units.c`, which differ; behaviour change in networked damage. |
| `dea5fe3b` crash past 256 actors | Reached with upstream's extra-enemies option, which this project does not have. |
| PR #69 browser sorting/UI, optional halo.milenko.org list | **Open**, not merged. This project's browser differs (signed discovery, own layout). Revisit when merged. |

## Should wait (protocol or design changes)

- **Upstream online co-op** (`8194c5a0` and PRs #89–#101: loading zones that bring the team along, doors/elevators/device states, Flood bodies, dropship doors, host allegiances, dead vehicles, the BSP-sync gate, extra enemies, friendly fire defaults, kick): a different co-op design on network 12–16. Adopting it means replacing or bridging this project's CE01 campaign protocol. That would lose mixed play with every existing 1.0.x device. It needs its own branch, a protocol decision by the owner and two-device testing. Ideas worth borrowing deliberately later: team-wide loading zones with a wait/rescue rule, device state sync, BSP-loaded acknowledgement.
- **Raising the PvP network version to 16**: requires implementing every wire change from 12 to 16 (several are co-op structures) and testing mixed versions. Until then, 1.0.x stays on 11 with the 9–11 window.
- **PR #68 AI sync** (merged upstream): its unit-control streaming resembles this project's host actor controls; a comparison is worthwhile only together with the co-op decision above.
- **PR #85 Steam Frame/OpenXR**: open; arm64 Linux only. See [PC-STEAM-FRAME-FEASIBILITY.md](PC-STEAM-FRAME-FEASIBILITY.md).

Not applicable: Windows console/logging, gamescope fullscreen, macOS Android build host, split-screen joins and divider, resolution/scaling settings (desktop UI).

## Build 128 (network 17), reviewed for test26 (1.0.8)

OpenCE's Build 128 is `2b0327bc` ("Network version 17"), 14 commits after
Build 125 (`13c14df9`). This project stays on PvP network 11 (9–11) and its
own two-player campaign protocol, now **CE02** (1.0.8 adds two campaign
messages; a 1.0.7 device is refused with a plain "different version of this
app" message). The launcher's updater still installs only this project's own
releases; it never replaces the game with an upstream build.

| Upstream | Decision | Notes |
| --- | --- | --- |
| `197c1994` ~80% faster with many enemies | **Adopted** (engine half, exactly) | `cluster_partitions.c/.h`, `object_lights.c`, `data.c`, `profile.c`, `game_state.c` (the partitions forgotten before a load). Not adopted: its `d3d8_gl.c`/`gl.h`/`xbox_textures.c` render-target cache, which keys targets in a way this tree's per-eye and resolution-scale targets would reuse wrongly. |
| `7a1ffca2` glass breaks the same for everyone | **Adopted** (glass half, adapted) | `breakable_surface_port_break` exactly; the host's breaks travel in a new CE02 message (reliable, with a slow resend of every broken pane so a lost message or a late join heals). The destructible-scenery half rides on upstream's `network_damage.c`, which this tree does not have. |
| `b843156f` a client never reverts its game on its own | **Adopted** | `main.c`: a network client neither reverts nor skips a cutscene by itself. |
| `1e74e9b0`, `8e6b9a21`, `99a31ca8` co-op scripts for every player | Not adopted; worth porting with two-device tests | Upstream's `coop_scripts.c` design (followers of player0, one player enough for `volume_test_objects_all`, a safe-to-save test for one player). Relevant to this project's two players (the Maw's bridge, a30's Pelicans) but not reported here yet. |
| `16361bde` a client waits on its floor for the host's BSP | Not adopted; candidate | Upstream's distributed-unit path; this tree's BSP switch differs. Port with a co-op BSP test. |
| `0acc3b13` damage events filled in one place | Not applicable | Upstream's `network_damage.c`. |
| `5d108579`, `9666575b`, `d0016bca` extra enemies; `a143d949`, `e55c29a9` loading zones | Not applicable | Upstream co-op features (extra enemies, team loading zones) this project does not have. |
| `2b0327bc` network 17 | Not adopted | Protocol boundary, as for 12–16 above. |

LivingFray/HaloCEVR PR #153 (open; the maintainer declined it as written)
targets the PC Direct3D 9 VR mod: it keeps a remote player's shots from
using the local VR hand's aim. Here that separation already holds: shots
from the hand (`vr_render_hand_origin`) apply only to the local player's
unit in a local game, and haptics only to the local player.

## Builds 129-138 (network 18-20), adopted for test27 (1.0.9)

OpenCE moved from network 17 (build 128) to 18 (build 129: networked glass
fix, hardening) to 19 (`62fa7e13`, co-op player collisions option) to 20
(`6112dcfc`, password-protected public lobbies) by build 138 (`76addf66`,
second hardening round, its own zlib). With the owner's decision to run
OpenCE's netcode (2026-10-06), 1.0.9 takes build 129 by a classified 3-way
merge from `7e00135d`, then those three commits, then makes the networking
files build 138's with only this app's additions (see
[OPENCE-COOP-COMPATIBILITY.md](OPENCE-COOP-COMPATIBILITY.md)). Not taken:
`94882796` anti-aliasing, `3dba558e` per-pixel lighting, `1dc533fe` shadow
maps, `8a8e7059`/`b115a412`/audio PRs (reverb, resampling, limiter, ADPCM,
distance), `9a128287` MP maps alone, `7ea61077`/`7e82e712` PC menu settings,
`22249cf1` Windows crash reports, `e4461981` render interpolation snaps,
`f5bb75c2`/`b449c43e` D3D constant serials (renderer, this tree's differs),
`d635d837` Windows linker. None changes the wire; the renderer and audio ones
risk VR regressions and want their own review.
