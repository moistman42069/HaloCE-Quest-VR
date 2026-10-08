# v1.0.16 release provenance

Release: [Halo CE Quest VR + Android 1.0.16](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.16)
Upstream: OpenCE Build 148, network 23
Version: 1.0.16 / Android code 45
Packages: `com.halo.decomp` and `com.halo.decomp.vr`; ARM64; minimum API 28
Runtime source commit: `09a95871e94f15d02d777c67bb2d9b927723d85d`
Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`

## APK assets

Final byte counts and SHA-256 digests are from the clean stable-identity builds
and the updater compatibility file generated from those APKs.

| Asset | Package | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `HaloCE-Android-1.0.16.apk` | `com.halo.decomp` | 32,631,276 | `dfe000e13c6554b10c20ca9d638c83d1e7d8363e80cd9d2c5ea6c6969dc1292a` |
| `HaloCE-Quest-1.0.16.apk` | `com.halo.decomp.vr` | 34,722,207 | `317f6c6ee7fd2f0d97aad2083b80e9a47f495a90ed2a1c8638767e702f4e2287` |
| `compatibility.json` | updater metadata | 821 | `8175f459494657fcc8208137c9d3d9acbe1a055fd1dd0e0a1a6838e1750b9355` |

## Build and validation

- Built both editions from the recorded runtime source commit and the same
  committed guide/settings sources. The stable version banner and offline
  guide identify v1.0.16 / Build 148 / network 23.
- The full registered Android/Quest build regression suites passed on both
  builds (`Failed suites: []`). The focused Build 148 particle/error tests
  passed. `tools/test_cache_file_formats.py` reports **127 passed, 4 skipped**;
  the skipped cases need real Custom Edition maps unavailable in the workspace.
- Both APKs pass signature/package/version/API/ARM64 checks, ZIP integrity,
  stale unindexed-payload detection, updater markers, bundled guide checks and
  flat/VR networking parity. The APK signer digest matches the established
  project certificate above.
- No Android or Quest device session on this exact APK pair is recorded.
  Publication authorization is not device acceptance.
- The build environment's Clang 18 does not use the available Clang 22 PGO
  profiles; builds use the supported non-PGO fallback.

## Release contents

Only the Android APK, Quest APK and updater-required `compatibility.json` are
attached as custom GitHub assets, in that order. GitHub's tag source archives
provide the source; no duplicate source/build ZIP, logs, game data or temporary
artifacts are attached. Earlier releases and the repository About description
are preserved.

Credits and user-facing compatibility limits are in [RELEASE-1.0.16.md](RELEASE-1.0.16.md).
