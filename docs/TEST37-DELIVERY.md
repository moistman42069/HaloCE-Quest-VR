# Test37 private candidate validation and delivery

**Candidate:** 1.0.18-test37 / Android code47 / OpenCE Build157.
**Branch:** `test37-network-browser`. Public v1.0.16 and preserved Test36 artifacts remain unchanged.
**Status:** both APKs compiled; owner device acceptance pending. No publication or installation authorized/performed.

## Artifacts and source

Delivery folder: `D:\HaloQuest\builds\test37-20261008-network-browser`.
The package manifest identifies the exact committed source and APK payload hashes.
`SHA256SUMS.txt` identifies the build/source archives without a self-referential hash.

| Edition | APK | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Android / flat | `HaloCE-Android-1.0.18-test37.apk` | 32660174 | `f35338def2e1dbd07b6da8a1ecad2f17c5e20b4885684a833ffa431d394d9557` |
| Quest / VR | `HaloCE-Quest-VR-1.0.18-test37.apk` | 34753309 | `94e0cf4aabdf90fd18ffc77e092f10d462aed628c5e481670d4395b95179e10d` |

Package IDs remain `com.halo.decomp` and `com.halo.decomp.vr`, arm64-v8a,
minimum API28, using the original signing certificate:
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.
Install as an update; do not uninstall to switch builds. Game files are not included.

## Changes and use

Open either launcher server browser, refresh, then select **Network**.
Choose an exact target11-24 or **All compatible networks**. Close the game
before changing the target. The default remains24; hosting always advertises24.
Counters are reported directory populations, sorted busiest first. The choice
controls native discovery and admission, not just launcher filtering.

Original Xbox-map PvP supports targets11-24; campaign and CE maps require23/24.
Known older CE directory entries are blocked. Native checks cover both initial
admission and later lobby settings changes, before map precache/copy. If an
older host changes to campaign/CE, the client explains and leaves through the
existing server-rejection path. Host-version tracking resets on a new attempt,
reset or disposal; the local loopback host remains24.

See TEST37-PLAYER-NOTES.md for device retests and TEST37-UPSTREAM-INTEGRATION.md
for pinned source evidence. Existing VR/body/scope/turret/input/save behavior
was not changed by this networking pass.

## Validation

- Both final flavors compiled successfully after the lobby-transition guard.
- All62 regression suites have passing final results. The final serial batch
  passed61 and exposed one test extractor matching a new forward declaration
  instead of the function definition. The extractor was corrected without
  runtime changes; `test_quest_browser.py` then passed independently. Logs:
  `build/test37-checks-delivery.log` and `build/quest-regressions/`.
- Native profile checks cover exact/all targets, unsupported values, concurrent
  first-use caching, original PvP vs campaign/CE floors, actual join-version
  capture/reset and post-join mode changes. Production packet codec/reassembly
  tests cover advertisement and four-fragment settings records.
- Cache-format pytest:127 passed,4 optional real-map fixtures skipped. No
  original/Rev1/Rev2 image matrix was available.
- Live production Java parsing accepted35 deduplicated listings spanning
  versions11,18,20,21,22,24. This is a directory check, not gameplay cross-play.
- Networking parity, ZIP integrity and orphaned ZIP-space checks passed on
  the final pair. Gradle left obsolete incremental ZIP records; the existing
  `compact-quest-apk.py` removed them, aligned and re-signed both files. Every
  non-signature entry hash and signing identity remained identical.
- The original `pthread_once` cache attempt failed the guest linker. It was
  replaced by the existing mutex facility before final compilation.
- `package-quest.py` is the final delivery gate: original certificate, package
  names/versions, flavor separation, native guard markers, guides/licenses,
  networking parity and source/build archive checks must all pass.

## Limits and continuation

No headset/phone gameplay run or historical-version cross-play matrix was
performed here. Device testing is still required for joins, co-op, gameplay,
performance and switching. Protocols below11, unknown future protocols and
retail PC/MCC/Xbox networking are not enabled. Original/Rev1/Rev2 compatibility
work awaits the owner's images. The old empty-browser log did not establish
an exact device-side cause; preserve the new launch log if it recurs.

The public updater source/installation policy and public release remain intact.
Do not advance accepted pointers or publish this pair without the owner's next
instruction. Both APKs and matching source are delivered for testing.

Rebuild in WSL with the existing SDK/key, serially preserving each flavor:
`HALO_CANDIDATE_GUIDE=37 bash tools/build-quest.sh flat` and then
`HALO_CANDIDATE_GUIDE=37 bash tools/build-quest.sh vr`.
