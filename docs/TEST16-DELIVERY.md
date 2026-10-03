# Test16 candidate delivery

VR and flat Android: `1.0-test16`, version code 17, ARM64, Android API 28 minimum.
Publication held for owner testing. Test14 remains the accepted public release.

This candidate adds VR Safe geometry defaults and native action arm handoff,
while preserving the final test15 controller/networking/launcher/co-op work.
See [implementation and targeted device checks](TEST16-PROGRESS.md).

The package manifest identifies the committed source, APK/guest/host hashes,
signing certificate and compatibility fields. `SHA256SUMS.txt` covers both APKs,
build/source ZIPs and manifests. No game assets, private recordings/logs or keys
are included. Both editions are rebuilt from the same runtime source because
launcher/config/parser changes are shared; flat geometry still defaults to Normal.

All ten automated regression suites passed, including the new state/matrix/config
suite and all nine test15 suites. Final APK build/integrity provenance is recorded
in the package manifest and SHA256SUMS after packaging. No device installation, game launch or GitHub release is performed.

## Final build provenance

Both APKs were built serially from runtime commit
`1288c6696d1d26cca21719cce062f762d0b1e022`. Subsequent delivery documentation/test
fixture changes do not change runtime source or APK payloads. The source archive
and manifest identify the final continuation commit, which includes this record.

| APK | Bytes | SHA-256 |
| --- | ---: | --- |
| HaloCE-Quest-test16.apk | 27843133 | `dcf419e5a4e427cd4f3e6cde7e6c7d771cd53dc2eff57df53160efb6ebcbc834` |
| HaloCE-Android-test16.apk | 25840110 | `d963bf392fea62a2e83698eeb3e2e75f8054bf6ba7c66cd778942c25ff1e6436` |

Both builds completed successfully. All ten regression suites passed (25 PASS
summaries); the added config write-failure fixture also passed. Both APKs were
compacted, aligned for 16 KB pages and signed with the established certificate;
every non-signature ZIP payload hash matched the preserved raw build. The flat
build keeps Normal geometry by default. Package identity/ABI/payload/guide checks
are enforced again by `tools/package-quest.py` before delivery.

Targeted headset/phone/co-op-observer testing remains pending. No installation,
game launch, accepted-build pointer change or GitHub release was performed.
