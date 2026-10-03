# Release provenance - test14

[Public release](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/halo-ce-quest-test14). Accepted for publication by the owner on 2026-10-03 after delivery of this exact pair. The prior test13a hold is superseded for test14 only. APKs are copied unchanged from the tested delivery; publication does not rebuild or re-sign them.

## Exact binaries and source

Both packages are ARM64, version `1.0-test14`, code 15, from build commit [`696a7bbe9321565d90207042067658cb8814cad1`](https://github.com/moistman42069/HaloCE-Quest-VR/commit/696a7bbe9321565d90207042067658cb8814cad1). Tag `halo-ce-quest-test14` points to that commit; later commits are documentation follow-ups.

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| HaloCE-Quest-test14.apk | 27650336 | `96c017a6bab47c333957e6143bf0761f329802fb3710687aec7e2b1dd3ed9a56` |
| HaloCE-Android-test14.apk | 25698413 | `192d351049abfee427c2c0ddee1ee5dd820b41e3757675e11077589f987a1437` |
| HaloCE-Quest-test14-source.zip | 10236093 | `26d99433fd9dadbb182a5f8fd607ec2bef328842975e2a920ebcabff9b3ad8bf` |

Package IDs: `com.halo.decomp.vr` and `com.halo.decomp`. Established signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. The key remains private. The source archive is the exact clean public build commit and therefore retains historical pre-acceptance documentation. The release bundle contains these same APKs plus current player guides, credits and dependency notices. `release-manifest.json` records build and documentation commits; `SHA256SUMS.txt` covers downloads. A bundle changes packaging/documentation, never APK bytes.

## Build and verification evidence

VR and flat were built serially with `bash tools/build-quest.sh vr` / `flat`, preserving each output before shared native staging changed flavor. The final VR APK was compacted, aligned with `zipalign -P 16` and signed with the existing key before user delivery. Every non-signature ZIP entry matched the original build; no runtime payload changed. The larger intermediate VR APK was never the accepted candidate.

Both builds completed. Package/version/ABI/certificate checks, ZIP integrity, payload checks and source/APK privacy scans passed. Five targeted suites passed: campaign actors, campaign lifecycle, browser compatibility, VR math/weapon lifecycle and render-target storage. Native logic harnesses use sanitizers and mocked engine/transport dependencies; they do not substitute for device testing. See the [compatibility audit](COOP-COMPATIBILITY-AUDIT.md) and [original delivery record](TEST14-DELIVERY.md).

The owner previously confirmed paired Quest/flat connectivity and remote VR body movement, then accepted test14 and authorized public release. No complete campaign playthrough, universal phone compatibility or public co-op directory registration is claimed. Publication itself performs no install/game launch.

## Privacy and attribution

Only the clean public history is tagged. Private original Git history, signing keys, game maps, raw logs/recordings, private invitations and workstation details are excluded. Required third-party copyright/license notices are retained; see [CREDITS.md](../CREDITS.md). `SOURCE-IDENTITY.json` belongs to the initial import, not this updated runtime.

The original pre-acceptance candidate manifest remains preserved privately and says `runtime_accepted: false`; the release manifest separately records the subsequent acceptance. [Withdrawn test13a provenance](RELEASE-PROVENANCE-TEST13A.md) is historical and does not describe current downloads.
