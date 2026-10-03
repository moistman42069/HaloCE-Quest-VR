# Test14 candidate delivery ? 2026-10-03

**Private testing candidate; no public APK release is authorized.** Both flavors are version `1.0-test14`, version code 15, ARM64. Source commit: `696a7bbe9321565d90207042067658cb8814cad1`. This delivery-record follow-up changes documentation only; the matching source ZIP is an archive of that exact source commit.

| File | Bytes | SHA-256 |
| --- | --- | --- |
| HaloCE-Quest-test14.apk | 27650336 | `96c017a6bab47c333957e6143bf0761f329802fb3710687aec7e2b1dd3ed9a56` |
| HaloCE-Android-test14.apk | 25698413 | `192d351049abfee427c2c0ddee1ee5dd820b41e3757675e11077589f987a1437` |

Matching source ZIP: `HaloCE-Quest-test14-source.zip`, SHA-256 `26d99433fd9dadbb182a5f8fd607ec2bef328842975e2a920ebcabff9b3ad8bf`.
Build ZIP: `HaloCE-Quest-test14-build.zip`, SHA-256 `48a375f86cce55e2de25b6185737ea33054d9232a3ef779820b7c203c0fe305b`.
The accompanying `manifest.json` records package IDs and guest/host payload hashes; `SHA256SUMS.txt` covers the delivery files.

## Scope

- Valid host NPC controls survive the client unit update, with bounded expiry and checkpoint/death cleanup.
- NPC rest/velocity updates are applied even inside position tolerance; stale grounded/airborne presentation is corrected.
- Reliable optional campaign message 39 carries one-shot AI animation impulses with object/enum/alignment validation and native graph guards. Existing protocols/IDs are retained; use test14 on both peers.
- Unarmed campaign vehicle occupants receive seat replication.
- Co-op opens the campaign pause/settings menu without freezing only one peer.
- Legs + Arms remains the default; body, fingers, grip, room-scale legs and negotiated remote VR avatars are preserved.

## Checks completed

Serial `bash tools/build-quest.sh vr` and `flat` completed with exit 0 from the same source. Both APKs were preserved immediately before switching shared native staging. Android package/version/ABI and native/Java feature markers were checked, including the new actor-control and impulse diagnostics in both guests. Both signatures match the established certificate `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.

All five targeted suites passed: campaign actor/physics packet and lifetime logic, campaign barrier lifecycle, browser/native compatibility, VR math/weapon lifecycle, and render-target storage. Native logic harnesses use AddressSanitizer/UndefinedBehaviorSanitizer. See [COOP-COMPATIBILITY-AUDIT.md](COOP-COMPATIBILITY-AUDIT.md) for exactly what is mocked and what remains a device check. Existing tests had stale fixture fields/expectations corrected; no runtime behavior was changed to satisfy those fixtures.

The incremental VR APK had about 11.6 MB of unused ZIP space. Its ZIP entries were compacted, aligned with Android `zipalign -P 16`, and signed again using the same existing local signing key. Every non-signature entry was compared byte-for-byte with the built APK; guest/host hashes are unchanged. The final compact APK above supersedes the intermediate packaging output. The flat APK required no compaction.

APK and ZIP CRC/integrity checks and a tracked-source/archive/decoded-APK privacy scan passed. Public commit identities use GitHub noreply emails. Original private history, owner email, workstation paths, recordings, logs and keys were not published. The public repo has zero releases and zero release tags; the old private workspace points to this canonical repo.

## Acceptance / next action

No game was launched or installed. The owner previously confirmed a Quest/flat session and remote VR body movement, but test14 itself still needs their paired-device result. Public APK publication remains blocked by the owner's explicit testing hold. Use both test14 APKs together and compare NPC walking/turning/firing, death/falling, pause/resume, a checkpoint/BSP transition and vehicle entry/exit on both host assignments. Preserve both launch logs for remaining issues; full campaign progression/cinematic acceptance is not claimed.
