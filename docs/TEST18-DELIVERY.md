> **Publication update:** the owner subsequently authorized these exact APKs as release 1.0. The historical candidate hold below is superseded for this pair. See [1.0 provenance](RELEASE-PROVENANCE-1.0.0.md). No new device playthrough was reported.

# Test18 delivery

**Private candidate, not a public release.** Version **1.0-test18 / code 19** for
both editions, ARM64, Android 9/API 28 minimum. Install over the corresponding
existing app; do not uninstall or clear its data.

Runtime build source: `f45e32dd73b15280a5db4e5d4a4b2643f2c28379`.
Later changes in this candidate's source archive only finalize delivery and
publication-status documentation; packaged runtime and bundled guides match
that build commit. The private package manifest records the archive commit.

| APK | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Android-test18.apk` | 25,909,812 | `8642b62c51b759818319d6cf3a9c5761dbf0b31b5c21c150564876355390e72c` |
| `HaloCE-Quest-test18.apk` | 27,912,835 | `4de104829123fa670adf1e1aff076bcafda1d95e05d2f340293332af79658efd` |

Package IDs remain `com.halo.decomp` (flat) and `com.halo.decomp.vr` (Quest).
Signing certificate SHA-256 remains
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.

## Included changes

- Campaign seat-camera lifetime fix for the symbolicated test14 b30 -> b40 crash.
- Headset gaze and slow head movement for the opening look tutorial; safe flag indexing.
- Third Person + Right Hand vehicle defaults, applied once on upgrade with config
  backup; subsequent selections retained. First Person and left/head/stick options.
- Global/per-vehicle first-person height, forward/back and side settings, bounded
  with map collision checks, in the dedicated Vehicles pages.
- Earlier accepted body, grip, native action, touch/gamepad, multiplayer/co-op,
  game-data management and logging implementations retained.

## Validation

Both serial native/Gradle builds completed successfully. All thirteen regression
suites passed, including the new production-code vehicle/lifecycle/head tutorial
checks with ASan/UBSan. Cache-format tests: **127 passed, 4 skipped** (external
real-map fixtures unavailable). APK ZIP CRCs, identity, package/version/ARM64,
existing certificate, VR/flat payload separation, native feature markers, current
offline guides and credits are checked. APK compaction preserves every non-signature
payload hash and verifies the same certificate plus 16 KB ZIP alignment.

These checks do not replace headset/phone testing. Campaign transition, opening
look tutorial, vehicle comfort/entry/exit and paired network regression remain
owner device checks; see [progress/evidence](TEST18-PROGRESS.md).

## Publication hold

Deliver the two APKs to the owner and wait. Do not tag, upload or publish 1.0 until
the owner tests and explicitly resumes the plan. Public test14 remains unchanged;
the release API still lists only test14. The future 1.0 requires a version code
above 19 and finalized nine-section release notes. Prepared 1.0 source/notes are
retained, with no existing release replaced or removed.
