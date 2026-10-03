# Test17 candidate delivery

VR and flat Android: `1.0-test17`, version code 18, ARM64, Android API 28 minimum.
Private candidate for owner testing; public test14 remains unchanged.

This pair fixes the running-match advertisement rejection and native unit-control
assertion identified in the six test16 logs, incorporates reviewed upstream
player departure/rejoin safeguards, and adds managed game-data sets in both
launchers. [Findings and scope audit](TEST17-PROGRESS.md).
[Import, selection and compatibility instructions](GAME-DATA-LIBRARY.md).

The owner's improved test16 animation result is preserved. Native melee online,
Safe VR geometry, flat Normal geometry, Legs + Arms, touch/gamepad, co-op and
avatar behavior remain. This is not a new action/IK experiment.

All eleven automated regression suites pass. The source archive/manifest record
the continuation commit; the final provenance section records the runtime commit
and exact APK hashes. Packaging validates signatures, package IDs/versions/ABI,
payloads, guide inclusion, ZIP checksums, and absence of game maps/signing keys.

## Owner testing

- Join a populated match already in progress, then repeat after leaving.
- Test melee, reload, interaction, deaths/respawns and a host map change while
  desktop/native peers are present. Capture the new launch log after any failure.
- Import/select two legal supported data sets in the launcher; switch back and
  confirm each set retains its own progress. Test both Android file pickers.
- Run paired Quest/flat campaign and confirm NPCs and remote body remain correct.
- Recheck existing grip/action playback and flat touch/controller behavior.

No universal compatibility, live 128-player load result, complete retail revision
matrix or new device acceptance is claimed. No APK installation, game launch or
GitHub release is performed for this delivery.


## Final build provenance

Both flavors built serially from runtime commit
`1c3af00a9c47e8110f8b453786b578d581b3ca6f`. Later documentation-only changes record
this delivery; the source archive/manifest identify that final continuation
commit. Each flavor was preserved before switching shared native staging.

| APK | Bytes | SHA-256 |
| --- | ---: | --- |
| HaloCE-Quest-test17.apk | 27879997 | `16c96c0a5a43547843fcc01d7f7669de779bac3bcfaf16b8dd3ecb6084fce290` |
| HaloCE-Android-test17.apk | 25856494 | `840561015f0d978144441950dfe1af164fb19254df9dad4c2c94f644f718f5b0` |

Both builds completed successfully. All eleven targeted regression suites passed
on the final runtime source. The additional cache-format suite passed 127 tests,
with four real-map tests skipped because their optional fixtures were unavailable.
A fresh public-directory response parsed six listings with 48 reported players;
this was discovery validation, not joining or a latency/reachability test.

Both APKs were compacted, aligned for 16 KB pages and signed with the established
certificate. Every non-signature ZIP payload matched the preserved raw build.
Package/ABI/version/guide/library/note/native-selector checks are enforced by the
packager. The manifest includes APK, guest and host hashes, certificate identity,
source commit and compatibility metadata. SHA256SUMS covers APKs and archives.
Source/privacy checks retain third-party notices and exclude game data, private
logs/invites/media, signing keys and private original history.

Source continuity is `test17-network-data-profiles`; public release/main remain
unchanged. No device install/game launch, public APK upload or new runtime
acceptance is implied by these build and deterministic-test results.
