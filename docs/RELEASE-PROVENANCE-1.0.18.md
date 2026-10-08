# v1.0.18 release provenance

Release: [Halo CE Quest VR + Android 1.0.18](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.18)
Upstream: OpenCE Build 157, network 24
Version: 1.0.18 / Android code 48
Packages: `com.halo.decomp` and `com.halo.decomp.vr`; ARM64; minimum API 28
Runtime source commit: `2680beaa42d9b53098a21198200f79c76aa3b308`
Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`

## APK assets

Final byte counts and SHA-256 digests are copied from the stable packaging
manifest after rebuild and package-gate verification.

| Asset | Package | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `HaloCE-Android-1.0.18.apk` | `com.halo.decomp` | 32,672,838 | `076ccb567c5b05c6d2e1a97e84bcd4b3f2c729d702822814327975ae9b5ab86e` |
| `HaloCE-Quest-1.0.18.apk` | `com.halo.decomp.vr` | 34,765,337 | `6f1b20b4e6f2a3e8aee35c3f6c2aa5a8f6c52bd6510922ef8b6904c5124864c4` |
| `compatibility.json` | updater metadata | 821 | `02a6ef05ba32e01c38953198da8815e665c592cc76452be05f6306bb52c1f621` |

## Build and validation

- Built from runtime source commit `2680beaa` with stable version name 1.0.18
  and Android version code 48. The offline player guide and VR startup identity
  use the stable release name; neither APK carries the Test37 version label.
- All 62 registered Android/Quest regression suites passed for both build
  flavors. Cache-format pytest reported 127 passed and 4 optional real-map
  fixture skips because the required real maps are unavailable here.
- The final stable package gate passed APK signing certificate, package/version,
  API/ARM64, ZIP/orphaned-payload, guide/license, updater markers and flat/VR
  networking parity checks. Both APKs use the established project certificate.
- OpenCE's clang 22 PGO profiles are unavailable to the installed clang 18, so
  this build uses the supported non-PGO build path.
- No exhaustive physical-device, historical server, co-op player-count or
  Original/Rev1/Rev2 XISO matrix is implied by source and automated checks.

## Release contents

Only the Android APK, Quest APK and updater-required `compatibility.json` are
attached as custom GitHub assets, in that order. GitHub's tag source archives
provide source; no duplicate source/build ZIP, logs, game data or temporary
artifacts are attached. Earlier releases and the repository About description
are preserved.
