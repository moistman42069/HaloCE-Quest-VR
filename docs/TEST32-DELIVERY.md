# Test32 private delivery

Target: private test candidate, version 1.0.13 / code 42, Quest VR and flat
Android. OpenCE Build 145 / network 22. Public v1.0.12 is unchanged.

Runtime source: `0f4b4078d56b1246d8f794a258a10f4d6fbf9511` on
`test32-launcher-vehicles`. The VR and flat APKs were built from this exact
commit, including the corrected bundled Server Browser instructions for
stick/D-pad or Android MOVE auto-scrolling. Subsequent documentation and
package-metadata updates do not change either APK.

## APKs

| Build | File | Size | SHA-256 |
|---|---|---:|---|
| Android / flat | `HaloCE-Android-test32.apk` | 31 MiB | `7db357b412c98d571de367a134c97e7c0b9ddaa92ca88655bd40e25d25bdb7e7` |
| Quest / VR | `HaloCE-Quest-test32.apk` | 33 MiB | `d51516a7ccf1126f99f12a1109e910b1a5d216806c9b83dfc5d83ca5b4e3d68d` |

Both packages use the previously accepted signing certificate, version code
42, Android API 28 minimum, and 16 KB-aligned native libraries. Package-level
checks verify the APK contents, guide files, revision/data handling, network
parity, Safe geometry defaults, retained Android controls and VR settings.

## Validation and test limits

- All 55 registered deterministic regression suites passed in the final run.
- The VR and flat build commands each reran the registered pre-build suite and
  completed compilation, signing, and 16 KB alignment successfully.
- Cache-format tests previously reported 127 passed and four optional real-map
  fixtures skipped. A final rerun was unavailable because `pytest` is not
  installed in the active Windows or WSL Python interpreters.
- No device or headset acceptance is recorded. In particular, owner testing is
  still needed for co-op passenger 6DOF behavior and vehicle comfort/recentering.
- Vehicle handle grabbing was explicitly deferred. No release, Git push, install,
  or game launch was performed.

See [TEST32-PROGRESS.md](TEST32-PROGRESS.md),
[TEST32-PLAYER-NOTES.md](TEST32-PLAYER-NOTES.md), and the build ZIP manifest for
the complete change list, controls, settings, source archive, and artifact checks.
