# Test31 menu settings: runtime audit

Source review on 2026-10-07 against pinned OpenCE Build 145,
`4e8ed2f196e0edd1f2830a4de9841686aabbf466`. This records the integrated
source and focused host checks, not device acceptance. Use the pinned Git
object; the reference checkout working tree is older than Build 145.

The complete screen inventory is in `TEST31-OPENCE-MENU-INVENTORY.md`.
Imported XML and configuration keys alone do not establish working settings.

## Audio

| Setting | Runtime status / required treatment |
| --- | --- |
| Master volume | `dsound_sdl.c::audio_update_volume` now reads changes on the game thread and updates the existing mixer under its mutex. No configuration reads were added to the audio callback. Existing positive custom gains above 1 remain supported. |
| Music/effects volume | `sound_manager.c::sound_manager_port_volume` now follows Build 145's class-gain multiplier. Music affects the music class; effects affects all other classes, including speech. Script class fades and scripted-dialog exemptions from nondialog attenuation remain intact. Defaults are **1.0**, not 100. |
| Audio enabled | Existing device-start gate; explicitly labeled **SOUND (RESTART)** with restart help. |
| Reverb | Implemented from OpenCE `8a8e7059` (MrBruh, based on Tyberious #44/#46), default **OFF**. ON enables room reflection/decay and high-frequency obstruction/occlusion filters. OFF preserves the accepted dry decoder, Catmull-Rom resampler, soft limiter, spatial gain and diagnostics. Unlike upstream, filtering also follows the toggle. DSP storage is static and bounded; quiet/OFF tails stop processing and clear history. Listener/source inputs are finite-clamped, environment changes fade for 85 ms, and master mute also silences stored tails. |

`tools/test_test31_audio.py` compiles the production gain helpers with
ASan/UBSan. It verifies defaults, separate controls, all sound-class baseline
gains, script/dialog attenuation, cached live changes, finite bounds, mute,
mutex discipline, legacy master boost and game-thread wiring. Passing it does
not validate actual speaker output, latency, crackling or room acoustics.
`tools/test_test31_reverb.py` additionally compiles the production mixer and
checks byte-identical OFF output against the prior commit, impulse decay,
2D bypass, environment transitions, finite/range bounds, master mute, and
OFF state cleanup under ASan/UBSan. Its optimized host CPU measurement was
0.043 ms per 1,024-frame room block (21.33 ms of audio); this is **not** a
Quest timing result.

## Video and presentation

| Setting / group | Current consumer and safe treatment |
| --- | --- |
| Mode, resolution, window size, resolution scaling, FPS cap, direct camera | Upstream XML marks these desktop-only. Keep them out of Quest/Android menus unless backed by a real platform implementation. The current Android display adapter returns the actual drawable size and must not recreate the headset context. |
| V-sync | Flat `platform_display_apply` updates SDL swap interval. Its VR branch deliberately leaves OpenXR scheduling intact; hide or explain runtime-managed VR synchronization instead of implying this changes headset frame pacing. |
| Interpolation | Current `halo_interpolation_enabled` rereads configuration generation. Preserve accepted VR interpolation defaults. |
| High-resolution HUD | `hud_hires_override_find` rereads configuration generation, including title-art high-resolution text selection. |
| High-resolution text | Font enablement and the rasterizer font lookup now invalidate on configuration generation changes. This also clears cached disabled-font misses, so OFF and ON both apply live. Title art retains its existing live path. |
| Anti-aliasing | Integrated target allocation/resolve and postprocess consumers in `d3d8_gl.c`, `xgpu_post.c` and `render.c`. Android exposes OFF, FXAA and MSAA 2x/4x; desktop retains SMAA/SSAA/8x. VR draws/resolve use private per-eye targets; the runtime swapchain stays single-sample. GPU limits and allocation failures fall back without ending VR. Default remains **OFF**. |
| Shadow resolution | Integrated 128/256/512/1024 target sizes and normalized blur scaling in `d3d8_gl.c` / `rasterizer_xbox_shadows.c`. Size changes are applied at the frame boundary, with target-cache invalidation. The existing shadow enable/preset gate remains independent. Default remains **128**. |
| Per-pixel lighting | Integrated actual model-program recognition, world position/normal capture, light uniforms and shader-key variants. Unrecognized or failed shaders retain the existing vertex-lighting path. Existing specular/dynamic-light settings keep their meanings. Default remains **OFF**. |
| Player names and name scale | Actual generation-aware consumers in `source/interface/hud.c`; preserve all/allies/enemies/none and existing scale bounds. |
| Scoreboard layout/background | Pinned full-screen scoreboard consumer integrated, including network ping rows, 128-player scrolling, team columns or score ordering, background color/enablement, quit-player filtering and co-op names/pings. Existing local split-screen keeps its compact rows. Hold score plus D-pad or right-stick vertical to page; keyboard Page Up/Down and mouse wheel also work. Input ownership expires on closure/map exit/focus loss; ordinary gameplay input remains unchanged outside the hold. |

Quest already has real `vr.resolution_scale`, `vr.refresh_rate` and per-headset
`graphics.preset`/effect switches. Keep these accessible through VR Settings,
with their existing safe defaults and script-aware effect gating. They are
platform controls alongside the separate AA, shadow-resolution and per-pixel
lighting features.

## Input, network and lifecycle

- Profile fields use the imported profile read/write adapter; keyboard/mouse
  bindings, Android controller/touch policy and tracked VR actions have
  different owners. Preserve separate adjustment paths and accurate labels.
- Mouse sensitivity, vertical sensitivity, inversion and aim-assist have real
  `xinput_sdl.c` consumers. Their newly generation-aware behavior and external
  mouse scope should remain explicit.
- Online/UPnP/clipboard invitation settings have existing P2P/SDL consumers.
  Co-op extra-enemy mode/percent/multiplier have real `coop_enemies.c`
  consumers. Friendly-fire/collision options flow through host game variants;
  their mere absence as literal strings in collision code is not a missing
  consumer (bipeds call `network_coop_player_collisions`).
- Android's update row now says **USE LAUNCHER**, with the exact Versions &
  compatible updates path. Its desktop `update.auto` spinner is excluded on
  Android, so there is no inert switch or unsafe upstream binary replacement.
- Defaults stages spinner values without writing configuration/profile data.
  Cancel posts the ordinary Back action and does not save staged subpage values.
  OK saves only changed selections. A failed write leaves the page open, names
  the failed setting in the log and shows a storage/retry explanation. Successful
  rows are not rewritten on retry; absent/unselected and spinner-item behavior
  is preserved. This is not an all-or-nothing configuration transaction: rows
  successfully saved before another row fails remain saved.
- Saved gametype PC options keep their original extension/header/checksum
  format. Compatible legacy normalization is followed by the existing engine
  bounds validator. Invalid timer/vehicle fields cannot bypass that validator
  with a correct checksum; missing/corrupt/invalid extensions use variant defaults.
  The previous async writer finishes before new option storage is overwritten.

## Remaining device checks

Both editions: save/cancel/defaults, persistence across restart, profile changes,
live music/effects/master changes, mute/unmute and background/resume. Quest:
headset audio and frame timing, settings pointer/input navigation, HUD/text
switching, refresh/resolution changes, geometry-safe default and lack of
OpenXR context resets. Flat: controller and touch navigation, V-sync behavior,
and external keyboard/mouse where available. No APK has been packaged for
this audit.

## Integrated renderer provenance and validation

The previously identified dependency patches are now integrated. Accepted
defaults remain shadow size 128, per-pixel lighting OFF and AA OFF. The following
source boundaries explain their scope; appearance/performance remain device checks.

- **Shadow resolution `1dc533fe`**: scales actual Xbox shadow targets, adjusts
  blur half-texel constants and adds normalized passes for the larger targets.
- **Per-pixel lighting `3dba558e`**: recognizes model lighting programs
  9/10/17/27 and adds lit shader variants, preserving the existing constant
  serial, mirrored culling, fog, transparency and fallback paths.
- **Anti-aliasing `94882796`**: adds postprocessing/SMAA resources, multisample
  target/resolve ownership and the scene-finish hook before HUD rendering.
  App target recycling, crosshair capture, eye/scope targets and state
  invalidation are retained. The Android menu follows upstream mobile choices.

`tools/test_test31_graphics.py` passed against actual software Mesa GLES with
GLSL 300 ES and 310 ES. It compares 67 OFF vertex-program outputs and 144 OFF
pixel-key outputs byte-for-byte with pre-integration `d6100629`, compiles/links
all four recognized lit programs, rejects mutated diffuse instructions, draws
FXAA while preserving alpha/outside-viewport pixels, recycles three eye/scope
scratch sizes through 100 cycles, and resolves actual 2x/4x MSAA color/depth.
Injected texture/FBO/MSAA failures preserve the source and keep VR ownership.
Production shadow configuration/blur helpers pass ASan/UBSan with frame-boundary
updates and normalized tent weights. This proves software-GL behavior only;
it establishes neither Quest frame rate nor headset visual acceptance, and
Mesa's four-sample limit means no 8x device result is claimed.

Reverb deliberately does not import unrelated upstream ADPCM 65-to-64 sample
changes, windowed-sinc resampling, distance-law changes or replacement limiter.
Those would alter the accepted audio baseline independently of this menu task.

`tools/test_test31_menu_presentation.py` compiles the production scoreboard,
settings, scaled-text and controller paging helpers with ASan/UBSan. It covers
128-player teams/score/co-op, opening on the viewer's page, empty lists, scroll
bounds, panel bounds, default text-geometry identity, live controls, color
parser saturation, paging debounce and release/expiry. The actual XDK header
supplies pad constants. Reverb tests also derive E_INVALIDARG from the real
project HRESULT header, preventing a mock-only declaration from hiding an
unknown SDK constant. Audio enabled now explicitly says SOUND (RESTART).

## Final handler and settings-save audit

`tools/test_test31_menu_settings.py` compiles production settings/profile
helpers and playlist extension/get/save helpers with ASan/UBSan. It exercises
failed Save and retry, nested rows, unchanged/unselected rows, Defaults staging,
profile inverse flags, serialized writer handoff, option roundtrips, legacy
fallback, checksum/header corruption and valid-checksum invalid fields. The
checksum primitive is mocked deterministically: these are framing/validation
tests, not new cryptographic algorithm claims. Guest disk-header integer width
and the real 28-byte option layout are asserted.

All imported XML event/data names are checked against actual dispatch tables.
At audit time there are **126 event names and 31 data names**, plus **49
setting keys in 50 widgets**. Every setting has a config/profile table entry
and matching display-label/value counts. Special handling:

- Gametype init/set names use the shared prefix dispatch and option-table code.
- Six inherited list/color disposal events are no-ops because the port owns
  static list state and the widget engine frees per-widget memory.
- The inherited spinner click event is served by the shared widget pointer and
  controller navigation paths; it needs no duplicate per-screen handler.
- Browser column headers are disabled and their sorting arrows hidden. The
  working browser remains ordered by population, with functional filter controls.
- The old Direct IP XML is unreachable from menu navigation. Direct Link opens
  the real browser and uses its paste/edit-invite path instead.
- Shared button-bar update is intentionally empty; native widget focus/input
  and explicit button events own the behavior. Cancel emits controller Back.

The separate pointer, lifecycle, presentation and input suites cover their
owners. Passing host tests does not replace testing flat touch/controller input
and Quest ray/controller navigation across every screen in the candidate.
The old `test_test15_io.py` touch harness now includes `<stdatomic.h>` needed by
its extracted production host code; its full suite passes without changing
production touch behavior.

## Configuration write failure boundary

`config_write_typed` now publishes a changed cached value and its generation
only after the file writer returns success. Previously a failed write changed
the cached value without advancing the generation, leaving cached and direct
consumers inconsistent. The settings suite compiles the complete production
configuration implementation for both flat Android and VR; injected ENOSPC
before writing verifies real/integer/boolean/string values and generation stay
unchanged, then verifies a successful retry publishes both.

**Pre-existing disk limitation:** Android's low-level config writer opens the
current file with `wb`. Failure after opening or during write/close can therefore
truncate or partially replace the file; this cache fix does not make that disk
operation atomic. A later isolated change should use a flushed temporary file
and atomic replacement, with write/close/rename fault coverage. Likewise,
multiple setting rows are saved individually, so one failing row does not roll
back earlier successful rows. Neither transactional disk writes nor whole-page
rollback is claimed by this baseline's Save behavior.
