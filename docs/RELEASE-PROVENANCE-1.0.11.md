# v1.0.11 release provenance

Release: [Halo CE Quest VR + Android 1.0.11](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.11)  
Candidate source: `D:\HaloQuest\builds\test29-20261007-v1.0.11`  
Runtime source commit: `e9ea658180dd1da7026742eb5761c4162329b61e` on `test29-opence-144`  
Version: 1.0.11 / code 37  
OpenCE: Build 144 / network version 21  
Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`

| Release asset | Package | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `HaloCE-Android-1.0.11.apk` | `com.halo.decomp` | 26,266,164 | `3f5c385fa35ad8dbf8d327b9d427199b71d74d7d1fff1daf8350a5c2a267cefd` |
| `HaloCE-Quest-1.0.11.apk` | `com.halo.decomp.vr` | 28,347,011 | `ba6b3e807ff9f09c9547be048b9d21ef3d2b51a97b9a89de85c968032b30ec60` |
| `compatibility.json` | updater metadata | 1,400 | `a776ef2da29adab13ecb2e2a26297ac3d5f1a1612b7577cf70c8fd1a46a5729c` |

Both APKs are ARM64, minimum API 28, and retain the established project signing
certificate. They install as an in-place update; preserve app data.

## Validation recorded for the candidate

- 32 regression suites passed, including test29 network/file identity, gesture,
  wrist placement, two-hand movement, graphics layout and eye-size checks.
- Cache-format checks passed; Android, Quest and host release builds completed.
- The live directory check found 4 co-op and 10 multiplayer listings compatible
  by network version 21 on 2026-10-07.
- **No physical-device session using this exact v1.0.11 APK pair was recorded
  before publication.** The previous v1.0.10 co-op confirmation does not verify
  this network-21 pair. High-player-count performance and resolutions above
  100% are also not performance-certified.

## Contribution credit

The glasses FOV and resolution contribution by [Willem Horak (PR #1)](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1)
is included in this build. OpenCE networking and co-op changes are from
[OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE).
Additional project credits and third-party notices are in [`CREDITS.md`](../CREDITS.md).
