# Android controller guide (v1.0.10)

For the flat ARM64 Android APK in v1.0.10, Android's input system and bundled
SDL3 translate common USB/Bluetooth gamepads into Halo's Xbox controller state.
Xbox-style controllers are the primary target. There is no Windows XInput DLL
to install. Pair in Android settings or connect USB, then launch the game.
The launcher has **Controller & touch settings** and **Controller input check**.
The latter displays Android buttons and both common right-stick/trigger axis
conventions; the launch log records SDL recognition and ready-controller count.
No device identifiers, input telemetry or settings are uploaded.

## Default controls

| Xbox position | Halo default |
| --- | --- |
| Left stick | Move / strafe; menu selection |
| Right stick | Aim; vehicle camera/steering follows Halo's controls |
| RT | Fire, analog trigger |
| LT | Throw selected grenade, analog trigger |
| A (south) | Jump / confirm |
| B (east) | Melee / cancel |
| X (west) | Reload; hold to use / pick up / enter or exit vehicles |
| Y (north) | Switch weapons |
| LB | Flashlight (original Xbox white button) |
| RB | Switch grenade type (original Xbox black button) |
| Left stick click | Crouch |
| Right stick click | Zoom |
| Start / Menu | Pause; launcher confirm |
| Back / View | Halo Back input / multiplayer score display |
| D-pad | Menu navigation and game-specific navigation |

These are the native default profile. Halo's Options retains controller layouts,
look sensitivity and inverted aim. PlayStation Cross/Circle/Square/Triangle map
by south/east/west/north position. Nintendo pads default to the same positions;
the optional A/B + X/Y swap follows the printed face labels in gameplay and
uses the same confirm/cancel swap in launcher dialogs. Guide/Home remains an
Android system function. Rear paddles depend on the controller's own mapping.

## Touch and reconnect behavior

- **Auto (default):** hide the complete touch HUD only after SDL has a mapped,
  opened gamepad with both sticks and triggers. A keyboard, TV remote or partial
  joystick cannot hide it. Show it again when the last ready pad disconnects.
- **Always show:** touch and the first gamepad merge into player one; releasing
  a touch cannot cancel a held controller button. Stronger stick input wins.
- **Always hide:** deliberate override, including after disconnect. Restore
  Auto/Show in the launcher. The in-game Touch button also opens this policy.

Detection refreshes every half second while the activity is resumed and on
Android device-change notifications. All touch contacts clear on visibility
changes. Active HUD editing stays visible until saved/cancelled. Unplugged SDL
handles are closed/recycled; reconnecting does not exhaust the handle table.
The first recognized pad shares player one. Additional native ports retain
existing behavior; this is not a new Android split-screen feature.

## Response and vibration

Launcher settings offer independent movement/aim dead zones (0-45%), horizontal
and vertical stick response (25-200%), trigger dead zone (0-40%), face-button
swap and vibration on/off. They apply on the next game launch. Defaults keep
the original Halo stick dead zone (~27.5%) and 100% response; trigger default
is 5%. The host compensates for the guest's existing 9000-unit dead zone so
two dead zones are not stacked. This does not change touch or VR input.

SDL handles Android trigger-axis aliases. A reviewed patch to pinned SDL 3.4.16
adds missing generic Android mappings for button-only L2/R2: Java carries their
capability bits and C maps them to independent trigger axes. Existing analog
mappings take priority; no duplicate button injection is used. Both
trigger values remain independently bounded. Halo motor values reach SDL rumble
when enabled; capability depends on Android version, controller driver and USB
versus Bluetooth. Unsupported vibration never blocks input. On focus loss the
flat physical pad returns neutral; rumble is stopped by the next feedback call
or expires within 100 ms. Gameplay is not paused by disconnecting during an
online match. Automatic touch recovery avoids leaving the player stranded.

## Menus and checking a controller

The native game menus receive the same Xbox state as gameplay. Launcher and
project dialogs use Android focus controls: D-pad/left stick navigates with
repeat, A confirms, B returns. Stick repeats stop on neutral, focus loss,
window closure or device removal. Text entry/file selection may use Android's
system keyboard/picker; their controller support is provided by Android.

1. Connect an Xbox-style pad by USB, then repeat using Bluetooth if supported.
2. Open input check; verify every button, both stick axes and independent triggers.
3. Navigate launcher/browser/options using only the pad; launch a campaign.
4. Check each action above, hold/release triggers, diagonal movement, menus,
   invert/sensitivity and supported vibration.
5. Unplug while moving/firing: no held input, touch returns in Auto. Reconnect.
6. Background/resume, switch gamepad models, and test touch plus pad in Always show.
7. Recheck Quest controllers, touch gameplay and paired co-op with both candidate APKs.

Automated checks execute the production host adapter with mock SDL devices,
all 65,536 raw stick values, 600 disconnect/reconnect cycles, focus/rumble gates,
trigger bounds, the production SDL analog/digital trigger mapper and
visibility/navigation policies. These do not certify a
physical controller/driver, Bluetooth transport, Android focus behavior or
headset regression. Device acceptance remains pending.

## Primary references

- [Android controller overview](https://developer.android.com/games/sdk/game-controller/overview)
- [Android controller actions and trigger aliases](https://developer.android.com/games/sdk/game-controller/controller-input)
- [SDL3 gamepad API](https://wiki.libsdl.org/SDL3/CategoryGamepad)
- Bundled SDL Android joystick/controller implementation, `host_sdl.c`,
  `xinput_sdl.c`, and `source/input/input_abstraction.c` are the implementation
  evidence for these mappings. SDL's mapping database remains bundled and does
  not download unreviewed runtime input code.
