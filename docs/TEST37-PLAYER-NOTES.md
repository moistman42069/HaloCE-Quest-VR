# Test37 player notes - private candidate

**Candidate:** 1.0.18-test37 / Android version code 47 / OpenCE Build 157 / network 24.
**Release status:** private test only. Public latest remains v1.0.16 / code45 / network23.

## Network choice and populations

Open **Browse multiplayer servers** or **Browse campaign co-op servers** on the launcher main screen. Refresh, then open **Network**. Reported players and servers are grouped by network version and sorted busiest first; individual rows also remain sorted by reported players. This is the network-version population selector.

Choose **All compatible networks** (11-24) or an exact version **11 through 24**. The default is **24**. This changes the native client's discovery and admission target for the next launch, as well as the launcher filter. It is not just a list filter. The choice is shared across both browsers and all imported game-data sets. Close the game before changing it; the running game keeps its startup choice.

**Hosting remains on network 24** in every mode, including signed public advertisements. Selecting an older target changes which hosts this client accepts; it does not downgrade a hosted game or make older clients understand network24 features.

| Host version/content | Client eligibility |
| --- | --- |
| 11-22, original Xbox-map PvP | Exact matching target or All compatible |
| 23-24, PvP or campaign co-op | Exact matching target or All compatible; compatible game files still required |
| Custom Edition maps | Host23 or host24 only; matching map/checksum required |
| Below11 or unknown future version | Visible if reported, but unavailable |

All compatible totals exclude unsupported versions, recognizable Custom Edition listings below23 and, in the co-op browser, versions below23. Recognizable old Custom Edition rows cannot be joined; native admission also checks the actual host content. Directory-wide totals can still include reported unavailable versions. Counts are catalog reports, not a guarantee of reachability or a census of private/LAN games. A refresh error means unavailable data, not zero population. Up to four HTTPS catalogs can be merged with duplicate invites removed; only the default ChupathingyCE/Delta catalog was verified as a public source in this pass.

The in-game browser remains the signed OpenCE MQTT + LAN browser and applies the startup client target. Its four MQTT brokers are discovery mirrors, not four separate game networks. Launcher HTTPS listings and in-game results can differ. Retail Halo PC/Custom Edition, MCC and retail Xbox networking are not supported by this selector.

PvP directory joins retain the installed map/game-set chooser. Campaign joins do not automatically select a matching ISO revision. NAT/firewalls, stale invites, closed/full hosts, passwords, maps and revision differences can still prevent a join. Original/Rev1/Rev2 image comparisons await the owner's files. Backward compatibility needs device cross-play tests; this candidate does not certify every historical server or campaign setup.

## Preserve prior behavior

The previous candidate, **1.0.17-test36**, remains preserved. Test37 retains its Safe geometry defaults, launcher font/ISO guidance, accepted VR/mobile controls, saves and diagnostics. The public 1.0.16 empty-server log predates Test36's broker-ready and listing-rejection diagnostics; it cannot establish the phone's exact discovery failure.

Two-hand aim centering diagnostics are unchanged.

Scope, aim, turret and vehicle behavior remain unchanged without device evidence.

A Halo-inspired launcher font is selectable.

## Device retest

1. Refresh both launcher browsers on Wi-Fi and mobile data; check population order and error states.
2. Select an exact target, close/relaunch, and confirm the log reports that client target while hosting still advertises24. Repeat with All compatible. Verify the choice follows a game-data-set switch.
3. Join representative original Xbox-map PvP hosts on older targets and on24. Test spawn, movement, damage, kills, vehicles, late join and reconnect; keep both peers' logs.
4. Test campaign co-op and CE maps on23/24 separately. Confirm older campaign/CE hosts are rejected clearly rather than loaded.
5. Test the in-game signed browser, LAN and direct invites independently of the launcher directory. Preserve the full Download/HaloCE log for an empty list or failed join.
6. Check Android touch and Quest pointer/controller navigation; Back must not change the saved target. Verify ordinary Play and existing input/VR features remain intact.

Automated checks and package provenance belong in TEST37-DELIVERY.md when complete. Device acceptance is still pending.
