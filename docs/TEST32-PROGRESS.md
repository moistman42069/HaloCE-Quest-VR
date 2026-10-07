# Test32: launcher guidance and VR vehicles

## Scope and preservation (2026-10-07)

The owner accepts Test31c mobile gameplay and touch controls. Preserve those
controls and their saved layout. Latest addition: Safe geometry is now the
default for BOTH APKs, superseding the prior Android Normal default. Preserve
later explicit user choices after the one-time upgrade migration. Preserve the accepted VR settings design,
body/grip/animation behavior and the Test31c occupied-vehicle glass correction.
Public v1.0.12 stays unchanged. No publication, push, installation or game launch.

Current work, before a new private test pair:

- Simplify duplicate launcher multiplayer/co-op entry points now that OpenCE
  provides the in-game browser and Server Setup. Explain the exact in-game
  routes; retain game data, updates, input setup, logs and saved user data.
- Investigate co-op passenger positional tracking; preserve 6DOF seated lean.
- Recenter on vehicle entry and exit.
- Add independent turret aim source selection, default physical right controller.
- Vehicle handle grabbing is explicitly deferred by the latest owner instruction;
  finish the other items and package without it.
- Refine deliberate HUD head gestures without changing flashlight gestures.
- Make Safe geometry the default for flat Android as well as Quest, with
  consistent launcher/native behavior and tested upgrade persistence.
- Review in-game arrow hit targets across the imported OpenCE menus, including
  Create Game's Multiplayer/Singleplayer selector. Keep the existing menu
  layout and controller/button navigation.
- Validate both editions and document host evidence separately from device tests.

The later M1–M29 / W1–W66 interaction backlog remains queued in
[VR-INTERACTION-REQUIREMENTS.md](VR-INTERACTION-REQUIREMENTS.md).

## Upstream recheck, before implementation

Live GitHub API checks of `releases/latest`, `commits/main`, and
`git/ref/tags/build-145` all resolved to
`4e8ed2f196e0edd1f2830a4de9841686aabbf466`, Build 145, on 2026-10-07.
The release was published at 11:05:07 UTC. No newer main commit or release
was available. This is the target already integrated in Test31–Test31c:
network/minimum/maximum are 22; namespaced Custom Edition maps and missing-map
preflight are present. Existing documented platform adaptations/deferrals
remain in [TEST31-UPSTREAM-DECISIONS.md](TEST31-UPSTREAM-DECISIONS.md).

Source: [OpenCE Build 145](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-145).

## Evidence received

The latest Quest 3 log identifies 1.0.13/code41 and first-person Warthog driver
seat 0 sessions. The occupied glass path executes and logs the hidden setting,
then the visible setting after the user's toggle. HUD visibility toggles occur
610 ms and 918 ms apart in one sequence. This supports reviewing rearming but
does not identify the user's intended hand motion without pose/video evidence.
No passenger seat transition was found in that log. Previously supplied clips
are being rechecked; raw logs and media remain private and outside the repo.

## Status

Implementation and paired builds are complete. The final registered regression
run completed with all 55 suites passing and no failed suites, including the
Test32 launcher, HUD gesture, vehicle, geometry migration, and all-region
menu-arrow suites. Both APK build commands reran that suite and completed
compilation, signing and alignment. No Test32 APK has yet been accepted on a
headset. The current code41 pair remains preserved as the comparison. Exact
APK hashes and candidate checks are recorded in [TEST32-DELIVERY.md](TEST32-DELIVERY.md).

## Source findings and implemented corrections

- The old guest seat cache was refreshed only from the facing-input callback.
  Seat state now refreshes before stereo rendering as well, validates salted
  unit/vehicle handles and seat bounds, and identifies driver/gunner/passenger.
- Seated lean previously inherited the walking origin even when co-op disabled
  room-scale walking. A stale offset could saturate the 35 cm lean limit.
  A fixed seat-local origin now preserves translation within that same bound;
  it is not rebased every frame. Entry, exit and seat transfer each queue one
  runtime recenter. The actual recentered frame refreshes the origin.
- Turrets previously used head aim unconditionally. `vr.turret_aim` now selects
  physical right/left controller, head or native stick, independently of driver
  steering. Lost selected-controller tracking retains native facing. Third-person
  vehicle view and right-hand driver steering defaults are unchanged.
- HUD rearming previously required only one sample outside a 5 cm margin, and
  dwell used world-space controller speed. The new helper uses head-relative
  motion, a 0.3 s stable hold, 0.25 s clear withdrawal and 0.8 s cooldown, with
  focus/menu/tracking/recenter guards. The flashlight block is byte-identical.
- Plain launcher Play retires abandoned one-shot host/join commands into local
  history before opening menus. Explicit external invites keep their existing
  path. Saved invites/preferences are retained; browse/host controls live in-game.
- Imported OpenCE value-spinner arrows were sometimes drawn outside their text
  hitbox, so pointer clicks could target the parent row and activate it instead
  of changing the value. Pointer hit bounds now include the exact rendered
  header/footer arrow rectangles for eligible imported PC-menu spinners, with no
  arbitrary padding. It respects hidden/disabled/missing art and the spinner's
  original text divider; controller/button routing and action callbacks are
  unchanged. Create Game's category selector also uses the full existing row
  as its hit target, with its text baseline preserved. Browser-list scrolling
  still uses the stick/D-pad (Android MOVE); its native scroll arrows are hidden.

Targeted production-helper tests cover these state transitions and camera/aim
math under address/undefined-behavior sanitizers. The final 55-suite run was
executed after the Safe-default and menu-arrow changes. Cache-format checks
previously reported 127 passed and four optional real-map fixtures skipped;
they could not be rerun in the current Windows/WSL Python interpreters because
neither has `pytest` installed. This does not reproduce the reported passenger
incident on a headset. Vehicle comfort and co-op passenger behavior still
require owner testing of the candidate.

Vehicle handle grabbing remains deferred by the owner's instruction. The
private candidate pair and source/build ZIPs are packaged for user testing. No
publication, push, installation or game launch is part of this delivery.
