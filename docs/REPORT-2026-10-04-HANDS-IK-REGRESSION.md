# Report: cut-off hands and arm IK during body turns

Updated 2026-10-04 from the owner's three private launch logs and one private
Quest recording. The files themselves remain outside Git; use the sanitized
observations here for cloud continuation.

## User-observed symptoms

- The previously fixed cut-off/floating-hand issue appears to have returned.
- Arm IK does not follow correctly when the player turns their body.
- The owner considers the latest public release to have regressed prior behavior
  and requests diagnosis without losing the already working features.

## What the provided evidence establishes

| Evidence | Directly recorded | Limits |
| --- | --- | --- |
| `halo_log_2026-10-04_12-36-45-231_4154.txt` | Quest 3, Android 14 / SDK 34. Native runtime banner says “test20d candidate”. Settings report `arms ik`, `hand tracking floating`, body legs, fingers on, two-hand grip; hand orientation pitch is −70°. Controller interaction and arm/body nodes are logged. | APK version string is 1.0.2 but this log does not establish Android version code or APK hash. It must not be presumed byte-identical to public v1.0.2. |
| `halo_log_2026-10-04_12-42-01-259_6322.txt` | Launcher reports installed 1.0.2/code 25 and public v1.0.2/code 25. It records the game data as Xbox cache v5, NTSC, build `01.10.12.2276`. | This launcher log identifies the build metadata but does not establish the hash of the installed Quest APK. |
| `halo_log_2026-10-04_12-42-16-354_6426.txt` | Quest 3, Android 14 / SDK 34. Native runtime banner says test20e candidate. It logs Body `legs`, Arms `ik`, fingers on, two-hand grip, and later `vr.arms=ik;vr.hand_tracking=floating`. It cleanly exits with status 0. | The native build banner is not a substitute for checking installed APK identity. Clean exit means no crash was captured, not that IK/rendering was correct. |
| `com.halo.decomp.vr-20261004-124558-0.mp4` | Roughly 107 seconds. Around 8 seconds, the overlay reads `BODY: ARMS + HANDS`, `HANDS: FLOATING`, `FINGERS: TRACKED`, `ROOM-SCALE: ON`; visible hands/forearms are shown close-up. The owner specifically identifies cut-off hands and arm IK lagging body turns. | The video setting differs from the `body legs` runtime snapshot in the logs; their exact temporal/config relationship is unknown and must be checked. Video is 30 fps, so it cannot fully characterize 72 Hz tracking. Do not infer the source transform or device OS beyond what the logs report. |

The two VR logs list the runtime setting `vr.arms=ik;vr.hand_tracking=floating`.
This is an observed combination, not yet a diagnosis: it may reflect a user
selection, preserved config, migration/default behavior, or interaction between
the IK and floating-hand paths. The video shows `BODY: ARMS + HANDS` with
`HANDS: FLOATING`, while a runtime snapshot says `body legs`. Determine when
each was selected and whether the display/config/log update is stale or reflects
separate session states. Inspect implementation and config history before
changing defaults or assuming floating mode is the sole cause.

The test20d lineage changed first-person gun anchoring and simplified the hands
settings; see [`TEST20D-PROGRESS.md`](TEST20D-PROGRESS.md). Test20e is the public
v1.0.2 baseline and includes later network/crosshair changes. Because the
12:36 log is test20d-labelled and the 12:42 run is test20e-labelled, compare the
actual package identity, code, hash, source, and config before deciding what
regressed. Do not alter release artifacts.

## Nearby reported orientation issue (keep distinct)

The same tester previously said Quest OS v78 caused hands to rotate 180 degrees
in another VR project. In the Halo CE Discord report near the 1.0.2 release,
they said the orientation option corrected the hands but not the weapons, and a
two-hand grip made the weapon upside down again. See source links and required
separation of confirmed versus inferred details in
[`FUTURE-RELEASE-FOLLOWUPS.md`](FUTURE-RELEASE-FOLLOWUPS.md). The current owner
video/logs identify Quest 3 / Android 14 and do not confirm OS v78; do not assume
the two reports share a root cause.

## Next diagnostic steps

1. Reproduce with the exact public v1.0.2 APK after verifying its SHA-256 against
   [`RELEASE-PROVENANCE-1.0.2.md`](RELEASE-PROVENANCE-1.0.2.md), then compare with
   test20d only if its exact APK can be identified.
2. Record selected body/arms/hands mode before and after restart, the resolved
   config keys and one-time migration markers, orientation and calibration rows,
   weapon/grip state, tracking origin and player yaw.
3. In source, trace controller/head pose from OpenXR acquisition through
   `vr_hand_pose`, arm IK target/pole construction, player/body yaw, skeleton
   application, first-person mesh visibility and avatar replication. Check
   coordinate-space conversion and whether body rotation is applied once.
4. Reproduce standing still while yawing the body, then yaw while moving each
   hand independently. Check both hands, wrist/cuff seams, shoulder reach,
   mirror/left-handed mode, recentering and tracking loss.
5. Compare floating, Body IK, animated, gun-only, hands-only and arms/hands
   modes. Separate visual wrist clipping from controller pose tracking and from
   the rendered/replicated avatar skeleton.
6. Add focused automated coverage before changing source. Keep the fix narrow,
   fail open per feature, preserve action-animation handoff and two-hand
   behavior, build both variants where shared code changes, and require headset
   testing before accepting the candidate.
