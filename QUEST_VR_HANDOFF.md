> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Quest VR port: handoff

State as of 2026-10-03. Read this before touching the VR code. CLAUDE.md
holds the standing rules.

Latest: `docs/TEST13A-DEFAULT.md` records the user's approval of Legs + Arms
and the requested VR-only default change. It overrides the test13 full default.

Active refinement: **docs/TEST13-PROGRESS.md**; test13 package provenance is in
**docs/TEST13-DELIVERY.md**. Test10 multiplayer, settings and
Downloads logging are user-confirmed. Test12 campaign implementation is compiled;
paired-device acceptance is pending: docs/CAMPAIGN-PROTOCOL-WIP.md. Follow
the newer checkpoint for current behavior; preserve this historical design.
User's test12 report confirms good room-scale leg following, but requests menu
overlap, shoulder/chest and arm snapping fixes. Test13 adds four local body modes
(full default) and negotiated observer avatars; see docs/NETWORK-VR-AVATARS.md.

For work after this original WIP snapshot, read
[`docs/TEST13-PROGRESS.md`](docs/TEST13-PROGRESS.md) first. It records the current
checkout, implementation progress, build results, and next action. Test13 is
packaged; await the owner's next device results before another candidate.

## What this is

A native Meta Quest 3 VR build of halo-ce-universal (the Halo CE Xbox
decompilation's Linux/Android port). On Android a 64-bit host (libmain.so,
SDL3, OpenXR) loads the game, a 32-bit arm64_32 guest ELF
(assets/halo_guest.elf, base 0x88000000). VR rendering is
astromaddie/HaloCE-VR's game-side code (CC0, merged in 60a2a311) plus a
Quest OpenXR host and many features added here. The headset owner sideloads
APKs and sends back logs and videos; no session has adb access to the device.

## Branches

- `quest-vr`: the last tested build, test8 (be7ec964). Device-tested: it
  launches immersive, the main menu is in 3D with a working laser pointer,
  campaign levels load and play, performance is about 72 fps on the Quest 3,
  audio is clean (0 underruns), and room-scale and arm-swing running work.
- `quest-vr-test9-wip`: the test9 candidate. The detailed test9 section below
  preserves the original design and starting WIP state. Its implementation
  checklist and current build results are in `docs/TEST9-PROGRESS.md`.
- `quest-vr-prototype`, `main`: upstream history. Don't rewrite them.

## Build

```
python3 configure.py --vr && ninja android_apk   # VR APK (com.halo.decomp.vr)
python3 configure.py && ninja android_apk        # flat APK, must keep building
```

- **Output:** `port/android/app/build/outputs/apk/vr/debug/app-vr-debug.apk`
  (VR) and `.../apk/debug/app-debug.apk` (flat).
- **Needs:**
  - clang and lld; clang must have the arm64_32 target, which builds the guest.
  - ninja, python3, JDK 17.
  - Android SDK with platform 35, build-tools 35, NDK 27.2.12479018.
  - Set `ANDROID_HOME` and `ANDROID_NDK_HOME`.
- **Native only:** `ninja android` builds just the host and guest, which is
  faster for checking the C compiles.
- **Signing:** test APKs have always been signed with the debug key in the
  original machine's `~/.android/debug.keystore`. An APK signed with any other
  key won't install over the user's current build without an uninstall, and
  an uninstall deletes their game data (Android/data/com.halo.decomp.vr). A
  new build machine (cloud, CI) needs that keystore copied in, or a
  signingConfig that points at it.
- **Original machine (maintainer workstation, WSL1 Ubuntu-24.04):**
  - The NDK's clang is wrapped to run through ld.so.
  - Commands go through scripts written to a scratch folder, because
    `bash -c` quoting fails.
  - Pipe `wsl.exe` output through `tr -d '\0'`.
  - Test APKs are copied to `<artifacts>\HaloCE-Quest-testN.apk`.
  - None of this applies to a normal Linux machine.
- **Check the APK contains the new code:** grep for new log strings in
  `unzip -p APK lib/arm64-v8a/libmain.so` and in
  `unzip -p APK assets/halo_guest.elf`.

## The test loop

1. The user installs the APK over the old one, and plays.
2. They send back the log, plus usually a YouTube video.
3. The log is at `/sdcard/Download/HaloCE/halo_log_<date>_<time>.txt`, a new
   file each run with the newest 10 kept. A copy is at
   `Android/data/<package>/files/halo_log.txt`. The game's own debug.txt is
   mirrored into it too.

Log lines worth reading:
- `[openxr] ...`: session states, the layers in use (`layers now: stereo hud
  pointer`, ...), interaction profiles.
- `[vr-perf]`: frames per second, time spent waiting on the headset vs the
  game's frame time, memory.
- `[audio] host: ... underruns`: the device side. `[audio] 10.0 s: ...`: the
  game's mixer.
- `[watchdog] no frame shown for N s`: every guest thread's stack. Symbolize
  it with `llvm-symbolizer --obj=halo_guest.elf 0x...`, taken from the same APK.
- `vr: settings: ...`: the settings in force, logged whenever one changes.
- `vr: first-person node N 'name' parent P`: the first-person model's bones,
  logged when the weapon's graph changes.
- `vr: the weapon hand holds ...`, `vr: the gun let go ...`: physical weapons.

Frames from a video can be pulled with yt-dlp plus a static ffmpeg
(`fps=1/3,scale=960:-2`) and viewed as images.

## Where things are

**Host (64-bit), `port/android/host/`:**
- `host_xr.c`: OpenXR. Swapchains are the eyes, quad (HUD/screen), reticle,
  fade and scope. Layers are composed in `host_xr_end_frame`, drawn in list
  order: the reticle goes under the quad unless `HALO_XR_LAYER_RETICLE_ON_TOP`.
  All enumerations ask for the count first.
- `host_sdl.c`: SDL bridge. Audio: the mixing thread runs the guest's
  callback one device buffer ahead (`audio_thread`), and the SDL device
  callback only copies.
- `host_main.c`: log files, environment, launcher markers. Marker files:
  `mods/custom_edition.on` sets `HALO_CUSTOM_EDITION`; `vr_menu_flat.on`
  sets `HALO_VR_MENU_3D=false`.
- `host_debug.c`: the frame watchdog and the stack sampler.
- `host_memory.c`: guest memory, and the SIGSEGV handler that logs the
  guest's frames.

**Guest↔host calls:** `port/android/host_imports.list`,
`host_imports_vr.list`, `guest/runtime/guest_host.h`, `guest_sdl.c`. A new SDL
function the guest calls needs a shim there, or the link fails.

**VR core (guest), `port/linux/src/vr_frame.c` and `vr.h`:**
- Poses: `view`, `to_halo` (OpenXR LOCAL, where x is right, y up, z back, to
  Halo's x forward, y left, z up, by the heading), `hand_view`,
  `vr_hand_world` (the grip pose: forward = −Z, up = +Y).
- Input layout: `layout_controls`.
- Gestures: `update_gestures` covers grips, finger curls, arm run, melee,
  flashlight, crouch, holsters and physical weapons.
- Presenting: `vr_present` (layers, fades), the menu pointer
  (`vr_ui_pointer`, `place_pointer`), the scope, settings
  (`vr_reload_settings`).

**Game-side VR, `port/linux/game/vr_render.c`:**
- Stereo windows: `vr_render_windows`.
- Cutscenes: `cinema_windows` (the 3D screen).
- Weapons: `vr_render_weapon_camera` places the first-person gun at the
  controller.
- Impact melee: `vr_render_impact_melee`.
- First-person arm IK: `vr_render_first_person_ik`, with `vr_solve_arm`,
  `vr_pose_fingers` and `vr_hand_out_of_walls`.
- Full body: `vr_render_body_matrices`.

**Other VR files:**
- `vr_menu.c`: the pause menu's VR SETTINGS, built from cloned widget tags
  added through `cache_file_add_tag` (in source/cache/cache_files.c).
- `vr_graphics.c`: graphics presets.
- `port/linux/include/halo_vr.h`: declarations for the game sources.

**Hooks inside the game's sources (`#ifdef HALO_VR`):**
- `source/main/main.c`: `vr_render_windows`.
- `source/render/render.c`: the passes, the HUD pass, the screen flash.
- `source/render/render_objects.c`: the full body.
- `source/interface/first_person_weapons.c`: IK call, gun visibility, gun draw.
- `source/game/player_control.c`: actions, drop and grab.
- `source/game/players.c`: `player_vr_grab_weapon`.
- `source/units/units.c`: `unit_vr_impact_melee`.
- `source/cache/cache_files.c`.

**Settings:** `port/linux/src/port_config.c`, all `vr.*` and `graphics.*`
entries, each documented, written to config.toml.

**Launcher (Java), `port/android/app/src/main/java/com/halo/decomp/`:**
- `LauncherActivity`: Play; Mods → SPV1; the main menu 3D/flat toggle;
  resetting settings.
- `ModInstaller`: SPV1's download, install and restore.

**Audio and Custom Edition:**
- `port/linux/src/dsound_sdl.c`: the mixer.
- `audio_codecs.c`: Ogg decoding and the Xbox ADPCM encoder.
- `port/linux/game/custom_edition_cache.c`: CE maps, and the `<map>.audio`
  sidecar at cache version 2.

## Gotchas learned the hard way

- **The game's allocator:** cseries.h maps malloc, free and realloc to the
  debug allocator. `free(NULL)` asserts, and so does freeing anything calloc'd
  or allocated by libc (calloc is not mapped). In game sources use
  malloc+memset. Buffers the codecs return are freed with `halo_audio_free`.
- **HaloCE-VR's code isn't trustworthy:** `vr_haptic` called itself forever
  (every vibration hung the game), and `cache_file_add_tag` called free(NULL).
  Review it before relying on it.
- **Xbox ADPCM blocks are 65 samples:** the header's predictor is sample 0,
  and the 64 nibbles follow it. Measured on real data.
- **Quest launch:** the launch intent needs the
  `org.khronos.openxr.intent.category.IMMERSIVE_HMD` and
  `com.oculus.intent.category.VR` categories. The game runs in the
  `:halo_game` process; the launcher is a 2D panel.
- **Duplicate gamepads:** the Quest also lists its controllers as SDL gamepads
  (vendor 0x2833). They're ignored while VR is active.
- **No storage permission:** writing new files to Download is allowed; a
  file another installation made can't be replaced.
- **Variadic logging:** a variadic `platform_log` call needs its prototype in
  scope on the guest ABI.

## test9: what the user asked for after test8

From the test8 video and log (the user's own words in quotes):

1. **Full body:** "the body is a bit mismatched".
   - In the video the body's own green arms, IK'd to the controllers, fill the
     view near the face.
   - Nodes hidden with scale 0 collapse each vertex to its own bone's origin,
     so triangles spanning bones become long dark or green slivers.
2. **Hands:** "hands dont move with wrist", "collide with walls", "fingers
   are peculiar", "move across guns/surfaces with alyx level finger
   reactions".
   - In full-body mode the first-person IK returns early, so it never stops
     the hands at walls, never makes them buzz, and never poses the fingers.
   - In arms mode the free hand only gets a position; its rotation follows
     the forearm.
   - The fingers add curl on top of the animation's grip, which gives a claw.
3. **Cutscenes:** "cutscenes not being in vr despite 3d being enabled". They
   show on a floating 3D screen. The user wants immersive cutscenes.
4. **Firing:** "guns dont fire ... i want guns to fire anyways". In physical
   mode the trigger was gated on the grip.
5. **Physical weapons:** "guns fall out of the hand unless you are holding
   grip". Holsters "dont seem to work". The user wants "proper sliders to
   adjust holster radius".
6. **A floating rectangle (seen, not mentioned):** the screen flash (shield
   damage, the cutscene fades) is drawn into the HUD pass, so it shows as a
   rectangle on the HUD panel.
7. **Menu overlap (seen):** in VR SETTINGS the right column's 5th row
   overlaps the button hints (B=CANCEL A=SELECT).
8. **Accidental weapon swaps (seen in the log):** gripping to hold your own
   gun picked up a weapon lying nearby (`player_vr_grab_weapon`, 35 cm
   radius from the shot origin).
9. "obvious fixes i shouldnt have to mention". Fix what you see without
   being asked.

### Done in quest-vr-test9-wip (compiles, untested)

**vr_frame.c:**
- **Firing:** the trigger fires whatever gun is in the hand. It is blocked
  only when the hand is empty.
- **Physical hand states:** the hand is `HAND_LOOSE` (the game put the gun
  there), `HAND_HELD` (gripped) or `HAND_EMPTY`.
  - A loose gun in play slips out after 2.5 s unless gripped (buzz at 1.2 s).
  - Letting go at a holster puts the gun away: `SWITCH`, then empty.
  - Letting go with the other hand on the gun passes it to that hand.
  - Letting go anywhere else drops it.
  - An empty hand gripping at a holster draws the ready weapon.
  - An empty hand gripping elsewhere grabs a weapon (`GRAB` action).
  - `vr_note_weapon(object index)` maps the game's weapon changes onto these
    states. Changes this side asked for are tracked with `pending_state`.
- **Holsters:** four zones (each shoulder, each hip) at `holster_places`,
  each reaching `vr.holster_size` (default 0.2 m). A buzz when the hand
  enters one, and log lines for switches.
- **New exports:**
  - `vr_hand_empty`
  - `vr_cinema_immersive`
  - `vr_head_local_yaw` (head yaw in LOCAL space; world yaw = heading + this)
  - `vr_view_blink`
- **vr.h:** the declarations for the above.

**port_config.c:** `vr.cutscenes` ("immersive" by default, or "screen" or
"flat") and `vr.holster_size`, plus updated docs for vr.weapons, vr.holsters,
vr.body and vr.fingers.

### Original remaining design (implementation status: docs/TEST9-PROGRESS.md)

**A. Game side, the weapon states** (vr_render.c and the game sources):

1. Call `vr_note_weapon()` every tick from `vr_render_actions`, passing the
   unit's current weapon object index:
   `unit_inventory_get_weapon(unit, unit->unit.current_weapon_index)`, or -1.
   **Until this is done, every weapon change is invisible to the hand state.**
   A grip released at a holster or a drop leaves the state at EMPTY for good,
   which blocks the trigger and cancels any grab.
2. `first_person_weapons.c`: skip the gun model's `render_model` when the
   hand is empty. Add `vr_render_first_person_gun_hidden()`, true when stereo,
   hand-aiming and `vr_hand_empty()`. Keep the hands model.
3. Grabbing (player_control.c and players.c):
   - Use the weapon hand's grip position, not `vr_render_hand_origin`. Add
     `vr_render_grab_point(unit, &point)` from `vr_hand_world(weapon hand)`
     seen from `unit_get_camera_position`.
   - A radius of about 0.25 m.
   - Only empty hands grab; the WIP already only sends GRAB from an empty hand.

**B. Hands** (vr_render.c, `vr_render_first_person_ik`):

1. **Keep the first-person arms in full-body mode.** Stop hiding them; only
   `vr.arms "hidden"` hides them.
   - When hiding, collapse every node of each arm to its upper arm's
     position, with scale 0 (one point, so no slivers).
   - Keep the gun (`frame gun` under `frame r wriste`) out of the collapse.
2. **Free hand**, for the off hand, and the gun arm too when `vr_hand_empty()`:
   1. Read the controller with `vr_hand_world`, giving f and u.
      Orthonormalize them. Let r = f × u. The palm P is −r for the right
      hand and +r for the left.
   2. Put the wrist target at grip − f·0.075 m. Stop it with
      `vr_hand_out_of_walls`, which should also return the hit plane's
      normal. Then run `vr_solve_arm`.
   3. Orient the hand. Build its frame from joint positions: F_b = wrist →
      middle knuckle, U_b = little knuckle → index knuckle (orthogonalized).
      Rotate the hand's subtree about the wrist by R = [f u f×u]·[F_b U_b
      F_b×U_b]ᵀ. This works whatever the bone axes are, and when mirrored.
   4. When pressed and the palm faces the surface (P·N < −0.2), rotate P
      toward −N by up to 85%, scaled by depth/5 cm. That lays the palm flat.
3. **Fingers**, posed outright rather than on top of the animation:
   - **Find the joints.** Each finger's joints come from the names ("thumb",
     "index", "middle", "ring", "pinky", or "finger0".."finger4"). The
     joint's place along the finger is how many of its ancestors belong to
     the same finger. The first-person arms' names are
     `frame l index low|mid|tip`, and the left middle's is
     `frame l middlelow`, with no space.
   - **Bend.** Each finger's base direction is wrist → knuckle with the palm
     component removed. Bend joint by joint toward P about base × P. Rest
     bends are 0.12, 0.15 and 0.10 rad; full curl adds 1.25, 1.6 and 1.1.
     Use `vr_rotation_between` (current bone direction → wanted) on each
     joint's subtree.
   - **The last joint** has no child. Use the axis of the middle joint that
     lies along the bone (|dot| > 0.8); if none does, skip it.
   - **Thumb.** Its direction runs from up (normalize(u·0.9 + f·0.3), a
     thumbs-up) to across the controller's face (normalize(f·0.75 + P·0.55 +
     u·0.1)) by its curl, with extra bends of 0.35 and 0.3 rad.
   - **Curls** come from `vr_finger_pose`: thumb, index, middle, ring+little.
   - **Alyx-like touch.** Test each finger from its knuckle to its tip end
     (`collision_test_vector` with `VR_HAND_TOUCH_FLAGS`, ignoring
     `object_get_ultimate_parent(player unit)`). Try curls {c, c/2, 0,
     min(c+0.4, 1), 1} until one is clear; if none is, keep the one with the
     greatest t. Pressed flat to something, fingers curled under 0.6
     straighten. Each finger touching adds to a light buzz (about 0.05 + 0.05
     per finger, 0.03 s); don't stack it on top of the pressure buzz.
   - Log the bones found once per graph.
4. **Two hands.** Keep the current rule: an off hand within 15 cm of its
   animated foregrip spot stays on the gun.

**C. Body** (`vr_render_body_matrices`):
- Stop solving the body's arms to the controllers.
- Collapse the head's subtree and each `upperarm` subtree to one point
  (its root's position, scale 0).
- Move the whole body 0.08 m back along the unit's facing.
- Return the plain matrices during immersive cutscenes:
  `vr_render_full_body` must be FALSE then, or cutscenes show the player's
  biped without a head or arms.
- Log the body's node names once.

**D. Immersive cutscenes** (`vr_render_windows`):
- When `cinematic_in_progress() && vr_cinema_immersive()`, take the stereo
  path with `vr_render.cinematic_view`.
- **Anchor** at the cutscene camera's position.
- **Heading** = camera yaw − `vr_head_local_yaw()`, as it was at the last cut.
  Detect a cut as the camera moving more than about 1.5 world units, or
  turning more than 30°, in one frame, or the cutscene starting. At each
  cut, call `vr_view_blink(0.85)`.
- Follow the camera's yaw between cuts. Ignore its pitch and roll.
- `view_heading` and `view_anchor` must use these.
- In `cinematic_render` (source/cutscene/cinematics.c), skip the letterbox
  bars when immersive, but keep the titles.
- The console window's titles already go to the HUD panel.

**E. Screen flash** (source/render/render.c): don't call
`rasterizer_screen_flash()` in the HUD pass. Call it at the end of each eye
and scope pass (`VR_RENDER_VIEW()`), after the lens flares.

**F. Menu** (vr_menu.c):

1. **Layout.** At most 5 settings in the left column and 4 in the right
   (the right box's 5th row hits the hints).
2. **Pages:**

   | Page | Left column | Right column |
   |---|---|---|
   | CONTROLS | CONTROLS, AIM, GUN HAND, TURNING, TURN SPEED | MOVE WITH, TWO HANDS, WEAPONS, HOLSTERS |
   | BODY | BODY, ARMS, FINGERS, ROOM-SCALE, CROUCH DEPTH | ARM RUN, RUN EFFORT, MELEE, MELEE SPEED |
   | VR | HAPTICS, FLASHLIGHT, HOLSTER SIZE, SCOPE, VEHICLES | STEERING, CUTSCENES, MP PHYSICAL |
   | GRAPHICS | PRESET, RESOLUTION, SHADOWS, LIGHTS, SPECULAR | REFLECTIONS, BUMP MAPS, GRASS, FOG LAYERS |
   | DISPLAY | DECALS, PARTICLES, CONTRAILS, WEATHER, LENS FLARES | CAMO, REFRESH |

3. **New settings:**
   - CUTSCENES: IMMERSIVE / 3D SCREEN / FLAT, mapped to `vr.cutscenes`
     "immersive" / "screen" / "flat".
   - HOLSTER SIZE: 10, 15, 20, 25, 30, 40 cm.
4. **Finer steps** for the slider-like settings: MELEE SPEED, RUN EFFORT,
   CROUCH DEPTH, HOLSTER SIZE, HAPTICS, TURN SPEED. Raise
   `VR_MENU_MAXIMUM_VALUES`.
5. **Slider look.** Show their values as `< 20 CM >`. Right or A steps up,
   left steps down.

**G. Ship test9:**
- Build both APKs and check the new strings are in the binaries.
- Commit with the attribution line.
- Report the exact build command and its result.
- Remind the user what the controls do:
  - Grip holds the gun.
  - Holsters are over the shoulders and at the hips.
  - Set WEAPONS to LOCKED to turn physical weapons off.

### Still unverified

- **SPV1** has never been played on the device.
- **Full-body node names** are unknown. Log them.
- **Old render targets leak** when the resolution changes
  (`render_target_get` in d3d8_gl.c).
- **"mission script is running"** showed in green text in the opening
  cutscene. Find where it is printed. It may be a debug overlay this port
  shows.

## The user

- They own the Quest 3 and test every build, with logs and videos.
- They want near-native VR with everything toggleable and on by default,
  and optimisation for the Quest 1 and 2 that goes beyond resolution.
- Act on your own recommendation; don't make them choose.
- Never scan whole drives. Their games are in D:\Games.
- Physical reload is deferred.
- **Feature list they asked for:**
  - IK hands and full body.
  - Hands colliding with the world.
  - Impact melee that damages vehicles too.
  - Physical weapons: grip to hold, a drop when let go.
  - Two-handed weapons.
  - Holsters.
  - Arm-swing running and crouch, with sensitivity steps.
  - Finger gestures: point, thumbs up, and a deliberately hard-to-trigger
    middle finger.
  - Alyx-like hands.
  - Haptics that ramp with pressure, two hands vs one.
  - The VR settings in the pause menu.
  - Graphics presets.
  - Smooth turn.
  - Both sticks clicked recentres.
  - A multiplayer-safe toggle.
  - The main menu in VR.
  - Logs in Download.
  - SPV1 install and restore in the launcher.
