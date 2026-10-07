# Test32 private candidate — Quest VR and Android

Version 1.0.13 / Android code 42. OpenCE Build 145 / network 22.
This is a private test build, not a new public release.

## Install

Install the matching Quest or Android APK over Test31c or the existing public
app. Keep the app installed to retain imported game files, saves and settings.
The original project signing certificate is required and verified when packaging.
Quest and flat Android remain separate apps; use the correct APK for each device.
Users still supply their own supported game files. Existing game sets remain.

## Changes to test

- The launcher directs multiplayer and online campaign co-op to the OpenCE
  in-game menus. It retains game-data management, updates, input setup, help
  and logs. See the launcher’s multiplayer/co-op guide for browsing, creating
  a server, direct links, passwords and troubleshooting.
- Create Game's category arrows have larger, aligned click targets. Use the
  left/right arrows to switch **MULTIPLAYER / SINGLEPLAYER** (and available
  custom categories). Stick/D-pad navigation and other menus stay as before.
- Vehicles recenter on entry and exit. Test leaning in a moving co-op passenger
  seat as well as driver/gunner seats, in first- and third-person views.
- VR Settings → Vehicles → TURRET AIM selects Right Hand (default), Left Hand,
  Head or Stick independently of driver STEERING. These mean physical hands,
  independent of which hand holds a weapon. Test mounted turrets and gunner seats.
- HUD gestures require a steady gun-hand hold by its own temple for about
  0.3 seconds; a buzz confirms. Withdraw clearly for at least a quarter second
  before repeating. HUD → Shown/Hidden and Head Tap → Off remain available.
  The flashlight gesture stays unchanged.
- The accepted circular Android touch layout and optional look-without-LOOK-pad
  behavior are preserved. The accepted VR settings design and glass toggle remain.
- **Safe geometry is the default on both Android and Quest.** This supersedes
  the earlier flat Android Normal default. The launcher still lets you choose
  Normal explicitly; restart after changing geometry compatibility.

Use the launcher **Versions & updates** for validated APK updates. The native
menu's **USE LAUNCHER** message points to this existing updater; do not replace
individual networking files with arbitrary upstream executables.

Vehicle handle grabbing is deferred at the owner's request. It is not included.
First-person vehicle comfort still needs headset testing; third-person remains
the default. The existing per-vehicle position and driver horizon options remain.

## Network and support

Match OpenCE network 22. The upstream latest release/main were checked before
this pass and still resolve to Build 145. Older network versions cannot join.
All peers need the map/revision/content required by the server; a listed server
does not guarantee matching game content or reachable NAT. Existing networking
behavior is preserved. Test co-op entry/exit and vehicle role swaps with both peers.

For a problem, provide exported launch logs, the installed build, headset/phone,
host versus joiner, vehicle/seat/view mode, relevant settings and a short clip.
Report in [the support Discord](https://discord.gg/S9uSCKxKx) or DM
**@MeWhenINameMyself**. Avoid posting private invitations or network details publicly.

Automated checks and build verification do not establish device acceptance.
Test32 device results are pending.
