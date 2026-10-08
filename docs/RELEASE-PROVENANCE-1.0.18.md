# v1.0.18 release provenance

Release: [Halo CE Quest VR + Android 1.0.18](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.18)
Upstream: OpenCE Build 157, network 24
Version: 1.0.18 / Android code 48
Packages: `com.halo.decomp` and `com.halo.decomp.vr`; ARM64; minimum API 28
Source commit: to be filled after the release commit is published.
Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`

## APK assets

Final byte counts and SHA-256 digests are copied from the packaging manifest
after the stable APK pair is rebuilt and verified.

| Asset | Package | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `HaloCE-Android-1.0.18.apk` | `com.halo.decomp` | pending | pending |
| `HaloCE-Quest-1.0.18.apk` | `com.halo.decomp.vr` | pending | pending |
| `compatibility.json` | updater metadata | pending | pending |

## Build and validation

- Built from the final release source commit with stable version name 1.0.18
  and Android version code 48. The offline player guide and VR startup identity
  use the stable release name; no test label remains in release APK identity.
- Test37's registered Android/Quest regression suites: 62 passed. Cache-format
  pytest: 127 passed, 4 optional real-map fixture skips. Final stable package
  gate results and exact source revision are recorded below after packaging.
- Both APKs must pass established signing certificate, package/version/API/
  ARM64, ZIP/orphaned-payload, guide/license, updater marker and flat/VR
  networking parity checks.
- No exhaustive physical-device, historical server, co-op player-count or
  Original/Rev1/Rev2 XISO matrix is implied by source and automated checks.

## Release contents

Only the Android APK, Quest APK and updater-required `compatibility.json` are
attached as custom GitHub assets, in that order. GitHub's tag source archives
provide source; no duplicate source/build ZIP, logs, game data or temporary
artifacts are attached. Earlier releases and the repository About description
are preserved.
