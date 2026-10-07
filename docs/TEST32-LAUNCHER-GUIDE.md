# Test32 launcher and in-game networking guide

This is the current private-build flow, using the full OpenCE Build 145 menus
and exact network 22. See [Test32 player notes](TEST32-PLAYER-NOTES.md) for the
candidate scope and [the multiplayer guide](MULTIPLAYER-BROWSER.md) for context.
No new public release or device acceptance is implied.

## Start and join

Press **Play**, then **Multiplayer** in the game's main menu. Create/select a
profile if requested.

| Goal | In-game path |
| --- | --- |
| Public PvP or co-op | Multiplayer > Join Game > Server Browser |
| A host on the same network | Multiplayer > Join Game > LAN |
| A private/current invite | Multiplayer > Join Game > Direct Link |
| Host online | Multiplayer > Create Game > Internet |
| Host on the local network | Multiplayer > Create Game > LAN |
| Save/edit multiplayer rules | Multiplayer > Edit Gametypes |
| Internet/UPnP/clipboard options | Settings > Network Setup |

**REFRESH** requests current listings. Public games are ordered with the most
players first. Navigate with stick/D-pad controls (or MOVE on Android); the
list scrolls as focus moves. No separate pager is shown. Select a server or **JOIN
GAME**. A locked listing opens a password screen. A game already in progress
may first open a lobby preview, where **JOIN GAME** continues into the game.

**FILTERS** includes empty/full servers, game type, teamplay, password and map
catalog. Set **GAME TYPE = CO-OP** to find campaign games, or **ANY** for all
types. **APPLY** saves changes; **DEFAULTS**, then **APPLY**, resets filters.
Known Maps uses the local catalog, not map fingerprints or verified revisions.
Ping is unavailable before a connection is made.

## Host PvP

1. Choose **Create Game > Internet** or **LAN**.
2. Select **MULTIPLAYER** (or supported installed **CUSTOM MULTIPLAYER** maps),
   choose a map and gametype.
3. In **Server Setup**, set **GAME NAME**, **MAXIMUM PLAYERS** and game/player/
   item/vehicle/indicator/teamplay options.
4. Internet hosts choose **PUBLIC** for discovery or **PRIVATE** for invites
   only. A public game may have a **PASSWORD**.
5. Select **START GAME** to enter the lobby, then **START NOW** when ready.
   Keep the host running. Internet hosting copies an invite when available.

## Host campaign co-op

1. Choose **Multiplayer > Create Game > Internet** or **LAN**.
2. On the map screen, change the category to **SINGLEPLAYER**, choose the
   mission and difficulty. **CUSTOM SINGLEPLAYER** lists supported installed
   custom campaign maps; their presence does not prove mod compatibility.
3. Set the name/player limit in **Server Setup**. Campaign options include
   **FRIENDLY FIRE**, **EXTRA ENEMIES** (per additional player or multiplier,
   with the corresponding amount) and **PLAYER COLLISIONS**.
4. Select public/private listing and an optional public-listing password.
   **START GAME** opens the lobby; **START NOW** begins. Join-in-progress is
   supported. All peers need matching network versions and compatible files.

The player-limit choices reach **128**. This is a capacity option, not a
Quest/phone performance certification. Start with a small group; extra enemies
and high counts raise host load.

**The separate CO-OP CAMPAIGN entry is local split screen, not online hosting.**
It and ADD PLAYER cannot create independent headset views and are blocked on
Quest with guidance to the network route. Flat Android retains local
split-screen paths with separate controllers; device checks remain necessary.

## Invites and passwords

In **Direct Link**, use **PASTE LINK** for a copied `halo://join/...` invitation
or **ENTER LINK** for the in-game keyboard. A bare 64-digit invite code is also
accepted. Wait for the host to appear, select it, and choose **JOIN GAME**.
This is the native-port invite format, not a retail PC IP-address connector.

For Internet hosts, **INVITE LINK** in Server Setup copies the current invite
again. The host also copies it automatically when available. LAN hosts have no
Internet invite. Invite links grant access without the public-listing password;
share private links only with intended players. Expired saved invites require
a fresh link from the host.

**Launcher > Multiplayer & co-op guide > Saved invites** retains read-only
access to entries from both former launcher browsers. You can view/select/copy
them for Direct Link. No save entries or custom-directory preferences are
deleted. Custom directory settings are not automatically imported into OpenCE's
in-game discovery. Saved entries are not uploaded or fetched as part of this
guide. Opening an invite from another app still follows the existing app path.

Ordinary **Play** also retires abandoned one-shot host/join commands from an
older crash. Their contents are preserved under `launcher-history/requests-*`
in the active game set; saves, configuration and the saved-invite stores are
unchanged. A current explicit external invitation is retained, including one
that waited while game data was imported. Clipboard auto-join remains controlled
by the existing JOIN FROM CLIPBOARD setting.

## Input, data and troubleshooting

- Quest: weapon-hand pointer + trigger, or stick navigation/A; B backs out.
- Android: tap uncovered menu areas or use MOVE and the circular A/B buttons.
- Gamepad: D-pad/stick, A confirm, B back; left/right changes option arrows.
- Names/passwords/invites open the in-game keyboard. Accept the text when done.
- The launcher retains game-set imports/selection, data fingerprints, updater,
  device input setup, network recovery settings including a fixed UDP port,
  geometry settings, mod restore/recovery, offline guides and launch logs.
- **Geometry compatibility** now defaults to **Safe on both APKs**, including
  the first Android upgrade to this default. Selecting Normal explicitly is
  remembered. Restart after changing it. Safe may reduce performance; desktop
  renderer defaults are unchanged.
- Some failures involve ISO/revision/modified-file differences. Use **Game
  files & versions** before launch to select a compatible set. The browser does
  not infer authoritative Original/Rev1/Rev2 requirements or switch sets for you.
- A visible listing is not a reachability test. Check Internet Play, filters,
  firewall/router restrictions and current invites; try ordinary Wi-Fi if a
  VPN or mobile-data connection fails. There is no relay fallback.
- Use **Versions & updates** for validated port builds. Do not replace native
  networking files with arbitrary upstream executables.
- For problems, provide both peers' logs from **Download/HaloCE** where possible,
  build/network versions, devices, map/game set, host/join roles and connection
  types, plus reproduction steps. Use [support Discord](https://discord.gg/S9uSCKxKx)
  or DM **@MeWhenINameMyself**. Review logs for private invites before posting.

## Implementation and checks

The main launcher removes its former browser/host buttons, without deleting
legacy classes or user preferences. `LauncherHelp` exposes topic pages using
`InGameNetworkGuide`, and its saved-invite view reads the old stores without
editing them. Essential launcher tools and external-invite startup stay intact.

`tools/test_test32_launcher.py` checks guide labels/routes against the actual
XML, compiles all five guide pages with a different network-version constant
to verify dynamic version text, checks retained launch tools/read-only saves,
and compiles production Android and SDL Java against the Android SDK. It also
runs 55 checks against real launch-request archival and extracted production
launcher geometry policy plus the actual atomic config writer: both edition
keys, pre-migration choices, persistent Normal opt-out, unrelated-data retention,
repeat launches and failed archival.
It does not launch an app or prove device dialog, clipboard or network behavior.
Existing touch lifecycle and browser/parser suites remain separate regression
checks; the accepted touch/gameplay source is unchanged by this work.
