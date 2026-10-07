# Test34 private candidate delivery record

## Build identity

- Candidate: Test34, Android/Quest version 1.0.15, Android version code 44.
- Runtime source commit: `43872afb4b6afda491d1ab414b9378ac70b4aeca`.
- OpenCE baseline: official Build 147 tag, commit
  `34e2d4fdd884d503e9e441155404612473591f8e`, network 23.
- Package output: `D:\HaloQuest\builds\test34-20261007-v1.0.15-scope-diagnostics\package`.
- Candidate input APKs are in
  `D:\HaloQuest\builds\test34-20261007-v1.0.15-scope-diagnostics`.
- Public GitHub release: none. Existing v1.0.12 remains unchanged.

## APKs

| Edition | File | Size | SHA-256 |
|---|---|---:|---|
| Quest VR | `HaloCE-Quest-test34.apk` | 34,730,887 bytes | `db637906f9087ab76a840366c979e54f9ff9d67455f62fd75e20ea7058700fd7` |
| Android flat | `HaloCE-Android-test34.apk` | 32,639,952 bytes | `796783b60d2db60f97a5aae7185a7e779d8deb88fd9cd5e85e8f0273982eaa53` |

Both are ARM64, version **1.0.15 / code 44**, min SDK 28, and signed with the
project test certificate (SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`). The VR
APK includes the OpenXR loader. The final package contains these APKs, a
matching source ZIP and candidate build ZIP, `manifest.json`,
`compatibility.json` and `SHA256SUMS.txt`.

## Verification

- `bash tools/build-quest.sh vr` and `bash tools/build-quest.sh flat` each
  completed; the script ran all **57 registered regression suites** before
  each flavor build. Both runs ended with `Failed suites: []`.
- Focused `test_test22.py` scope transform and `test_test34_opence.py`
  Build147/scope diagnostics checks passed.
- `aapt dump badging` confirms package IDs `com.halo.decomp.vr` and
  `com.halo.decomp`, version code 44/name 1.0.15, min SDK 28 and target SDK 35.
  Both APK signatures match the existing project test certificate.
- Native release-mode builds and Gradle APK assembly completed for both
  editions. The installed compiler is Clang 18; this build has no Clang 22 PGO
  profile, so the build script correctly fell back to non-PGO compilation.
- The Test34 scope log is from 1.0.12/Test30 and shows no engine zoom state or
  scope layer. The new build logs scope setting, trigger, native zoom and
  rendering-gate transitions; it does not claim the reporter's hardware issue
  is fixed until their retest identifies the gate.
- Cache-format pytest was not rerun because pytest is absent from the WSL
  Python environment. The earlier Test34 cache-format result was 127 passed,
  4 optional real-map skips; no cache-format code changed in this follow-up.
- APK parity, candidate archives, manifest and checksums are verified by the
  final package step; archive hashes are listed in the package's
  `SHA256SUMS.txt`.

No physical Android or Quest test is represented as passing until the owner
reports it.

## Device acceptance still required

Follow the [Test34 player notes](TEST34-PLAYER-NOTES.md): launch both variants,
exercise the pointer-select server list, load representative maps, and test
network-23 joins/co-op. Preserve logs from all peers. No publish or push is
authorized in this task.
