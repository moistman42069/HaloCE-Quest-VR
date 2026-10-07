# Test31c / 1.0.13 / code41 — touch presentation and VR glass repair

This private pair keeps the preferred Test31b VR settings design and fixes the
reported Android touch layout and VR Warthog glass issues. The accepted Quest
code40 APK remains preserved as a comparison baseline; neither code41 edition
has owner device acceptance yet. Public v1.0.12 is unchanged.

## Changes and controls

- Android keeps the familiar circular controls and saved positions in menus
  and gameplay. The rectangular replacement strip is removed.
- Direct native menu/keyboard taps remain available in uncovered space.
  Controls own their contacts, so they cannot click through to a menu row.
- **HUD > OPTIONS > Drag anywhere to look (hide LOOK pad)** hides only LOOK
  and frees its area for camera dragging. MOVE, FIRE and other buttons remain.
  LOOK stays visible in the editor; disabling the option restores its saved
  position. Default OFF. Save keeps the choice; Cancel restores it.
- **VR Settings > Vehicles > HOG GLASS** now receives the real rendered
  vehicle handle. Ordinary model surfaces had supplied an effect-owner field
  equal to zero, causing the existing glass check to reject the Warthog.
  Hidden/Visible remains scoped to your occupied first-person Warthog view.
  Third-person vehicle defaults, controls, geometry and collision are retained.

Install each code41 APK over its existing edition; **do not uninstall or clear
data**. See [player notes](TEST31C-PLAYER-NOTES.md) for complete current controls
and the retained OpenCE Build145/network22 features. No publication or device
installation is authorized by this private delivery.

## Validation scope

The Android production-view tests check circle coordinates/labels across menu
transitions, saved layouts, free-look hide/restore, pointer ownership, editing,
visibility and reconnect. The new glass test uses the real model-owner/queue
assignments and consumer call, including a negative control with the old wrong
field, all three seats, toggle changes, third-person/outside views, attached and
unrelated objects, non-glass shaders and stale state.

Object storage, Android framework and GPU boundaries in those host tests are
fixtures. They do not establish headset appearance or phone gameplay. Final
build/artifact results and hashes will be appended after both builds complete.

## Owner checks

1. Android: confirm the same circular layout remains when the menu appears;
   try original buttons and uncovered direct taps, then enter gameplay.
2. Enable free look in HUD > OPTIONS, Save, and confirm only LOOK disappears.
   Move/fire with other fingers; turn the option off to restore LOOK. Check
   layout editing, touch visibility, controller reconnect and pause/resume.
3. Quest: enter a Warthog, select first-person view, and toggle HOG GLASS
   Visible/Hidden. Try each seat, leave/re-enter, and switch to third-person.
   Confirm other vehicle geometry and the preferred VR settings remain intact.
4. Retest the prior menu/turret/network workflows as appropriate. Both editions
   remain network22 and need compatible peers/content.

Logs remain in Download/HaloCE. Include device/OS, content/revision, vehicle,
seat/view, settings and reproduction steps. Support: [project server](https://discord.gg/S9uSCKxKx),
[Flat2VR](https://discord.gg/flat2vr), or **@MeWhenINameMyself**.
