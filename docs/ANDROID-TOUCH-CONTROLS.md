# Flat Android controls and HUD editor

Test15 candidate, `com.halo.decomp`, Android 9+ / ARM64. Quest has no touch overlay.

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

## Customize during play

Tap **HUD** in the upper-left safe area. Held inputs are released. Drag any of the 19 controls. Selected controls turn amber. **Options** adjusts the selected control's horizontal/vertical position, size (65-160%) and opacity (15-100%). Its **Select a control** list can recover a control hidden under another control or the toolbar.

Global options include scale (65-150%), opacity, independent horizontal/vertical sensitivity (0.25-3), radial dead zone (0-30%), floating movement origin, invert vertical aim, swipe versus held-stick aiming, and blue/cyan/white/amber/green colors. Individual and global opacity multiply. Labels retain a minimum readability level.

**Save** commits the layout and all options to private app preferences. **Cancel** restores the last saved settings. **Reset** restores defaults in the working editor; Save commits that reset, Cancel undoes it. Editing and options suppress gameplay input, but an online match continues; find somewhere safe first. Editing does not pause the server.

One full safe-area screen-width swipe turns 180 degrees at sensitivity 1. Start inside LOOK or FIRE, then drag beyond its circle if needed. Floating movement starts within MOVE and places the stick origin under that initial touch. Dead zone affects MOVE and held-stick look, not swipe look. Positions are normalized to the usable display and clamped to keep circles clear of edges and display cutouts. Resizing does not permanently rewrite saved positions.

## Input safeguards

Contacts own their initial control by pointer ID until release; sliding across another control does not press it. Quick button taps survive between native polls. Cancel, pause, focus loss, hide, resize, editor entry and detachment clear held input and pending edges. Relative aim is accumulated in radians and consumed once, independent of the game's stick turn rate; motion older than 250 ms is discarded. Cancellation generations clear already-polled motion. The host/guest record is 32 bytes, with four axes, a button mask, relative yaw/pitch and generation. VR compiles out the writer/merge.

## Validation and references

`tools/test_test15_io.py` executes the production JNI snapshot functions with mocked time, and checks pure touch layout math over 16:9, 20:9, 4:3 and portrait dimensions. Tests cover taps, cancellation, stale motion, NaN, clamps and diagonal analog movement. Android Java and both native flavors must compile. These checks do not constitute phone gameplay acceptance.

Usability references: Activision's [Warzone Mobile control customization guide](https://www.callofduty.com/uk/en/blog/2024/03/call-of-duty-warzone-mobile-complete-control-plus-customization-controller-options) (position, scale, transparency and sensitivity), and Android's [multi-touch guidance](https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi). No game control code or artwork from those references was copied.

Device checks: simultaneous move/fire/aim/jump, menus and controller profiles, cancel/focus/rotation, save/reopen/cancel/reset, controls under toolbar, notches, gamepad coexistence and Quest overlay absence. Test15 is awaiting owner results.

Additional native-port reference: id Software's public [DOOM iOS HUD editor](https://github.com/id-Software/DOOM-iOS/blob/master/code/iphone/hud.c), reviewed for drag ownership, screen-edge clamping and saved-control lifecycle. This was design comparison only; none of its GPL code/art was copied into this implementation.

Controller & touch settings in the launcher controls automatic hiding and recovery. Auto is the default; only a fully mapped SDL gamepad hides the HUD. Always hide is an explicit override; restore visibility in the launcher. See [controller support](ANDROID-GAMEPAD.md).
