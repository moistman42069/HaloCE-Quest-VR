# Test34 private candidate — Android and Quest VR

**Version:** 1.0.15 / Android code 44

**Networking:** OpenCE Build 147 / network 23

**Status:** private test candidate; not device-accepted or publicly released.

## Install

Use the matching flat Android or Quest APK from the Test34 delivery folder.
Install over the existing app to retain imported game files, saves, and
settings. Do not uninstall or clear app data. The two APKs are separate app
variants. Provide your own legally obtained game files; none are included.

## What changed

- Pointer hover now selects server rows in the in-game server browser. Stick
  and D-pad navigation remain available; lists with nested controls remain
  click-to-select.
- OpenCE Build 147 networking uses protocol version 23. Custom Edition maps
  are compared by map name and header checksum before loading when a nonzero
  checksum is available. The app's CE loader now uses the matching upstream
  tag schemas with Android/Quest-specific combined-file ranges and cache size.
- Build 147 capacity and safety updates cover widgets, light volumes, vehicle
  home tracking, CE linear bitmap pitch, bounded co-op enemy growth, missing
  Oddball spawn fallback, and host-only `bringto`.
- The owner-accepted Android touch behavior and VR settings design are carried
  forward. The existing upright co-op camera behavior remains; invalid axes
  safely skip that camera update.
- VR scope alignment now uses the same calibrated shot direction for the
  compositor layer and zoom view. Its physical center stays on the gun, uses
  the same 90 cm reach clamp as the rendered weapon, and the pistol/sniper
  scope offsets can be adjusted through ±30 cm. This applies to every zoomed
  weapon's scope shape, including the round and rocket-style overlays.

## Multiplayer and compatibility

Every peer must use network 23. Network 21 and 22 clients/hosts cannot join
this candidate. Select **Play → Multiplayer → Join Game → Server Browser** to
browse, or **Create Game → Internet/LAN** to host. For campaign co-op, select
**SINGLEPLAYER** in Create Game and then choose the mission, difficulty and
Server Setup options. The launcher remains for game files, updates, input
setup, help and logs.

The map checksum applies to Custom Edition cache headers and is not an Xbox
ISO/XISO revision detector. A zero checksum does not guarantee content
identity. Matching protocol versions do not guarantee a server is reachable;
maps, NAT, firewall and network conditions still matter. See
[Test34 multiplayer/upstream notes](MULTIPLAYER-BROWSER.md) and the
[upstream integration audit](TEST34-UPSTREAM-INTEGRATION.md).

## What to test

1. Launch flat Android and Quest VR; verify menus, touch/gamepad controls, and
   Safe geometry startup remain usable.
2. In the in-game browser, move the pointer across several server rows, select
   one, then verify stick/D-pad navigation still works.
3. Join a Build147/network-23 host using the same game data. If possible,
   compare matching and intentionally different CE map-header checksums.
4. Load campaign and multiplayer maps, transition a co-op mission, and report
   any crash, desync, missing map, or unexpected rejection.
5. Export logs from every peer and include headset/phone model, OS version,
   host/join role, map, game-data revision, network type and exact steps.

Send reports in the [Halo CE Decomp Discord](https://discord.gg/S9uSCKxKx) or
DM **@MeWhenINameMyself**. Automated tests do not substitute for this device
testing.
