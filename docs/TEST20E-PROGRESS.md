# Test20e checkpoint: Quest/Android multiplayer parity and join diagnostics

Updated 2026-10-04. Private candidate **1.0.2 / code 25**, branch
`test20-safe-upload-performance`. Builds on [TEST20D-PROGRESS.md](TEST20D-PROGRESS.md)
(gun anchoring, left-handed mode, simplified settings; owner: "all right,
great"). No release without explicit owner approval.

## Evidence (owner, 2026-10-04; raw files kept private)

| Item | Device / build | Finding |
| --- | --- | --- |
| Log 11:39:53 | Android flat, moto g stylus 5G (2022), test20d code 24 | Public address 166.172.186.62 (a mobile-carrier range). STUN: two servers saw **different ports** (46845, 21622): "this network's NAT gives each destination its own port". Joined host 122f9b1c2e16 (the BIG CTF): signalling worked ("reaching host" at 11:40:05.687), then "could not connect" exactly 30.0 s later (11:40:35.698); repeated every 30 s until 11:42:55 ("no answer from the invite's host", which was wrong: the host had answered five times). "UPnP: no UPnP router on this network". The same phone **did** join host 8e738407bfe9 (Wizard, 15 players) in 0.35 s at 11:41:05. |
| Log 11:43:27 | same phone | Launcher "Multiplayer join requested: the BIG CTF"; new public port pair 42256/57992 (strict again); same failure. The Y (Create Game) button then started a local lobby at 11:44:16 (also at 11:40:57). |
| Screenshot | same phone | Red "event handler 'start server if none advertised' failed" lines under the System Link list. |
| Log 11:42:41 | Quest 3, test20d code 24 | Public address 108.76.107.75; both STUN servers saw **port 46236** (lenient NAT). Joined host 122f9b1c2e16 at 75.129.197.163:44308 in 0.6 s, then the 36-player BIG CTF. 57–71 fps. The same red handler lines are logged (11:42:47) when A is pressed while connecting. |
| Video 11:45:33 (29 s) | Quest, a30 | Anchored assault rifle and pistol in play; nothing networking-related. |

## Cause

Both devices ran the same code. The difference is the network:

- The phone was on a carrier NAT that maps each destination to a new public
  port ("strict", or symmetric). The host 122f9b1c2e16 filters unsolicited
  packets per port, and the transport has no relay, so no packet from either side
  reached the other within the 30 s hole-punch window. The failing stage was the
  **direct UDP connection (stage 2)**: discovery, signalling, keys and the
  invite all worked, and the version check was never reached.
- The Quest's home NAT keeps one public port for every destination, so the
  same host's packets reached it immediately.
- The phone reached a different host whose router is lenient or forwards a
  port, which shows that its networking works.

No protocol, version, authentication or dependency difference is involved.

## Parity audit (Quest vs Android)

| Area | Finding |
| --- | --- |
| Native networking sources (`p2p*.c`, `xnet.c`, `posix_net.c`, `posix_upnp.c`, `network_browser.c`, `source/networking`, `source/bungie_net`; 60 files) | Identical for both builds. No `HALO_VR` branch; the `HALO_ANDROID` branches apply to both APKs. |
| Build (`tools/android_build.py`) | Same guest and host sources; the only flag difference is `-DHALO_VR=1` (and the OpenXR include/loader). miniupnpc is in both host libraries. |
| Java (browser, launcher, co-op/PvP, network settings, listings) | One `main` source set; the `vr` source set has only a manifest and the app name. No `.vr` checks in networking classes. |
| Manifests / permissions | INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE and CHANGE_WIFI_MULTICAST_STATE are in `main` (both). The VR manifest adds only the OpenXR permissions, queries and the immersive activity. |
| Config | Every `network.*` key is `_platform_all` with the same defaults (online, UPnP, STUN servers, tunnel port, public lobby, host public). |
| Delivered test20d APKs | Same entries except `libopenxr_loader.so`. Every networking string is the same in both guest images and both host libraries; the differences are VR rendering and touch/gamepad JNI only. Same app classes. |

Recent multiplayer work (test17 network data, test19 public browser and
directory, test20 performance) all lives in this shared code, so nothing reached
only one target.

## Changes (shared code; both APKs)

1. **Join stages in the log** (`p2p.c`):
   - stage 1/3: asking the host through signalling;
   - stage 2/3: the host answered with N addresses (listed); try number and
     this network's NAT class;
   - stage 3/3: direct connection open after N ms.
   - A failed try now says whether nothing arrived (a blocked path, with the NAT
     class) or packets arrived but did not open (a session or build mismatch;
     counted per peer).
   - The final message after 90 s distinguishes "the host answered N times but
     no direct connection opened" from "the host never answered".
   - A lenient NAT is now logged too ("keeps one public port for every
     destination").
2. **An early invite is queued, not "ignored".** An invite that arrives before
   Internet play has started now says it will be joined once Internet play is
   up, instead of the misleading "Internet play is off … the invite is ignored".
3. **The in-game browser follows the join** (`p2p_join_status`):
   - It shows "Asking the host…", "Host answered. Opening a direct connection
     (try N)…" or "Try N found no direct path; asking again…".
   - It gives up only when the join ends, with the reason. For a strict NAT the
     reason is "No direct path to this host: your network (often mobile data)
     and its router both block it. Try Wi-Fi."
   - Other limits: 45 s for a connected host whose game never appears, 120 s
     overall.
   - Before, it gave up at a fixed 30 s with "Host did not answer", even
     though p2p was still trying.
4. **No red spam.** The stock "start server if none advertised" fallback always
   declines while the browser owns the list (the list always has rows). Its
   on-screen warning is suppressed in that case only; the log line remains.
5. **The device's network type is logged** (`NetworkSettings.describe`): at game
   start ("Network: Wi-Fi, unmetered, internet validated" or "mobile data …")
   and with every launcher join.
6. **Parity guards:**
   - `tools/package-quest.py` refuses an APK pair whose entries (except the
     OpenXR loader), networking strings (guest and host) or app classes differ.
   - `tools/test_test20e_network.py` fails on any VR-only branch in networking
     sources or Java, on VR-only non-OpenXR permissions, on platform-specific
     `network.*` defaults, and on missing stage logging.
   - `test_test19_network_browser` now also simulates the join stages.

Not changed: the wire protocol, keys, STUN servers, timeouts, UPnP, the
directory, and every VR/touch-specific behaviour.

## Not possible without new infrastructure

A strict-NAT phone reaching a strict or port-restricted host needs either a
forwarded port on one side or a relay server. The transport has no relay, and
adding one needs a hosted service. Port prediction would not work here: the
phone's carrier picked random ports (46845/21622, 42256/57992). Wi-Fi is the
practical fix.

## Status

| Item | Implemented | Automatically verified | Confirmed on device |
| --- | --- | --- | --- |
| Quest/Android networking parity | Shared since the start | Yes (source test, APK parity in packaging) | Phone joined the Wizard host; Quest joined BIG CTF |
| Join stage logging and browser reasons | Yes | Yes (browser stage simulation, static checks) | No |
| Network type in the run log | Yes | Static | No |
| No red handler spam | Yes | Static | No |
| Gun anchor, left-handed mode, simple settings (test20d) | test20d | Yes | Owner satisfied with test20d |

## Device checks needed

1. Phone on **Wi-Fi** (the Quest's network): join the BIG CTF from the in-game
   browser. The log should show "Network: Wi-Fi", a lenient NAT line and stage 3/3.
2. Phone on mobile data: the same join should now show the stages and, after
   about 90 s, "No direct path … Try Wi-Fi." in the browser, with no red lines.
3. Quest: join as before; the log shows all three stages.
