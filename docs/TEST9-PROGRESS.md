> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test9 candidate and continuation checkpoint

**Superseded by TEST10-PROGRESS.md.** User subsequently confirmed test9
multiplayer and fingers and reported remaining input/log/body/contact issues.
The text below records the historical test9 candidate, not the latest status.

Updated 2026-10-02. **Accepted runtime baseline: test8 (`be7ec964`). Test9 is
a candidate awaiting headset results.** Read this before the original design
in `QUEST_VR_HANDOFF.md`. Its old remaining-work list describes the starting
WIP state; this file records the current implementation.

## Location, scope and identity

- Active checkout: `<workspace>`, branch `quest-vr-test9-wip`.
- Historical remote `origin`: `https://github.com/moistman42069/HaloCE-Quest-VR`.
- Public remote `upstream`: `bnunu/halo-ce-universal` (read only for this work).
- Candidate artifacts: `<artifacts>`; build caches/temp stay in the
  D: checkout. Scratch/reference/build logs: `<private-work>`.
- C: and `<home>/halo-ce-universal` copies are historical. Do not resume
  in those copies. The Halo-MCC-VR checkout is a separate project; no MCC
  package, installation or PR is part of this Quest task.
- The candidate manifest identifies the exact source commit, APK/source ZIP
  hashes, package names and signing certificate. Source ZIP is `git archive`
  of that commit, excluding ignored build folders and maps.
- New startup identity: `vr: HaloCE Quest test9 candidate (hands, immersive
  cinema, multiplayer browser)`.

User reference: https://www.youtube.com/watch?v=6At5X656E-U (161 seconds).
Reviewed frames showed stretched body geometry, menu overlap and rectangular
screen flash. Prior requirements came from repository handoff files and this
chat. Other workspace chat history is not automatically accessible.

## Every requested item

"Implemented" means present in the candidate source and compiled, not proven
in a headset. All affected visual/input behavior needs the user's device test.

| Item | Candidate work and remaining evidence |
| --- | --- |
| Fire without holding grip | Existing WIP fires a gun in the hand; game inventory now calls `vr_note_weapon` every tick. Empty hands block gun firing. |
| Physical drops, holsters, transfer | Connected inventory state; retains loose/held/empty states, 1.2s warning and 2.5s loose-gun drop, four shoulder/hip zones, grip draw and hand transfer. Empty inventory cannot invent a held gun. Verify transitions and two-weapon inventory in play. |
| Hidden gun with empty hands | Only the first-person gun draw is skipped; arm models remain. |
| Accidental pickups | Pickup origin is controller grip, radius 25cm, empty hand required; no shot-origin grab. |
| First-person arms with full body | Arm IK remains active in full-body mode. Explicit HIDDEN collapses arm descendants to one root point, excluding the gun subtree. |
| Wrist orientation | Derived from wrist/knuckle positions and controller forward/up; mirrored frame math checked. |
| World contact and pressure | Wrist target is 7.5cm behind grip; wall collision returns normal/depth; palm flattens toward the surface with bounded blend; pressure haptics retained. Device tuning pending. |
| Fingers and gestures | Absolute segment posing replaces additive animation curl; thumb direction, ancestry-sorted joints, segment lengths, contact curl retries and contact haptics implemented. Existing gesture inputs retained. This is an approximation, not a claim of Half-Life: Alyx-equivalent physics. |
| Two-handed weapons | Existing grip/auto behavior retained; offhand within 15cm of animated foregrip remains attached. |
| Full-body slivers | Biped head and arm subtrees each collapse to one root point; torso moved 8cm back. First-person arms provide tracked hands. Normal character remains in immersive cutscenes. Body node names logged once per graph. |
| Immersive cinematics | Stereo at camera position with headset rotation; yaw reference reset at start or cuts over 1.5 world units/30 degrees, 0.85 blink; sample current XR frame. Camera pitch/roll ignored per design. Screen/flat modes retained. |
| Cinema letterbox/titles | Letterbox suppressed only in immersive mode; title drawing retained. |
| Floating flash rectangle | Screen flash moved from HUD to eye/scope passes after lens flares; flat path preserved. |
| Menu overlap | All five pages at most 5 left/4 right settings; requested layout applied. |
| Menu options | Immersive/3D screen/flat modes; holster radius 10/15/20/25/30/40cm; finer turn/crouch/run/melee/haptic steps and numeric `< value >` labels. Numeric endpoints clamp. |
| Resolution target retention | Recycles inactive storage across size changes, preserving concurrently used eye/HUD/scope sizes. Counted GL harness: 100 resolution changes used 6 textures; steady passes made no new storage allocations. Real GPU memory/FPS not measured. |
| Green mission-script text | Exact map string not found in source. `hs_print` is the green script terminal path; active VR logs that text and hides its overlay by default. `vr.script_messages = true` restores it. Confirm the reported string uses this path on device. |
| Graphics presets / Quest 1–2 | Existing presets change multiple effects beyond resolution. No Quest 1/2 measurements available; no unmeasured performance gain or device compatibility claimed. Profiling remains open. |
| SPV1 | Installer retained; SPV1 has never been played on the device in available evidence. Needs runtime test. |
| Physical reload | Explicitly deferred in prior scope; not implemented. |
| Existing features | Roomscale, arm-run, crouch, impact melee including vehicles, flashlight, both-stick recenter, scope, audio, smooth turn, laser menu and MP physical toggle retained. Regression checklist below. |
| Multiplayer browser | Added launcher browser with real ChupathingyCE directory, population sorting, map/mode/count/version, saved invites and custom HTTPS catalogs. Reviewed host versions 9–10 accepted; other versions and retail/MCC/Xbox protocols excluded. See `MULTIPLAYER-BROWSER.md`. |
| Repo/Cloud handoff | Checklist, evidence, build/check tools and resume prompt tracked. WIP stays separate from accepted test8. No headset install or game launch performed. |

`vr.diag_finger_sign` remains accepted for old configs but is inert under the
absolute-pose solver; setting help now says so.

## Build and checks

Use Ubuntu-24.04 WSL, clang 18 (arm64_32 capable), JDK 17, SDK 35/build-tools
35.0.0 and NDK 27.2.12479018. Existing installed tools are reused; build output,
Gradle cache and temp files are under D:. clang 18 cannot consume the clang-22
PGO profile, so configure disables that profile.

```sh
cd <workspace>
bash tools/build-quest.sh vr
# Preserve the VR APK before switching the shared native graph to flat.
bash tools/build-quest.sh flat
python3 tools/test_quest_vr_math.py
python3 tools/test_quest_browser.py
python3 tools/test_quest_render_targets.py
```

The wrapper always invokes Gradle after Ninja, because upstream's Ninja APK
edge does not itself track launcher Java/resource edits. Outputs:

- VR: `port/android/app/build/outputs/apk/vr/debug/app-vr-debug.apk`.
- Flat: `port/android/app/build/outputs/apk/debug/app-debug.apk`.

Current verification:

- VR and flat APK builds passed (exit 0); both signatures verify and their
  certificates equal test8. VR package is `com.halo.decomp.vr`, flat package
  is `com.halo.decomp`; both are arm64-v8a.
- ASan/UBSan production VR helper harness passed: 36 rotations (including
  antiparallel handedness), mirrored wrist frames, 30 finger poses, bounded
  malformed ancestry and weapon lifecycle cases.
- Production Java parser passed invalid/old/overlong invites, malformed and
  duplicate listings, full/closed states, input caps and a real downloaded
  directory (6 servers, 27 reported players at the time of that query).
- ASan/UBSan native compatibility gate passed 30 version/flag combinations
  plus missing client and out-of-range slot cases.
- ASan/UBSan target-cache harness passed stable storage and bounded
  allocations across 100 unique resolution settings.
- No emulator/headset render, controller or live game-session test performed.
  No build/test result advances runtime acceptance.

Expected test8/9 signing certificate SHA-256:
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.
Keep the original `~/.android/debug.keystore` private; it is not in Git or the
source archive. A new Cloud-generated key cannot upgrade this app in place.

Preserved build APK SHA-256 values:

- VR: `076ec3f128054cd484a9873b6b62ef47e4d7f8c14931b62898a01e66e4a39902`
- Flat: `8f366c65c51437cdf99f1bb57048c131f3a750f398cefb51f8169b2bcf4c9c58`

Package command, after committing the exact built source:

```sh
python3 tools/package-quest.py \
  --vr <private-work>/package/HaloCE-Quest-test9.apk \
  --flat <private-work>/package/HaloCE-Android-flat-test9.apk \
  --build-tools <home>/Android/Sdk/build-tools/35.0.0 \
  --out <artifacts>/test9-20261002
```

The packager requires a clean committed tree, checks APK signatures, native
ABI/package identity, browser classes/default endpoint, VR identity and
OpenXR/flat separation, then creates the two APKs, build ZIP, matching source
ZIP, manifest and SHA256SUMS. It refuses to overwrite an existing output
folder and never installs anything. Build logs remain in
`<private-work>\logs\test9-vr-final.log` and `test9-flat-build.log`.

## User device checklist / next action

Deliver the candidate, then obtain the user's log/video; do not silently
install it or call it accepted. Prioritize:

1. Install VR APK over test8. Confirm startup identity in the newest
   `Download/HaloCE/halo_log_<date>_<time>.txt`; preserve it with the APK hash.
   Keep test8 available for rollback.
2. Opening cinematic: immersive motion/cuts/fades, no letterbox, titles still
   present, complete character; then try 3D screen and flat modes.
3. Body and hands: look down, rotate wrists, point/thumb/fist/middle gesture,
   press palms/fingers against world/vehicles; inspect bone logs if wrong.
4. Weapons: fire loose without grip; grip/hold, release/drop, each holster,
   draw, transfer, two-hand aim, pickup with empty hand, both handedness modes.
   CONTROLS > WEAPONS > LOCKED disables physical drops. Holsters are at each
   shoulder and hip; adjust VR > HOLSTER SIZE to fit.
5. Menus: inspect each page and numeric directions/endpoints. Cycle resolution
   repeatedly, then scope/cutscene; record memory/FPS if problems remain.
6. Regressions: roomscale, arm-run/crouch, both-stick recenter, melee vehicle
   damage, flashlight, audio, smooth turn, recoil, laser pointer and scope.
7. Multiplayer: directory/pointer use; join v10 desktop/Mac and v9 native
   hosts; LAN; offline/stale/full/version states; MP physical default OFF;
   inspect gameplay/host-rule logs.
8. Separate SPV1 run and Quest 1/2 performance traces if devices are available.
   Preserve device/runtime/refresh/preset and candidate hash.

Fix failures from logs and bounded reproductions. Do not merge this broad
test9 completion candidate into `quest-vr` before explicit device acceptance.
