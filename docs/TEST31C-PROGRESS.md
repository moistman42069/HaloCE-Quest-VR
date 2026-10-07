# Test31c — preserve accepted VR; restore familiar Android touch controls

## Additional owner request before packaging

Fix the non-working VR Warthog HOG GLASS toggle, then deliver BOTH editions.
This supersedes the Android-only build plan below. Both target 1.0.13/code41.
Preserve the original code40 Quest artifact as the comparison baseline and
the owner's preference for its new VR settings. Scope the VR change to glass.
The model draw queue populates `object_index` from its real object identifier;
ordinary surfaces have `source_object_index = 0`. The glass callback was
incorrectly receiving that latter field and rejecting the vehicle match.
Validate the real queue-to-consumer route and shader selection before delivery.

Read-only inspection of available Silent Cartographer and Blood Gulch tags
identifies `vehicles\\warthog\\shaders\\warthog windshield` as glass (`sgla`).
The existing Custom Edition converter maps stored type9 to engine glass type8;
no broader material-name filter or conversion change is needed. The wrong
queue-field wiring also existed in Test25; helper-only tests supplied a valid
object handle and therefore missed it. The new regression must use the actual
queue assignments and consumer call expression.

## Owner request and evidence (2026-10-07)

The owner reports Test31b VR works great and likes the new VR settings.
**Standing preference: preserve that VR settings design.** The exact code40
Quest artifact is accepted as the comparison baseline. The later glass request
adds a narrow VR repair to this pass while retaining that settings design.
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
- Build both 1.0.13/code41 APKs. Preserve the Quest code40 baseline artifact;
  VR changes are limited to the glass correction and identity. Flat native and
  network payloads remain unchanged. No publishing, install or game launch.

## Required validation

Production-view draw/event tests must assert that entering a menu does not swap
the controls' style, labels or positions. Cover original controls plus direct
taps, multitouch cancellation, gameplay/menu transitions, saved layout, touch
visibility and free-look hide/restore. Run the full existing regression suite,
build the Android APK with the original signing identity, and compare native
payload hashes with Test31b. Record actual results and device-test limits.

## Paired build checkpoint

Both 1.0.13/code41 APKs built from `173708ec068993a7256c7f0431b5d001ba46f8e6`. All 50 regression suites
passed before each build; cache tests passed 127 with four optional skips.
The original circular Android layout passes 276 view checks; glass passes 62
production-route checks and the wrong-field negative control. Flat native
payloads match Test31b byte-for-byte. The accepted Quest artifact is preserved.
See [TEST31C-DELIVERY.md](TEST31C-DELIVERY.md) for hashes and the exact scope.
Await owner testing of both corrected editions before publication or later
interaction work. No universal device/ISO acceptance is claimed.
