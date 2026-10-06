# Release v1.0.10 provenance

Prepared 2026-10-06 for the new GitHub Latest release. Before publication, the
previous public releases remain intact. The two APKs are the exact test28 candidate artifacts,
copied and renamed for stable release filenames; they were not rebuilt or
re-signed for publication.

- Tag/title: `v1.0.10` / **Halo CE Quest VR + Android 1.0.10**.
- Runtime source: `235c2f5b249c5f68de9fd425c31643bcebeb28f2`.
- Publication source: this tagged repository commit; test28 source and checks
  are documented in [TEST28-PROGRESS.md](TEST28-PROGRESS.md).
- Internal version: **1.0.10 / code 36**, ARM64, minimum Android API 28.
- Packages: `com.halo.decomp` (Android flat) and `com.halo.decomp.vr`
  (Quest VR).
- Signing certificate SHA-256:
  `53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.
- Network: OpenCE Build 138, exact-match network version 20.
- Release assets: Android APK, Quest APK, updater `compatibility.json`.
  GitHub supplies the source ZIP/tarball. Candidate archives, logs, manifests
  and temporary build artifacts are not attached.

| Release asset | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Android-1.0.10.apk` | 26,253,876 | `70c712edb5a7b525a0f806ff6643e0ed6be61067022223dd45532ae60c0f28d8` |
| `HaloCE-Quest-1.0.10.apk` | 28,265,091 | `5e7beecb4ea9216b3f3d8268899fd210db1f4b8adfbe47bea3f714caa1f207ba` |
| `compatibility.json` | 1,400 | `ab4af57307d50036c9b48096829a68f31076cd083964683768d6ac46f516c983` |

`compatibility.json` is specific to tag v1.0.10 and the two release APK
names/hashes. It preserves save/configuration policy and provides network-v20
and campaign co-op metadata for the integrated updater.

## Changes

The release directly uses OpenCE Build 138 netcode/co-op at network v20. Test28
fixes the host-watching camera orientation fault seen when joining a campaign
already underway, builds with OpenCE release-mode handling, expands the
campaign host selector to OpenCE's available sizes up to 128, and adds optional
flat-Android gyro aim. The owner reports co-op works well in testing; exact
pairing, mission and lobby size were not recorded. High-count performance and
gyro behavior were not reported as tested.

## Validation

Candidate records show 30 regression suites passing, including network/browser
coverage, the join camera across 19,032 views, release-mode checks, co-op size
choices and gyro math/wiring. Cache-format checks and both Android/Quest release
builds passed. The owner subsequently confirmed co-op works well. This does not
establish every game revision, mission, network or high-player-count setup.
