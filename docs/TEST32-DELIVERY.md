# Test32 private delivery

Target: private test candidate, version 1.0.13 / code 42, Quest VR and flat
Android. OpenCE Build 145 / network 22. Public v1.0.12 is unchanged.

Runtime source: `a5e17680d873a354d4a5df9aad60082e34972217` on
`test32-launcher-vehicles`. The VR and flat APKs were built from this exact
commit. Subsequent documentation and package-metadata updates do not change
either APK.

## APKs

| Build | File | Size | SHA-256 |
|---|---|---:|---|
| Android / flat | `HaloCE-Android-test32.apk` | 31 MiB | `ccdb02f6489cb3f15ad43565112b04f1fa48f1d8e595c14cf3ac12a1ae70f439` |
| Quest / VR | `HaloCE-Quest-test32.apk` | 33 MiB | `e67dee1df4a9475011f0871e7c0cceecceb07ef00f2436086fe9da6d63e2c98e` |

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
