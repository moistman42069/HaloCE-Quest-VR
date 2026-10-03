# Public release provenance — test13a

This release deliberately pairs the newest Quest APK with the current flat APK. Both are preserved bytes from their original builds; public publication does not rebuild or re-sign them.

| Artifact | Version | Original build source identity | SHA-256 |
| --- | --- | --- | --- |
| HaloCE-Quest-test13a.apk | 1.0-test13a, code 14 | `6c7aabf7c8974ac15e3ab302f94997ab2684dbfd` | `b84f21633e3f12cb26f5fde4c02768646f28da452e842895d0a2e59dae5824fa` |
| HaloCE-Android-test13.apk | 1.0-test13, code 13 | `68aebbc07f9731f6341a599a7b991f9233a16ac2` | `20f5d59eddb64a6088b1304199bf6ba6026523032151235f166f0bdaf4a2894a` |

Those identities belong to preserved private history and are provenance labels, not public commit links. It contains personal author metadata, so the public repository begins with a clean current snapshot using a GitHub noreply author. No private history is pushed.

The public VR and flat source archives preserve every original tracked runtime/build-source file byte for byte for their respective build revision. Markdown documentation, GitHub publishing metadata and ignore rules are refreshed/sanitized. One optional Steam Frame deployment helper now requires explicit `FRAME_HOST` instead of a personal LAN endpoint; it is not compiled into either APK. A per-file runtime/build-source manifest records hashes and permits comparison. GitHub's automatic source archive describes the release tag/current source; the separate flat archive is the precise older flat build source.

The APK certificate SHA-256 is `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. The private key is not included. Package IDs/ABI, signatures and archive integrity were checked during original packaging. Publication rechecks the bytes/signatures and the public assets. No device install/game launch is performed.

Build commands were serial `bash tools/build-quest.sh vr` / `flat`, with each APK preserved before shared native staging changed flavor. VR test13a was a later VR-only rebuild. Compiler/native/Gradle completion and signature checks do not establish campaign/avatar/phone runtime acceptance.

`release-manifest.json` and `SHA256SUMS.txt` on the release list the public artifact hashes and the public repository/tag. Dependency notices accompany the bundle. Original private source ZIPs are not uploaded because their documentation contains identifying workstation details.
