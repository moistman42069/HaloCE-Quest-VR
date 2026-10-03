# Game data compatibility and graphics evidence

Updated for test17, 2026-10-03. Disc labels and installed cache formats are different facts.

## What is established

The inherited decomp target is the Xbox PAL debug build 2342, not a restriction that every player's disc must have that label. The port's cache code recognizes Xbox cache format 5 and build strings `01.01.14.2342`, `01.10.12.2276`, and `01.08.15.1749`; its existing PAL tag normalization remains automatic. Launcher **Game data & compatibility** reads the installed header/build/type and can compute per-file SHA-256 fingerprints locally. The report is added to the existing launch log; it uploads nothing.

Original, Rev1 and Rev2 disc variants are catalogued, but a disc revision label alone does not prove which installed map bytes a report used. No verified Original/Rev1/Rev2 map hash matrix is available here. No confirmed Rev1 device result was found in the reviewed Flat2VR thread. Original and Rev2 both have working reports; one reporter reproduced the same stretched geometry with both. Another described mostly clean multiplayer maps. This contradicts treating Rev2 alone as the cause.

No local legal stock Original/Rev1/Rev2 dataset was available for byte comparisons or a three-revision gameplay test. Synthetic header tests verify recognition and malformed/truncated rejection; they do not validate the complete content of those discs. Test17 adds a real managed-data selector with detected cache builds and SHA-256 fingerprints; exact disc revision labels remain unverified. See [Game files & versions](GAME-DATA-LIBRARY.md). Maps with incompatible format/build cannot be selected for launcher PvP hosting. Custom content remains experimental and needs matching resources on peers.

## Geometry changes

- Stream and index uploads now copy the actual payload length, reserving alignment padding separately. Tests use exact-sized allocations under AddressSanitizer.
- Persistent-buffer availability is tracked per ring slot; failed immutable allocation/mapping gets a new mutable buffer before fallback.
- A failed frame-fence wait completes queued GPU work before reusing storage.
- Static mirror writes use ordered `glBufferSubData`, including first writes. Adapted from [Andiweli/HaloCE-Android-AAOS a88f257](https://github.com/Andiweli/HaloCE-Android-AAOS/commit/a88f25763b8a51335554ef02e613127ee92677d4), whose diagnostic described zero GPU pages despite populated CPU geometry. Its global 30 FPS/interpolation-off policy is not imported.
- **Geometry compatibility > Safe** bypasses persistent streaming, static mirrors and GPU base-vertex rebasing. Restart required; potentially slower. Safe is the VR default since test16, including one-time migration; Normal remains the flat default.

The owner reports Safe fixed the submitted bridge rendering fault. This is a specific device/scene result; other scenes and devices remain unverified. Keep the launch log and data fingerprints when reporting a new issue.

## Networking is separate

Native v9/v10/v11 protocol support concerns message layouts, not disc revision names. Retail PC/Custom Edition/MCC/Xbox multiplayer protocols cannot join native-port games merely by choosing different data. Co-op needs matching mission/resource content and the campaign-capable project build. Unsupported/missing maps, full/closed sessions, expired invites and NAT failure can independently prevent joins.

Header-format reference: [SnowyMouse's Halo cache documentation](https://gist.github.com/SnowyMouse/39168bddd597549038a35d78aee39513), CC BY 3.0, author attribution retained. The launcher checks the 2048-byte header, signatures, format, build string and type; it does not authenticate a whole map from its header.


## Test17 join investigation

Different ISO/revision or modified map files can cause content incompatibilities;
the launcher now explicitly says so in both browsers and the data screens.
Revision names alone do not establish a cause. The supplied test16 failures
instead exposed a PvP in-progress/campaign flag collision and an unmasked
keyboard action-only control bit. [Detailed evidence](TEST17-PROGRESS.md).
The native map guard retains recognized cache-build checks because distributed
object/damage messages refer to tag definitions. The public feed does not
advertise per-map hashes or disc revisions, so set selection offers maps by
availability and never claims a verified per-server revision match.
