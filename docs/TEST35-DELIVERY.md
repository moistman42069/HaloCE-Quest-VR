# Test35 pre-release candidate artifact record

These test35-named APKs were the private candidate inputs before the v1.0.16
stable-identity rebuild. They are not the public release assets. Use
[`RELEASE-PROVENANCE-1.0.16.md`](RELEASE-PROVENANCE-1.0.16.md) for the final
published filenames and hashes.

## Candidate identity

- Candidate: Test35, Android/Quest version **1.0.16**, version code **45**.
- Upstream baseline: OpenCE Build 148, commit
  `ff47e47ad6f54bc533cee2a0fe57232c8f63d614`, network 23.
- Package output: `D:\HaloQuest\builds\test35-20261007-build148\package-test35`.
- Public GitHub release: none. Preserve existing public releases.

## APKs

| File | Package | Size | SHA-256 |
| --- | --- | ---: | --- |
| `HaloCE-Android-test35.apk` | `com.halo.decomp` | 32,955,769 bytes | `DC63E228CC71F29B94EE10DB72EEC8180E697DB223037F315CAE10EF1B811996` |
| `HaloCE-Quest-test35.apk` | `com.halo.decomp.vr` | 53,096,320 bytes | `80D8F5D7C1EA64D37EEFDBB34A4CA5D411E88C86C4720E23CFCC4B32BDAE9EAC` |

Both report version name **1.0.16**, version code **45**, minimum Android API
28, and native ABI `arm64-v8a`. Both verify with APK Signature Scheme v2 and
the existing test signing certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.
The candidate folder also contains the two raw APKs. The package directory
contains a combined build ZIP, matching source ZIP, `manifest.json`,
`compatibility.json`, and `SHA256SUMS.txt`.

## Validation

- `tools/build-quest.sh flat` and `tools/build-quest.sh vr` both completed.
  The full registered Quest/Android regression suite passed on both build
  runs; `tools/run-quest-checks.py` reported `Failed suites: []`.
- `python3 -m pytest -q tools/test_cache_file_formats.py`: **127 passed, 4
  skipped**. Those four cases require real Custom Edition map fixtures, which
  are not available in this workspace.
- Focused Test35 checks passed for negative/NaN radius repair, the runtime
  physics guard, schema wiring, halt-screen diagnostics, updater Build 148
  metadata and the SPV1 size note.
- Both APKs passed signature, package/version, ARM64, ZIP integrity and 16 KB
  native-library alignment checks. Networking assets, app classes and all APK
  entries matched except the VR-only OpenXR loader.
- The build environment uses Clang 18 while saved PGO profiles require Clang
  22. The build completed successfully without profile-guided optimization.

## Limits and device follow-up

No Android or Quest device was launched or installed by this build process;
device acceptance remains pending. Host checks do not certify all hardware,
maps, servers or multiplayer sessions. Test both APKs over existing installs
without uninstalling or clearing app data.

SPV1 remains **experimental and unverified**. Its ten listed map files range
from 157 to 253 MiB, so they exceed a 128 MiB limit. The current Custom Edition
reader's file-size caps are 384 MiB for ordinary caches and 576 MiB with
OpenSauce upgrades; the listed files fit those bounds. This only means file
size alone does not rule them out. Protected-map conversion, resources and an
SPV1 campaign still require device testing.
