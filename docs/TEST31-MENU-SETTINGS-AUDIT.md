# Test31 menu settings: runtime audit

Source review on 2026-10-07 against pinned OpenCE Build 145,
`4e8ed2f196e0edd1f2830a4de9841686aabbf466`. This is an implementation
snapshot during integration, not device acceptance. Use the pinned Git object;
the reference checkout working tree is older than Build 145.

The complete screen inventory is in `TEST31-OPENCE-MENU-INVENTORY.md`.
Imported XML and configuration keys alone do not establish working settings.

## Audio

| Setting | Runtime status / required treatment |
| --- | --- |
| Master volume | `dsound_sdl.c::audio_update_volume` now reads changes on the game thread and updates the existing mixer under its mutex. No configuration reads were added to the audio callback. Existing positive custom gains above 1 remain supported. |
| Music/effects volume | `sound_manager.c::sound_manager_port_volume` now follows Build 145's class-gain multiplier. Music affects the music class; effects affects all other classes, including speech. Script class fades and scripted-dialog exemptions from nondialog attenuation remain intact. Defaults are **1.0**, not 100. |
| Audio enabled | Existing device-start gate; requires restarting the game. Label/help must say so. |
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
| High-resolution text | **Font path still caches once** in `text_hires.c::text_enabled`, while title art is live. Adopt the pinned generation-aware helper or clearly label restart required; otherwise the same menu toggle partially applies. |
| Anti-aliasing | **No app consumer for `display.anti_aliasing` found.** Build 145 adds renderer passes/targets for FXAA/SMAA/SSAA/MSAA. The app OpenXR swapchain has `sampleCount = 1`; legacy D3D multisample state wrappers are not evidence of a working MSAA pipeline. Do not expose the upstream AA choices as working until implemented. |
| Shadow resolution | **No app consumer for `display.shadow_resolution` found.** Build 145 scales shadow targets and related render state. The app's existing `graphics.shadows` is an enable/preset control, not a substitute for shadow-map size. |
| Per-pixel lighting | **No app consumer for `display.per_pixel_lighting` found.** Build 145 changes model-lighting shader selection and uniforms. Existing specular/dynamic-light toggles have different semantics. |
| Player names and name scale | Actual generation-aware consumers in `source/interface/hud.c`; preserve all/allies/enemies/none and existing scale bounds. |
| Scoreboard layout/background | **No consumer found beyond newly imported keys/XML.** Integrate the pinned scoreboard presentation consumer, or explicitly leave unavailable. Merely saving these keys is inert. |

Quest already has real `vr.resolution_scale`, `vr.refresh_rate` and per-headset
`graphics.preset`/effect switches. Keep these accessible through VR Settings,
with their existing safe defaults and script-aware effect gating. They are
useful platform controls, but do not satisfy the missing AA, shadow-resolution
or per-pixel features by renaming them.

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
- `update.auto` comes from the desktop self-updater. The menu must route to
  the app's validated APK updater or explain launcher ownership; it must not
  enable blind desktop/upstream binary replacement on Android.
- Default/Save/Cancel need checks per settings page. Hidden unsupported rows
  must not accidentally be committed as default values to active VR settings.
- Recheck the gaps above after root integration. They are identified work,
  not permission to declare the full menu requirement complete.

## Remaining device checks

Both editions: save/cancel/defaults, persistence across restart, profile changes,
live music/effects/master changes, mute/unmute and background/resume. Quest:
headset audio and frame timing, settings pointer/input navigation, HUD/text
switching, refresh/resolution changes, geometry-safe default and lack of
OpenXR context resets. Flat: controller and touch navigation, V-sync behavior,
and external keyboard/mouse where available. No APK has been packaged for
this audit.

## Exact pending renderer dependency patches

These are feasible upstream integrations, not permanently unsupported options.
Keep accepted defaults: shadow size 128, per-pixel lighting OFF, AA OFF.

- **Shadow resolution `1dc533fe`**: 168 additions / one deletion overall.
  The 74-line renderer change identifies the game's 128x128 R5G6B5 shadow
  targets, applies scales 1/2/4/8 and invalidates recent target lookup between
  frames. The 86-line `rasterizer_xbox_shadows.c` change scales half-texel blur
  constants and adds two blur passes per doubled scale. Merge the prototype
  into source fixups. Preserve VR eye-target scaling and apply changes only
  before either eye; test target identity, scale/cache switching, blur width,
  and memory/performance at 1024. Existing shadow-effect OFF still wins.
- **Per-pixel lighting `3dba558e`**: 444 additions / 36 deletions overall,
  spanning `d3d8_gl.c`, `nv2a_vsh.c`, `nv2a_psh.c`, `xgpu.h`, the vertex-shader
  initializer, fixup declaration and config. It recognizes actual model
  lighting program instructions (9/10/17/27), captures skinned normal/world
  position, adds a program-key variant and light uniforms, and falls back to
  existing vertex lighting when recognition/compile/link fails. Preserve the
  app's constant-serial and cull/mirror fixes. Verify OFF shader text/program
  choice remains identical, lit and unlit cache keys differ, recognized/
  rejected programs behave correctly, and left-hand mirrors/fog/transparency
  keep their existing output. GPU cost/appearance still need device checks.
- **Anti-aliasing `94882796`**: 2,434 additions / 51 deletions overall,
  including a 524-line `xgpu_post.c`, SMAA source/tables/license, target
  allocation/resolution changes, renderer finish hook and asset embedding.
  It is a separate renderer integration, not a spinner-only patch. Android
  choices are FXAA/MSAA 2x/4x; desktop also has SMAA/SSAA/MSAA 8x. Quest needs
  per-eye target/postprocess ownership reviewed independently of desktop
  back-buffer presentation. Keep OFF and preserve accepted safe geometry.

Reverb deliberately does not import unrelated upstream ADPCM 65-to-64 sample
changes, windowed-sinc resampling, distance-law changes or replacement limiter.
Those would alter the accepted audio baseline independently of this menu task.
