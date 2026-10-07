# Test33 private candidate delivery

## Candidate identity

- Version: **1.0.14 / code 43**
- OpenCE: **Build 145 / network 22**
- Runtime source: `e522f34c04969daaa87bfa952bb0256b222be590`
- Branch: `test33-network-browser-recovery`
- Status: private test candidate; no release, tag, or device acceptance
- Signing certificate: project test certificate, SHA-256
  `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`

## APKs

| Edition | File | Size | SHA-256 |
|---|---|---:|---|
| Quest VR | `HaloCE-Quest-test33.apk` | 34,544,259 bytes | `23ff31ad4be6d2a494fbe7637a29b26e3f5eec3218576e79330e2f63a39297e4` |
| Android flat | `HaloCE-Android-test33.apk` | 32,455,220 bytes | `f63cafe0f90b311bf1d7dbf2559c3b816c74b4f500c4686c7d01f6fca889edbe9` |

Both packages are ARM64, min SDK 28, version name 1.0.14/code 43, and use the
same project signing certificate. The VR APK carries the OpenXR loader; shared
networking code, packaged native networking strings and app classes were
verified equivalent between editions. The APKs and matching source/build ZIPs
are under `D:\HaloQuest\builds\test33-20261007-v1.0.14-final`.

## Checks completed

- All **56 registered regression suites passed** for the VR build and again for
  the Android build; both logs end with `Failed suites: []`.
- Both native builds and Gradle APK assembly completed. Payload-preservation,
  signing-certificate and 16 KB alignment checks passed.
- Candidate packaging verified APK metadata, guide assets, source privacy,
  bundled licenses, native payload identity, and checksums.
- Both APKs contain the Test33 recovery log marker. Existing Test31c Android
  controls/gameplay implementation is retained; this pass changes the shared
  browser-client lifecycle only.
- The first compile exposed obsolete declarations in the UI adapter that
  conflicted with the upstream header. The declarations were removed, and both
  clean flavor builds then passed. No files under `source/networking` or
  `source/bungie_net` differ from the Test31b runtime.

These are host and package checks. **The Test33 server-join behavior has not yet
been confirmed on a headset.** Please test the specific sequence from the
supplied log: create or join a local lobby, return to the menu, open the
in-game/public browser, and join a public server. Also test browser entry when
already searching and after a previously joined game. If joining still fails,
export a fresh launcher/native log and note the candidate version, Quest model,
network type, server name, and whether a local host was used first.

No APK was installed and no game was launched during this pass.
