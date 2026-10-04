# Release 1.0 provenance

The owner explicitly authorized 1.0 using the exact delivered test18 APKs.
Release tag: `v1.0.0`. Previous public test14 remains unchanged. No APK is rebuilt,
modified or re-signed: only the download filename changes.

Runtime build source: `f45e32dd73b15280a5db4e5d4a4b2643f2c28379`.
Candidate documentation source: `636452895e7b67dd19cd0565c64c844230565a88`.
The release tag adds public documentation to that source; runtime code is identical.
The tag is also the source for GitHub's normal ZIP/tar.gz archives.

| Release asset | Bytes | SHA-256 |
| --- | ---: | --- |
| HaloCE-Android-1.0.0.apk | 25,909,812 | `8642b62c51b759818319d6cf3a9c5761dbf0b31b5c21c150564876355390e72c` |
| HaloCE-Quest-1.0.0.apk | 27,912,835 | `4de104829123fa670adf1e1aff076bcafda1d95e05d2f340293332af79658efd` |

Internal app version: **1.0-test18**, Android code **19**, ARM64/API 28 minimum.
Package IDs: `com.halo.decomp` / `com.halo.decomp.vr`.
Certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.
See TEST18-DELIVERY.md for original candidate names and matching hashes.

Only both APKs and `compatibility.json` are uploaded. Metadata uses tag `v1.0.0`,
release filenames, real code 19, exact hashes/sizes, Network 9-11 and CE01.
No invented version code or runtime version is used to bypass updater validation.
Users already on test18 have identical bytes; its same-code update message and
preserved candidate/offline-guide wording are explained in release notes.

Validation: both serial builds, thirteen targeted regression suites, 127 cache
checks with four unavailable-fixture skips, signature/ABI/version, payload/ZIP
integrity and 16 KB ZIP alignment passed for the delivered pair. Publication
preflight rechecks those artifacts and the exact source/digests. Owner approval
for release does not imply a newly reported full headset/campaign playthrough.
The published release/downloads and unchanged test14 metadata are checked after
publication; private inspection records are kept outside source control.
