# v1.0.16 release provenance

Release: [Halo CE Quest VR + Android 1.0.16](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.16)
Upstream: OpenCE Build 148, network 23
Version: 1.0.16 / Android code 45
Packages: `com.halo.decomp` and `com.halo.decomp.vr`; ARM64; minimum API 28
Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`

## APK assets

Final byte counts and SHA-256 digests are recorded below after the stable
release-identity rebuild and package verification.

| Asset | Package | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `HaloCE-Android-1.0.16.apk` | `com.halo.decomp` | pending | pending |
| `HaloCE-Quest-1.0.16.apk` | `com.halo.decomp.vr` | pending | pending |
| `compatibility.json` | updater metadata | generated from the final APK hashes | pending |

## Build and validation

- Build both editions from the recorded runtime source commit and the same
  committed guide/settings sources.
- Record the source commit, runtime source commit, test results, APK signature,
  ZIP integrity, ABI, version, compatibility metadata and networking parity
  after final packaging.
- No Android or Quest device session on this exact APK pair is recorded.
  Publication authorization is not device acceptance.
- The Test35 host-check record reports 127 cache tests passed and 4 skipped
  because real Custom Edition map fixtures are unavailable. Re-run the current
  focused tests and full Android/Quest build checks for this release.
- The build environment's Clang 18 does not use the available Clang 22 PGO
  profiles; builds use the supported non-PGO fallback.

## Release contents

Only the Android APK, Quest APK and updater-required `compatibility.json` are
attached as custom GitHub assets, in that order. GitHub's tag source archives
provide the source; no duplicate source/build ZIP, logs, game data or temporary
artifacts are attached. Earlier releases and the repository About description
are preserved.

Credits and user-facing compatibility limits are in [RELEASE-1.0.16.md](RELEASE-1.0.16.md).
