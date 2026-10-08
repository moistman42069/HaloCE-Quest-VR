# Test36 private candidate delivery record

**Status:** validated private APK pair, ready for owner device testing.
**Candidate:** 1.0.17-test36 / Android code46 / OpenCE Build157 / network24.  
**Public release:** v1.0.16 remains Latest; no publication is authorized.

## Package artifacts

Final folder: `D:\HaloQuest\builds\test36-20261008-network24`.
Final app source: `a1e0402617fc76105aea2e084bc36f9ada888c2b`.
Native source was compiled at `ceaa304ddc55976243499f5ddfe40a19d927bfc1`;
the only later app change is the Gradle private version label. Native payload
bytes were explicitly compared before and after Java/manifest regeneration.
Later commits only update package verification and documentation. The source
archive's exact commit is in `manifest.json`; archive hashes are in
`SHA256SUMS.txt` to avoid a self-referential checksum in this document.

| Edition | APK | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Android / flat | `HaloCE-Android-1.0.17-test36.apk` | 32650278 | `1a52d5874318eafb17397b600a222b6f73180dbca1019251646c1147a7a007ad` |
| Quest / VR | `HaloCE-Quest-VR-1.0.17-test36.apk` | 34742773 | `992c82cd1a6882655cef4807e089c1aa84191d34e43a506ff82d00f67fff6ddc` |

Both are 1.0.17-test36/code46, arm64-v8a, minimum API28, network24, with their
existing package IDs and original signing certificate
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.

## Checks

Before building: all 59 suites in serial `tools/run-quest-checks.py` passed.
Cache-format pytest completed with 127 passed and four optional real-map
tests skipped because the stock CE/OpenSauce fixture set was not configured.
The live signed-discovery/native admission check accepted an actual
current listing under network24 and rejected it under network23; see
TEST36-PROGRESS.md. `git diff --check` and Python syntax compilation passed.

The first Quest compilation caught an unavailable `PIN` macro in the new
diagnostic-only angle calculation. It was replaced with explicit bounds
checks; the finite-value guard and aim behavior are unchanged. The affected
Test21/Test36 checks and the real Quest-target `vr_frame.c` compilation then
passed. Both APKs are rebuilt from the corrected source before delivery.

Package validation also caught the Gradle fallback labeling a private build
as `1.0.17` instead of `1.0.17-test36`. The branch now defaults to the private
identity without requiring a shell override. Both Gradle packages are
regenerated; their native payloads must remain byte-identical to the corrected
native builds. The parity check explicitly recognizes only the exact reviewed
VR startup banner, whose change summary happens to contain the word "lobby";
altered banners and networking differences remain rejected by fixture tests.

Final APK verification passed: signatures, package IDs, versions, ABI/API,
shared networking runtime strings/imports and Java classes, flavor-specific
OpenXR/touch payload separation, new diagnostics, offline guidance, licensed
font/hash, ZIP integrity and stale ZIP payload checks. Source/build archives
also passed checksum validation. The packaging parity fixture rejects altered
identity strings and genuine runtime/config/import differences.

Live read-only discovery succeeded through all four default brokers using
both MQTT3.1.1 and MQTT5. At 12:05 EDT the MQTT5 sample included 16 signed
network24 listings and zero network23 listings. This is not an Android gameplay
connection test. No app was installed or launched, and no release was pushed.

## Rebuilding and owner retest

Use the established local SDK/signing setup and run serially, preserving each
APK before switching flavors:

```sh
HALO_CANDIDATE_GUIDE=36 bash tools/build-quest.sh flat
HALO_CANDIDATE_GUIDE=36 bash tools/build-quest.sh vr
```

See TEST36-PLAYER-NOTES.md for browser, scope and vehicle diagnostic checks.
The owner must report Quest and Android results separately. Network24 cannot
join public v1.0.16/network23 sessions. Gameplay/co-op/device performance are
not certified by host tests. Scope, turret and save reports without matching
failure evidence retain their existing behavior. The previously deferred
interaction backlog remains in VR-INTERACTION-REQUIREMENTS.md.
