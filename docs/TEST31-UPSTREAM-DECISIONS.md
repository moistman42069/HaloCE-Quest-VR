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
That driver is retained here because the menu helper is outside the current
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
| PC scoreboard | Keep existing UI; display-only, no network dependency. Reconsider with approved menu scope. |
| Desktop GL/MSAA and texture-window changes | Keep Android GLES/OpenXR render paths and existing memory allocation. Upstream's expanded desktop virtual-address reservation is not this guest's address layout. |
| Full tag_schema/tag_validate | Defer this large validator integration: it is coupled to upstream tag expansion/CE loader and desktop memory assumptions. Retain existing map-format, tag-header, BSP and script bounds checks; take portable hardening below. Do not claim equivalent full validation. |
| OpenSauce removal | Do not take the removal: owner explicitly requires preserving the existing experimental .yelo loader. This does not imply stock OpenCE can load .yelo or that its extra gameplay is interoperable. |
| Desktop CE loader replacement | Retain app CE/.yelo conversion and resource paths, upgraded cache and Android audio conversion. Take network namespace/missing-map behavior. New desktop protected/large-map workarounds and expanded menu catalog require separate loader validation before adoption. |
| XML menus, filters and Server Setup | Await owner's required scope choice in TEST31-MENU-PLAN.md. Existing in-game browser and launcher remain usable. |

## Every changed upstream path

"Partial" means only the described behavior was integrated. It does not mean
the rest of that file was silently taken. Full upstream snapshots and three-way
merge results are retained privately for continuation.

| Path | Decision |
|---|---|
| `docs/custom_edition_caches.md` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/assets/menus/ce/main_menu.new_select.port.xml` | Keep current UI; upstream desktop menu-dependent changes await owner scope decision. |
| `port/linux/README.md` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |
| `port/linux/game/bmp_files.c` | Already identical / taken byte-for-byte. |
| `port/linux/game/bmp_files.h` | Already identical / taken byte-for-byte. |
| `port/linux/game/cache_file_formats.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/cache_file_formats.h` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_behaviours.inc` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_bitmaps.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_cache.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_cache.h` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_geometry.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_maps.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_maps.h` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_objects.c` | Already identical / taken byte-for-byte. |
| `port/linux/game/custom_edition_scripts.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/custom_edition_sounds.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/linux/game/menu_functions.c` | Keep current UI; upstream desktop menu-dependent changes await owner scope decision. |
| `port/linux/game/network_test.c` | Keep existing automation; upstream CE co-op test driver tied to new map/menu catalog is not required for wire compatibility. |
| `port/linux/game/stb_vorbis.c` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |
| `port/linux/game/tag_schema.h` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_collision.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_effects.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_models.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_schema_render.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/game/tag_validate.c` | Deferred: full schema validation integration (see rationale above). |
| `port/linux/include/halo_linux_source_fixups.h` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |
| `port/linux/include/halo_port_capacity.h` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/include/halo_port_limits.h` | Taken: network22 integration, preserving app additions. |
| `port/linux/src/platform.h` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/src/port_config.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/src/xbox_files.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/src/xbox_memory.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `port/linux/src/xbox_textures.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `port/tools/bmp_file_report.c` | Already identical / taken byte-for-byte. |
| `port/tools/cache_file_report.c` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `port/windows/src/win32_memory_watch.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `source/cache/cache_files.c` | Partial: namespace, missing-map checks and correct allocated CE cache bounds; retain existing loader/PAL/BSP guards. |
| `source/cache/cache_files.h` | Partial: namespace, missing-map checks and correct allocated CE cache bounds; retain existing loader/PAL/BSP guards. |
| `source/cache/cache_files_windows.c` | Partial: namespace, missing-map checks and correct allocated CE cache bounds; retain existing loader/PAL/BSP guards. |
| `source/cache/physical_memory_map.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `source/cache/xbox_texture_cache.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/game/game_engine.c` | Partial: weapon-list/vehicle prediction bounds; existing CE placement behavior retained; desktop scoreboard stays out. |
| `source/hs/hs.c` | Taken through clean three-way merge: CE-aware bounds and refusal to recompile untrusted cached scripts. |
| `source/hs/hs_compile.c` | Already identical / taken byte-for-byte. |
| `source/interface/hud_draw.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/interface/ui_widget.c` | Partial: deferred custom error text and dialog wrapping; desktop menu replacement awaits decision. |
| `source/interface/ui_widget.h` | Partial: deferred custom error text and dialog wrapping; desktop menu replacement awaits decision. |
| `source/interface/ui_widget_event_handler_functions.c` | Keep current UI; upstream desktop menu-dependent changes await owner scope decision. |
| `source/interface/ui_widget_game_data_input_functions.c` | Keep current UI; upstream desktop menu-dependent changes await owner scope decision. |
| `source/main/main.c` | Keep app address layout/config/data management; desktop memory window and CE install drive are not Android game-set storage. |
| `source/networking/network_client_manager.c` | Taken: network22 integration, preserving app additions. |
| `source/objects/object_types.c` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |
| `source/rasterizer/rasterizer.h` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/rasterizer_geometry.h` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/rasterizer_text.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/xbox/rasterizer_xbox.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/xbox/rasterizer_xbox_draw_primitives.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/rasterizer/xbox/rasterizer_xbox_dynavobgeom.c` | Keep app render/CE conversion path; upstream expanded-node/alpha/HUD behavior depends on its new loader. VR display correction is a separate app change. |
| `source/saved games/player_profile.c` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |
| `source/tag_files/tag_groups.c` | Already identical / taken byte-for-byte. |
| `source/text/text_group.c` | Keep current UI; upstream desktop menu-dependent changes await owner scope decision. |
| `tools/custom_edition_script_names.py` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `tools/linux_build.py` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |
| `tools/map_validate.c` | Deferred: full schema validation integration (see rationale above). |
| `tools/port_settings.py` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |
| `tools/test_bmp_files.py` | Already identical / taken byte-for-byte. |
| `tools/test_cache_file_formats.py` | Retain app CE/.yelo implementation and tests; namespace/preflight adapted in cache/maps units. Desktop loader replacement deferred. |
| `tools/test_linux_port.py` | Keep app tooling/docs/profile implementation; upstream desktop changes are outside Android integration. Review again with loader/menu work. |

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
