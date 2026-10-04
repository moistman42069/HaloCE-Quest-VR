# Release notes and asset contract

Every public release must be self-contained, accurate for its exact binaries,
and organized in this order. Use RELEASE-1.0.0.md as the complete baseline;
update it for the new build instead of linking away the essential instructions.

1. Installation — Android APK then Quest APK links, requirements, update/import steps.
2. New Features / Major Changes — changes since prior public release.
3. Controls / Inputs — Quest, gamepad and touch; online/default distinctions.
4. VR Features and Settings — defaults, gestures, body, graphics and calibration.
5. Android / Mobile Features and Settings — touch editor, controller and recovery.
6. Multiplayer / Co-op / Server Compatibility — versions, hosting, capacity, limits.
7. Game Revision / Version Compatibility — actual detected data, switching, updater.
8. Known Issues or Important Notes — actionable limits and log/report guidance.
9. Additional Technical Details / Credits — source/version, checks, attribution.

Keep sections scannable with tables and bullets. Do not claim unverified hardware,
full-campaign or server compatibility. Preserve required third-party notices in
each APK and credit upstream work. Retain previous releases unmodified.

Use stable vMAJOR.MINOR.PATCH tags, matching app version names, monotonically
increasing Android version codes and HaloCE-Android-VERSION.apk /
HaloCE-Quest-VERSION.apk filenames. Check UpdatePolicy and compatibility.json.
The APK links lead the release page; upload Android first, Quest second. GitHub
may choose its own Assets-list sorting, so do not rely on that UI for priority.
Only compatibility.json is additionally required for the integrated updater.
Use GitHub's normal source archives; avoid duplicate bundles, logs and manifests.
Record detailed hashes/provenance in tagged source and metadata, without adding
clutter to release assets. Check the exact source tag, APK payloads/signatures,
version/ABI, links and published downloads before announcing completion.

The owner explicitly requested exact preserved test18 APKs for 1.0. That one
promotion retains internal 1.0-test18/code 19 and documents the updater/guide
labels; do not generalize it into permission to mislabel or replace future builds.
