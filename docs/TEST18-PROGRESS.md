> **Publication update:** the owner subsequently authorized these exact APKs as release 1.0. The historical candidate hold below is superseded for this pair. See [1.0 provenance](RELEASE-PROVENANCE-1.0.0.md). No new device playthrough was reported.

# Test18: campaign transition, head tutorial and vehicle controls

## Delivery/publication state

Private candidate **1.0-test18 / code 19**. The owner's newest instruction is to
receive both APKs, test, then explicitly resume the 1.0 publication plan. No new
release/tag/upload is authorized now. Public test14 remains unchanged. Draft
1.0 notes, template, credits and stable updater policy remain prepared. A final
1.0 must increment Android's version code above this candidate.

## Campaign crash evidence

The supplied campaign log identifies **test14**, Quest 3, Android 14 and Oculus
runtime 207.297.0. It starts on b30 and transitions to b40 after the Pelican
cinematic: **Silent Cartographer -> Assault on the Control Room**, rather than
an observed transition into the Library. The fatal message is an unused/changed
object handle in memory/data.c:412 (`0xe5f9038a`, index 906).

The exact public Quest test14 APK has SHA-256
`96c017a6bab47c333957e6143bf0761f329802fb3710687aec7e2b1dd3ed9a56`.
Its embedded guest ELF retains assembly-converted NOTYPE function symbols.
Symbolication and call-site disassembly identify:

- `0x882754d0`: `vr_render_windows+0x450`, calling `object_get_marker_by_name`.
- `0x8819778c`: `object_get_marker_by_name+0x3c`.
- `0x88159d90`: `datum_get+0xf0`.

The inlined `view_anchor` loads cached `vr_render.seat.unit_index`. The cache was
refreshed in player control, which skips cinematics, and survived map disposal.
The first frame in the next map could therefore use the previous map's seat.
The same path remained in test17. This is concrete evidence for the fix; the
log's earlier memory warning does not establish an out-of-memory crash.

Fix: clear seat identity on both map disposal and initialization, validate object
pool, salted unit/vehicle handles and live parent/seat relationships before the
strict head-marker lookup. Invalid state falls back to the native camera. Keep
engine assertions and native object ownership intact. Both lifecycle calls are
VR-only. No raw log, device recording or private identifying metadata is tracked.

## Opening head calibration

Source findings:

- Script `objects_can_see_flag/object` ultimately used the unit looking vector,
  which is the weapon/controller direction when hand aiming is enabled.
- The earlier VR action-test bridge measured changes in gameplay aim and could
  therefore count controller motion. Its per-tick threshold also missed slow
  deliberate head movement.
- `hs_unit_can_see_flag` treated index 0 as false and index -1 as true.

Fix: local VR script gaze uses a fresh valid focused headset frame and the same
world heading/head offset as the VR view. Flat, remote and AI visibility retain
native behavior; weapon aim is unchanged. Tutorial direction flags accumulate
head rotation independently of weapon aim, with a 0.02-radian dead band and
reset on script reset, recenter, loss of focus/tracking and map lifecycle.
Script flag bounds accept zero and reject missing/out-of-range indices.
This tracks headset direction, not eyes. Tutorial device completion is pending.

## Vehicles

First-person and chase cameras already existed. Prior defaults were first-person
and stick; prior Hand mode reused the selected weapon aim, including two-hand
and handedness state. New defaults are **Third Person + Right Hand**, as requested.

- Dedicated paginated **VR Settings > Vehicles** category.
- Third Person / First Person camera, and Right Hand / Left Hand / Head / Stick
  driver steering. Left stick remains movement/throttle; gunners retain head aim.
- Right/left are explicit physical controller directions, independent of on-foot
  aim mode, weapon hand, grip attachment and scope smoothing. Missing tracking
  holds native facing rather than unexpectedly steering with the head.
- Stick mode retains native stick facing while updating seated input state.
- First-person retains a level horizon and the vehicle/seat heading. If a custom
  rig lacks a head marker, use its unit camera position rather than chase origin.
- Global and Warthog/Ghost/Banshee/Scorpion/Pelican Up/Forward/Right adjustments,
  1 cm increments, +/-50 cm per axis. Global and matching profile values add,
  then clamp; unknown/custom vehicles and turrets use global values. Offset ray
  checks shorten movement at map structure, excluding the vehicle's own hull.
  These settings only affect First Person; zero is native positioning. The
  existing bounded physical head lean remains separate from configured offsets.
- First VR startup applies new chase/right defaults once, backs up the config
  and atomically replaces it after TOML validation. Subsequent saved camera and
  steering choices are retained. Failure preserves the prior file, applies the
  defaults in memory and logs/retries. Unusual TOML syntax is never guessed.

Flat vehicle controls and networking protocol are unchanged. No body/grip/native
reload, grenade, melee, multiplayer or co-op replication redesign is included.

## Automated evidence

- `test_vr_vehicle_lifecycle.py`: production cache helpers, ASan/UBSan, stale and
  reused handles, map-pool invalidation, seat changes, chase/cinematic behavior,
  and 10,000 repeated transition cycles.
- `test_test18_vehicle_tutorial.py`: production steering/head code, independent
  modes, lost tracking, on-foot aim retention, slow head motion, controller-only
  false positives, recenter/focus/invalid resets; actual config upgrade/persistence
  and failed write/backup; profile lookup/axes/bounds/NaN/collision; script gaze
  cone/local ownership/fallback and flag indexing.
- All eleven existing test17 suites pass alongside these two suites. They cover
  native actions, body math, render targets, campaign actors/lifecycle/capacity,
  browser/network data, input/controller and config/update/import behavior.
- Full APK build and artifact checks are recorded in TEST18-DELIVERY.md.

## Required owner device checks (not claimed as completed)

1. Replay b30 -> b40, including Pelican cinematic and first playable frame. Also
   retry the originally described pre-Library transition if it was a separate case.
2. Start a fresh normal/easy a10 look tutorial. Use head-only turns, including
   slow looks; point controllers away while keeping the head on the prompted light.
3. Warthog, Ghost, Banshee, Scorpion: entry/exit, third/first view, right/left/head/
   stick modes; reverse, tight turns and firing. Test passenger/gunner seats too.
4. First-person adjustment pages, both increase/decrease, collision near walls,
   vehicle profiles and persistence. Recenter, pause/resume and controller loss.
5. Recheck accepted two-hand reload/grenade/melee, body/legs, both flat controller
   and touch input, then paired campaign and PvP driving with matching candidates.

A build/test pass cannot establish headset comfort, every custom vehicle's seat,
or all network/campaign behavior. Keep candidate and acceptance status distinct.
