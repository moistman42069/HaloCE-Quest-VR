# Test31c — preserve accepted VR; restore familiar Android touch controls

## Owner request and evidence (2026-10-07)

The owner reports Test31b VR works great and likes the new VR settings.
**Standing preference: preserve that VR settings design.** The exact code40
Quest artifact is accepted and will not be rebuilt for this Android-only pass.
Later manual reload/hand/world/NPC requirements remain queued.

The 9.47-second Android video shows the familiar circular controls during
startup (~3.2–3.8 s), then a rectangular menu control strip (~4.4 s onward).
The switch is implemented by `TouchControls.refreshMenuMode`/`onDraw`, which
selects a different menu layout. This is an unwanted design change, not a
recurrence of the NULL-free crash or failure to construct the imported menus.
Both flat launch logs identify 1.0.13/code40, zero controllers, and successful
construction of 878 widgets / 226 string lists / 89 bitmaps. One uses Auto
touch visibility, the other Always Show; both switch to the menu overlay.
The completed flat session exits normally through Quit. The supplied VR-app
log is a launcher-only session on the phone; VR acceptance above comes from
the owner's explicit headset report, not that phone log.

The launcher video contains a cached updater message mentioning code39;
the launch logs identify code40. Do not infer the running code from cached
release-status prose. Raw logs/video stay outside Git and delivery archives.

## Exact scope

- Keep one familiar circular touch layout across menus and gameplay, including
  saved control placement/size/opacity and the existing Touch/HUD affordances.
- Retain direct taps on native menus and native keyboards. Touch controls own
  their contacts: pressing one must not also activate the menu item behind it.
- Retain original D-pad, action, Menu and Back navigation, so stock fallback
  remains usable. Preserve input cancellation and controller visibility handling.
- Optional **Drag anywhere to look** hides only the LOOK disk and releases that
  area to free-look input. MOVE, FIRE and all other action buttons remain.
  Keep LOOK visible in layout editing, so the existing position can be edited
  and restored when free look is disabled. Preserve Save/Cancel and defaults.
- Build only Android 1.0.13/code41. Preserve Quest code40 and native game/network
  payloads. No publishing, install or game launch.

## Required validation

Production-view draw/event tests must assert that entering a menu does not swap
the controls' style, labels or positions. Cover original controls plus direct
taps, multitouch cancellation, gameplay/menu transitions, saved layout, touch
visibility and free-look hide/restore. Run the full existing regression suite,
build the Android APK with the original signing identity, and compare native
payload hashes with Test31b. Record actual results and device-test limits.
