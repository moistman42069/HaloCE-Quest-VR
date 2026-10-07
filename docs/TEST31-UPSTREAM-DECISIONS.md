# Test31 upstream integration decisions

Compared three ways: app test30 `fe725aff`, OpenCE build 144 `76b1898e`,
OpenCE build 145 `4e8ed2f196e0edd1f2830a4de9841686aabbf466`. This is a
network-22 integration with selected portable fixes, not a claim that every
desktop feature or every custom map is supported. Public release remains
unchanged while this private candidate is prepared.

## Protocol evidence

28 networking/co-op files are byte-identical to build 145; 8 retain
exactly the same app-only line additions/removals as test30 versus build 144.
The remaining difference is `port/linux/game/network_test.c`: upstream's
debug host driver now selects CE campaign levels through its new menu helper.
That driver is retained here because replacing the automation is outside the current
integration. It is not a runtime message or protocol difference.

The only build144-to145 `source/networking` change is the client-manager
missing-map preflight. Header gates remain exactly 22. Message IDs and tunnel
crypto/wire structure are unchanged. Existing avatar 37/38, co-op host request
format 3/name, resting-object resend and upright camera remain. The new p2p.c
local probe schedule adds ordinary authenticated pings without changing offers,
packet IDs, authentication, replay checks, endpoint adoption or game messages.
No cross-play session has been run for test31.

## Previously excluded features

| Feature | Decision and reason |
|---|---|
| PC scoreboard | Integrated the Build 145 scoreboard, presentation settings and 128-player paging; adapted paging for Quest/touch/gamepads. |
| Desktop GL/MSAA and texture-window changes | Adapted optional FXAA/MSAA, shadow resolution and per-pixel model lighting to Android GLES/OpenXR while preserving private eye targets and safe fallback. Existing guest memory layout remains; upstream desktop virtual-address expansion is not imported. |
| Full tag_schema/tag_validate | Defer this large validator integration: it is coupled to upstream tag expansion/CE loader and desktop memory assumptions. Retain existing map-format, tag-header, BSP and script bounds checks; take portable hardening below. Do not claim equivalent full validation. |
| OpenSauce removal | Do not take the removal: owner explicitly requires preserving the existing experimental .yelo loader. This does not imply stock OpenCE can load .yelo or that its extra gameplay is interoperable. |
| Desktop CE loader replacement | Retain app CE/.yelo conversion and resource paths, upgraded cache and Android audio conversion. Take network namespace/missing-map behavior. The menu catalog API is adapted to the active managed game set, retaining .map/.yelo and separate campaign/multiplayer capacity. Desktop protected/large-map loader workarounds remain deferred pending validation. |
| XML menus, filters and Server Setup | Full Build 145 menu setup imported after owner scope expansion. Includes browser filters, host setup, profiles, settings and platform input adapters; see TEST31-OPENCE-MENU-INVENTORY.md. |

## Every changed upstream path

This path table starts from the Build 144-to-145 diff; the later full-menu
integration also imports dependencies from earlier upstream commits, recorded
in the final section and the menu inventory.

"Partial" means only the described behavior was integrated. It does not mean
the rest of that file was silently taken. Full upstream snapshots and three-way
merge results are retained privately for continuation.

| Path | Decision |
|---|---|
| `docs/custom_edition_caches.md` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/assets/menus/ce/main_menu.new_select.port.xml` | Imported/adapted in the full menu integration authorized by the owner; existing Android/VR controls and game-set loader retained. |
| `port/linux/README.md` | Retain the app implementation; this upstream desktop/tooling path is outside the reviewed Android menu/network dependency set. Reassess if its corresponding loader/tool behavior is later adopted. |
| `port/linux/game/bmp_files.c` | Already identical / taken byte-for-byte. |
| `port/linux/game/bmp_files.h` | Already identical / taken byte-for-byte. |
| `port/linux/game/cache_file_formats.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/cache_file_formats.h` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_behaviours.inc` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_bitmaps.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_cache.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_cache.h` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_geometry.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_maps.c` | Adapted Build 145 menu/campaign catalog APIs and custom_maps namespace to the existing managed game-set scanner. Preserve .map/.yelo and the app loading path; desktop loader replacement remains deferred. |
| `port/linux/game/custom_edition_maps.h` | Added the menu/campaign catalog API declarations without replacing app map-loader semantics. |
| `port/linux/game/custom_edition_objects.c` | Already identical / taken byte-for-byte. |
| `port/linux/game/custom_edition_scripts.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_sounds.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/menu_functions.c` | Imported/adapted in the full menu integration authorized by the owner; existing Android/VR controls and game-set loader retained. |
| `port/linux/game/network_test.c` | Keep existing automation; upstream CE co-op test driver tied to new map/menu catalog is not required for wire compatibility. |
| `port/linux/game/stb_vorbis.c` | Retain the app implementation; this upstream desktop/tooling path is outside the reviewed Android menu/network dependency set. Reassess if its corresponding loader/tool behavior is later adopted. |
| `port/linux/game/tag_schema.h` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_collision.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_effects.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_models.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_render.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_validate.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/include/halo_linux_source_fixups.h` | Added shadow-scale, model-lighting and pre-HUD anti-alias entry points for the optional graphics consumers; existing app/source fixes retained. |
| `port/linux/include/halo_port_capacity.h` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/include/halo_port_limits.h` | Taken: network22 integration, preserving app additions. |
| `port/linux/src/platform.h` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/src/port_config.c` | Merged typed live settings, safe persistence/default access and menu/audio/graphics/browser keys while retaining Android storage, network and VR defaults. Desktop allocation assumptions remain excluded. |
| `port/linux/src/xbox_files.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/src/xbox_memory.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/src/xbox_textures.c` | Connected embedded menu-art textures and live high-resolution HUD lookup. Retained existing Android upload, texture/CE conversion and safety paths; unrelated desktop loader changes remain excluded. |
| `port/tools/bmp_file_report.c` | Already identical / taken byte-for-byte. |
| `port/tools/cache_file_report.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/windows/src/win32_memory_watch.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `source/cache/cache_files.c` | Integrated menu tag lifecycle and separate runtime tag count alongside namespace/missing-map preflight and CE cache bounds. Raw map header count and existing loader/PAL/BSP guards retained. |
| `source/cache/cache_files.h` | Added runtime tag-table/menu lifecycle accessors and map compatibility helpers while preserving the on-disk cache format. |
| `source/cache/cache_files_windows.c` | Partial: namespace, missing-map checks and correct allocated CE cache bounds; retain existing loader/PAL/BSP guards. |
| `source/cache/physical_memory_map.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `source/cache/xbox_texture_cache.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/game/game_engine.c` | Integrated Build 145 full-screen/co-op scoreboard, 128-player paging and presentation consumers; weapon-list/vehicle bounds retained. Compact local split-screen rows preserved. |
| `source/hs/hs.c` | Taken through clean three-way merge: CE-aware bounds and refusal to recompile untrusted cached scripts. |
| `source/hs/hs_compile.c` | Already identical / taken byte-for-byte. |
| `source/interface/hud_draw.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/interface/ui_widget.c` | Merged full OpenCE widget/focus/spinner/custom-event handling, deferred errors, native text-entry polling and shared pointer routing. Preserved app VR/touch and network-pause behavior. |
| `source/interface/ui_widget.h` | Added required menu/widget helpers and runtime interfaces with existing app widget layout constraints retained. |
| `source/interface/ui_widget_event_handler_functions.c` | Imported/adapted in the full menu integration authorized by the owner; existing Android/VR controls and game-set loader retained. |
| `source/interface/ui_widget_game_data_input_functions.c` | Imported/adapted in the full menu integration authorized by the owner; existing Android/VR controls and game-set loader retained. |
| `source/main/main.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `source/networking/network_client_manager.c` | Taken: network22 integration, preserving app additions. |
| `source/objects/object_types.c` | Retain the app implementation; this upstream desktop/tooling path is outside the reviewed Android menu/network dependency set. Reassess if its corresponding loader/tool behavior is later adopted. |
| `source/rasterizer/rasterizer.h` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/rasterizer_geometry.h` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/rasterizer_text.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/xbox/rasterizer_xbox.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/xbox/rasterizer_xbox_draw_primitives.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/xbox/rasterizer_xbox_dynavobgeom.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/saved games/player_profile.c` | Adopted the CE campaign guard: levels without a stock campaign index do not write an invalid stock completion slot. Existing profile/save format retained. |
| `source/tag_files/tag_groups.c` | Already identical / taken byte-for-byte. |
| `source/text/text_group.c` | Imported/adapted in the full menu integration authorized by the owner; existing Android/VR controls and game-set loader retained. |
| `tools/custom_edition_script_names.py` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `tools/linux_build.py` | Added Expat parser sources/includes for menu compilation; existing desktop build and bundled compression dependencies retained. |
| `tools/map_validate.c` | Deferred: full schema validation integration (see rationale above). |
| `tools/port_settings.py` | Retain the app implementation; this upstream desktop/tooling path is outside the reviewed Android menu/network dependency set. Reassess if its corresponding loader/tool behavior is later adopted. |
| `tools/test_bmp_files.py` | Already identical / taken byte-for-byte. |
| `tools/test_cache_file_formats.py` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `tools/test_linux_port.py` | Retain the app implementation; this upstream desktop/tooling path is outside the reviewed Android menu/network dependency set. Reassess if its corresponding loader/tool behavior is later adopted. |

## NAT limits and relay decision

RFC 4787 distinguishes mapping from filtering; observing the same STUN port
alone does not prove an open firewall. Test31 also compares the IP, avoiding
calling two equal-port/different-IP egress mappings lenient. Bounded probes may
help predictable symmetric mappings; they cannot discover arbitrary new IPs
or guarantee randomized mappings. The same tunnel socket is already used for
STUN and game traffic; a second socket would lose the observed mapping.

References: https://www.rfc-editor.org/rfc/rfc4787 and
https://www.rfc-editor.org/rfc/rfc5128 (port prediction limitations).

A relay would need a hosted authenticated service, abuse/rate controls,
bandwidth monitoring and client negotiation. Cost depends on region/provider
and aggregate relayed traffic; for illustration, a sustained aggregate 1 Mbit/s
is about 0.45 GB per hour of outbound traffic, before overhead. No provider
price or game bandwidth has been measured. Unmodified OpenCE has no relay
negotiation, so a port-only relay cannot promise mixed-client compatibility.
Owner decision and an interoperability design are required before implementing
one. No relay is deployed or included here.


## Full menu dependency integration (owner scope update)

The later full-menu approval superseded the initial menu deferrals. The current
per-path decisions above include the completed source integration.
Import uses the pre-menu ancestor and pinned Build 145 Git objects, preserving
app differences rather than replacing the Android renderer or CE loader.
Dependencies include Expat and embedded menu assets, tag-table ownership,
widget custom events/spinners, profile/gametype option persistence, keyboard
bindings, native text entry, SDL platform adapters, scoreboard/text scaling,
audio controls and optional rendering consumers. The raw map-header tag count
stays immutable; generated menus and VR pages use a separate runtime count.
Unload order is widgets/textures, VR pages, menu definitions, then map data.

Upstream dependency commits: shadow size `1dc533fe`, per-pixel model lighting
`3dba558e`, anti-aliasing `94882796`, and reverb `8a8e7059`. App defaults remain
128-pixel shadows, per-pixel OFF, AA OFF and reverb OFF. Android AA uses GLES
FXAA/MSAA; desktop SMAA assets retain their license. VR retains per-eye/scope
resolve, HUD alpha, reticle capture, safe uploads, mirror/cull guards and target
recycling. Headset appearance and timing still need testing.

Android's menu updater displays USE LAUNCHER guidance to the validated APK
updater; it does not open an installer during gameplay. Desktop
window modes/resizing are not offered as Android features. VR synchronization
continues to use OpenXR. Split screen is upstream local-screen functionality,
not multiple tracked headsets in a single Quest process.

Latest-target recheck: GitHub API `releases/latest`, `commits/main`, and
`git/ref/tags/build-145` still resolve to Build 145 / `4e8ed2f1` on 2026-10-07.
The web search cache returned an obsolete build-78 page; live API results and
pinned Git objects are the evidence used here. The reference checkout's
`origin` points to bnunu; the reviewed upstream is cybersecurity/OpenCE, now
redirecting to OpenCommunityEdition/OpenCE. Do not mistake origin/main for
the upstream pinned by this document.
