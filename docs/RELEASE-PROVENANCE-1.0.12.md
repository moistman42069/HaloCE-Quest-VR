# v1.0.12 release provenance

Release: [Halo CE Quest VR + Android 1.0.12](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.12)  
Candidate source: `D:\HaloQuest\builds\test30-20261007-v1.0.12`  
Runtime source commit: `688a63e3635efc97b93caeb62b5a07a0db1f6325` on `test30-profiles-coopname`  
Version: 1.0.12 / code 38  
OpenCE: Build 144 / network version 21  
Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`

| Release asset | Package | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `HaloCE-Android-1.0.12.apk` | `com.halo.decomp` | 26,270,260 | `63af9c7ac012c3d68d4036af9c432ef7134e274f11a0c69b5f56b9c09151fcf1` |
| `HaloCE-Quest-1.0.12.apk` | `com.halo.decomp.vr` | 28,347,011 | `dcbce7fed5d02161a22441b7d18cdfc9ded59250b181e83b21ffc1c9e9b27f22` |
| `compatibility.json` | updater metadata | 1,400 | `a5241304e3a92a1680cfbb0353c586aeea7009830b83dea5e30afefb17ab1e89` |

Both APKs are ARM64, minimum API 28, and retain the established project signing
certificate. They install as an in-place update; preserve app data. The network
remains OpenCE Build 144 / version 21, so v1.0.11 peers remain protocol-compatible.

## Validation recorded before publication

- 33 regression suites passed, including test30 checks for menu button behavior,
  gameplay binding preservation, and campaign host-name parsing and request
  handling.
- Android and Quest release builds completed.
- **No physical-device session using this exact v1.0.12 APK pair was recorded
  before publication.** Verify VR profile deletion, named and unnamed campaign
  hosting, joining and normal Android/Quest gameplay after updating.
- Campaign lobby sizes through 128 remain selectable; this does not establish
  stable Quest/phone performance at high player counts.

## Carried-forward credits

The glasses FOV and resolution contribution by [Willem Horak (PR #1)](https://github.com/moistman42069/HaloCE-Quest-VR/pull/1)
remains in the build. OpenCE networking and co-op changes are from
[OpenCommunityEdition/OpenCE](https://github.com/OpenCommunityEdition/OpenCE).
Additional project credits and third-party notices are in [`CREDITS.md`](../CREDITS.md).
