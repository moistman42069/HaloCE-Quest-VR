> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test12 candidate packaged: device acceptance remains open

Updated 2026-10-03. Checkout `<workspace>`, branch
`quest-vr-test9-wip`. Test12 APKs and matching build/source ZIPs were packaged
from `4fe781ed1571fc098d65b53976bede23be2e1902`; see TEST12-DELIVERY.md for
hashes and build evidence. Await owner-device results. The historical development
checkpoints below retain their original state; the delivery record supersedes
their pending-build/packaging notes. Runtime acceptance is still open.

## User packaging hold (2026-10-03)

The user explicitly instructed: do not package until EVERYTHING is done, then
provide both APKs. No intermediate feature-only release or APK delivery. Complete
the entire standing scope below, including real co-op and body refinement, before
assembling the final Quest VR and flat Android APKs together. Use compilation
checks during development without assembling further APKs or release ZIPs.
Preserve existing internal compile artifacts as historical WIP only.

Before final packaging, audit every requirement against implementation and
available verification evidence. Unfinished items remain open; do not describe
stubs, launcher buttons or successful compilation as working co-op or runtime
acceptance. Record any checks that require the owner's devices explicitly.
Keep documentation/source handoff current while the packaging hold is in force.

## Required outcomes and current evidence

| Requirement | Current status / proof still needed |
| --- | --- |
| Arms/hands only by default | Changed `vr.body` default to `arms`; existing explicit settings preserved. Both Android builds pass; device verification pending. |
| Physical run off by default | Changed `vr.arm_run` default to false. Existing explicit settings preserved. |
| Physical crouch threshold 0.35 | Changed `vr.crouch_height` default from 0.15 to 0.35 metres. |
| Crosshair hidden/native selection, native animations and enemy red state, size/opacity menu controls | Implemented native crosshair draw capture and a separate XR layer, retaining native sprites, animation and targeting colors. Added independent hide/native, size and opacity controls. Menu pointer remains independent. VR and flat native compilation pass; headset appearance/state verification pending. |
| Fully rendered, better positioned body and natural arms, without clipping | Added authored-frame wrist-twist distribution, bounded free-hand shoulder reach, degenerate elbow-pole recovery, and idle foot planting with alternating turn steps. Locked weapon/support poses remain anchored. Native compilation passes. Video deformation causes and full-body appearance are not yet confirmed fixed; geometry review and headset verification remain. |
| SPV1 easy uninstall with originals restored | Added one action that restores before deleting downloaded maps. Added atomic replacement, checked deletion, preflight missing-backup refusal and interrupted-change marker/recovery. Host filesystem fixtures and both Android builds pass; Android UI/device verification pending. |
| Proper launcher co-op host/join, Quest and flat interoperability | Implemented native host/join, campaign negotiation, host AI/scripts, presentation/actor/device/object replication, map/resource hashes, BSP/checkpoint/next-level barriers and opt-in live-host publication. Final VR/flat native and both launcher Java compiles pass. Two-client runtime and directory acceptance remain unverified. See CAMPAIGN-PROTOCOL-WIP.md. |
| All discoverable compatible PvP servers, descending population | Full bounded feeds now merge without the silent 512 cap; all rows remain accessible in pages of 50, sorted first. Latest recheck: five v10 listings; no additional compatible provider verified. LAN and private invites retained. |
| Separate working Quest and flat phone APKs | Separate build flavors/package IDs already exist. Both must be rebuilt from the final source. Quest is tested by user; no phone runtime result yet. |
| Flat phone touch controls, no VR options | Implemented a flat-only multi-touch overlay, four analog axes, full combat/menu buttons, fire-and-drag aim, saved visibility toggle and lifecycle release. Merges into player one without adding/reordering physical controllers. Both Android builds and APK checks pass. Phone/device acceptance remains pending. See ANDROID-TOUCH-CONTROLS.md. |
| Thorough handoff and matching source ZIP | Maintain this checkpoint, build logs, source commit and manifest. No final delivery yet. Preserve all earlier standing requests in test9-11 docs. |

## New supplied evidence

- Log: `<private-evidence>\halo_log_2026-10-03_00-51-53-079_4547.txt`.
  Runtime identifies test11; Quest 3 / Adreno 740 / OpenXR 72 Hz.
- Recording: `com.halo.decomp.vr-20261003-005505-0.mp4`, 184.792 seconds.
  Contact sheet extracted/viewed at `<private-work>\test12\video\contact.jpg`.
  Exact extracted frames at 4, 44 and 116 seconds show the close wrist/arm
  surfaces under review. The contact-sheet labels were about four seconds early;
  exact 40 seconds shows an Elite, not the stretched green arm. Later menu changes switch
  arms/body modes and turn off arm run. Need detailed frame comparisons when
  making the body fix; the contact sheet does not prove controller button state.
- Body filter log: kept 26/86, 2/2, 917/3651 and 0/120 triangles. These include
  strip degenerates; do not interpret ratios as an exact visible surface loss.
  No filter-fallback message in the reviewed matches.
- Support-grip engage/release messages recur, including 00:56:02/00:56:13 and
  00:57:29/00:57:32. This proves state transitions, not flawless visual attachment.
- User ends at body=arms, arm_run=off, crouch=0.35, matching requested defaults.
  Performance samples after loading are generally around 72 fps; one early
  sample is 63.5 fps with a 264.80 ms maximum game-frame interval.

## SPV1 changes this pass

`ModInstaller.delete(mod, progress)` restores an active mod before deleting only
its named map/audio/partial files. Shared CE resources and unrelated files remain.
Failures propagate to launcher status. `Files.move(ATOMIC_MOVE, REPLACE_EXISTING)`
avoids the old destination-delete-before-rename window.

Restoration preflights every map before moving anything. A missing backup is
accepted only when the active file already has the Xbox cache header/version,
allowing an interrupted restore to resume. Otherwise mod data and markers remain
and the error explains that the original is missing. Installation now checks
originals before swapping. A `.changing` marker brackets map swaps/restoration;
the launcher blocks playing mixed maps and opens the recovery actions after an
interruption. Originals are restored through existing same-filesystem moves.

Host fixture command (temporary directories must be new per run):

```sh
javac -d <private-work>/test12/java-classes \
  port/android/app/src/main/java/com/halo/decomp/ModInstaller.java \
  tools/tests/ModInstallerRestoreTest.java
java -cp <private-work>/test12/java-classes \
  com.halo.decomp.ModInstallerRestoreTest \
  <private-work>/test12/mod-fixtures-2
```

Result: PASS for active uninstall, restored resource maps/audio, preservation of
unowned files, repeated deletion, refusal before mutation when a backup is missing,
resuming partial restoration, and recovering an interrupted install. These are
small synthetic files, not the user's maps. Android filesystem/UI behavior is
not proven by the host fixtures.

## Flat touch controls / build checkpoint

The user explicitly requested preservation of existing work while adding touch
controls. The overlay is created only by the flat package. Native touch writers
and player-one merging are excluded from the Quest build. No physical controller
is added or reordered. Existing VR tracking/IK/grip/collision and networking code
were not changed for this feature. Runtime regression freedom remains unproven.

Source for defaults/SPV1 recovery is committed as `864c2172`; touch source and
handoff documentation follow it on the same WIP branch. Full controls, integration
boundaries and the pending device checklist are in ANDROID-TOUCH-CONTROLS.md.

Builds completed on 2026-10-03, serially, exit 0:

- `bash tools/build-quest.sh flat`: log `<private-work>\test12\build-flat-touch.log`.
- `bash tools/build-quest.sh vr`: log `<private-work>\test12\build-vr-touch.log`.
- Both passed APK ZIP integrity, expected package/ARM64 ABI, original signing
  certificate, and native feature separation: touch JNI only in flat, OpenXR
  loader only in VR. Inspection output: `touch-artifact-checks.json` in that folder.
- Preserved internal WIP APKs:
  `flat-touch-wip.apk`, SHA-256
  `cdc009e0b4dc021d8b6ffa2577c36f366905984cab79916603d56c23a212a701`;
  `vr-touch-wip.apk`, SHA-256
  `4b8b94cbe3f41c4662b5a5f8e45cbc5344ed256ddbd46a0d30de78d5ff90f5bd`.
- These still carry the existing test11 runtime identity. They are compile
  checkpoints, not a delivered test12 package or an advancement of acceptance.
  Assign the final identity before the next user-facing package.
- The preliminary interrupted flat build (`build-flat-current.log`) failed with
  an unresolved new host import while edits were in progress. The subsequent
  serialized builds reconfigured import generation and both passed. Do not treat
  the preliminary staging output as a candidate or build modes concurrently.
- No phone/headset installed or launched. No touch runtime result is claimed.

## Next actions

1. Commit the audited implementation, assemble both APKs from that source, and
   inspect signing, payload separation and package integrity. Deliver both APKs
   and matching build/source ZIPs together. Do not install or launch a game.
2. Obtain owner-device results using TEST12-README.md: paired campaign lifecycle,
   flat touch, native crosshair appearance and body/grip/PvP regression checks.
3. Record those results before declaring runtime acceptance or changing the
   stable branch. Preserve the exact package source commit when diagnosing.

No goal completion is claimed. No APK installed, game launched, or PR opened.
The historical steps above are supplemented by the latest continuation below;
do not reimplement already completed launcher/protocol work from stale wording.

## Native crosshair and arm/body source checkpoint

Native-only builds completed with exit 0, without APK/ZIP assembly:

- VR: `<private-work>\test12\native-body-stance.log`.
- Flat: `<private-work>\test12\native-flat-refinements.log`.
- Command: `bash <private-work>/test12/compile-native.sh vr` (or `flat`);
  it runs `configure.py` and `ninja -j 6 android` only.

Crosshairs are captured around the actual `crosshairs_draw` calls, with a
transparent per-frame target and authored color/animation, then cropped into the
256-pixel XR reticle image. A failed capture/compositor falls back to the native
HUD draw with a diagnostic. The alpha reconstruction shares the existing HUD
limitation: pure black details cannot be recovered from RGB on a black target.
The old white dot is retained only as the independent menu pointer.

Arm twist uses the authored forearm/hand relationship and controller target; it
distributes axial rotation without moving hand, gun or support anchors. Free-hand
shoulder extension is limited to 8 cm; locked hands retain their anchor behavior.
Idle feet hold world positions until an 18 cm displacement or 35-degree turn,
then alternate eased steps. Walking/jumping restores the authored gait. These
are render-pose changes, not player physics or network movement changes.

No runtime acceptance or completed co-op is claimed by these compile results.

## Campaign implementation checkpoint (not playable yet)

- Native protocol identity: 0xCE01 + campaign flag; settings require the campaign
  map marker, zero competitive engine, exactly two slots and a known campaign
  path. The fixed join token receives a campaign-specific capability echo on
  both ends; hardware identity and PvP packet layouts stay intact. This is a
  compatibility check, not authentication.
- Campaign presentation uses message 32; IDs 19-31 remain reserved, including
  upstream v10 ping. The decoder rejects campaign traffic in PvP. Ordered
  records have round/seed, allowlisted opcodes, exact argument counts and type/
  index/finite-value checks. No pointers, console text or script source is sent.
- Host mission scripts run; campaign client scenario script threads stay idle.
  Supported HUD, camera, fade, title and control effects are queued after object
  creation. Audio, custom animation, globals and lifecycle coverage remain open.
  These incomplete paths must not be exposed as working co-op.
- Campaign object mask adds scenery, devices and sound scenery; PvP retains its
  original four object kinds. Device state is a separate reliable record, using
  object identity and local group mapping, with changed-state sends at 10 Hz and
  full refresh every three seconds. Flat native compilation passed.
- `native-campaign-protocol.log`: flat native compile exit 0 for initial protocol
  and presentation. Device compile encountered a missing diagnostic header and
  a nonexistent game_time header; both corrected before the next compile.
- Launcher review also fixed false-success join callbacks, blocked writing
  invites during mod recovery, made partial-download cleanup accessible, and
  removed the VR-settings instruction from the flat launcher. Both Java variants
  compiled (`java-flat-launcher.log`, `java-vr-launcher.log`), without APK assembly.
- Remote campaign players now use independent saved-unit slots during BSP
  teleports; client respawns, all-dead decisions and BSP triggers remain host
  owned. Online sessions cannot overwrite the owner's persistent solo save or
  last-solo resume path. `native-campaign-player-authority-2.log` passed (flat).
- Device follow-up `native-campaign-devices-3.log` passed after correcting the
  two header errors. No device runtime, BSP barrier or checkpoint result is
  implied by these compile checks.

Crosshair/body source and documentation are pushed in `e59a3b48`. Campaign source
foundation is pushed in `5a0652fe`. Later campaign work is tracked in
CAMPAIGN-PROTOCOL-WIP.md. The native host route now consumes a validated one-shot
launcher request, but no launcher host control or public listing is exposed yet.
Packaging hold remains.

### Campaign continuation, same day

Flat native compile-only checkpoints passed:

- `native-campaign-presentation-audio.log`: bounded string arguments, scripted
  sounds/music, camera/custom animations, list animation expansion and actual
  AI speech playback capture. No pointer or object-list datum travels remotely.
- `native-campaign-barriers.log`: content hashes, initial/BSP barriers, tick
  generations and snapshot-before-resume.
- `native-campaign-checkpoints.log`: paired local checkpoints and clock resets.
- `native-campaign-session.log`: host bootstrap, restart/next-level route and
  explicit end on partner disconnect. Local saves remain protected.
- `native-vr-campaign-lifecycle.log`: VR native compile exit 0 for the same
  lifecycle/host source, including rejection of legacy campaign input packets.

These are source/compilation findings, not two-client runtime results. Outstanding:
review object visibility/attachments/animation and mission side effects, launcher
host/join, public announce/withdraw, final native compilation of both flavors and
the final scope audit. Then package both APKs together, with source. No APK or
release ZIP has been assembled during this continuation.

### Latest implementation audit (2026-10-03)

Object presentation, actor controls, damage and launcher work described in
CAMPAIGN-PROTOCOL-WIP.md are now implemented. Both final native and Java variants
have compiled; final APK assembly and artifact checks are next. Final identity is test12,
version `1.0-test12` / code 12 in both Android packages. The stable/accepted pointer
has not advanced. TEST12-README.md contains the user workflow and candid limits.

Compile-only results, exit 0 unless noted:

- `native-campaign-launcher.log` (VR): native host status and object metadata.
- `native-campaign-actors-2.log` (VR): actor controls, navpoints/effects and
  cross-map packet generations. The first actor compile failed on an incorrect
  unit-field name; corrected to the source-defined `player_index` before this run.
- `native-campaign-damage.log` (VR): AI hit effects, scenery/device hit reports,
  non-player health and damaged-region state, collision/suspension presentation.
- `native-campaign-complete-flat.log`: full 1492-step flat native compile passed.
- `native-campaign-exit-flat.log`: bounded native-exit publisher cleanup passed.
- `java-campaign-launcher-flat.log`, `java-campaign-launcher-vr.log`: both launcher
  variants compiled.
- `native-test12-final-vr.log`: final-identity VR native compile passed (1492 steps).
- `java-test12-final-flat.log`, `java-test12-final-vr.log`: both final Java variants,
  including the native-exit publication cleanup and candidate identity, passed.

The object metadata's initial link failure was a call to a private transform
validator; it now shares the existing validator through its declared interface.
Device full snapshots bypass the ordinary 10 Hz send gate. Online saved-unit
restoration, teleport assertions and second-player loadout slots were audited and
corrected. New network paths are campaign-gated; PvP retains its layouts/rules.

Standing-scope audit: crosshairs, body/arms/feet, deliberate grip, fingers/contact,
melee, offline sprint/contact, menu decrement, launch logs, PvP full-feed coverage,
SPV1 restoration, flat touch and campaign implementation are represented in source.
Physical reload stays explicitly deferred by the earlier scope. Quest 1/2
performance, full-body visual quality and all new paired campaign behavior need
owner-device evidence; no unsupported equivalence to Alyx/Titanfall is claimed.
No new gameplay/unit-test suite was run during this continuation. No APK was
installed, no game launched, and no PR opened. Final package checks remain.
