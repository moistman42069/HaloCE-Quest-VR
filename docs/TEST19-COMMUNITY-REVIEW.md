# Test19 community report review

Private candidate; no new runtime acceptance or release approval. Review covered
the Halo CE Flat2VR thread from its first post through October 3, 21:52 displayed
time, and all available requested developer DMs through 21:43. Newest two complete
logs and both owner-supplied recordings were examined. Raw messages, usernames,
invites, IPs, recordings and logs remain outside public source.

## Distinct reports and disposition

| Report | Evidence / action | Still needed |
| --- | --- | --- |
| Blue screen after joining populated PvP | Test18 v11 successful 37-player join, then objects_update cluster assertion, resolved against exact shipped ELF. Add activation/PVS bounds guard and diagnostic; preserve replica ownership. | Retry populated hosts, late join, death, respawn and map rotation. Producer/object ID was absent in old log. |
| Intermittent left-eye geometry in Autumn cryo room | New 03:39 recording shows large textured triangles in left eye, right eye intact; matching test18 log uses Safe on Quest 3/Adreno 740, with no fatal error. Safe now uses ordered transient uploads; renderer restores its VAO after compositor passes. | Hardware reproduction and timing comparison. Driver-operation root cause is not established by the recording; do not call it confirmed fixed. |
| Shots above reticle with either hand | 03:27 recording visibly shows impacts above the pistol ring; follow-up says either hand. Source used separate reticle and projectile origins, particularly online. Reticle now uses engine pre-spread unit ray with guarded local hand origin, mapped back into XR LOCAL space. | Both hands, near/far targets, stationary/moving, scopes, two-hand and native reload, offline/PvP. The supplied 03:29 launch log starts after this recording, so it is not falsely treated as its exact firing log. |
| Same image imports on phone but not Quest 1 | No rejected file or matching log; transfer corruption was suspected by reporter, not established. Deep valid directory trees now traverse iteratively; precise header/extent/path/transfer errors replace ambiguous format error. | Compare source/device byte size and SHA-256; Quest 1 import/runtime remains unverified. |
| Earlier geometry follows weapon motion; save/reload helps | Historical test14 report, including two alleged disc revisions without verified hashes. Preserve Safe default; current ordered upload/VAO candidate also targets rendering robustness. | Actual revision fingerprints and reproduction with test19. No claim that disc label alone caused or fixes it. |
| Earlier upside-down weapon on old Quest firmware | Reviewed 20-second historical recording; hand-held pistol rotated while world is upright. Reported firmware v78. Existing test15+ per-hand pose/rotation calibration and Head aim fallback retained. | Current-build log, active interaction profile and calibration result. No automatic OS-version rotation heuristic from an unproven cause. |
| Co-op host/join unclear | Expanded launcher dialog and player guide into ordered host/partner steps; public listing opt-in, matching builds/data, two-player and reconnect limits explicit. | Paired Quest/flat regression and service availability. |
| Flashlight toggle / accidental hand transfer | Existing off-hand-near-head gesture and palms-together grip transfer explained in controls. Button flashlight mode and explicit handedness settings retained. | Reproduction only if documented controls do not match current build. |
| Head-light tutorial / vehicle discomfort / transition crash | Earlier reports addressed by preserved test18 gaze and vehicle-cache lifecycle changes; third-person/right-hand defaults retained. | Regression during candidate playthrough; no new unrelated camera changes. |
| Installation, seated use, logging questions | Player guide begins with install/import, explains Xbox versus PC/MCC data, normal recenter and physical crouch settings; per-launch Download/HaloCE logs retained. | Seated ergonomics across devices are not certified by recenter support. |
| Manual reload, dual wield, PCVR, SPV1 and larger campaign lobbies | Recorded feature requests, not failures reproduced in this pass. Button/native reload stays; no new dual wield or PCVR build. Custom caches remain experimental. Campaign limit remains two after the earlier lifecycle audit. | Separate implementation/testing scope; 128 PvP slots are not 128-player campaign support. |
| Good flat phone play, VR performance, first levels/co-op | Useful positive reports; preserve accepted controls/actions/IK and flat Normal default. | These reports do not certify all missions, devices, servers or this untested candidate. |

## New log correlation

Both newest complete logs identify test18, Quest 3, Android 14/API 34, Adreno 740,
OpenGL ES 3.2 and Safe geometry. Neither contains a new assertion/fatal stack.
The 03:33 session loads Autumn around 03:35 and closes normally at 03:40, matching
the 03:39 rendering recording. Focus/recenter events accompany recording overlays.
Known missing optional movie/audio-backend messages are not evidence of the
left-eye corruption. No map bytes or GPU capture were provided.

## Primary-source cross-checks

- [OpenCE build-84 browser commit](https://github.com/cybersecurity/halo-ce-universal/commit/c04765d7f49f49bda706a258826134ef41c566ca): signed broker listings, host identity, limits and native discovery. Integrated selectively through `3304965653692fc2f4cbea84f1bea2bb7d0f2bdd`; no wholesale PC menu transplant. Newest reviewed [c3adcfe](https://github.com/cybersecurity/halo-ce-universal/commit/c3adcfe5bf917922d732f2551341b1ad00977867) changes release ZIP compression only.
- [XboxDev extract-xiso source](https://github.com/XboxDev/extract-xiso/blob/master/extract-xiso.c): XDVDFS sector/header/partition layout and explicit warning about valid, deeply unbalanced directory trees. Iterative bounded traversal avoids truncating a valid import at depth 64. This supports format handling, not universal map/engine compatibility.
- [Khronos OpenGL ES 3.2 specification](https://registry.khronos.org/OpenGL/specs/es/3.2/es_spec_3.2.pdf), buffer mapping and vertex arrays; [ES map-range reference](https://registry.khronos.org/OpenGL-Refpages/es3.0/html/glMapBufferRange.xhtml): unsynchronized mapping puts overlap avoidance on the application. Ordered Safe uploads are a conservative candidate workaround; the log does not prove overlap happened.
- [OpenXR quad composition](https://registry.khronos.org/OpenXR/specs/1.1/man/html/XrCompositionLayerQuad.html): quad poses are relative to their supplied space. The engine collision point is inverse-transformed into the same XR LOCAL frame as eye submission, including room-scale/clamped head offset. 680 deterministic inverse checks cover that conversion.
- Existing [Andiweli static upload fix](https://github.com/Andiweli/HaloCE-Android-AAOS/commit/a88f25763b8a51335554ef02e613127ee92677d4) remains. Dynamic Safe uploads extend the ordered approach; this is an inference to test on hardware, not a copied claim of the same root cause.

## Continuation boundary

Preserve public test14 and 1.0 assets. Deliver the new pair privately; do not install
or publish them. Gather matching device logs before accepting render/reticle/network
behavior. Keep unresolved reports visible here instead of silently calling them done.
