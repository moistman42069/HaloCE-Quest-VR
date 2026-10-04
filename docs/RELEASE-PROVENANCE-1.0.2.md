# Release 1.0.2 provenance

The owner authorized publishing the exact test20e APK pair as the latest release. The withdrawn v1.0.1 release and prior test14/v1.0.0 releases are preserved. APKs are renamed copies: no rebuild or re-sign occurred during publication.

- Tag: `v1.0.2`; app version 1.0.2, Android version code 25.
- Candidate/package source commit: `245d14ed3a067f9c92eeafba680c84212b20ccfc`.
- Runtime source commit: `4e7e1e4a415727fdefdfe91ad3d1eb61d6968c68`.
- Package IDs: `com.halo.decomp` and `com.halo.decomp.vr`; ARM64, API 28 minimum.
- Established certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.

| Release asset | Bytes | SHA-256 |
| --- | ---: | --- |
| HaloCE-Quest-1.0.2.apk | 28080771 | `efcf6e67593b7fc5141ca6d054ba6251f62bfbfcbd13a492290365177a25c457` |
| HaloCE-Android-1.0.2.apk | 26073652 | `08b42aef08e5fc7a8ccaeea3a7db3cf6317d97da0dbf88243b27bb56349cd8fd` |

The runtime adds Quest/Android parity guards, network-stage/NAT diagnostics and a per-frame VR crosshair update. Test20 restored fenced Safe geometry uploads and added `[render-perf]` diagnostics after the v1.0.1 slowdown. Performance recovery was confirmed on device in test20b; test20e networking and crosshair behavior still need user device checks. The public source tag adds documentation after the candidate commit. GitHub generates source archives. Only compatibility.json accompanies the two APKs.

The delivery record reports 21 runner suites, cache checks (127 passed, 4 missing-fixture skips), package/version/signature, payload and 16 KB alignment checks. Automated checks do not establish test20e phone/headset join success, universal multiplayer, a full campaign run or resolution of left-eye corruption. Previous releases remain unchanged.
