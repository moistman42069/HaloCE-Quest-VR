# Test21b release provenance

GitHub Latest release: `halo-ce-quest-test21b` (title: Halo CE Quest VR + Android 1.0.2, test21b). This release promotes the exact signed APK pair from the owner-provided test21b candidate artifacts. It is the first public test21b package, not a new internal version name: both APKs report **1.0.2 / version code 27**. The previous stable `v1.0.2` release (code 25) remains intact.

- Candidate/package source commit: `3afa9b1156c685502b0a890f62ab489eaadb95b4`.
- Runtime source commit: `3ab3b5053a9db395b0c9aa10628be9a5d14f3ed`.
- Package IDs: `com.halo.decomp` (flat Android) and `com.halo.decomp.vr` (Quest VR).
- ABI / minimum Android API: ARM64 / 28.
- Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`, matching the prior public release.
- Native host network version 11; reviewed compatibility range 9-11. Campaign protocol `52737`; this does not certify full campaign runtime compatibility.
- The exact updater metadata shipped as the third and only non-APK release asset is tracked at [`releases/test21b/compatibility.json`](../releases/test21b/compatibility.json).

| Release asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Android-test21b.apk` | 26,077,748 | `24bbdd4be22056dd8641fdfe6089f0852701efdd3d092847f1988d691eaa7905` |
| `HaloCE-Quest-test21b.apk` | 28,084,867 | `b2264664cd290411e3113cb815796cb0dd0e338f9c0b26a1ca81c33804c76550` |
| `compatibility.json` | 839 | `4a5eac8c27da83429be004e1b4baae504ac0ab65597d73e86e949ed8806dd8e3` |

The candidate source ZIP SHA-256 was `ebaa684e357ddfd16905c0f9f084f33df6c050019b9ed714aa2496572d5597ad`; GitHub's source archives for the release tag are generated automatically and differ because they include the release documentation. The release includes no build ZIP, duplicate source ZIP, logs, raw media, game data, private paths or signing key.

The candidate delivery reports 22 runner suites passing, cache checks with 127 passed and 4 missing-fixture skips, matching Quest/Android network parity, APK package/ABI/version/signing checks, payload validation and 16 KB alignment. **No phone or headset session was performed for test21b.** Inferred body behavior, the reticle/impact alignment and vehicle horn still need real-device confirmation. The campaign co-op protocol has not been fully runtime-verified. See [`RELEASE-TEST21B.md`](RELEASE-TEST21B.md), [`TEST21B-DELIVERY.md`](TEST21B-DELIVERY.md) and [`TEST21B-PROGRESS.md`](TEST21B-PROGRESS.md) for feature details, checks and remaining work.

The APK's bundled Field Guide was not regenerated for this candidate and still reports code 25; its Two Hands text is also older. Use the test21b release page as the current guide. The exact signed APKs are intentionally preserved; no rebuild or re-sign occurred for this publication.
