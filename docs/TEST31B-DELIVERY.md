# Test31b / 1.0.13 / code 40 — private startup and touch repair

This candidate repairs the rejected Test31/code39 pair. **Public v1.0.12 is
unchanged.** No device acceptance or public release is implied. See
[player notes](TEST31B-PLAYER-NOTES.md) for the complete controls, installation
and retained OpenCE menu/network changes.

## What changed

- Restored the guarded first-load VR menu cleanup from the preceding release.
  The game's debug allocator rejects NULL frees; the old host test used libc
  behavior and missed the crash. Menu allocation growth and cleanup now also
  preserve ownership on failure.
- Corrected the menu text attribute that rejected the entire OpenCE menu set.
- Android retains compact D-pad, A/B/X/Y, Start and Back controls in menus,
  including stock fallback, with Hide/Show controls and direct taps.
- Added **HUD > OPTIONS > Drag anywhere to look (unused gameplay space)**.
  Default OFF. Save the touch layout to retain it; Cancel restores the prior
  choice. Existing buttons, movement and menu contacts keep their roles.
- Launch logs identify code40. Tests now exercise production allocator
  semantics, complete XML-to-game-tag construction and Android input lifecycle.

OpenCE Build145/network22, turret controls/reticle, Warthog glass settings and
the other Test31 work remain. No broader hand, weapon, body, locomotion or
network behavior change is intended in this repair. The M1–M29 and W1–W66
interaction work remains queued.

## Validation and build provenance

The final delivery manifest records the exact runtime/source commits, original
signing certificate, package/version/API/ABI and APK hashes. SHA256SUMS covers
the APKs and matching source/build archives. Both variants must be built
serially from the same clean runtime source and pass the complete checks before
delivery. This document is prepared before those final build gates; their
completed results are recorded below when the artifacts exist.

No connected Quest or Android device was available during this repair.
Host integration tests exercise real production paths with map/renderer/OS
fixtures; they do not establish device startup, appearance or network acceptance.

## First device checks

1. Update in place; do not uninstall or clear data. Confirm 1.0.13/code40 in
   the new launch log. Check a cold launch, exit and second launch on both apps.
2. Quest: reach usable VR menus, open VR Settings, then enter campaign and
   pause/resume. Check pointer and native A/B/X/Y navigation.
3. Android: navigate both normal and stock fallback menus with the compact
   controls and direct taps. Enter gameplay, pause/resume, and return to menus.
   Test controller connection/disconnection with Auto touch visibility.
4. In HUD > OPTIONS, enable drag-anywhere look, Save, and drag unused gameplay
   space while moving/firing with another finger. Check OFF and Cancel as well.
5. Continue the turret, window, graphics, input and network22 PvP/co-op checks
   listed in the player notes, using matching peer versions and game revisions.

If a problem occurs, retain the launch log from Download/HaloCE and include
device/OS, content/revision, map, settings and reproduction steps. Both peers'
logs help with network reports. Support: [project server](https://discord.gg/S9uSCKxKx),
[Flat2VR](https://discord.gg/flat2vr), or **@MeWhenINameMyself**.
