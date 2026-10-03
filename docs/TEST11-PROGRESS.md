> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Quest test11: body, grip and contact candidate

Updated 2026-10-03. Continue in `<workspace>` on
`quest-vr-test9-wip`, private remote `moistman42069/HaloCE-Quest-VR`.
This is the native Halo CE Quest project, not Halo-MCC-VR. Build output,
temporary files and Gradle caches stay on D:. No stable-branch merge.

## Read this before continuing

The user wants accurate body IK, smoother fingers, deliberate fixed two-hand
grips, hand/weapon contact, actual gesture sprint, compatible populated server
discovery, and native campaign co-op. Co-op remains **unfinished**, not cancelled.
Do not describe this candidate as delivering co-op or perfect mesh collision.
Earlier requirements are preserved in TEST10-PROGRESS.md, TEST9-PROGRESS.md and
QUEST_VR_HANDOFF.md. They are not superseded by this narrower candidate.

## Device evidence

- Prior candidate: test10, source `d8cfab730a7f2f4657cb4b357d2d28c89708b439`.
- User confirms improved play, working multiplayer and settings that now move
  both directions. Body still looks unnatural; arm running feels stock speed.
  Support hand attaches without a grip press and slides on the weapon.
- Reviewed `com.oculus.vrshell-20261002-235047-0.mp4` (171.952 seconds).
  Green stretched geometry is visible around 60, 100 and 150 seconds.
  Controller button state cannot be established from video alone.
- Reviewed `halo_log_2026-10-02_23-51-10-068_30052.txt`: Quest 3, Android 14 /
  SDK 34, Adreno 740, OpenXR 72 Hz. Full body, IK arms, physical weapons,
  impact melee, arm run and close contact enabled. Downloads logging works.
- Body hierarchy recorded by this build: pelvis 0; thighs 1/2; spine 3;
  calves 4/5; spine1 6; clavicles 7/10; feet 8/11; neck 9; head 12;
  upper arms 13/14; forearms 15/16; hands 17/18. Code discovers names and
  ancestry, not these indices. FP rifle has wrists 5/6 and gun frame 7 under
  the right wrist; fingers are complete three-joint chains.
- Originals remain in Downloads. Contact sheet and build logs are local under
  `<private-work>\test11`; private recordings/logs are not in Git.

## Candidate changes and limits

### Deliberate two-hand grip

- Root cause in source: FP rendering treated the support hand as attached
  whenever it was within 15 cm of its authored hand target, independently of
  `vr.two_handed`. Removed that proximity-only attachment.
- Settings > VR > Controls > **TWO HANDS: GRIP / AUTO / OFF** already exists.
  GRIP is the default. AUTO remains explicitly optional; OFF disables support
  locking. Existing explicit user settings are retained.
- In GRIP, press the support controller's grip near the authored support
  point (16 cm acquisition radius). Merely approaching does not attach.
- Attachment is captured in weapon-local space and retained until release;
  animation changes no longer move the held support hand along the barrel.
- Inventory changes, loss of tracking/focus, empty hands and leaving active
  aiming clear the grip. Acquisition has a short haptic pulse and log entry.
- Spawn/pickup support until the first deliberate main-hand grip, holsters,
  transfer and backward-stick priority from test10 remain.

### Body IK and stretched geometry

- Head-derived torso heading with a 25-degree neck comfort cone and time-based
  follow. Pelvis follows bounded head lean/crouch; spine supplies remaining lean.
- Both legs use analytic two-bone IK with measured current bone lengths,
  fixed hips, clamped ankle reach and forward/outward knee hints. Nearby ground
  queries support feet without pulling airborne legs to distant floors.
- FP shoulders use the actual solved avatar shoulders when full body is on.
  Both eyes use one cached body solve per predicted OpenXR frame.
- Source inspection shows zero-scale hidden head/arm bones can leave triangles
  blended with visible torso bones. A new local-avatar draw-buffer filter removes
  triangles influenced by those hidden bones. This is an evidence-backed
  candidate explanation for the video ribbons, not headset-confirmed resolution.
- Filtering reads the registered buffers that the native renderer uses, decodes
  the actual compressed node/weight format, expands strips with correct alternating
  winding, and retains visible triangles. Bounded per-map cache; teardown releases
  its buffers. Logs include kept/source counts or a specific fallback. Original
  meshes, other players and shadow geometry are unchanged.
- Node-count mismatch leaves the body pose stock and logs the mismatch. Limb
  lengths and reach have finite/bounds checks. Body affects rendering only.
- Three tracked devices infer the pelvis and legs. This is not external full-body
  tracking, and natural appearance still requires the user's headset result.

### Fingers and tactile contact

- Critically damped finger input smoothing; analog trigger works independently
  of the capacitive index-touch flag. Contact release is smoothed while collision
  constraints take priority on contact.
- World hand/finger queries now include every engine solid object type, including
  dropped weapons/equipment. Own body/attached world colliders remain excluded to
  prevent self-blocking; effects without solid collision are not made solid.
- Held first-person gun has a separate tracked capsule derived from authored
  weapon hand anchors. Palm sweep/projection permits approaching its sides instead
  of treating every head-to-hand ray through the gun as a wall. Finger segments
  also query it. Existing pressure/contact vibration is used.
- Constrained palms are cached per predicted frame so a fast sweep cannot put
  the two eyes' hands on opposite sides of the barrel. World collision takes
  priority when gun contact would otherwise push a hand through a wall.
- This is an approximate gun volume, not per-triangle weapon contact or physical
  force feedback. Individual weapon shapes, magazine motions and dense finger
  contacts still need device checks and refinement.

### Gesture sprint

- Strong arm pumping increases offline local forward movement/acceleration up
  to 1.5x stock speed. Crouch, alert movement restrictions, stun and collision stay
  in effect. Backward/lateral stick intent suppresses the boost.
- All network games keep stock movement speed; no client-only speed advantage or
  unnegotiated sprint protocol. Network arm running remains ordinary locomotion.

### Multiplayer directories

- Rechecked the Chupathingy primary repository and live feed on 2026-10-03:
  HTTP 200, eight non-comment listing lines at the time of this check.
- Current launcher consumes the whole feed, merges up to four custom compatible
  HTTPS directories, deduplicates, and orders globally by descending player count.
  Its 512-entry cap is well above the observed feed size.
- No second independently verified compatible native directory was found.
  Classic Halo PC/SAPP and browser WebRTC/streaming rooms are not compatible
  native session presets. No fabricated provider, server or population was added.

### Native campaign co-op: still open

- Further source audit confirms `network_game_create_game_objects` already takes
  network map/difficulty/seed and spawns remote player slots. This is a reusable
  loading route, not evidence of working network campaign.
- `game_update` gives AI authority to the host but still calls `hs_update` on
  clients. HS runtime threads execute without a network campaign authority gate.
  Existing messages do not synchronize campaign script side effects, checkpoints
  or BSP/next-level transitions. Simply skipping all client scripts would also
  lose local presentation/cinematics without replacement messages.
- Host/browser/join needs a negotiated campaign session type, content identity,
  mission-state replication and lifecycle handling before exposure. Keep normal
  competitive v9/v10 compatibility. See COOP-FEASIBILITY.md for implementation order.
- User is willing to try a two-client session but did not identify the pairing.
  Start with two matching Quest builds; do not assume a desktop co-op client exists.
- No co-op host/join feature is shipped or claimed playable by test11.

## Other standing requests retained

Detailed Downloads logs, menu decrement/increment, melee sweeps, closer offline
collision radius, pickup/holster/transfer, backward movement, multiplayer sorting,
immersive cutscenes, scopes/vehicles, graphics/Quest 1-2 performance, SPV1 and
physical reload remain recorded in earlier checkpoints. Reload and additional
device/platform validation remain open. Do not infer fresh acceptance for them.

## Build and handoff

Both final VR and flat Android builds succeeded (exit 0), including the stereo
contact correction. APKs were preserved separately. Existing compiler visibility /
macro and Android deprecated-API warnings remain. Earlier compile attempts exposed
C89 loop-variable redeclarations; those were corrected before the successful builds.

- Commands: `bash tools/build-quest.sh vr`, preserve VR APK, then
  `bash tools/build-quest.sh flat`, preserve flat APK. Run-log identity is test11.
- Package with `tools/package-quest.py --label test11` from clean committed
  source. Manifest ties both APKs and source ZIP to the commit and signing key.
- Delivery directory: `<artifacts>\test11-20261003`. Consult its
  `manifest.json` / `SHA256SUMS.txt` for exact commit, payload and archive hashes.
- No headset installed/launched; no new automated gameplay test suite run.
  A build is not runtime acceptance. Stable `quest-vr` remains the test8 baseline.
- Push only private WIP. Deliver APK, build ZIP and matching source ZIP, then
  wait for the user's headset result before advancing an accepted-build pointer.

## Next headset report

1. TWO HANDS = GRIP: approach barrel without grip, press grip, move both hands,
   fire/reload, release; repeat after switching weapon and transferring hands.
2. Feel held/dropped guns and world surfaces with palm and each finger; report
   weapon names and positions where contact is offset or sticky.
3. Look down, lean, crouch, turn head/body, walk stairs, jump and respawn. Include
   the latest Downloads log so mesh filtering/fallback is identifiable.
4. Compare forward stick alone with forward stick + arm pumping offline;
   confirm backward/diagonal control, and stock speed on a multiplayer server.
5. Continue regular multiplayer join/refresh and check population ordering.
   This candidate cannot yet be used to test network campaign co-op.

## Primary references

- [ChupathingyCE compatibility and directory](https://github.com/ChupathingyCE/chupathingyce)
- [Two-bone IK target/hint model](https://docs.unity.cn/Packages/com.unity.animation.rigging%401.3/manual/constraints/TwoBoneIKConstraint.html)
- Local source: `vr_render.c`, `vr_frame.c`, `models.c`, `bipeds.c`,
  `network_game_manager.c`, `game.c`, `hs_runtime.c`, `network_distributed.h`.
