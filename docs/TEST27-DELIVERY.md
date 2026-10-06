# Test27 — 1.0.9 candidate (private): OpenCE's netcode and co-op

Not a release. GitHub's Latest is v1.0.6; v1.0.7 and v1.0.8 were delivered as
candidates only. Do not publish without explicit owner approval. Details:
[TEST27-PROGRESS.md](TEST27-PROGRESS.md),
[OPENCE-COOP-COMPATIBILITY.md](OPENCE-COOP-COMPATIBILITY.md).

## Installation

- Quest/VR: `HaloCE-Quest-test27.apk` (package `com.halo.decomp.vr`)
- Android/flat: `HaloCE-Android-test27.apk` (package `com.halo.decomp`)

Both are **version 1.0.9 / code 35**, ARM64, API 28+, signed with the same
certificate as every release since v1.0.2, so they install over v1.0.6,
1.0.7 or 1.0.8 without uninstalling (`adb install -r <apk>`). Do not uninstall
or clear data.

**Network change:** 1.0.9 plays OpenCE's network version **20** (OpenCE
build 138), for co-op and multiplayer alike. It plays with OpenCE build 138
players and other 1.0.9 devices. It does **not** play with this app 1.0.8 or
older, or with older or newer OpenCE builds; those are listed but refused, by
name.

## Changes

1. **Co-op as OpenCE plays it.** Up to 16 players, with Quest, Android and
   OpenCE's Windows/Mac/Linux players together. Players can join while a
   mission is under way; the host runs the scripts, AI, doors, level changes
   and checkpoints; a dead player watches a teammate until it is safe to come
   back.
2. **Hosting** (launcher: Campaign co-op > Host campaign): mission,
   difficulty, most players (2–16) and Public. A public game is listed in
   this app's in-game list, OpenCE's server browser and the community list.
3. **Finding games:** in the game, Multiplayer > System Link > Refresh lists
   public co-op and multiplayer games. The launcher's Browse / join and
   Multiplayer servers lists show the community list, co-op apart from
   multiplayer. Games you can't join say why. Password-protected games are
   marked LOCK (use the host's invite).
4. **Multiplayer** also plays with OpenCE build 138 hosts (network 20).
5. Everything from 1.0.8, 1.0.7 and earlier is kept: VR, controls, vehicles,
   comfort, the co-op crash fix, glass and the rest.

Retired: this app's own two-player co-op (1.0.0–1.0.8) and the network 9–11
multiplayer window.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test27.apk` | 28,314,243 | `d60e50b188d3794ce17629a72589387ddc398094170907e2dfc7d7c9da929206` |
| `HaloCE-Android-test27.apk` | 26,237,492 | `f9fbc88f0350c91e609b1aae66fb67664e80c26574c54d790c35d50b9e85b3bb` |

Runtime source `23898ce6` on branch `test27-opence-netcode`; later
commits change only documentation. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. Built
serially from a clean tree; payload, signing and 16 KB alignment verified.

## Checks performed

- 29 regression suites pass, including the new `test_test27`:
  - network 20;
  - 15 OpenCE files byte for byte;
  - message numbers;
  - the receive path;
  - restored gameplay;
  - the join gate;
  - the host request;
  - locked lobbies.
- `test_quest_browser` also ran against the live community list. On 2026-10-06 it had one co-op game and 10 multiplayer games on network 20, all joinable by this build.
- Cache formats: 127 passed, 4 missing-fixture skips. Both editions build without errors.
- **Not done:** no device session, and no session with OpenCE players. **Cross-play with OpenCE is implemented but not yet proven.**

## Please test (record for each: app version on every device, the OpenCE build if any, devices and OS, Wi-Fi or mobile data, game data revision)

1. **Quest hosts, phone joins** (both on 1.0.9):
   - Host campaign on the Quest: Pillar of Autumn, Normal, up to 4, Public.
   - On the phone: Play > Multiplayer > System Link > Refresh, then join the Quest's game.
   - Play past the first cutscene and some fights.
   - Send both logs.
2. **Phone hosts, Quest joins:** the same steps the other way round.
3. **Join an OpenCE co-op game:** on a PC, or with a friend on OpenCE build 138, host co-op (Create Game > a SINGLEPLAYER map). The Quest and the phone join it from System Link. Send both logs and OpenCE's `debug.txt`.
4. **OpenCE joins you:** a PC on OpenCE build 138 joins a co-op game the Quest hosts, from its Server Browser.
5. **More than two:** three or more players in one game, any mix.
6. **Multiplayer:** join a network 20 multiplayer game from the list, then host one from the launcher.
7. **Everything else:** a few minutes of single player in VR and on the phone (controls, vehicles, menus), to confirm nothing else changed.

If something fails, note the time, keep both apps open if you can, and send both players' logs from `Download/HaloCE` (plus OpenCE's `debug.txt`).
