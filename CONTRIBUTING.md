# Development and continuation

Start with [CURRENT-STATE.md](docs/CURRENT-STATE.md), [release provenance](docs/RELEASE-PROVENANCE.md), [controls](docs/CONTROLS-AND-OPTIONS.md) and [architecture](docs/VR_ARCHITECTURE.md). `main` is the current canonical source. Create a focused branch/PR for changes; no private chat access is needed to resume.

## Local setup

Use Linux or WSL, Python 3.11+ (packaging uses `hashlib.file_digest`), Ninja, clang with the `arm64_32` target, JDK 17, Android SDK platform/build-tools 35 and NDK 27.2.12479018. Current shipped builds used clang 18. Set `ANDROID_HOME` and `ANDROID_NDK_HOME` as required. Build scripts keep caches/temp under the checkout. On the maintainer's Windows workstation, new work/builds belong on the D: drive; other environments use their own writable checkout.

```sh
bash tools/build-quest.sh vr
# Copy app-vr-debug.apk to an artifact directory before changing flavor.
bash tools/build-quest.sh flat
```

Both commands share `build/android` native staging, so run them serially. Gradle is explicitly invoked after Ninja so Java-only changes are included. Outputs are `port/android/app/build/outputs/apk/vr/debug/app-vr-debug.apk` and `port/android/app/build/outputs/apk/debug/app-debug.apk`.

Public source does not contain the project signing key. A locally generated debug key can install a separate clean app, but generally cannot update the published app in place. Do not commit keys, passwords, game maps, logs, invites, personal recordings, SDKs or build caches. Use GitHub's noreply identity for new commits if email privacy matters.

## Change and report discipline

- Preserve both VR and flat paths. Scope gameplay changes narrowly; keep feature failure local and retain bounds/finite-value/teardown guards.
- Inspect actual code/evidence before relying on a historical checkpoint. Date findings and distinguish source implementation, build checks and device results.
- Build the affected variant; shared native/launcher/network changes normally require both. Use focused checks appropriate to the changed behavior. Do not claim a headset result from compilation.
- Record controls/default/protocol changes in player docs and CURRENT-STATE. New protocols need explicit compatibility/ownership/bounds handling; preserve old-peer fallback.
- Do not alter game maps on disk or bundle copyrighted data. Mod installation work must preserve originals and recovery.
- Do not install to devices, launch games, publish releases or push to unrelated upstreams without the maintainer's authorization.

## Release process

1. Commit source and record exact revisions for every APK; build flavors serially and preserve outputs immediately.
2. Verify package/version/ABI/certificate, payload identity and archive integrity. Preserve hashes and existing signing identity.
3. If a release combines a VR-only update with the prior flat binary, label both versions and source revisions honestly. Do not rebuild merely to make filenames match.
4. Package individual APKs, a bundle, privacy-reviewed source snapshots, dependency notices, manifest and checksums. Keep code out of Git LFS/binary commits; attach downloads to a GitHub Release.
5. Obtain the maintainer's explicit approval after candidate testing before any public binary upload. The owner accepted test14 and explicitly authorized it as the latest release on 2026-10-03; this overrides its earlier hold. Future releases require their own authorization. Label experimental feature limits even when the accepted build is a normal GitHub release. Update the README links and CURRENT-STATE without relabeling untested features as accepted.
6. Preserve reproducible release notes and receive user logs/device results before another candidate.

Historical `tools/package-quest.py` expects a freshly built pair from one clean commit (pass the correct `--label`); publication of preserved accepted binaries is a separate operation and must not silently rebuild them. The withdrawn initial release manifest records VR test13a and flat test13 separately. Test14 again uses a matched pair from one source commit.

## Reports

Include APK/version, hardware/OS, mission/map/content, settings, exact steps, host/client and peer versions, and relevant launch logs. Remove private invitations/device details before posting. For co-op/avatars, provide both peers' logs. For body/grip/menu faults, attach video if possible. Use the issue templates; contributions should state observed behavior and remaining verification.

Test15 onward: `tools/package-quest.py` emits `compatibility.json`. Include that exact metadata with both approved stable release APKs; the in-launcher updater checks its hashes, edition/version and save/config policies. Review `docs/TEST15-UPSTREAM.md` before changing protocol acceptance or update schema. Public release publication is the approval boundary; candidates stay private until the owner accepts them.

If incremental Gradle packaging leaves obsolete ZIP space, `tools/compact-quest-apk.py` can compact a preserved APK, align for 16KB pages and re-sign with the same key. It compares every non-signature payload hash and signing certificate before/after. Its password comes from an environment variable. Never substitute a different key or alter the accepted release binary in place.

Test16 adds `python3 tools/test_test16_actions.py` for native action blending and
VR/flat config migration. Run it alongside the nine test15 regression suites.

Test17 adds `python3 tools/test_test17_network_data.py` for action flag/queue
regressions, synthetic ISO imports and matching Java/native data selection.
The browser suite now includes native in-progress flag combinations.
See `docs/TEST17-PROGRESS.md`; run all eleven suites for this candidate.

Release 1.0 publishes the exact preserved test18 pair by explicit owner instruction.
See RELEASE-PROVENANCE-1.0.0.md under docs for build identity and filename mapping.
Future APKs need code >19 and new publication approval; never rebuild an accepted
APK just to change its public label.
