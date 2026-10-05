# Active work checkpoint — Quest hand rendering and arm IK follow-up

Updated 2026-10-04. This is the current handoff for Claude Code/Claude Cloud.
The canonical source is `moistman42069/HaloCE-Quest-VR`, branch `main`.

## Progress (test25, 2026-10-05)

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

## Accepted release and work boundary

- The latest public release is [`v1.0.2`](https://github.com/moistman42069/HaloCE-Quest-VR/releases/tag/v1.0.2), the exact test20e APK pair, Android version code 25. Its provenance and SHA-256 values are in [`RELEASE-PROVENANCE-1.0.2.md`](RELEASE-PROVENANCE-1.0.2.md). Preserve the release and prior releases; do not replace or withdraw them based only on this report.
- The present task is diagnosis and a private candidate for the Quest/VR rendering regression reported on 2026-10-04: the previously corrected cut-off/floating-hand appearance has returned, and arm IK does not follow correctly when the player's body turns.
- Do not assume the public v1.0.2 binary caused the symptoms. The supplied logs include both a test20d-labelled runtime and a test20e-labelled runtime. Match APK hashes/version codes and source revisions before calling this a public-release regression.
- No release or public APK upload is authorized by this checkpoint. Keep the accepted release intact and ask for device acceptance before any later publication.

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
7. Keep raw logs/video, personal paths, game assets and private data out of Git. Update this checkpoint, current-state pointer, player notes and candidate provenance as work progresses. Do not advance the accepted-release pointer or publish until the owner tests and explicitly authorizes it.

## Other open work

Preserve all unresolved items in `docs/FUTURE-RELEASE-FOLLOWUPS.md`, including the Quest 1 XISO import report and the Quest OS v78 hand/weapon orientation report. The owner has also previously authorized a broad continuation scope; consult `docs/CONTINUATION-REFINEMENT-LIST.md` if present, and check current source before assuming any item is missing or already complete. Do not expand this focused regression pass into unrelated work.
