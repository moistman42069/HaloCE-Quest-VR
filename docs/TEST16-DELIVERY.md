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
