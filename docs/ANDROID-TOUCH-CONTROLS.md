# Flat Android touch controls

Implementation checkpoint, 2026-10-03. Part of test12 WIP, not a phone-tested
release. This adds controls to `com.halo.decomp` only. The Quest activity never
creates the overlay; its native build excludes the touch JNI writer and the
player-one touch merge. Existing Quest input and physical controller enumeration
are preserved.

## Controls

| Control | Default game action |
| --- | --- |
| MOVE | Analog left stick: walk, strafe, reverse |
| LOOK | Analog right stick: hold away from centre to turn; release to stop |
| FIRE | Right trigger; dragging while held also controls aim |
| A / Jump | Jump / menu confirm |
| B / Melee | Melee / menu cancel |
| X / Use | Reload / hold to interact or pick up |
| Y / Swap | Change weapon |
| Crouch | Left stick click, held while touched |
| Zoom | Right stick click |
| Grenade | Left trigger |
| Type / Light | Xbox white / black (grenade selection / flashlight) |
| Menu / Back | Start / Back |
| Direction arrows | D-pad, including menu navigation |
| Touch | Show/hide overlay; choice saved across launches |

These are ordinary Xbox controller inputs, so the game's controller profile
still determines their actions. Aim is rate-based, as on a gamepad. It is not
relative swipe/mouse aim. MOVE + FIRE/drag gives movement, firing and aiming with
two fingers; additional contacts can jump, crouch, reload or use another button.
The stick dead zone is radial and preserves analog magnitude and diagonals.

## Implementation and regression boundaries

- `TouchControls.java` draws a translucent landscape overlay on SDL's existing
  activity layout. It reserves display-cutout/system-bar insets, does not claim
  keyboard focus and retains a Touch button when hidden.
- Contacts are keyed by Android pointer ID, not the moving pointer index. Each
  owns its initial control until release; crossing another button cannot trigger
  it. Multiple contacts on the same control are ignored. Native snapshots OR
  buttons and choose the stronger look stick if LOOK and FIRE/drag coexist.
- Finger input is consumed by the overlay so SDL cannot duplicate a tap as a
  mouse click/fire. External mouse events continue to SDL. Hiding controls still
  consumes finger taps outside the Touch button.
- Up releases that contact. Cancel, activity pause, focus loss, resize, hiding
  controls and detachment clear axes, held buttons and pending button edges.
- `halo_touch.h` specifies the 20-byte host/guest snapshot: four signed 32-bit
  axes, one unsigned button mask. `host_sdl.c` has the JNI writer and a small
  mutex-protected snapshot. Down edges survive a short tap between game polls;
  normal releases clear held state, and lifecycle reset discards pending edges.
- `xinput_sdl.c` merges this only into player zero, only in flat Android and
  outside the debug console. Buttons are ORed; the stronger axis wins. There is
  no synthetic SDL device, no new controller slot and no reassignment of a
  connected physical pad. Desktop and Quest builds omit the merge.
- No networking, VR tracking, IK, grip, melee, collision or renderer behavior is
  changed by the touch implementation. Prior uncommitted defaults/SPV1 recovery
  work is preserved independently.
- Startup and visibility changes use the existing per-launch Downloads RunLog.

Android pointer ownership/cancellation follows the official
[multi-touch guidance](https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi).
Insets use Android 28-compatible APIs to preserve the app's minimum SDK.

## Build and device evidence

Run `bash tools/build-quest.sh flat` and `bash tools/build-quest.sh vr`, preserving
each APK before switching flavor. Both rebuild the shared native staging area;
never start them concurrently. A successful compile is not phone/headset
acceptance. See `TEST12-PROGRESS.md` for current build results.

The owner still needs to exercise:

1. Navigate menus with arrows, A and B; pause/resume with Menu.
2. Move diagonally/backward while holding FIRE and dragging to turn. Release
   fingers in different orders; ensure no held fire or movement remains.
3. Jump, crouch, use/reload, switch weapons/grenades, scope and use the flashlight.
4. Background/foreground the app and rotate landscape sides while holding inputs.
5. Use a physical gamepad before and after hiding Touch; verify player one stays
   assigned. Reopen the app and confirm the visibility choice is retained.
6. Check small/large phone layouts and cutouts. The initial positions and size
   are fixed to screen proportions; per-control layout editing is not implemented.
7. On Quest, confirm no phone overlay and normal existing tracking/controller
   behavior. No device installation or game launch is performed by the agent.
