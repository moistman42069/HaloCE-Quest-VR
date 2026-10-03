# Halo CE VR on Steam Frame: architecture and status

Historical Steam Frame notes below, preserved from the upstream VR work.
They are not Quest test9 acceptance results. For the active Quest candidate,
read [TEST9-PROGRESS.md](TEST9-PROGRESS.md) and `QUEST_VR_HANDOFF.md`.

This fork adds a VR build of the Android port for the Steam Frame. The headset runs Android
apps inside Lepton, a container, and the build uses OpenXR to talk to SteamVR. Desktop and phone
builds are unchanged: everything here is behind `configure.py --vr` (`HALO_VR`).

## Status (2026-10-02)

| Area | State |
| --- | --- |
| Build, deploy, OpenXR session | Done; played in the headset. |
| Menus and loading on a flat screen | Done; played. |
| Stereo gameplay with a HUD layer | Done; played. The HUD's alpha is made from its brightness. |
| Performance | **72 Hz held at 1.5× resolution (2592² an eye)**, played. Fixed: lens-flare occlusion reads that stalled the CPU on the GPU (now asynchronous), Mesa's trace markers, per-draw buffer maps (now persistently mapped). The game thread is busy 53% of a 72 Hz frame. |
| 90 Hz | Set in the Frame's display settings. The game thread needs about 7.3 ms of CPU a frame, against 90 Hz's 11.1 ms. **Not yet seen worn at 90.** |
| Hand-aimed weapons | Default (`vr.aim = "hand"`); verified unattended with synthetic hands. **Not yet played.** |
| Arm IK | Default (`vr.arms = "ik"`); verified unattended. **Not yet played.** |
| 3D cutscenes on a screen, fades | Default (`vr.cinema_3d`); verified unattended. **Not yet seen worn.** |
| Vehicles: first-person seats, stick steering | Built, **not yet run on the device** (the headset went offline mid-test). `vr.vehicle_view` "first_person" (default) or "chase"; `vr.vehicle_steering` "stick" (default), "head" or "hand". |
| VR-native controls, gestures, left-handed play | Built (`vr.controls = "vr"`, default; `"pad"` keeps the Xbox mapping). **Not yet run on the device.** |
| Aim smoothing when zoomed, haptics | Built, **not yet run on the device.** |
| Picture-in-picture scope | Built (`vr.scope`), **not yet run on the device.** |
| Far HUD drawn from the head | Built (15 m away, 10 m wide), **not yet seen worn.** |
| Menu laser pointer | Built, **not yet run on the device.** |
| Room-scale walking | Built (`vr.roomscale`, off by default), **not yet run on the device.** |
| VR settings in the pause menu | Built, **not yet run on the device.** |
| Comfort options, foveation | Not started. |

## Device facts (Steam Frame, Lepton 2.8.14, 2026-10-02)

- **Android:** Android 11 (API 30), arm64-v8a, 4 KB pages. Upstream's limit on 16 KB pages
  does not apply here.
- **GL:** OpenGL ES 3.2 is Mesa **Zink** on Turnip (Adreno 750). `GL_EXT_sRGB_write_control`
  is available.
- **OpenXR:** the runtime is SteamVR 2.17.10, found through
  `/vendor/etc/openxr/1/active_runtime.json`; the Khronos runtime broker is absent.
  - Eyes are 1728×1728, and the default refresh is 72 Hz.
  - Swapchain formats: `SRGB8_ALPHA8`, `SRGB8`, depth.
  - `XR_VALVE_frame_controller_interaction` is present.
- **Missing services:** Lepton runs without a clipboard service.
  `port/android/patches/sdl3-no-clipboard-service.patch` handles that in SDL3.
- **Storage:** `/sdcard/Documents` is the headset's `~/Documents`, which survives Lepton
  resets. Game data, `config.toml` and saves go to `Documents/HaloCE`.

## Build and deploy

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk JAVA_HOME=/opt/homebrew/opt/openjdk@17
python3 configure.py --lto=off --pgo=off --vr
ninja android_apk          # port/android/app/build/outputs/apk/vr/debug/app-vr-debug.apk
tools/steam_frame/extract_maps.py "Halo.iso" /tmp/halo   # once: maps out of your disc image
tools/steam_frame/deploy.sh --maps /tmp/halo/maps        # copy, install, start
```

**To play** on the headset alone, launch **HaloCEVR** from the Steam library. It is a Lepton
devkit title running `~/devkit-game/HaloCEVR/HaloCE-VR.apk`, and `deploy.sh` refreshes that
copy. To register it on another headset, copy the APK there, then run:

```bash
ssh steamos@<device-ip> 'cd ~/devkit-utils && python3 steam-client-create-shortcut --parms "{\"gameid\": \"HaloCEVR\", \"directory\": \"/home/steamos/devkit-game/HaloCEVR\", \"force_appid\": \"\", \"argv\": [\"HaloCE-VR.apk\"], \"env\": {}, \"settings\": {\"steam_play\": \"1\", \"compat_tool\": \"lepton\"}, \"lepton_args\": \"\"}"'
```

**The refresh rate** follows the Steam Frame's display setting: SteamVR offers the app only
the rate it is on.

**To develop**, start **Lepton Development** from the Frame's Steam library first. Logs:
`adb -s 127.0.0.1:5555 logcat -s halo`.

Ninja does not rerun Gradle when only Java sources changed (the SDL patch, for example). Run
`./gradlew -PhaloVr assembleVrDebug` in `port/android` in that case.

## How it fits together

**Host (64-bit, `port/android/host/host_xr.c`).** The host owns:
- the Khronos loader, 1.1.63, fetched from Maven Central with its SHA-256 checked;
- the instance and a GLES session on the game thread's EGL context;
- six swapchains: left eye, right eye, a quad (the flat screen or HUD), the hand's reticle, a
  fade to black, and the scope;
- controller actions for the Frame, Touch and Index profiles;
- recentring.

The guest calls seven functions (`host_imports_vr.list`) with plain structures
(`halo_android_abi.h`, layout asserted on both ABIs). Swapchain images go to the guest as GL
texture names, which it draws into directly.

**Guest platform layer (`port/linux/src/vr_frame.c`, `vr.h`).**
- **Frame protocol.** The runtime's frame is begun by whichever comes first: `vr_aim`
  (`player_control_update`), `vr_stereo_begin` (`main_game_render`) or `vr_present`
  (`D3DDevice_Present`). It is ended in `vr_present`, which replaces the window blit and swap,
  so `xrWaitFrame` paces the loop. Halo already interpolates its 30 Hz simulation to the display
  rate, so no display-time scheduler is needed.
- **Screen.** In VR the game draws its 640×480 screen at the eye resolution
  (`vr.resolution_scale` × 1728, through the existing `screen_scale`).
- **Flat frames** (menus, loading, cutscenes) copy the picture to an opaque quad floating ahead
  (`vr.screen_distance`, `vr.screen_width`).
- **Eye views.** An eye's view is the game camera's position plus the tracked eye offset (head
  reach clamped to 0.35 m; 1 world unit = 10 ft), turned by the VR heading. Its frustum bounds are
  `{tanL/A, tanR/A, tanD, tanU}` with a 90° vertical field of view and A = 4/3. That is exactly
  `render_camera_build_frustum`'s off-centre form.
- **Copies to swapchains** run with `GL_FRAMEBUFFER_SRGB_EXT` disabled. The game's pixels are
  gamma-encoded already.

**Game side (`port/linux/game/vr_render.c`, `port/linux/include/halo_vr.h`).**
- **Windows.** `vr_render_windows` turns `main_game_render`'s single player window into four
  windows: left eye, right eye, HUD, console. While a hand-aimed weapon is zoomed it makes five:
  left eye, right eye, scope, HUD, console. `render_frame` then renders them in its own window
  loop. `render.frame_index` advances once per frame, and each eye has its own `window_index`, so
  lens-flare occlusion and fog history stay per eye.
- **Eye resolve.** `vr_render_window_end` copies each eye's back buffer into its swapchain image.
- **HUD pass.** It clears to transparent and draws only `interface_draw_screen`, the screen
  flash and the UI widgets. `vr_present` shows that image head-locked with alpha, far away
  (`vr.hud_distance` 15 m, `vr.hud_width` 10 m, about 37° across, as HaloCEVR's), so the eyes
  needn't refocus between it and the world.
  - It is drawn from the head's camera, with frustum bounds matching the panel's field
    (`vr_hud_bounds`). Nav points and friends' names are projected from where the eyes are, so
    they sit over what they mark (not where the hand points).
  - The motion sensor turns with the head (`vr_render_motion_sensor_yaw`), as the HUD does.
- **Once per frame** (left eye only): the sky's animation phase (`render_sky.c`), weather
  simulation, glow particles, and the first-person weapon's pose. The weapon is posed from the
  head between the eyes. The fog's screen layers are left out of the eyes.
- **Head aim.** `vr_player_control_facing` (in `player_control.c`) sets the player's facing to
  the head's direction turned by the heading.
  - The right stick turns the heading, not the game: `vr.snap_turn` (30°) or
    `vr.smooth_turn_speed`.
  - Pressing both sticks recentres.
  - When the game turns the player itself, the heading follows.
  - View magnetism is off while the head aims.

**Hand aim (`vr.aim = "hand"`).**
- **On foot.** The right controller's aim pose sets the facing. Shots, grenades and melee follow
  the aiming vector.
  - The left stick is turned to move relative to the head.
  - In local games shots start at the hand, through `unit_adjust_projectile_ray`, unless a wall
    stands between the hand and the unit's eye.
- **Weapon model.** It is posed from a camera at the grip minus `vr.weapon_offset_*` (in the aim
  frame).
- **Reticle.** The HUD crosshair is hidden. A reticle quad is drawn where
  `collision_test_vector` along the hand's ray meets the world.
- **Seats.** In vehicle and turret seats the head aims.

**Input.** The headset's controllers merge into the first Xbox pad (`xinput_sdl.c`). Each frame
`layout_controls` (`vr_frame.c`) builds that pad from the controllers by `vr.controls`:
- `"pad"`: the Frame controllers map one-to-one onto the Xbox pad (A/B/X/Y, bumpers as
  white/black, d-pad, view/menu as back/start).
- `"vr"` (default), a VR-native layout from each hand's own buttons (`hand_buttons` in the frame):

  | Input | Action |
  | --- | --- |
  | Weapon hand's trigger | Fire |
  | Off hand's trigger | Zoom (the scope) |
  | Right A | Jump |
  | Right B | Action / reload |
  | Right X | Switch grenades |
  | Right Y | Switch weapons |
  | Right stick click | Melee |
  | Weapon hand's bumper | Throw a grenade |
  | Off hand's bumper | Flashlight |
  | Left stick | Move; click to crouch |
  | Right stick | Turn |
  | Menu | Pause |
  | View | Back; held 1 s, recentre (with a buzz) |

While the head or hand aims, the right stick is consumed for turning.

**Gestures** (`update_gestures`, either layout; injected in `handle_one_player_input`):

| Gesture | Does | Setting |
| --- | --- | --- |
| A hand swung up or down fast | Melee | `melee_speed` (2.5 m/s) |
| Off hand at the side of the head | Flashlight | `flashlight_distance` (0.2 m) |
| Head lowered below the height at the last recentre | Crouch (held) | `crouch_height` (0.15 m) |
| Weapon hand's grip at a shoulder | Switch weapons | `holsters` |
| Off hand's grip held (with the gun) | Two-handed aim: the gun points from the weapon hand to the off hand | `two_handed` ("grip", "auto", "off") |
| Palms together, gripping | Swap the weapon hand | |

`vr.left_handed` starts with the gun in the left hand; the first-person model is drawn
mirrored (`halo_vr_mirror_winding` flips the triangles' winding).

**Weapon feel.** When zoomed, the aim is eased toward the hand's (`steady_aim`, after
HaloCEVR's half-life formula), steadying the scope. Shots buzz the weapon hand by weapon (and the
off hand when two-handed), scaled by `vr.haptics`.

**VR settings in the pause menu** (`port/linux/game/vr_menu.c`). Halo's menus are widget
tags in each map, so when a level's tags load the VR build adds its own, cloned from the solo
pause menu's: same font, colours, buttons and boxes.
- **The pause menu** gets a fifth item, VR SETTINGS. Its button hints (B back, A select) move
  from under the list to under the mission objectives, making room.
- **VR SETTINGS** is the pause menu's backdrop and boxes with nine settings in two columns:
  controls (VR / Xbox), aim (hand / head), gun hand, turning (snap 30 / snap 45 / smooth),
  room-scale, scope, vehicles (inside / chase), steering (stick / head / hand), cutscenes
  (3D / flat).
- **Changing a setting:** A or right steps it on, left steps it back, and B returns to the pause
  menu. The laser pointer clicks them too.
- **Saving:** each change is written into `config.toml` (`config_write_*`) and taken up at once
  (`vr_reload_settings`).
- **How the tags are added:** `cache_file_add_tag` puts tags made in memory after the map's own,
  in a copy of its tag table. A button's text comes from code (game data input function 41), and
  its changes run event handler functions 102 and 103, one past the end of each table.

**Menus' laser pointer** (`vr_ui_pointer`, behind `halo_ui_pointer_update`). The weapon hand
points at the screen the menus are on, as the desktop builds' mouse does: the flat screen, or
in stereo (the pause menu) the HUD's panel. Its trigger clicks (with a tick of buzz), the right
B goes back, and a dot on the reticle's layer shows where it points. The pad's buttons still work.

**Room-scale** (`vr.roomscale`, off by default; after HaloCEVR's). Each tick on foot,
`biped_update_moving` moves the player's collision pill by how far the head walked from where
the player stands (`vr_room_step`), with `collision_move_pill`, so a step into a wall slides
along it as walking does. Then that place to stand moves to the head.
- The whole step is taken even where a wall stopped the player. The view stays with the player
  rather than in the wall, and the room and the game drift apart; recentre to line them up.
- The eyes lean from that place, blended between its last two ticks as the game's camera is
  (`head_offset`). Walking then has no added latency and no judder at the 30 Hz ticks.
- Vehicles, cutscenes, scripts holding the player, death and network games hold it. Walking
  resumes from wherever the head is then, as does a jump of more than 0.5 m in a tick (tracking
  lost, a recentre).
- `vr.diag_walk_speed` walks the synthetic head ahead and logs how far the player went each
  second.

**Scope** (`vr.scope`, with the hand aiming). While zoomed:
- A pass between the eyes and the HUD (window 2, a repeat pass) renders the view along the gun.
  The camera is the hand's aim, rolled with the gun and kept out of walls. Its field is the middle
  of the game's zoomed one: half its height for a round sight, the sniper rifle's wide rectangle
  for the sniper.
- It draws into a square at the corner of the back buffer, as large as the scope's image (768²),
  so its cost scales with the scope, not the eyes. It has no HUD, fog screen or mirror, and the
  first-person gun is left out.
- `vr_resolve_scope` copies it through a mask (disc or rounded rectangle, a darker rim, a thin
  cross) into the scope swapchain. The image is shown on a layer held at the gun, at HaloCEVR's
  per-weapon offsets (pistol, sniper rifle, rocket launcher), `vr.scope_size` across.
- The eyes are never zoomed: the first-person gun stays in the hand, and the HUD layer leaves out
  the zoom mask.

## Measuring without wearing the headset

- `vr.force_render` renders stereo with the headset in standby. It uses a synthetic head and
  hands: the head is turned by `vr.diag_yaw`, the right hand by `vr.diag_hand_yaw`.
- `vr.dump_frame` and `vr.dump_cinema_frame` write the eyes and HUD of a gameplay or cutscene
  frame, and the scope when one is shown (`vr-scope.bmp`). A dump logs the aim state (seated or
  on foot, hand or head, yaws).
- `vr.diag_zoom_seconds` zooms in that long into play, switching first to a weapon that zooms.
  `vr.diag_two_handed` holds the synthetic left hand on the gun.
- `vr.timing` logs where a frame's time goes (`[vr-frame]`); `vr.timing_gpu` waits for the GPU
  to time it separately.
- `debug.telnet_console` opens a script console on 127.0.0.1:2323. Reach it with
  `adb forward tcp:2323 tcp:2323`. Useful commands: `map_name levels\a30\a30` loads a level,
  and `cinematic_skip_start_internal` / `cinematic_skip_stop_internal` skip its intro.
- `simpleperf` from the NDK runs in Lepton (`adb push` it to `/data/local/tmp`) and profiles the
  game thread. Threads' CPU time: `/proc/<pid>/task/*/stat`.
- Large copies over SSH time out while the game runs; use `adb pull`.

## Settings (`config.toml`, `[vr]`)

`enabled`, `stereo`, `resolution_scale` (1.5), `refresh_rate` (90), `world_scale` (0.328084 units/m),
`cinema_3d`, `cinema_separation`, `cinema_convergence`, `cinema_distance`, `cinema_width`, `arms`
("ik" / "hidden" / "animated"),
`screen_distance`, `screen_width`, `hud_distance`, `hud_width`, `aim` ("head"/"hand"),
`weapon_offset_right`/`_up`/`_back`, `snap_turn`, `smooth_turn_speed`, `vehicle_view`,
`vehicle_steering`, `controls` ("vr"/"pad"), `move_relative` ("head"/"left"/"right"),
`two_handed`, `left_handed`, `melee_speed`, `flashlight_distance`, `crouch_height`, `holsters`,
`haptics`, `scope`, `scope_size` (0.06 m), `roomscale` (false).

Diagnostics:
- `probe_seconds`: dim colours in each eye.
- `force_render` + `diag_yaw`: synthetic head with the headset in standby.
- `dump_frame`: writes `vr-eye0.bmp`, `vr-eye1.bmp` and `vr-hud.bmp` to the data folder.

`tools/steam_frame/deploy.sh --config vr.KEY=VALUE` edits these on the headset.

## Known gaps and next steps

- **Scope.** Its offsets and size are HaloCEVR's starting points and need tuning in the headset.
  Its reticle is our own cross, not the game's (the HUD isn't drawn into it). With the head
  aiming (`vr.aim = "head"`) a zoom shows nothing.
- **Gesture thresholds** (melee speed, duck depth, holster spots) are HaloCEVR's defaults and
  need tuning worn.
- **Vehicles.** `vr.vehicle_view = "first_person"` makes the director treat every seat as first
  person, which hides your own body. The eyes sit at your character's `head` marker. A seat's
  camera marker is the chase camera's place, so it isn't used.
  - The view turns with the vehicle's yaw only, keeping the horizon level. A passenger seat
    facing aside (the Pelican's) keeps the turn it had when you sat down.
  - The driver's right stick steers as in flat Halo, and your head only looks. Gunner seats aim
    with your head, and the handheld weapon is hidden in driver and gunner seats.
  - `vr.diag_drive_seconds` seats you as a driver for unattended tests; spawn a vehicle first
    with `cheat_all_vehicles`.
  - Untested on the device.
- **The HUD** is a flat panel locked to the head. Its image is the quad swapchain (1280×960,
  about 34 px a degree at the default size), shared with the flat screen.
- **Existing `config.toml` files** keep the HUD's old 1.5 m / 1.4 m (the file holds every key):
  set `vr.hud_distance = 15` and `vr.hud_width = 10` there.
- **Comfort options** are missing: no vignette, no seated or standing height.
- **Map loads** block the game loop. SteamVR shows its own loading state while one runs.
- **Battery.** The Frame discharges even on the Mac's USB.

## Credits

The controls, gestures, aim smoothing, haptics and scope follow the designs of LivingFray's PC
mod [HaloCEVR](https://github.com/LivingFray/HaloCEVR), re-implemented here for the decompiled
game.
