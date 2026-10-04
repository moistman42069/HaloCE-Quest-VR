# Test20e — 1.0.2 candidate (private): Quest/Android multiplayer parity and join diagnostics

Not a release. v1.0.1 was withdrawn; the public release is v1.0.0. Supersedes
test20d (code 24) and keeps all of its changes (gun anchored to the controller,
left-handed mode, simpler settings). Do not publish without explicit owner
approval. Evidence, cause and audit: [TEST20E-PROGRESS.md](TEST20E-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test20e.apk`
- Android/flat: `HaloCE-Android-test20e.apk`

Both are **1.0.2 / version code 25**, ARM64, API 28+, signed with the
established certificate; they install over every earlier 1.0.x and test20 build
(`adb install -r <apk>`). Do not uninstall or clear data. Back up first.

## Why the phone could not join

Both apps already ran the same multiplayer code. The phone was almost certainly on mobile data
(its public address is in a mobile-carrier range and no router answered UPnP). The carrier gives every connection its own
public port, and the BIG CTF host's router most likely only accepts replies from the exact
port it talked to. So the direct connection could not open, even though the
host answered the phone's request every time. The Quest's home network keeps
one port, so it connected in under a second. The phone joined another host
(Wizard) fine. There is no relay server, so the fix for that host is **Wi-Fi**.

## Changes (both APKs)

1. The log now names each join stage: 1 asking the host, 2 opening the direct
   connection (with the host's addresses and this network's NAT type), 3
   connected. A failure says why. It also records whether the device is on
   Wi-Fi or mobile data.
2. The in-game browser follows the join and shows what is happening and why it
   failed, for example "No direct path to this host: your network (often mobile
   data) and its router both block it. Try Wi-Fi." Before, it showed "Host did
   not answer" after a fixed 30 s.
3. No more red "event handler 'start server if none advertised' failed" lines
   when you press A while a join is in progress.
4. An invite opened before Internet play has started is no longer logged as
   "ignored" (it never was ignored).
5. Packaging now refuses an APK pair whose networking differs, and a test keeps
   Quest-only code out of networking files.
6. **Quest: the crosshair moves at the headset's frame rate.** On foot it was
   placed from the game's 30-per-second simulation (aim, camera, hand), so it
   stepped behind the smoothly moving gun and scenery. It now follows the
   controller every frame, and still marks where the shot goes.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test20e.apk` | 28,080,771 | `efcf6e67593b7fc5141ca6d054ba6251f62bfbfcbd13a492290365177a25c457` |
| `HaloCE-Android-test20e.apk` | 26,073,652 | `08b42aef08e5fc7a8ccaeea3a7db3cf6317d97da0dbf88243b27bb56349cd8fd` |

Runtime source `4e7e1e4a415727fdefdfe91ad3d1eb61d6968c68`; later commits are documentation only.
Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. Built
serially from a clean tree; payload, signing and 16 KB alignment verified.

## Checks performed

- 21 runner suites pass, including new `test_test20e_network` and `test_test20e_reticle`:
  - 60 networking source files have no VR-only branch;
  - networking Java, permissions and `network.*` defaults are shared;
  - the stage logging is present.
- `test_test19_network_browser` now also simulates the join stages.
- Cache formats: 127 passed, 4 missing-fixture skips.
- Packaging verified:
  - The two APKs have the same entries except the OpenXR loader.
  - They have identical networking strings in the game and host libraries, and
    identical app classes.
  - The join-stage and network-type logging is present in both.
- **Not done:** no phone or headset session.

## Please test

1. **Phone on Wi-Fi** (the same Wi-Fi as the Quest): in-game browser → the BIG
   CTF. It should join. Send the log: it should say "Network: Wi-Fi", "keeps
   one public port" and "stage 3/3".
2. **Phone on mobile data**, same server: the browser should show "Host
   answered. Opening a direct connection…", then after about 90 s "No direct
   path … Try Wi-Fi.", with no red lines. Send that log too.
3. **Quest:** join any server as before; the log shows all three stages.
4. **Quest crosshair:** on foot, sweep the gun slowly and quickly across the
   scenery and fire at a few targets. The crosshair should glide with the gun,
   and shots should land on it.
5. Avoid **Y = Create Game** in the server list unless you want to host: it
   starts your own lobby, which is what happened at 11:40:57 and 11:44:16.
