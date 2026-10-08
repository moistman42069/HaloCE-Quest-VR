# Test35 progress — OpenCE Build 148

**Status:** Test35 is the engineering record for the published v1.0.16/code45
release. Its original candidate APK hashes below are historical and are not
the stable-identity release APK hashes; use
[`RELEASE-PROVENANCE-1.0.16.md`](RELEASE-PROVENANCE-1.0.16.md) for the public
assets. Host checks passed, while device acceptance for the exact public pair
remains unrecorded.

## Candidate identity

- Android flat and Quest VR: version **1.0.16**, version code **45**.
- Upstream baseline: official OpenCE **Build 148**, commit
  `ff47e47ad6f54bc533cee2a0fe57232c8f63d614`.
- Multiplayer protocol remains **network 23**; Build 148 did not change it.
- Preserve the Test34 scope diagnostics/alignment, CE map and BSP validation,
  server-row pointer selection, co-op safeguards, accepted Test31b VR settings,
  and accepted Test31c Android touch/gameplay behavior.

## Integrated changes

1. **Correct invalid particle collision radii during tag validation.** Negative
   and NaN values become zero across particle and particle-system radius
   bounds/multipliers, contrail point widths, weather particles, effect
   particles, and breakable-surface particles. The correction is logged by the
   existing tag validator and leaves nonnegative authored values unchanged.
2. **Keep a runtime fallback.** `point_physics_update` clamps a computed
   negative or NaN radius to zero before the engine assertion. The first such
   event emits one silent error entry; later events do not spam the log.
3. **Improve native error identification.** The game version command and halt
   screen identify the native platform/build flavor. The halt screen displays
   the newest eight useful error lines first, truncates exceptionally long
   lines safely, and points to the full `debug.txt` log. Android's native
   source build receives the same release/debug build defines used by the
   updater build configuration.
4. **Clarify SPV1's size boundary in the launcher.** All ten listed SPV1 maps
   are 157-253 MiB, larger than the often-quoted 128 MiB figure but below this
   reader's 384 MiB ordinary / 576 MiB OpenSauce-upgraded file caps. The launcher
   now says SPV1 remains experimental and unverified rather than claiming the
   custom-map parser cannot accept its file sizes.

## Verification

The focused Test35 suite exercises the actual correction helper with negative,
NaN, zero and positive values, the native error-tail formatter, all schema
callback registrations, and the runtime fallback. The full Quest/Android host
suite passed with no failed suites. `pytest -q tools/test_cache_file_formats.py`
reported 127 passed and 4 skipped because real Custom Edition map fixtures are
not present. Both release-mode guest builds and APK package checks passed.
Automated results do not replace owner testing on an Android device and Quest
headset.

## Device checklist

- Install both APKs over existing installs; preserve app data and settings.
- Open representative campaign and custom-map content that exercises particles
  and effects; confirm the map loads and normal effect rendering continues.
- Confirm the in-game server browser selects rows with pointer hover and keep
  network-23 multiplayer/co-op checks from Test34 in the matrix.
- For any halt/error, capture the on-screen native build label, its recent
  messages, and the complete `debug.txt` file.
- Verify Android touch controls and Quest startup/settings still work.

Exact APK, archive and checksum details belong in
[`TEST35-DELIVERY.md`](TEST35-DELIVERY.md).
