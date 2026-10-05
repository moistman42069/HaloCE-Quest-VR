# Release v1.0.6 provenance

Published on 2026-10-05 as the new GitHub Latest release. The previous public
releases remain intact. The APK binaries are the exact owner-provided test24b
artifacts; they were copied and renamed for stable release filenames, not
rebuilt or re-signed.

- Public tag/title: `v1.0.6` / **Halo CE Quest VR + Android 1.0.6**.
- Runtime source commit: `d066d1e2ac685225645f751cce7126f9922995f7`.
- Candidate provenance commit: `e9c14a64` (test24b delivery record).
- Internal APK version: **1.0.6 / code 32**, ARM64, minimum API 28.
- Package IDs: `com.halo.decomp` (flat Android) and `com.halo.decomp.vr` (Quest).
- Signing certificate SHA-256: `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.
- Release assets: the two APKs plus updater `compatibility.json`. GitHub supplies
  the source ZIP/tarball for the tag; no candidate ZIP, duplicate source ZIP,
  manifest, raw logs or temporary files are attached.

| Release asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Android-1.0.6.apk` | 26,081,844 | `13a9c827701585cbbb51f38ce41b5a6a899892eceed08c51b91093a1584f490b` |
| `HaloCE-Quest-1.0.6.apk` | 28,154,499 | `18441ebf48a8485d35a4f7fe63c7b2f89f9e3ea34c5f0dbe18a71a312c3db2c9` |
| `compatibility.json` | 665 | `02057f85da319371e59b81430740e7a089e0f14ac7afd7e61dbf0b7995b6a840` |

`compatibility.json` is tailored to tag `v1.0.6`, uses these release APK names,
and carries the verified byte counts and SHA-256 values. It preserves save and
configuration data, requires code 15 or newer for the integrated updater, and
describes the included VR/co-op integration and native networking compatibility.

## Included changes

The test24b build adds the Quest COMFORT settings page (smooth/snap turning,
turn speed, snap angle and vignette controls) and the SPV1 nonfunctional-status
notice. It includes test24 co-op client cutscene activation and launcher
host/join/listing guidance, test23 Quest button remapping and grenade input
changes, and test22's campaign host-crash guard. The owner reports campaign
co-op working again. Campaign remains a two-player mode; this does not certify
every mission, network or device combination.

## Validation record

The candidate record reports 26 runner suites, 127 cache-format checks passed
with 4 missing-fixture skips, and package/payload/signing/version/16 KB
alignment checks for both APKs. The source delivery record is
[`TEST24B-DELIVERY.md`](TEST24B-DELIVERY.md), with detailed implementation and
test notes in [`TEST24B-PROGRESS.md`](TEST24B-PROGRESS.md).

The owner reports co-op working again. Comfort/vignette visuals and SPV1
messaging should still be checked on target devices. Automated checks do not
replace a full campaign playthrough or establish universal multiplayer
compatibility.
