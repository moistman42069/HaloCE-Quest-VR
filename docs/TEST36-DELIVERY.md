# Test36 private candidate delivery record

**Status:** pending final package generation.  
**Candidate:** 1.0.17-test36 / Android code46 / OpenCE Build157 / network24.  
**Public release:** v1.0.16 remains Latest; no publication is authorized.

## Package artifacts

APK filenames, SHA-256 hashes, source commit, package output directory and
source/build archive hashes will be recorded here after the final committed
source is built and packaged. The VR and flat APKs must come from the same
runtime source commit and use the established signing key.

## Checks

Before building: the full serial `tools/run-quest-checks.py` completed with
no failed suites. Cache-format pytest completed with 127 passed and four
skipped. The live signed-discovery/native admission check accepted an actual
current listing under network24 and rejected it under network23; see
TEST36-PROGRESS.md. `git diff --check` and Python syntax compilation passed.

The first Quest compilation caught an unavailable `PIN` macro in the new
diagnostic-only angle calculation. It was replaced with explicit bounds
checks; the finite-value guard and aim behavior are unchanged. The affected
Test21/Test36 checks and the real Quest-target `vr_frame.c` compilation then
passed. Both APKs are rebuilt from the corrected source before delivery.

Record the results of the complete serial `tools/run-quest-checks.py` suite,
Android/VR builds, APK signature/package/version/network-parity checks, package
archive checks and SHA-256 verification here. No APK is installed or launched
by this workflow. Successful host tests are not device acceptance; the owner
must report Quest and Android results separately.
