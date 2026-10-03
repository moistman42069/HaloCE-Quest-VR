> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test13 active continuation (2026-10-03)

Repo <workspace>, private branch quest-vr-test9-wip. Preserve test12
source 4fe781ed and delivery record; stable quest-vr remains test8.

Delivery update: both APKs and matching ZIPs passed final build/artifact checks.
See TEST13-DELIVERY.md for source commit, exact hashes and preserved build logs.
Await the owner's next device results; runtime acceptance remains open.

## User scope and evidence

User reports test12 room-scale leg following is good. Remaining issues: VR
settings overlap, chest/shoulder clipping and arm/elbow snapping. Improve full
body comfort; provide optional chest-hidden legs+arms without replacing the
full-body refinement. Replicate the VR avatar to co-op peers, including flat
Android observers; extend to PvP only where compatible. Finish and deliver both
APKs, build/source ZIPs; preserve all prior features and handoff documentation.
No device install or game launch. Physical reload remains previously deferred.

New evidence:

- halo_log_2026-10-03_07-47-16-544_15433.txt: test12, Quest 3, Android 14,
  per-launch Download/HaloCE log working. User switches full body at 07:49:02.
- com.halo.decomp.vr-20261003-074755-0.mp4: 110.422 seconds, 1920x1080.
  Menu/category overlap and free-arm/body movement, contact sheet reviewed.
- com.halo.decomp.vr-20261003-075044-0.mp4: 12.697 seconds, 1920x1080.
  Shoulder/chest surfaces crowd the view during raised-arm movement.
- Scratch extraction/contact sheets in <private-work>\test13\video.

Confirmed menu cause: category six wraps at left_count=5 with column_x=0,
placing CROSSHAIR on CONTROLS. Settings storage also had a hard nine-item limit.

## Implementation plan/status

1. Menu: generated pages, four rows per column plus reserved navigation/hints
   row; capacity derived from definitions. Preserve next/previous setting
   actions; directional custom-value stepping. Implemented. Names, allocation
   tracking and navigation storage grow from definitions; generated tags grow
   beyond the old 128-slot reserve (engine tag-index bound still applies).
2. Local avatar: continuous elbow bend history, soft reach and flexion limits,
   bounded shoulders; head/chest clearance and remove duplicate local shoulder
   geometry. Existing foot placement retained. Four views implemented: full,
   arms+hands, legs+arms, hands only. Latest user override: full is now the default
   for unset/new configs; explicit saved choices remain. Hands-only keeps IK.
3. Network avatar: bounded visual-only pose snapshots, owner validation,
   interpolation, timeout fallback and explicit capability handshake; render on
   both flat/VR clients. No hitbox, input, damage, movement or stock PvP packet
   changes. Co-op and compatible PvP peers only. Implemented in both variants;
   see NETWORK-VR-AVATARS.md. No two-device result is claimed.
4. Native and Java compilation passed for both variants. Final paired APK
   assembly and signature/archive checks passed; exact artifact hashes and source
   revision are recorded in TEST13-DELIVERY.md and the delivery manifest.

Runtime success, freedom from clipping and paired networking remain unproven
until the owner's next results; do not convert source inspection into acceptance.

## Compile/source-review evidence

- `compile-vr.log` was interrupted by a user turn; its handle was gone and no
  compiler process remained. It is not a successful build record.
- `compile-vr-2.log` failed on the legacy compiler's function-scoped loop-variable
  redeclaration. Fixed; `compile-vr-3.log` and `compile-vr-4.log` passed.
- `compile-flat.log` passed a full 1493-step native build. Source review then moved
  the observer header outside HALO_VR so the flat pointer-return declaration is
  explicit. `compile-flat-final.log` passed with that and dynamic tag capacity.
- `compile-vr-final.log` passed all 1493 native steps after menu capacity/identity
  changes. `compile-java-vr.log` and `compile-java-flat.log` both report BUILD
  SUCCESSFUL. Final APK assembly/signature/archive results belong in the delivery
  record; these compilation results do not establish device acceptance.
- Reviewed the supplied log through normal exit code 0. Per-launch Downloads
  logging remains functional; no crash was shown in that log.
- Reviewed menu row coordinates, directional threshold stepping and separate
  numeric-choice handling for flashlight gesture/button mode. All settings remain
  referenced; no fixed nine-setting/category overlap is retained.
- Reviewed avatar ownership, node bounds, full-snapshot assembly, ordering,
  reset/expiry, flat header integration and render-only weapon attachments.
  Quaternion reconstruction resets scale/translation; fade now explicitly restores
  both, avoiding a latent timeout-to-origin rendering error.
- No new gameplay/unit-test suite run. No device install, game launch or PR.

## Reviewed primary references

- [FRIK release notes](https://github.com/rollingrock/Fallout-4-VR-Body/releases):
  minimum elbow bend, bounded flexion, smooth transitions, frame-rate independent
  smoothing, limited shoulder reach and distributed twist. These guide an
  original implementation for Halo's own skeleton; no foreign offsets copied.
  Also inspected its actual [Skeleton.cpp](https://github.com/rollingrock/Fallout-4-VR-Body/blob/main/src/skeleton/Skeleton.cpp)
  around reach/flexion and elbow-plane handling. Scratch copy only, not vendored.
- [HVR IK](https://github.com/hai-vr/hvr-ik/blob/main/README.md): head/hip
  constraints and first-person comfort tuning; it explicitly records unfinished
  extreme-angle behavior, so it is a reference rather than proof of correctness.
- [Unity Two Bone IK](https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.2/manual/constraints/TwoBoneIKConstraint.html):
  target and bend hint are independent controls.
