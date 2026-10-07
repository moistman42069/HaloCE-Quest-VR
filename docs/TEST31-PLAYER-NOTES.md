# Test31 / 1.0.13 private testing guide

This candidate updates both Quest VR and flat Android. It is a private test
build, not a published release or a device-accepted replacement for v1.0.12.
The following changes take priority over the older public guide below. Final
APK/signature/artifact checks are pending at this source checkpoint; install
only the completed pair supplied with its matching delivery record.

## Install

Install the Quest APK on a Quest, or the Android APK on a phone/tablet, over
the existing project app. The original project signing certificate is retained.
Do not uninstall or clear data. Keep a backup of saves and imported game files.
Continue using the launcher to import/select your own game files and revisions;
no maps, ISOs or game assets from your installation are included in these APKs.

## In-game menus

OpenCE's full menu set is available inside the game: campaign, profiles,
multiplayer creation/joining, Server Setup, gametype editing, settings and
controls. The launcher remains available for game-file management, diagnostics,
APK updates and its existing browser/hosting shortcuts.

- **Quest:** point with the weapon hand and pull its trigger to select. The
  native menu buttons use their displayed Xbox letters: A selects, B backs
  out, X performs a displayed X action such as profile deletion, and Y performs
  a displayed Y action. With mirrored left-handed controls, left Y is the
  pointer Back button and right B also emits the native B action. These menu
  mappings do not change gameplay bindings.
  VR Settings is available from the main menu, the profile Settings hub and
  pause/settings routes. Existing VR pages and choices remain available.
- **Android touch:** tap menu items directly, including native keyboard keys.
  The gameplay overlay is suppressed while menus are active; Back remains
  available. Controller auto-hide policies still apply during gameplay.
- **Gamepad:** D-pad/sticks navigate, A selects and B backs out. Use the
  displayed action letters. An external mouse and keyboard also work; the
  keyboard/mouse controls page changes those devices, not tracked VR actions.
- **Text entry:** profile names, passwords and direct invite fields use a
  native on-screen keyboard. Its Done key accepts; Back/Cancel restores the old
  value. Server names are editable through the same keyboard.
  Long invite text scrolls within its visible field; password text is masked.
- **Settings:** OK saves the page; Cancel discards staged edits,
  and Defaults prepares that page's default choices before OK. If saving fails,
  the page stays open with a storage/retry message. Rows already saved before
  that failure remain saved; retry completes the remaining rows. The VR menu
  still applies its existing adjustments immediately. Sound enable/disable needs restart;
  volume and reverb controls can be changed in play.

## Browse and join

Open **Multiplayer**, then **SERVER BROWSER** under **JOIN GAME** for
OpenCE's signed public directory. **LAN** and **DIRECT LINK** are separate
join choices on that same screen. Games are listed by player population,
most populated first. Filters can include/exclude empty and full games, select
game type (including campaign co-op), team/FFA games, password status and known
map names. Refreshing/resorting keeps the selected game identified correctly.

The known-map filter checks the catalog; it does not prove that every required
file/revision is installed. Joining still validates the actual map. Public
directory entries do not provide measured ping; unavailable ping is not shown
as a fabricated latency. In **DIRECT LINK**, use **PASTE LINK** for a copied
OpenCE invite or **ENTER LINK** to type it with the native keyboard. Existing launcher
direct-connect options remain available.

## Host campaign co-op or PvP

1. Open **Multiplayer > Create Game > Internet** (or LAN for the local network).
2. On the map chooser, select **SINGLEPLAYER** (or **CUSTOM SINGLEPLAYER**)
   for network campaign co-op, then choose its level and difficulty. Choose
   **MULTIPLAYER** / **CUSTOM MULTIPLAYER**, then a gametype, for PvP.
3. Use **Server Setup** to choose the name, player limit, public/private listing
   and other applicable settings. Public Internet games appear in the browser;
   private games use their invite. Passwords are supported for public games.
4. Campaign settings include friendly fire, player collision and extra-enemy
   scaling. PvP exposes its gametype/team/player/item/vehicle rules. Save custom
   gametypes to reuse their additional options.
5. Start the game. Have the other device refresh its Internet/LAN browser or
   use your invite. The game continues running while network players use menus.

The engine offers co-op limits from 2 through 128 (16 initially in in-game
Server Setup). This is not proof that a Quest can host 128 players smoothly.
Begin with a small group. The separate **CO-OP CAMPAIGN** item asks for a
second local profile and starts the upstream local split-screen route; use
**CREATE GAME > INTERNET/LAN** for co-op across devices. Local split-screen
does not create multiple independently tracked VR views on one Quest.

## Network and game compatibility

This pair uses **OpenCE Build 145 / network 22**. Peers must use a compatible
network-22 build. v1.0.12's network 21 is incompatible; everyone in a test
session should update. Source integration preserves the project's VR-avatar
extension without requiring it from unmodified OpenCE peers.

Build 145 identifies Custom Edition maps with `custom_maps\<name>` and reports
missing maps explicitly. A similarly named Xbox map is not a replacement for
a missing Custom Edition map. The app retains its reviewed Xbox/PAL/CE/.yelo
loading paths; this is not a promise that arbitrary modified maps or different
revisions are mutually compatible. Use matching files/revisions with the host.
Manage installed sets through launcher **Game files & versions**.

Additional bounded NAT probes may help some mobile-data/VPN joins, using the
existing OpenCE packet format. They cannot guarantee traversal of random
destination-dependent ports or unadvertised addresses. If a join stalls, try
Wi-Fi, disable the VPN, or use a reachable host/port forwarding. No relay has
been added. Preserve both host and client logs for connection failures.

## VR fixes and optional settings

- Seated fire is no longer suppressed by the physical-weapons empty-hand rule.
  Test Warthog/stationary turrets and both VR and Xbox control layouts.
- Mounted reticles use the native muzzle/aim preview. Test against actual shots.
- **Vehicles > HOG GLASS** chooses Hidden or Visible for your first-person
  Warthog glass. Hidden preserves the preceding build's behavior. Third-person
  vehicles with right-hand steering remain the initial defaults. First-person
  vehicles still need device feedback; this change is not a new camera rewrite.
- Left-handed weapon-part winding handles the AR display's actual vertex
  influences, including queued transparent parts. Mixed/large parts keep the
  previous fallback; test both hands and other weapons.
- Video settings now connect to shadow-map resolution, optional per-pixel
  lighting and anti-aliasing. Defaults remain 128, OFF and OFF respectively.
  Android offers FXAA and MSAA 2x/4x where supported. These consume extra GPU
  time/memory; start at defaults. VR resolution/refresh/effect presets remain in
  VR Settings; headset synchronization is controlled by OpenXR.
- Separate master/music/effects volume, optional room reverb (OFF initially),
  live high-resolution HUD/text and scoreboard presentation settings work
  through the imported menus. While holding the scoreboard, D-pad up/down or
  the right stick scrolls long player lists; mouse wheel/Page Up/Down also work.

The existing body/hand/animation/grip behavior, Safe VR geometry, Normal flat
geometry, touch/controller settings and gameplay bindings are preserved. Manual
reload and the larger hand/world/NPC interaction requests are a later phase;
they are not included in this candidate.

## Updates, logs and feedback

Use launcher **Versions & compatible updates** for validated project APK
updates. The Android in-game update row reads **USE LAUNCHER** and explains
this route; it does not install desktop OpenCE binaries or replace the running
game's components.

Report through [the support server](https://discord.gg/S9uSCKxKx), the
[Flat2VR Discord](https://discord.gg/flat2vr), or **@MeWhenINameMyself**.
Include device/OS, APK version, selected game set/revision, map, host/client role,
network type, reproduction steps and logs from **Download/HaloCE**. Avoid posting
private invites or other personal details publicly.
