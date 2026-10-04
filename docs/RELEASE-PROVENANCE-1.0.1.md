# Release 1.0.1 provenance — WITHDRAWN

> **Withdrawn 2026-10-03.** The owner deleted the v1.0.1 GitHub release after a severe Quest VR performance regression: owner logs on Quest 3 show 17–22 fps in menus and 4–7 fps in campaign/populated PvP, against 58–72 fps for test18/1.0 on the same headset and settings. The measured evidence and cause (Safe-mode per-draw `glBufferSubData` uploads) are in [TEST20-PROGRESS.md](TEST20-PROGRESS.md). Its source stays in history for continuation only; do not republish these APKs or treat them as accepted. The current public release is v1.0.0. The record below is preserved unchanged for traceability.

Owner authorized publishing the delivered test19 pair as the new latest release. Existing v1.0.0 and test14 releases must remain unchanged. These APKs are renamed copies, never rebuilt or re-signed.

- Runtime/build source: `bc1f04465f68e3b14f1bf7de306854ae8cb36dc1`.
- Final candidate provenance commit: `bb4a6a43ca82dc039de897ae50a1e30fc2d8024f`.
- Public source: tag `v1.0.1`; publication-only documentation follows the runtime commit.
- Both: ARM64, Android API 28+, version 1.0.1, code 20.
- Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| HaloCE-Android-1.0.1.apk | 26069556 | `e31e47df5e9d01123c19411562f0460e7925bd38018560ed45abcb54b613afef` |
| HaloCE-Quest-1.0.1.apk | 28060291 | `a1bbfa09181c52abb5af728eac192c48595409b760edb3604b1288344d721bd0` |

Only the two APKs and required compatibility.json are uploaded. GitHub supplies source archives. Internal native test19 markers and the bundled candidate guide are preserved to keep approved binaries identical; current web documentation reflects the public release.

Validation: 15 targeted suites, cache checks 127 passed / 4 missing-fixture skips, both flavor builds, version/signature and 16 KB ZIP alignment checks, payload checks, UTF-8 bundled-guide comparison and source privacy review. See TEST19-DELIVERY.md. These do not certify all hardware, servers or campaign paths. In particular, intermittent left-eye corruption needs device confirmation and two-player co-op remains experimental.
