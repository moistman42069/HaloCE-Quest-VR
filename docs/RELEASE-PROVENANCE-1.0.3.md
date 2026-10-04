# Release 1.0.3 provenance

The owner requested that the test21b build appear as the new top release. GitHub now has a semantic version tag `v1.0.3`, which sorts correctly in the releases list and is recognized by the stable updater. The existing `halo-ce-quest-test21b` release remains intact as a legacy download. The v1.0.2/code-25 release is also unchanged.

- Release source/documentation commit: see the `v1.0.3` Git tag.
- Runtime source commit: `3ab3b5053a9db395b0b9caa10628be9a5d14f3ed`.
- APK artifact source package commit: `3afa9b1156c685502b0a890f62ab489eaadb95b4`.
- APK contents are byte-for-byte the supplied signed test21b artifacts; only release asset filenames and compatibility metadata were adjusted.
- APK internal version name **1.0.2**, version code **27**; public tag/title **v1.0.3**. The previous public APKs are code 25. The code increase allows install-over updates.
- Package IDs: `com.halo.decomp` and `com.halo.decomp.vr`; ARM64, minimum API 28.
- Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, matching prior releases.

| Release asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Android-1.0.3.apk` | 26,077,748 | `24bbdd4be22056dd8641fdfe6089f0852701efdd3d092847f1988d691eaa7905` |
| `HaloCE-Quest-1.0.3.apk` | 28,084,867 | `b2264664cd290411e3113cb815796cb0dd0e338f9c0b26a1ca81c33804c76550` |
| `compatibility.json` | 820 | `0f27a4a327bde06f1d52ea881a5b1641b28e40f5dd1df17e0eab2f7794aeea8e` |

The release contains only the two APKs and updater metadata; GitHub creates the source archives automatically. The same APK SHA-256 values and code 27 are already present on the test21b release; no runtime code or signature changed. The updater expects standard `v1.0.3` APK filenames, verifies the metadata tag/digest/size, and offers code 27 to code-25 installations.

Candidate checks are recorded in [`test21b provenance`](https://github.com/moistman42069/HaloCE-Quest-VR/blob/v1.0.3/docs/RELEASE-PROVENANCE-TEST21B.md): 22 runner suites, 127 cache checks passed with 4 missing-fixture skips, both APK package/ABI/signature/payload checks and 16 KB alignment. No phone or headset session was performed for test21b. The bundled Field Guide still reports code 25 and older Two Hands instructions; the release page is the current guide.
