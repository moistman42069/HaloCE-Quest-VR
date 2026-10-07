# Test31b — repair the rejected Test31 startup/input candidate

Owner report, 2026-10-07: Test31 (1.0.13/code39) crashes on Quest 3 before a
usable VR menu and leaves the Motorola Android port without usable touch
navigation. **Test31 is rejected, not an accepted baseline.** Public v1.0.12
remains unchanged. Current branch: `test31b-startup-touch`; target 1.0.13/code40.
Do not publish, install or launch a game automatically. Prepare a corrected
private pair after the failures are reproduced and the fixes validated.

## Evidence and identified causes

- All three Quest launch logs show the same debug allocator failure at
  `0xffffffe0`. Symbolization against the exact delivered ELF identifies
  `debug_check_pointer_header -> debug_free -> vr_menu_tags_loaded`.
  The first menu load calls cleanup while its allocation array is NULL.
  Test30 runtime `688a63e3` guarded that free; Test31 accidentally removed it.
  Production `free` is the game's debug allocator and does not accept NULL.
  The host harness substituted libc free, masking this defect.
- Both Android launches and all Quest launches reject menu construction at
  `network_setup.xml:67`. The Android USE LAUNCHER text widget was given
  `strings`, which belongs to spinners. XML parsing succeeded, but building
  actual game tags rejected the whole menu set. Previous tests parsed assets
  and tested helpers separately; they did not build those parsed assets into
  game tags with the real guest ABI.
- Android suppressed navigation controls whenever any menu was active, even
  after the import failed and the engine displayed its stock menus. Direct
  pointer input plus a Back button did not provide a complete fallback.

GitHub's latest release is still v1.0.12, tag source `3968feca`, runtime
`688a63e3`. Both locally preserved public APKs match GitHub's published SHA-256
digests and release provenance. The prior guarded cleanup is present there.
No connected Android/Quest device was available in `adb devices -l` during
this repair; host integration evidence must not be labelled a device run.

The OpenXR logs reach session READY, session begun and a first submitted frame;
the subsequent guest failure prevents a usable VR startup. Network signalling
after the fault is not evidence of a network-related cause. Private raw logs
remain outside Git; addresses, invites and device data are not published.

## Work and required checks

1. Restore the prior allocator contract, audit related failure cleanup, and
   exercise first load, successful and failed menu import, repeated unload/load
   and allocation failures using production allocator semantics.
2. Correct the widget attribute and add a complete asset-to-game-tag test using
   an ILP32 ABI. Keep tag layout and stock/VR integration assertions active.
3. Preserve touch navigation for both imported and stock menus, including
   controller auto-hide/reconnect, pause/resume, menu-to-game transition,
   pointer and button release, and multi-touch lifecycle.
4. Add optional touch-anywhere camera dragging to the existing in-game touch
   customization. Default OFF; buttons/movement/menu interactions retain
   ownership of their contacts. Persist the choice and document it.
5. Compare the public v1.0.12 release metadata, source and shipped artifacts;
   retain Test31's requested network22/menu/turret/window features. Run full
   regressions, compile both editions, verify signed artifacts and sources.

No host check can establish headset or phone runtime acceptance. Record the
exact validation performed; do not repeat the previous inference that isolated
helper tests cover the full startup/input path. The larger M1–M29 and W1–W66
interaction scope remains queued behind this repair.
