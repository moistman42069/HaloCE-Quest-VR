# Test31 — private candidate in progress

Target: 1.0.13 / Android code 39. Branch `test31-network-menus-vehicles`.
Based on test30 `fe725aff`. No publication, upload, tag, installation or game
launch is authorized for this candidate. Device results remain the acceptance test.

## Current packaging gate (latest owner override, 2026-10-07)

The owner now requests the two APKs after the full OpenCE menu integration,
turret fixes, Warthog window setting and current upstream/network upgrade are
finished and validated, BEFORE manual reload/hand contact and world/NPC work.
Deliver that complete baseline for testing. Later tasks remain queued and
unimplemented; no publication or installation is authorized.

### Earlier gate (superseded for baseline delivery)

**No packaging until every item across all three task prompts has been worked
through.** Finish test31, manual reload/finger/palm interaction, then world
interaction/NPC handling in order, validating available source/build behavior
between subsystems. A test31-only APK pair is no longer the delivery plan.
The indexed follow-on requirements and dependencies are in
[VR-INTERACTION-REQUIREMENTS.md](VR-INTERACTION-REQUIREMENTS.md). A queued or
acknowledged item is not complete. Eventual device results are still required
for acceptance, but are not a reason to skip the remaining pre-package work.

## Current evidence and outstanding work

| Work | Current status | Remaining proof / action |
|---|---|---|
| Build 145 / exact network 22 | Integrated; three-way delta audit; 28 files identical and 8 preserve app-only deltas | Real mixed OpenCE/Quest/Android sessions; no cross-play claim yet |
| CE namespace / missing-map preflight | Implemented, compiled and regression checked | Device missing-map dialog and CE/PAL/.yelo regression checks |
| Portable script/tag/resource bounds | Integrated selected upstream fixes; range helper tested with sanitizers | Broad tag validator and desktop CE loader explicitly deferred in upstream decisions |
| LTE / VPN traversal | Bounded standard pings, current IP+port STUN classification and failure guidance implemented | Real LTE/VPN tests; random/unadvertised endpoints remain unsupported without relay design |
| OpenCE menus | Full screen set imported; browser filters, native keyboard, VR routes, Android direct touch, settings consumers and scoreboard integrated | Final combined regression/build checks and device navigation/host/join acceptance |
| First-person Warthog glass | Persisted setting; prior hidden default; relevant view only | Headset visibility checks for Warthog variants and other views |
| Left-hand AR display | Per-part winding uses actual vertex influences; bounded CPU work | Headset visibility/orientation/counter updates, right-hand and other-weapon checks |
| Seated VR trigger | Physical empty-hand suppression no longer blocks seated fire | Actual mounted/stationary turrets and primary/secondary input checks |
| Turret reticle | Native muzzle/aim preview without writing aim-assist targeting state | Both VR and Xbox layouts; shot alignment and frame-time checks |
| Manual reload / hand contact | All M1–M29 recorded; not implemented | Investigation/plan after baseline and approved menus, then sequential work |
| World interaction / NPCs | All W1–W66 recorded; not implemented | Prior interaction dependencies, investigation/plan, sequential viability/implementation work |
| Version / guides / packaging identity | 1.0.13/code39; candidate guide, credits and package gates updated | Complete final validation, then signed private pair/source packaging |

Before menu integration, all 32 suites in `tools/run-quest-checks.py` passed;
cache-format pytest: **127 passed, 4 skipped**. VR and flat guest release
compile/link checks and the Android VR host library compiled successfully.
Build configuration reports no PGO because installed clang 18 does not match
the clang 22 profiles. No performance acceptance is inferred from compilation.
The subsequent STUN refresh review added an actual packet-parser test covering
same-response classification, XOR/legacy replies, wrong source/transaction,
truncation, multiple egress IPs and repeated route changes; focused test31 passes.
Final combined source checks now pass: **46 suites** in
`tools/run-quest-checks.py`, plus **127 passed / 4 skipped** in cache-format
pytest. The final settings and lifecycle suites were rerun after the config
failure fix. Signed pair/artifact validation is the remaining delivery step.

No test31 APKs have been packaged, signed, installed or published.

## Network target and integration

On 2026-10-07 the fetched OpenCE **build-145** tag and main both resolve to
`4e8ed2f196e0edd1f2830a4de9841686aabbf466`, network **22**. The earlier
handoff's untagged-main warning is superseded by that tag. The actual browser
parser accepted 3 co-op and 5 multiplayer listings from the saved directory
snapshot at version 22 (29 total listings). These counts are transient and
are not connection/session evidence.

Three-way staging compares build 144 `76b1898e` to build 145 and the test30
tree. Network 22's changed client manager is merged, including missing-map
preflight. CE map selection advertises `custom_maps\name`; a missing map in
that namespace cannot fall through to an Xbox map with the same basename.
Missing-map text uses upstream's deferred in-game error dialog and wrapping,
adapted to the launcher's active game-set folder. The app's existing CE/.yelo
loader, PAL conversion and co-op pause handling remain in place.

Initial evidence: the VR release guest compiles and links. The new test31
suite pins 28 unchanged networking files to upstream build 145 SHA-256 values.
The browser suite passes against the downloaded feed. Earlier test29 protocol
checks now allow the exact current version while preserving their file hashes
and local rest-state/camera checks. The later validation results are above;
the latest owner override permits baseline APK packaging after the final checks.

## Test31 completion order

- Complete independent source review of current fixes and resolve its findings.
- Implement the approved full OpenCE in-game menu scope; see TEST31-MENU-PLAN.md.
- Finish approved menu scope, focused regressions, full checks and guides.
- Per latest owner override, finalize version identity, signing/hash verification
  and the baseline device checklist, then package both APKs for testing. The
  two added interaction prompts remain queued for the next phase.

## Subsequent interaction work — queued after stable test31

The owner added a separate manual-reload and hand-contact workstream. Complete
test31 source work, available validation and the requested baseline APK delivery
first. Then investigate and report a concrete plan and engine limits
before committing to architecture changes. Manual reload must default OFF and
retain classic reload fallback. Start with authentic AR magazine geometry;
expand to pistol only after the first weapon is sound. Cover grip-only left
shoulder AND hip retrieval, both weapon hands, spatial/oriented insertion,
magazine removal, charging components, bounded object lifetime, distinct
haptics, and real engine ammo with cancellation/death/switch/vehicle/pause/
checkpoint/network/level reset safety. No visual-only ammo or duplication.

The related hand work requires continuous independent finger contact, joint
and palm probes, bounded visual hand compliance, contact/release hysteresis,
held-object filtering and poses, stable support-hand interaction priorities,
subtle contact haptics, opt-in diagnostics, and a measured Quest CPU budget.
Investigate current reload/ammo/model-node/animation, hand/grab, collision,
haptic, two-hand and replication paths before selecting the architecture.
Automated logic coverage and the owner's detailed physical checklist are
required; neither substitutes for device testing. The complete request is
preserved privately with the test31 work records.


## Full menu implementation and integration checks

- OpenCE XML menu screens and assets are embedded; Expat is built for the
  ILP32 Android guest. Native widget events, profile names, gametype options,
  campaign/map selection and menu textures are connected to their consumers.
- Main, profile Settings and pause paths expose generated VR screens without
  assuming a fixed stock pause layout. Network pages do not pause the game.
- Browser filters save six choices and preserve selected/pending host identity
  through population sorting and refresh. No packet format or version gate
  was weakened. Public directory ping remains explicitly unavailable.
- Android taps/mouse and Quest laser use the same widget/keyboard pointer path.
  Native keyboards support full invite strings and masked passwords. Cancel,
  focus loss and map teardown release input state. Touch gameplay overlay and
  gyro suspend in menus and resume with gesture release isolation.
- Menu settings have backend consumers: audio gains, optional I3DL2 reverb,
  scoreboard layout/background and paging, live high-res text/HUD, shadows,
  optional model lighting and AA. Defaults preserve the preceding behavior.
- Integration tests caught and corrected repeated TOML sections in fresh
  defaults, menu dependencies missing from the Android guest, and host SDL
  string pointers that cannot cross the guest's 32-bit ABI. Scancode names now
  use SDL's licensed local guest table. Added tag count/OOM/reload and typed
  config round-trip sanitizer tests.
- The first combined run found stale test doubles for the expanded render
  target and atomic touch structs plus the menu gyro guard; these were
  updated while retaining their existing runtime assertions. Final results
  belong in TEST31-DELIVERY.md, not inferred from interim builds.

All M1-M29 and W1-W66 later interaction tasks remain queued for after this
baseline APK delivery. No manual-reload/world/NPC implementation is claimed.


## Graphics integration evidence (2026-10-07)

The shadow-resolution (`1dc533fe`), per-pixel model-lighting (`3dba558e`)
and anti-aliasing (`94882796`) integrations now have runtime consumers.
Defaults remain shadow size **128**, model lighting **OFF**, and AA **OFF**.
The app keeps its accepted geometry path, eye/scope target recycling and
separate reticle capture. Three bounded postprocess scratch sizes avoid
reallocating texture storage every time eye and scope dimensions alternate.

`tools/test_test31_graphics.py` runs production C on software Mesa GLES 3.2,
with both GLSL ES 300 and 310 shader headers. It verifies:

- OFF shader text is byte-identical to the pre-integration `d6100629` output
  for all **67** embedded vertex programs and **144** pixel-state keys.
- Model programs **9, 10, 17 and 27** are recognized; their lit vertex/pixel
  pairs compile and link. Altered diffuse writes reject optional lighting.
- Real FXAA rendering smooths a diagonal while preserving destination alpha
  and every pixel outside the selected split-screen viewport. Three scratch
  dimensions are reused across **100** cycles without allocation churn.
- Actual MSAA **2x and 4x** color/depth resolves, destination alpha, same-size
  reuse, resized renderbuffer storage and transitions to OFF work.
- Injected texture/FBO and MSAA storage/attachment-pair failures leave the
  source intact or use complete single-sample targets. A failed optional AA
  mode logs once and stops retrying for that session; it does not terminate
  the game or OpenXR. Failed FBOs never enter the cache, and renderbuffer
  storage changes invalidate affected framebuffer attachments.
- Shadow selection accepts power-of-two sizes **128/256/512/1024**, clamps
  invalid/extreme inputs and changes only between frames (ASan/UBSan).
  The extra blur passes preserve the normalized tent kernel at every size.

The accepted `test_quest_render_targets.py` assertions remain intact. Its
mock now includes the added shadow/MSAA fields and checks MSAA invalidation
when storage is recycled. **100** resolution changes still use **6** texture
names, with no per-frame storage churn for active eye/scope sizes.

A pinned Build 145 Git delta audit found no later changes to the imported
vertex/pixel translators, shadow code or shader initializer. The one later
postprocess dependency is `76addf66`'s desktop SMAA `zlib_prefixed.h` include;
that include was carried forward. Later sampler caches, desktop VAO/
multibind, water-mip dirty tracking and CPU visibility changes are separate
renderer optimizations, not missing AA/shadow/model-lighting fixes.

These results are **software GL and host logic evidence**, not Quest GPU
performance, visual acceptance, physical device compatibility, or 8x MSAA
validation. Device checks still include both eyes, scopes, reticle capture,
HUD/text sharpness, alpha effects, settings transitions and frame timing.
The graphics test needs clang, Mesa EGL/GL and existing Khronos headers (the
installed Android NDK is supported); it never installs packages or launches
the game. Its OFF comparison uses the named Git baseline.
