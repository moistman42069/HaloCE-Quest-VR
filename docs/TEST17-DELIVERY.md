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
