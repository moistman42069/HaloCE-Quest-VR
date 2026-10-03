# Test16: VR geometry and native action handoff

2026-10-03. Branch `test16-native-actions`, based on final test15 source `cf4763b`.
Private testing candidate; test14 remains the accepted public release. Do not publish
new APKs or advance the accepted pointer without the owner's candidate result.

## Evidence and requested behavior

The owner supplied two test15 Quest 3 logs, a bridge screenshot and a roughly
19.8-second recording. The first run logged normal geometry at 18:13:54; the next
logged Safe streaming / CPU index rebasing at 18:15:15. The owner reports Safe
fixed the Halo bridge and flat Android appears unaffected. This supports a VR
default change, not a claim that all GPUs/maps or performance settings passed.
Video frames around 7-8 seconds show a stretched arm during the rifle action.
Private originals and extracted frames remain outside Git and source archives.

Source inspection found the support-hand subtree overwritten from a cached grip
every frame, including native actions. The arm solver then preserved that hand
anchor while attempting to join it to the body shoulder. The free-hand path also
overrode native grenade/reload trajectories with controller and finger poses.

## Implemented

- Safe geometry defaults on in VR; flat Android's default remains off. Native
  configuration initialization also handles direct game starts without the launcher.
- Existing VR configs migrate once to Safe, recording `renderer.vr_geometry_revision=1`.
  Migration backs up the original as `config.toml.pre-safe-geometry`, validates the
  replacement and renames a temporary file in the same directory. Write failures
  retain the old file, use Safe in memory and retry later. Unusual inline/dotted
  TOML that cannot be safely rewritten is retained; Safe is selected in memory
  until an explicit choice is saved. Malformed configs retain the original file.
- Launcher Geometry compatibility shows the effective VR default even before
  the first native launch. An explicit Safe/Normal choice writes both fields;
  later launches honor it. No config deletion, save migration or game-data edit.
- The actual first-person state animation supplies an arm ownership mask.
  Normal grenade throw owns the support arm. Reload (including all shotgun
  stages), melee, draw/put-away, light switching and heat/vent animations own
  both arms; overheated grenade throw retains both-arm native presentation.
  Idle, ordinary firing, posing and charging retain existing tracked behavior.
  CE has no separate equipment-use animation state to map; no fictitious state
  or fixed-duration button timer was added.
- Capture the authored palette after left-hand mirroring, before grip/IK/finger
  overrides. Blend affected arm/finger subtrees to this native palette over
  80 ms and back over 160 ms, using normalized quaternion rotation blending.
  At full native ownership, contact/IK work for that arm is skipped. Gun and
  attachment descendants remain unchanged. Leg/torso solving is unchanged.
- Preserve an existing support grip through the action; never capture a new grip
  from an animated action pose. Returning to tracking respects the current grip
  state, including release during the action. Weapon/unit/graph/hand/settings
  changes and stale/non-monotonic frame times reset cached ownership and anchors.
  Both eyes use the same predicted frame time. Fully animated arm mode now avoids
  the support lock entirely. Hidden/hands-only visibility still applies.
- Observer avatar solving can consume fresh displayed action hand/elbow targets
  instead of pulling them back to the physical controller. Same unit, 50 ms age
  and bounded-distance checks apply. Existing avatar protocol and flat receiver
  remain unchanged; world skeletons still do not carry separate finger bones.
- Sanitized config tests exposed a bundled tomlc17 allocation-size expression
  that formed a member pointer through NULL. Replaced that expression with
  `offsetof(page_t, data) + size`, preserving layout/allocation size and license.

## Preserved current pass

All test15 networking v9-v11 adapters, population-sorted PvP browser/hosting,
reviewed project updater, per-hand alignment, flat controller/touch work, logging,
co-op actor/lifecycle fixes and body modes remain. Legs + Arms is still default.
CE01 remains two-player for the documented lifecycle/snapshot/recovery blockers
in [COOP-PLAYER-LIMITS.md](COOP-PLAYER-LIMITS.md); 128-player PvP is not evidence of
128-player campaign safety. Physical reload remains deferred: this pass handles
native button/engine actions. No upstream binary substitution or new release.

## Automated verification

`tools/test_test16_actions.py` executes production config code in VR and flat
build modes against clean, legacy, explicit opt-out, missing-key, old-revision,
CRLF, malformed and inline fixtures, loading each twice. It checks preservation
and migration backup. Production state/matrix helpers cover all 24 native states,
30-144 Hz transitions, interrupts, both-eye timing, identity/time resets, 5,050
rotation blends including reflection, finite-value fallback, native descendants
and unchanged gun/attachment descendants. Address/undefined sanitizers fail fast.
The nine test15 regression suites must also pass for delivery; see delivery record.
Builds and integrity checks are recorded separately from device acceptance.

## Required owner checks (not yet observed in test16)

1. Upgrade existing VR config; revisit the Halo bridge before changing settings.
   Check FPS and other BSPs; choose Normal then restart to verify opt-out persists.
2. Rifle full/partial reload, repeated/interrupted shotgun reload, both grenade
   types, melee, weapon swaps, plasma overheating/venting. Try right/left weapon
   hands, one/two hands, grip held/released during each action, firing immediately
   after reload and all body/arm modes.
3. Watch shoulder continuity during native takeover, magazine/weapon alignment,
   elbow shape and return to support grip. Authored animations are weapon-space
   poses; extreme controller positions/custom rigs still need headset assessment.
4. Co-op Quest-to-flat/Quest observer: action hand/elbow movement, held weapon,
   normal tracked body/room-scale legs, death/respawn, checkpoints and transitions.
5. Flat phone/controller/touch regression. Normal geometry remains the default;
   this pass supplies a matching flat build for shared config/launcher/parser code.

If a candidate fails, preserve its logs, settings and exact binary identity.
Do not infer a headset success from these mathematical tests or a clean build.
