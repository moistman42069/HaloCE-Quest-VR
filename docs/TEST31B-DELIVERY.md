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
delivery. Completed build results follow; final packaging also verifies the delivered
artifacts against these records.

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

## Completed build checks

- All **49 regression suites passed before each edition's build**.
- Cache-format tests: **127 passed, 4 skipped** (optional real-map fixtures).
- Actual ILP32 menu layouts, production debug allocator/CRC and the real
  parser/tag builder constructed all **50 XML assets**. UI, multiplayer client
  and host fixtures passed **134 first/last allocation-callsite fault cases**,
  rollback and recovery. This is not exhaustive injection at every allocation.
- The original invalid XML and NULL-free defects are negative controls: each
  reproduces its failure under the new tests. Corrected paths pass.
- The preserved final Quest ELF was disassembled: `vr_menu_tags_loaded` has
  the `cbz w0` guard at `0x882a8b20`, skipping `debug_free` at `0x882a8b30`
  when the allocation array is NULL. This verifies the fix in the compiled
  payload, not only in source. These addresses identify this candidate only.
- Android's production touch view passed **142 lifecycle/event/dialog checks**,
  including controller visibility, pointer ownership, cancellation and
  touch-anywhere Save/Cancel. Android framework/renderer boundaries are fixtures.
- Both native release-mode variants compiled and linked, and both APKs retained
  the original certificate. APK compaction verified unchanged non-signature
  payloads, signing and 16 KB alignment.
- Build145/network22 is retained. No game data, private logs or signing keys are
  included. The mismatched upstream PGO profile remains disabled; these checks
  do not claim Quest performance or device acceptance.

Runtime source: `3399023ae8b7d0ec57e8c42c68c40ab6c33346af` on `test31b-startup-touch`. Both builds use this exact
clean commit; subsequent source-snapshot differences are delivery documents
only. The packaging manifest records both commits.

| APK | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Android-test31b.apk` | 32,438,836 | `c705b113b913c232e0d212ff19499a3b548f5302989cae20343406833dac9904` |
| `HaloCE-Quest-test31b.apk` | 34,527,875 | `d391f40a9bce4d127d5f91ceb34c84c96011ba5366db4cb99224d80c274de020` |
