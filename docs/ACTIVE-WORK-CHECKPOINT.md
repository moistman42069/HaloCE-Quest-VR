# Active work checkpoint — Test34 private candidate (2026-10-07)

Read [TEST34-PROGRESS.md](TEST34-PROGRESS.md),
[TEST34-UPSTREAM-INTEGRATION.md](TEST34-UPSTREAM-INTEGRATION.md), and
[TEST34-DELIVERY.md](TEST34-DELIVERY.md). The active private candidate targets
version 1.0.15/code44 and official OpenCE Build147/network23. Preserve the
owner-accepted Test31b VR settings and Test31c Android touch/gameplay. Build147
is Latest on its direct official release page; the general listing has shown
stale Build145 metadata. Current integration includes the tag-schema validator
for CE and retail tags, CE range adaptation, structure-BSP validation before
conversion, network-23 map identity, capacity/co-op/camera safeguards, and
server-row pointer hover. The source audit fixed the CE map file-data range to
the declared file length and added the previously missing BSP validator call.
The full regression suite passes; the CE cache-format suite has 127 passes and
4 skips because no local CE map files are installed. VR scope alignment is also
fixed across every zoom scope shape: calibrated view orientation, gun-anchored
center, shared 90 cm reach clamp, and ±30 cm pistol/sniper offsets. Build, sign,
and verify both release APKs before delivery. Then report exact hashes and ask
the owner to test Android and Quest, including scope alignment, menu pointer
selection, representative maps, and network-23 joins.
This is not device acceptance. Keep the public v1.0.12 untouched; do not push,
tag, publish, install, or launch the game.

Earlier Test31/Test32 task notes below are historical; Test32 vehicle features
are already incorporated in the candidate and documented in
[TEST32-PROGRESS.md](TEST32-PROGRESS.md). The queued later interaction backlog
is still tracked in [VR-INTERACTION-REQUIREMENTS.md](VR-INTERACTION-REQUIREMENTS.md).

## Historical Test31c task (mobile now accepted above)

Owner feedback on 2026-10-07: VR works great; its new VR settings are the
preferred design going forward. Keep the exact Test31b Quest code40 artifact
and VR/native implementation. Android's switch from circular controls to a
rectangular menu strip is rejected. Retain the familiar circular controls,
their saved placement and direct menu taps. Optional free-space look should
hide only LOOK, keeping MOVE and action buttons. Branch `test31c-flat-ui`,
**Latest addition before packaging:** fix the VR Warthog HOG GLASS toggle too,
then supply BOTH 1.0.13/code41 APKs. Preserve the code40 Quest artifact as the
comparison baseline and its new VR settings design. See `TEST31C-PROGRESS.md`.
No release/push/install.

## Active priority: repair rejected Test31

The owner rejected Test31 on 2026-10-07: Quest startup crashes and Android
loses usable touch navigation. Follow `TEST31B-PROGRESS.md` on branch
`test31b-startup-touch`, targeting 1.0.13/code40. Fix the reported paths,
add optional touch-anywhere look in the in-game touch customization, and
deliver both corrected private APKs after strengthened integration checks.
The corrected pair is built from `3399023ae8b7d0ec57e8c42c68c40ab6c33346af`; see `TEST31B-DELIVERY.md` for
checks/hashes. Await owner device results. The Test31 delivery record below
is historical evidence, not acceptance.

## Historical Test31 delivery and retained scope (superseded above)

Branch `test31-network-menus-vehicles`, based on test30 `fe725aff`. Target
1.0.13/code 39 is built and signed from runtime source `585a5643`; see
`TEST31-DELIVERY.md` for exact identities, checks and the device checklist.
All 47 host regression suites passed; the subsequent device report rejected
this pair. Those results did not cover the failing startup/input paths.
**Latest owner override:** finish the
full OpenCE in-game menus, turret/window fixes and current upstream/network
upgrade, validate them, then package BOTH APKs for testing before moving to
manual reload/hand contact and world/NPC interactions. This supersedes the
earlier all-three-prompts packaging hold. All later tasks remain on the checklist.
Do not publish, push, tag, install or launch.

Read [TEST31-PROGRESS.md](TEST31-PROGRESS.md),
[TEST31-UPSTREAM-DECISIONS.md](TEST31-UPSTREAM-DECISIONS.md),
[TEST31-MENU-PLAN.md](TEST31-MENU-PLAN.md), and the complete indexed follow-on
checklist [VR-INTERACTION-REQUIREMENTS.md](VR-INTERACTION-REQUIREMENTS.md).
The owner now requires the full OpenCE in-game menu setup, superseding the
earlier browser + Server Setup-only approval. Adapt it for all app inputs;
launcher equivalents alone do not satisfy this scope.
Work through the subsystems sequentially; acknowledgment alone is not completion.
Public/accepted build pointers below remain unchanged.

The latest public release is [v1.0.12](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.12), built from test30. Preserve v1.0.11 and all earlier releases. Provenance and APK hashes are in [RELEASE-PROVENANCE-1.0.12.md](RELEASE-PROVENANCE-1.0.12.md). The repository About description was not changed.

## Current Test31 implementation status

The initial mobile-data/menu/upstream queue has been worked through in source.
It is no longer an unstarted future list:

1. **Mobile-data / VPN joins:** bounded nearby-port authenticated probes and
   current STUN IP+port classification are implemented, with clearer failure
   guidance. The motivating phone+VPN and Quest session reached signalling
   stage 2/3 but exchanged no game packets; the same phone worked on Wi-Fi.
   These changes still need device/network retests. They cannot guarantee
   randomized destination-dependent mappings or discover unadvertised public
   IPs. OpenCE has no relay, and this candidate does not add one.
2. **OpenCE menus:** the complete pinned Build 145 menu payload is imported
   (50 XML files, plus embedded art), with campaign/profiles, Server Setup,
   public/LAN/direct-link browsing, persisted filters, password/invite entry,
   native keyboard, saved gametype options, VR Settings entry points, direct
   Android touch and mouse support. The scoreboard and real audio/graphics
   setting consumers are integrated. Desktop-only choices are filtered or
   explained for Android. See the current menu plan and settings audit.
3. **Upstream/network:** Build 145 `4e8ed2f1` / exact network 22 is integrated.
   The earlier untagged-main warning is superseded by the fetched Build 145
   tag. Version-21 peers, including v1.0.12, do not match this protocol.
   Namespaced CE maps and missing-map preflight are adapted to the existing
   Android game-set loader. The broader desktop CE loader and full schema
   validator remain explicitly deferred; see upstream decisions.
4. **VR source fixes:** seated trigger ownership, mounted native reticle,
   first-person Warthog glass setting and per-part left-hand display winding
   are implemented. Existing body, grip, hand/action animation, Safe geometry
   and gameplay control defaults are preserved.

The final combined checks passed 47 suites plus 127 cache-format tests (4 skipped).
Both APKs are built and signed; delivery/source identities are recorded in
TEST31-DELIVERY.md. Owner device testing remains required. Source and automated results do
not establish cross-play, headset comfort or performance acceptance. The
current checklist is [TEST31-PLAYER-NOTES.md](TEST31-PLAYER-NOTES.md).

## Subsequent work retained for the next phase

After the baseline pair is delivered for testing, continue the indexed manual
reload / hand-contact requirements **M1–M29**, then world/object/NPC requirements
**W1–W66**, in their documented dependency order. These are acknowledged and
queued, not implemented in Test31. Preserve their opt-in defaults, native
fallbacks, synchronization constraints, resource budgets and required device
checks in [VR-INTERACTION-REQUIREMENTS.md](VR-INTERACTION-REQUIREMENTS.md).
No publication, upload, installation or game launch follows automatically
from preparing this private pair.

## Current release: test30

Version **1.0.12 / code 38**, branch `test30-profiles-coopname`, on v1.0.11. It fixes Quest face-button actions in VR menus (A/X/Y match the displayed Xbox labels; X deletes the selected profile; B backs out once) and adds an optional remembered campaign co-op server name up to 15 printable ASCII characters. Gameplay mappings are unchanged; X still throws grenades during play. OpenCE Build 144/network 21 is unchanged, so v1.0.11 peers remain compatible.

No device session on the exact v1.0.12 APK pair was recorded before publication. The next step is owner validation using [TEST30-DELIVERY.md](TEST30-DELIVERY.md): test profile deletion/back/select, gameplay controls, named/unnamed co-op hosting and joining, then basic Android and Quest play. Keep logs for any failure. The automated test and build results in the delivery notes do not replace device acceptance.

## Previous release: test29 (v1.0.11)

Test29 added OpenCE Build 144/network 21, the held HUD tap fix, HUD and wrist-HUD settings, two-hand movement alignment, glasses FOV and higher resolution options. The exact pair had no recorded device session at publication. See [TEST29-DELIVERY.md](TEST29-DELIVERY.md) and [RELEASE-PROVENANCE-1.0.11.md](RELEASE-PROVENANCE-1.0.11.md).
## Release details

Published test28 (**1.0.10 / code 36**, branch `test27-opence-netcode`) builds on test27:
- **Owner's first cross-play session:** a Quest on 1.0.9 joined an 18-player OpenCE co-op game in progress, which proved join and load. It then halted on an upstream camera check. That check is fixed and squared, and the APKs now build in release mode as OpenCE's do.
- **Co-op hosting:** sizes now match OpenCE's, 2 to 128.
- **Gyro aim:** added to the flat Android port as an option, off by default.

Details: [TEST28-PROGRESS.md](TEST28-PROGRESS.md); delivery: [TEST28-DELIVERY.md](TEST28-DELIVERY.md).

The older checkpoint starts below; its dated priorities are historical. Use the current device-validation list above unless new evidence points to a regression.

## Earlier progress (test27, 2026-10-06)

Private candidate **test27** (1.0.9 / code 35, branch `test27-opence-netcode`, from test26 `a537c4b6`) runs OpenCE build 138's netcode (network 20) and its co-op, so Quest and Android players host and join co-op lobbies of up to 16 with OpenCE players, through the same browsers. This app's CE01/CE02 co-op and the v9-11 window are retired. Details: [TEST27-PROGRESS.md](TEST27-PROGRESS.md), [OPENCE-COOP-COMPATIBILITY.md](OPENCE-COOP-COMPATIBILITY.md). Next: real sessions (1.0.9 Quest/Android host and join; join an OpenCE build 138 co-op host; an OpenCE player joins a 1.0.9 host).

## Earlier progress (test26, 2026-10-05)

Private candidate **test26** (version 1.0.8 / code 34, branch `test26-coop`, from test25 `9bca3958`) fixes the co-op client's halt on a replayed death scream, places and animates cutscene characters on the joining device as on the host (resting teleports sent at once; every user animation and its movement flags sent), syncs broken glass, moves co-op to protocol CE02, ends the Quest 2 client's red text, makes the first Quest's memory reservation work on its older kernel, and adds the reticle toggle (left stick click; crouch on the right stick held down, or kept on the click: Controls → L Stick Click), the HUD head tap, adjustable flashlight tap, an optional wrist HUD, melee along the gun and continuous finger contact. Details: [TEST26-PROGRESS.md](TEST26-PROGRESS.md); delivery: [TEST26-DELIVERY.md](TEST26-DELIVERY.md); upstream Build 128: [UPSTREAM-REVIEW-2026-10-05.md](UPSTREAM-REVIEW-2026-10-05.md). Next: the owner's co-op test with 1.0.8 on both devices (Quest joining), then single-player checks of the new controls.

## Earlier progress (test25, 2026-10-05)

v1.0.6 (test24b) is released and the owner accepted it on device, except first-person vehicles. Private candidate **test25** (version 1.0.7 / code 33, branch `test25-vehicle-recenter`) adds one-line diagnostics for every recentre, seat change and seated view switch (a player's "sideways after recentring in a Warthog" report is not in their log), hides the seated vehicle's own glass in first person, adds a first-person driver HORIZON option (default Level = unchanged), widens and renames VR settings rows so none are clipped, adds Vehicles → RESET OFFSETS, and adopts four reviewed OpenCE fixes. Details: [TEST25-PROGRESS.md](TEST25-PROGRESS.md); delivery: [TEST25-DELIVERY.md](TEST25-DELIVERY.md); upstream: [UPSTREAM-REVIEW-2026-10-05.md](UPSTREAM-REVIEW-2026-10-05.md). Next: owner's headset test of test25; an in-world retest of the recentre report with the new log lines; then PC/Steam Frame scoping ([PC-STEAM-FRAME-FEASIBILITY.md](PC-STEAM-FRAME-FEASIBILITY.md)).

## Progress (test24b, 2026-10-05)

Private candidate **test24b** (version 1.0.6 / code 32) adds, on top of test24: a COMFORT page in VR Settings (Turning smooth/snap, Smooth Speed, Snap Angle, a comfort Vignette and when it shows; a player's request plus the owner's), Snap 22.5 and 60 on Controls → Turning, and an SPV1 notice in the launcher that SPV1 does not work yet. Details: [TEST24B-PROGRESS.md](TEST24B-PROGRESS.md); delivery: [TEST24B-DELIVERY.md](TEST24B-DELIVERY.md). Nothing is accepted until tested on devices.

## Progress (test24, 2026-10-04)

Private candidate **test24** (version 1.0.6 / code 31) after test23: the owner's 1.0.5 test still showed co-op cutscene characters T-posing and sliding on the joining Quest, with no dropped cutscene cue in its log. Cause: a machine animates only what its players see plus the place a script activates for a cutscene, and the joining device was never told of that place, so the cutscene's area stayed asleep there. The host's activation calls (and the seat posture call) are now sent to joining devices; test23's cutscene change is withdrawn. Details: [TEST24-PROGRESS.md](TEST24-PROGRESS.md); delivery: [TEST24-DELIVERY.md](TEST24-DELIVERY.md). Nothing is accepted until tested on devices.

## Progress (test23, 2026-10-04)

Private candidate **test23** (version 1.0.5 / code 30) after test22 (1.0.4): co-op cutscene characters on a joining device are placed where the host has them at each cut (they T-posed and slid on the Quest client), dropped cutscene cues are logged, and the Quest's buttons are remappable (VR Settings → BUTTONS, Reset Buttons) with the grenade on Left X in both weapon modes; the locked grip no longer throws. Details: [TEST23-PROGRESS.md](TEST23-PROGRESS.md); delivery: [TEST23-DELIVERY.md](TEST23-DELIVERY.md). Nothing is accepted until tested on devices.

## Progress (test22, 2026-10-04)

Private candidate **test22** (version 1.0.4 / code 29) after the published v1.0.3 (test21b): the Android/Quest co-op campaign host crash (upstream PR #73's unarmed-melee guard), a steadier first-person vehicle view, the left-hand ammo display, adjustable pistol/sniper scopes, shot and catch-up-tick diagnostics, and reviewed upstream fixes (no protocol change). The other player's aim report came from v1.0.2 (fixed in v1.0.3). Details: [TEST22-PROGRESS.md](TEST22-PROGRESS.md); delivery: [TEST22-DELIVERY.md](TEST22-DELIVERY.md). Nothing is accepted until tested on devices.

## Progress (test21, 2026-10-04)

Private candidate **test21b** (1.0.2 / code 27, replacing test21 code 26, branch `test21-hands-body`) addresses this report plus the owner's later additions (floating toggle kept arms, Warthog horn, easy online melee, automatic two-hand lock on by default, the Quest OS v78 two-hand gun roll, the tester's pistol reticle with per-gun aim, and the multiplayer avatar question). Causes, changes and headset checks: [TEST21-PROGRESS.md](TEST21-PROGRESS.md); delivery: [TEST21B-DELIVERY.md](TEST21B-DELIVERY.md) (test21b notes: [TEST21B-PROGRESS.md](TEST21B-PROGRESS.md)). The video/log mismatch is resolved: the overlay and the `body legs` lines are different moments of one session (video starts 12:45:58). Signing key matches v1.0.2. Nothing is accepted until the owner tests on a headset.

## Historical hand and IK report (2026-10-04)

- At the time, the latest public release was [`v1.0.2`](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.2), the exact test20e APK pair, Android version code 25. This is historical; the current release is v1.0.12 above.
- The original report concerned a Quest/VR rendering regression: cut-off/floating hands and arm IK not following body turns. Keep the evidence below for reference; reopen only if new reports point to a regression.
- Do not assume the public v1.0.2 binary caused the symptoms. The supplied logs include both a test20d-labelled runtime and a test20e-labelled runtime. Match APK hashes/version codes and source revisions before calling this a public-release regression.
- The owner later authorized test29 as v1.0.11 and test30 as v1.0.12. The exact v1.0.12 pair still needs device validation; see the current release section above and `TEST30-DELIVERY.md`.

## Evidence available in Git

The raw user files are private and were not added to Git. Their sanitized findings are recorded in [`REPORT-2026-10-04-HANDS-IK-REGRESSION.md`](REPORT-2026-10-04-HANDS-IK-REGRESSION.md). The owner supplied:

- `com.halo.decomp.vr-20261004-124558-0.mp4`
- `halo_log_2026-10-04_12-36-45-231_4154.txt`
- `halo_log_2026-10-04_12-42-01-259_6322.txt`
- `halo_log_2026-10-04_12-42-16-354_6426.txt`

The logs identify a Quest 3, Android 14 / SDK 34. The 12:36 session identifies its native runtime as test20d; the launcher log at 12:42:02 reports installed 1.0.2/code 25, and the next native log at 12:42:16 identifies test20e. Logged settings include `vr.arms=ik;vr.hand_tracking=floating`, body `legs`, fingers on, and two-hand grip. Around 8 seconds, the recording's settings overlay shows `BODY: ARMS + HANDS`, `HANDS: FLOATING`, `FINGERS: TRACKED`, and `ROOM-SCALE: ON`. The difference between the visible body-mode setting and the runtime's logged `body legs` snapshot must be reconciled against timing and config updates; do not silently treat them as one simultaneous state. These observations prove configurations shown at different points, not why they were selected or that floating mode alone explains the visible defect. The owner reports that the cut-off/floating hand defect had already been fixed and has returned, and that the arm IK fails to follow body turns.

Related community evidence is summarized in [`FUTURE-RELEASE-FOLLOWUPS.md`](FUTURE-RELEASE-FOLLOWUPS.md): Sophia SPRKLZ's separate Quest OS v78 hand-orientation report and the later Halo CE report that hands became upright while weapons remained inverted, with two-hand grip restoring the inversion. Treat this as a separate, possibly related transform issue; the newer Halo CE report did not confirm the active OS/build. Do not merge these symptoms into a single presumed cause.

## Required investigation and acceptance

1. Read `CLAUDE.md`, `CONTRIBUTING.md`, `docs/CURRENT-STATE.md`, `docs/TEST20D-PROGRESS.md`, `docs/TEST20E-PROGRESS.md`, `docs/TEST20E-DELIVERY.md`, and the report linked above. Inspect the actual current source and commit history; historical narrative is not proof of current behavior.
2. Trace the full-body yaw/body-turn transform and both first-person and avatar arm IK inputs. Verify whether the targets are transformed in world, tracking-origin, or player-local space and whether body yaw is applied once, omitted, or applied twice. Inspect stale/cached pose paths and setting migration/default selection too.
3. Trace the hand mesh, wrist/cuff/forearm visibility, arm ownership, and the transition between floating hands, Body IK, animated hands, gun-only, and hands-only modes. Find the exact code path that could reintroduce cut-off wrists or detached hand/forearm geometry.
4. Compare test20d (code 24, runtime source `346b0c074f5ed9ae2627de7bb8dfd19019eb7610`) to the accepted test20e release (code 25, runtime source `4e7e1e4a415727fdefdfe91ad3d1eb61d6968c68`). Confirm byte identity of the installed test20e APK to the public release before attributing the issue to it. Test for a saved-config/migration interaction: the log's `arms=ik` plus `hand_tracking=floating` may be a deliberate selected mode or a bad default/migration.
5. Preserve the v1.0.2 defaults and already accepted behavior unless direct evidence requires a narrow change: Legs + Arms/full-body representation, room-scale legs, fingers, hand and weapon alignment, two-hand grip locking only after grip, native reload/grenade/melee action handoff, Safe VR geometry, and multiplayer-visible body/avatar replication. Keep failures isolated and log feature-local fallback.
6. Add regression coverage for stationary and turning body yaw, both hands, yaw wraparound, recenter/tracking loss, floor/wrist bounds, all supported hand/body modes, config migration, weapons/two-hand grip, and action-animation ownership. Build affected Quest and flat variants serially when changes are shared; automated checks do not replace Quest headset verification.
7. Keep raw logs/video, personal paths, game assets and private data out of Git. Update this checkpoint, current-state pointer, player notes and release provenance as work progresses. The owner explicitly authorized v1.0.12 publication; record device acceptance separately. For future releases, preserve older releases and publish only when explicitly authorized.

## Other open work

Preserve all unresolved items in `docs/FUTURE-RELEASE-FOLLOWUPS.md`, including the Quest 1 XISO import report and the Quest OS v78 hand/weapon orientation report. The owner has also previously authorized a broad continuation scope; consult `docs/CONTINUATION-REFINEMENT-LIST.md` if present, and check current source before assuming any item is missing or already complete. Do not expand this focused regression pass into unrelated work.
