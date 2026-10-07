# Flat Android controls and HUD editor (Test31c / v1.0.13 code41)

Applies to the flat Android package `com.halo.decomp` (Android 9+ / ARM64). Quest
uses tracked controllers and has no flat touch overlay.

## Play with the defaults

| Control | Default action |
| --- | --- |
| MOVE | Walk, strafe and reverse; radial analog dead zone |
| LOOK | Swipe to turn; lift to stop; dragging FIRE also aims |
| FIRE | Shoot while held |
| A / Jump | Jump / menu confirm |
| B / Melee | Melee / menu cancel |
| X / Use | Reload; hold to interact / pick up |
| Y / Swap | Change weapon |
| Crouch / Zoom | Left / right stick clicks |
| Grenade | Throw selected grenade |
| Type / Light | Xbox black / white: grenade type / flashlight in default profile |
| Menu / Back | Start / Back |
| Arrows | D-pad and menu navigation |
| Touch | Auto / Always show / Always hide visibility policy |
| HUD | Open layout editing while the overlay is visible |

The game's selected controller profile still determines button actions. MOVE + FIRE/drag permits movement, aim and fire with two fingers. More fingers can operate other controls. Physical gamepads remain player one; stronger analog input wins and buttons merge. External mouse events pass through to SDL.

## Menus and fallback navigation

The original circular controls keep their saved positions in menus and gameplay;
there is no separate rectangular menu strip. MOVE or the arrows navigate,
**A / Jump** confirms, **B / Melee** or **Back** cancels, **X / Use** and
**Y / Swap** perform the game's displayed X/Y actions, and **Menu** sends Start.
These controls also work with the original stock menus if OpenCE loading fails.

Tap native menu rows or keyboard keys directly in uncovered space. A contact
belongs to either its circular control or the direct pointer, never both.
The existing **Touch** button changes visibility; **HUD** opens the editor.
Those recovery buttons remain reachable in menus when controls are hidden.
Returning to gameplay follows the saved visibility/controller policy. A finger
held through Resume must lift before it can operate a gameplay control.

## Customize during play

Tap **HUD** in the upper-left safe area. Held inputs are released. Drag any of the 19 controls. Selected controls turn amber. **Options** adjusts the selected control's horizontal/vertical position, size (65-160%) and opacity (15-100%). Its **Select a control** list can recover a control hidden under another control or the toolbar.

Global options include scale (65-150%), opacity, independent horizontal/vertical sensitivity (0.25-3), radial dead zone (0-30%), floating movement origin, invert vertical aim, swipe versus held-stick aiming, optional drag-anywhere camera look, and blue/cyan/white/amber/green colors. Individual and global opacity multiply. Labels retain a minimum readability level.

**Save** commits the layout and all options to private app preferences. **Cancel** restores the last saved settings. **Reset** restores defaults in the working editor; Save commits that reset, Cancel undoes it. Editing and options suppress gameplay input, but an online match continues; find somewhere safe first. Editing does not pause the server.

One full safe-area screen-width swipe turns 180 degrees at sensitivity 1. Start inside LOOK or FIRE, then drag beyond its circle if needed. Floating movement starts within MOVE and places the stick origin under that initial touch. Dead zone affects MOVE and held-stick look, not swipe look. Positions are normalized to the usable display and clamped to keep circles clear of edges and display cutouts. Resizing does not permanently rewrite saved positions.

## Optional drag-anywhere camera look

In gameplay, tap **HUD > OPTIONS**, enable **Drag anywhere to look (hide LOOK
pad)**, choose **Back to editor**, then **SAVE**. It is off by default.
The option appears in the existing Touch options dialog; it does not require a
new menu or launcher screen.

When enabled, only the **LOOK** joystick is hidden. Its former area joins the
free-look space; MOVE, FIRE and the other controls retain their positions.
LOOK stays visible in the editor and returns to its saved position when the
option is disabled. In menus its uncovered area accepts direct menu taps.

A finger that starts outside all controls can drag to turn the view. Its camera
control lasts until it lifts, even when crossing over a button. MOVE and all
buttons have priority when a touch starts inside them, including a button held
by another finger. One free-space finger can aim alongside movement and other
buttons. It uses the existing horizontal/vertical sensitivity and invert
settings, always as a relative swipe even when the dedicated LOOK control uses
held-stick mode. It does not operate in menus or the HUD editor, does not change
physical gamepad mappings, and is absent from Quest VR. **Cancel** restores the
saved choice; **Reset + Save** disables it again.

## Gyro aim (1.0.10, an option)

Turn the phone to aim. It is **off by default**. Turn it on in the game (tap **HUD**, then **Options**, then **Gyro aim**, then **Save**) or in the launcher (**Controller & touch settings**). Both places change the same setting.

- **Always on:** the phone's turn always aims.
- **Only while a finger is on LOOK or FIRE:** the phone aims only while you touch LOOK or hold FIRE. Lift your thumb to turn the phone back without moving the view, like lifting a mouse off the desk.
- **Gyro horizontal / vertical sensitivity** (0.25-4 in the game, 25-400% in the launcher): at 1 (100%) the view turns as far as the phone does.
- **Invert gyro vertical aim.**

Gyro aim works together with swipes, sticks and a controller. It uses the gravity sensor where the phone has one, so turning your body turns the view whether you hold the phone upright or tilted back. A phone held still does not drift. Like swipe aim, it turns off the controller's aim magnetism while you use it, unless `input.mouse_aim_assist` is on. It pauses while you edit the HUD, in menus, and when the game is in the background. Phones without a gyroscope show "no gyroscope on this device".

## Input safeguards

Contacts own their initial control by pointer ID until release; sliding across another control does not press it. Quick button taps survive between native polls. Cancel, pause, focus loss, hide, resize, editor entry and detachment clear held input and pending edges. Relative aim is accumulated in radians and consumed once, independent of the game's stick turn rate; motion older than 250 ms is discarded. Cancellation generations clear already-polled motion. The host/guest record is 32 bytes, with four axes, a button mask, relative yaw/pitch and generation. VR compiles out the writer/merge.

## Validation and references

`tools/test_test31_touch_lifecycle.py` compiles the complete production
`TouchControls` view with deterministic Android framework doubles. It executes
real touch streams, menu/fallback navigation, menu-to-game transitions,
controller hide/disconnect, editing dialogs, Save/Cancel/Reset, free-space look
and multi-touch ownership. It does not prove Android rendering or device
acceptance. `tools/test_test31_flat_pointer.py` additionally checks the actual
JNI snapshot and native pointer bridge.

`tools/test_test15_io.py` executes the production JNI snapshot functions with mocked time, and checks pure touch layout math over 16:9, 20:9, 4:3 and portrait dimensions. Tests cover taps, cancellation, stale motion, NaN, clamps and diagonal analog movement. Android Java and both native flavors must compile. These checks do not constitute phone gameplay acceptance.

Usability references: Activision's [Warzone Mobile control customization guide](https://www.callofduty.com/uk/en/blog/2024/03/call-of-duty-warzone-mobile-complete-control-plus-customization-controller-options) (position, scale, transparency and sensitivity), and Android's [multi-touch guidance](https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi). No game control code or artwork from those references was copied.

Gyro aim math and wiring: `tools/test_test28.py` (display rotations, tilt, sensitivity, invert, still phone, bad samples).

Device checks to collect: simultaneous move/fire/aim/jump, menus and controller profiles, cancel/focus/rotation, save/reopen/cancel/reset, controls under toolbar and notches, gamepad coexistence, and confirmation that Quest has no touch overlay. Automated checks do not establish physical-device acceptance.

Additional native-port reference: id Software's public [DOOM iOS HUD editor](https://github.com/id-Software/DOOM-iOS/blob/master/code/iphone/hud.c), reviewed for drag ownership, screen-edge clamping and saved-control lifecycle. This was design comparison only; none of its GPL code/art was copied into this implementation.

Controller & touch settings in the launcher controls automatic hiding and recovery. Auto is the default; only a fully mapped SDL gamepad hides the HUD. Always hide is an explicit override; restore visibility in the launcher. See [controller support](ANDROID-GAMEPAD.md).
