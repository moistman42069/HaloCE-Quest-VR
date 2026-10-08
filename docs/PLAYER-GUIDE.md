# Halo CE Quest VR + Android player guide

This guide describes the unpublished **test36 candidate / 1.0.17-test36 / OpenCE Build 157 / network 24**. It is provided for testing, not as a public release. For the current public build see [v1.0.16 release notes](RELEASE-1.0.16.md).

## Install and update

Use the Android APK for a phone/tablet and the Quest APK for standalone VR. On Quest, enable Developer Mode and sideload with SideQuest or ADB. Install over the existing project app so imported game data, saves and settings remain. Do not uninstall or clear app data. Supply your own supported Xbox Halo CE game files; none are included.

Open the launcher’s **Game files & versions** to import an ISO/XISO or extracted game folder, inspect the recognized cache build and select an installed set. You can import multiple sets and switch between them without replacing the original. The **Versions & updates** page checks the project's compatible releases and provides official upstream downloads separately. Upstream files are not applied blindly to the integrated VR/network runtime.

## Browse, join and host in game

The OpenCE multiplayer flow is in the game menus. Create/select a profile if prompted.

| Goal | Menu path |
| --- | --- |
| Join a public PvP or campaign game | **Play → Multiplayer → Join Game → Server Browser**; refresh and choose a listing |
| Join a nearby LAN game | **Play → Multiplayer → Join Game → LAN** |
| Join from an invite | **Play → Multiplayer → Join Game → Direct Link** and paste/enter the invite |
| Host PvP | **Play → Multiplayer → Create Game → Internet or LAN → Multiplayer → map → game type → Server Setup** |
| Host campaign co-op | **Play → Multiplayer → Create Game → Internet or LAN → Singleplayer → mission → difficulty → Server Setup** |

In **Server Setup**, choose the server name, player limit, public/private listing and password as needed. PvP also has match rules; campaign has co-op options. Start the lobby, invite players or publish it, then start the match when ready. The campaign player selector offers limits up to 128; start with a small group because the maximum is not a performance guarantee.

All players need **network 24** for this candidate, compatible maps/resources and a reachable network route. It cannot join network-23 sessions from public v1.0.16. Public listings do not relay traffic. NAT, firewall/VPN, mobile-data restrictions, Wi-Fi isolation, passwords, full lobbies and missing or different game content can prevent joining. If joining fails, record logs from both host and client and note the network type and selected game-data set.

The launcher no longer hosts or browses through its old server lists. It retains help, saved-invite access, game-data management, updates, controller/touch settings and logs. Copy a saved invite into the in-game Direct Link flow.

## Controls

### Quest Touch

- Left stick moves; right stick turns and, when held down, crouches by default.
- Weapon-hand trigger fires; off-hand trigger zooms.
- Right A jumps/confirms; right B reloads/uses. Left Y switches weapons; left X throws a grenade, and holding X changes grenade type.
- Left stick click toggles the reticle (visible at startup); right stick click performs native melee; clicking both sticks recenters.
- Weapon-hand grip handles physical weapons; the off-hand grip locks to the support point when the two-hand option is enabled.
- Bring the off hand to the left side of the head to toggle the flashlight when its gesture is enabled. Adjust or disable the reach in **VR Settings → Head Gestures → Flashlight**.
- Hold the gun hand by its own temple to toggle the HUD when enabled. A cycles co-op spectate targets or votes in a skippable cutscene.
- Point at a menu row and press the trigger. Thumbstick/D-pad menu navigation is available as well. B returns/back. Left-handed mode mirrors supported actions.

To put crouch back on left-stick click, open **VR menu → Controls → Page 2 → L Stick Click → Crouch**. Reassign the reticle on **Buttons** if needed.

### Android gamepad

The default Xbox-style mapping is: left stick move, right stick aim, RT fire, LT grenade, A jump, B melee/cancel, X reload/use, Y switch weapon, LB flashlight, RB grenade type, stick clicks crouch/zoom, and Start pause. D-pad or left stick navigates menus; A confirms and B returns. Controller labels can vary; use **Controller & touch settings** for face-button swap, dead zones, response, trigger threshold and vibration.

### Android touch

Use **MOVE + swipe** to move and aim, or drag **FIRE** to move, aim and fire together. Tap **HUD** while playing to reposition or resize touch controls and adjust opacity, color and response. Gyro aiming is optional and off by default. Touch visibility can be **Auto**, **Always show** or **Always hide**; Auto restores touch when a connected controller disconnects.

## VR settings

Open the pause menu and choose **VR Settings**. Use Next Page and Back to move between settings pages. Arrow controls decrease/increase values; A/right advances or confirms. **Legs + Arms**, **Safe geometry**, **Third Person vehicles** and **Right Hand steering** are defaults. First-person vehicle view remains experimental. Changes save; restart after changing geometry compatibility.

Settings include body/hand modes, fingers, hand/gun calibration, weapon grip and support grip, controls, gestures, HUD/wrist HUD, scopes, vehicles/seats, comfort, graphics, display and controller tracking corrections. Optical finger tracking is not used; fingers follow controller sensors. See [controls and options](CONTROLS-AND-OPTIONS.md) for exact defaults and the full menu inventory.

## Revisions, logs and support

For the best compatibility, use the original Xbox Halo: Combat Evolved XISO. Rev 1 and Rev 2 images can be imported, but are not recommended; different revisions may contain different game or map files and can prevent players from matching. The launcher recognizes supported Xbox cache format/build identifiers, but cannot determine every disc label from a filename or promise full-disc integrity. The server browser cannot automatically prove which ISO revision a host uses. SPV1 is experimental and unverified; file sizes fitting the current reader limits do not establish protected-map/resource/campaign support.

Each launch writes a detailed log under **Download/HaloCE** when Android allows; app-private storage is used as fallback. For crashes, failed joins or desyncs, share logs from each peer and include device/model, OS, app/network version, game-data set, map/mission, network type and reproduction steps. Contact **@MeWhenINameMyself** or the [Halo CE Decomp Discord](https://discord.gg/S9uSCKxKx). Remove private invite/device details before sharing.
