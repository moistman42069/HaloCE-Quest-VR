"""Focused Build 147 compatibility and safety regression checks."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def function(source, name):
    match = re.search(r"^(?:static )?(?:inline )?[\w *]+\b" + re.escape(name) + r"\s*\([^;{]*\)\s*\{", source, re.M)
    assert match, name
    start = source.index("{", match.start())
    depth, end = 1, start + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


limits = read("port/linux/include/halo_port_limits.h")
for suffix in ("", "_MINIMUM", "_MAXIMUM"):
    assert re.search(r"#define HALO_PORT_NETWORK_VERSION%s 23\b" % suffix, limits)

# The zoom scope plane follows the calibrated scope view while its center
# stays on the physical gun, using the same extended-arm clamp. Ensure config
# loading and the VR menu both accept the documented ±30 cm adjustment.
frame_vr = read("port/linux/src/vr_frame.c")
menu_vr = read("port/linux/game/vr_menu.c")
config_vr = read("port/linux/src/port_config.c")
vr_header = read("port/linux/src/vr.h")
scope_layer = function(frame_vr, "place_scope")
scope_origin = function(frame_vr, "tracked_hand_origin")
hand_view = function(frame_vr, "hand_view")
scope_menu_change = function(menu_vr, "vr_menu_setting_change")
assert "#define VR_SCOPE_ADJUST_LIMIT_METRES 0.30f" in vr_header
assert "tracked_hand_origin(&vr.aim_pose, origin);" in scope_layer
assert "memcpy(layers->scope_pose.orientation, vr.shot_pose.orientation" in scope_layer
assert "VR_HAND_REACH_METRES" in scope_origin and "VR_HAND_REACH_METRES" in hand_view
assert "VR_SCOPE_ADJUST_LIMIT_METRES" in frame_vr
assert "_vr_setting_scope_centimetres?VR_SCOPE_ADJUST_LIMIT_METRES" in scope_menu_change
assert "_vr_setting_scope_centimetres" in menu_vr
assert config_vr.count("(-0.30..0.30)") == 6
assert "up to ±30 cm" in read("docs/CONTROLS-AND-OPTIONS.md")

# The field report did not show an engine zoom state or scope compositor
# layer. Keep the diagnostic path transition-only and make its gates legible.
reload_settings = function(frame_vr, "vr_reload_settings")
layout_controls = function(frame_vr, "layout_controls")
set_zoom_level = function(frame_vr, "vr_set_zoom_level")
scope_view = function(frame_vr, "vr_scope_view")
render_vr = read("port/linux/game/vr_render.c")
scope_window = function(render_vr, "scope_window")
scope_path_log = function(render_vr, "scope_path_log")
assert "previous_scope_setting != enabled" in reload_settings
assert "previous_zoom_input_state" in layout_controls and "vr.frame.trigger[off_hand]" in layout_controls
assert "routed to gamepad zoom" in layout_controls
assert "vr.zoom_level != zoom_level" in set_zoom_level and "game zoom state" in set_zoom_level
assert "scope view gate" in scope_view and "weapon-hand aim pose is not tracked" in scope_view
assert "scope_path_log(0, zoom_level, 0)" in scope_window
assert "scope_path_log(5, zoom_level, shape)" in scope_window
assert "state == previous_state" in scope_path_log
assert "hold the off-hand index trigger" in scope_path_log
package_gate = read("tools/package-quest.py")
assert 'if vr:\n                    for marker in [b"OpenCE Build 147 / network 23"' in package_gate
assert 'b"scope render path %s"' in package_gate
assert 'b"left trigger for right-handed play"' in package_gate

schema = read("port/linux/game/tag_schema.h")
validator = read("port/linux/game/tag_validate.c")
models = read("port/linux/game/tag_schema_models.c")
scenario = read("port/linux/game/tag_schema_scenario.c")
render_schema = read("port/linux/game/tag_schema_render.c")
assert "_tag_schema_tool_maximum_bit" in schema and "TAG_SCHEMA_TOOL_BLOCK" in schema
assert "TAG_VALIDATE_MAXIMUM_TAG_CACHE_SIZE = 0x02280000" in schema
assert "MAXIMUM_TAG_CACHE_SIZE" in validator
assert "tag_schema_custom_edition_groups" in validator
assert "TAG_SCHEMA_TOOL_BLOCK(struct animation_graph, unit_seats" in models
assert "TAG_SCHEMA_TOOL_BLOCK(struct animation_graph, animations" in models
assert "TAG_SCHEMA_TOOL_BLOCK(struct scenario, vehicles" in scenario
assert "long maximum_count = tag_validate_custom_edition(validation) ? SHORT_MAX" in models
assert "padded_pitch" in render_schema and "tag_validate_custom_edition(validation)" in render_schema

# Run the real upstream Build 147 extent checker with small memory fixtures.
# It must preserve CE editing-tool blocks within their byte bounds, while still
# clamping stock-tool blocks and refusing negative/out-of-range CE extents.
extent = function(validator, "validate_block_extent")
fixture = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>
typedef int boolean;
typedef unsigned char byte;
#define TRUE 1
#define FALSE 0
#define _tag_schema_tool_maximum_bit 2
#define FLAG(bit) (1u << (bit))
#define TEST_FLAG(flags, bit) (((flags) & FLAG(bit)) != 0)
struct tag_schema_definition { unsigned long size; };
struct tag_schema_field { struct tag_schema_definition const *definition; unsigned flags; long maximum; };
struct tag_block { long count; void *address; void *definition; };
struct tag_validation { byte *region; unsigned long region_size; int refused; };
static struct { int custom_edition; } tag_validate_globals;
static int region_contains(struct tag_validation *v, void *pointer, unsigned long size) {
 unsigned long base=(unsigned long)(uintptr_t)v->region, address=(unsigned long)(uintptr_t)pointer;
 return address>=base && address-base<=v->region_size && size<=v->region_size-(address-base);
}
static int claim(void *address, unsigned long size) { (void)address;(void)size;return 1; }
static void tag_validate_refuse(struct tag_validation *v, const char *format, ...) { (void)format;v->refused=1; }
static void tag_validate_correct(struct tag_validation *v, const char *format, ...) { (void)v;(void)format; }
'''
out = ROOT / "build/test34"
out.mkdir(parents=True, exist_ok=True)
source = out / "tag_extent.c"
binary = out / "tag_extent"
source.write_text(fixture + "\n" + extent + r'''
int main(void) {
 byte storage[4096]; struct tag_validation v={storage,sizeof(storage),0};
 struct tag_schema_definition def={4}; struct tag_schema_field field={&def,FLAG(_tag_schema_tool_maximum_bit),10};
 struct tag_block block={100,storage,NULL};
 tag_validate_globals.custom_edition=1; validate_block_extent(&v,&block,&field);
 assert(!v.refused && block.count==100); /* CE tool maximum is not the runtime limit */
 v.refused=0; tag_validate_globals.custom_edition=0; block.count=100; block.address=storage;
 validate_block_extent(&v,&block,&field); assert(!v.refused && block.count==10);
 v.refused=0; tag_validate_globals.custom_edition=1; block.count=100; block.address=storage;
 v.region_size=128; validate_block_extent(&v,&block,&field); assert(v.refused && block.count==100);
 v.refused=0; block.count=-1; validate_block_extent(&v,&block,&field); assert(v.refused);
 puts("PASS: CE tool-sized blocks are preserved inside bounds; stock blocks clamp; malformed CE extents refuse");
}
''')
subprocess.run(["clang", "-std=gnu11", "-O1", "-fsanitize=address,undefined", str(source), "-o", str(binary)], check=True)
subprocess.run([str(binary)], check=True)

cache = read("port/linux/game/custom_edition_cache.c")
assert '#include "tag_schema.h"' in cache
load_validation = function(cache, "custom_edition_cache_tags_validate")
for marker in ("report->identity.file_length", "COMBINED_AUDIO_OFFSET", "COMBINED_BITMAPS_OFFSET",
               "COMBINED_SOUNDS_OFFSET", "tag_validate_custom_edition_tags(", "report->tag_cache_bytes"):
    assert marker in load_validation, marker
assert "report->identity.file_size" not in load_validation
conversion = function(cache, "custom_edition_cache_tags_convert")
assert conversion.index("custom_edition_cache_tags_validate(tag_cache, report)") < conversion.index("custom_edition_bitmaps_verify")
assert "if (model_data)\n\t\tfree(model_data);" in cache

# Exercise the real file-range predicate with a declared CE cache length
# shorter than the physical file. Tag file-data may not point into trailing
# bytes merely because they exist on disk.
file_contains = function(validator, "tag_validate_file_contains")
file_range_source = out / "file_ranges.c"
file_range_binary = out / "file_ranges"
file_range_source.write_text(r'''
#include <assert.h>
#include <stdio.h>
typedef int boolean;
#define FALSE 0
#define TRUE 1
struct tag_validate_file_range { unsigned long offset, size; };
struct tag_validation {};
static struct { struct tag_validate_file_range file_ranges[4]; short file_range_count; } tag_validate_globals;
''' + file_contains + r'''
int main(void) {
 struct tag_validation validation;
 unsigned long physical_size=1024, declared_file_length=900;
 tag_validate_globals.file_range_count=1;
 tag_validate_globals.file_ranges[0].offset=0;
 tag_validate_globals.file_ranges[0].size=declared_file_length;
 assert(physical_size>declared_file_length);
 assert(tag_validate_file_contains(&validation,880,20));
 assert(!tag_validate_file_contains(&validation,900,1));
 assert(!tag_validate_file_contains(&validation,1000,1));
 puts("PASS: CE file-data references cannot escape declared file_length into trailing bytes");
}
''', encoding="utf-8")
subprocess.run(["clang", "-std=gnu11", "-O1", "-fsanitize=address,undefined", str(file_range_source), "-o", str(file_range_binary)], check=True)
subprocess.run([str(file_range_binary)], check=True)

geometry = read("port/linux/game/custom_edition_geometry.c")
assert "if (scratch)\n\t\t\tfree(scratch);" in geometry

client = read("source/networking/network_client_manager.c")
assert "message_packet->map.version != client->game.map.version" in client
assert "cache_files_map_present(message_packet->map.name, (unsigned long)message_packet->map.version)" in client
server = read("source/networking/network_server_manager.c")
assert server.count("cache_files_map_version(server->game.map.name)") >= 3
assert "cache_files_map_version(game->map.name)" in read("port/linux/game/network_pvp_session.c")
map_identity = read("source/cache/cache_files.c")
assert "custom_edition_level_name(map_name) ? custom_edition_map_checksum(map_name) : 0" in function(map_identity, "cache_files_map_version")
assert "if (checksum && identity.checksum != checksum)" in cache
stock_load = function(map_identity, "scenario_tags_load")
assert stock_load.index("tag_validate_tags(") < stock_load.index("cache_file_globals.tag_header = tag_cache_base_address")
bsp_load = function(map_identity, "scenario_structure_bsp_load")
assert bsp_load.index("custom_edition_structure_bsp_reference_valid(") < bsp_load.index("cache_file_structure_bsp_reference_verify(reference)")
assert bsp_load.index("tag_validate_structure_bsp(") < bsp_load.index("structure_bsp_header_register_vertex_buffers")
assert bsp_load.index("tag_validate_structure_bsp(") < bsp_load.index("custom_edition_structure_bsp_load(")
assert "!cache_file_structure_bsp_reference_verify(reference)" in bsp_load
ce_reference_validator = function(cache, "custom_edition_structure_bsp_reference_valid")
ce_reference_source = out / "ce_bsp_ranges.c"
ce_reference_binary = out / "ce_bsp_ranges"
ce_reference_source.write_text(r'''
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define _error_silent 0
#define CACHE_FILE_HEADER_BYTES 0x800
#define CUSTOM_EDITION_TAG_CACHE_ADDRESS 0x40440000UL
struct scenario_structure_bsp_reference { long file_offset, file_size; void *base_address; };
struct custom_edition_cache_globals { int tags_loaded; unsigned long tag_cache_bytes, file_length, loaded_bytes; };
static struct custom_edition_cache_globals custom_edition_cache_globals;
static void error(int level, const char *format, ...) { (void)level; (void)format; }
''' + ce_reference_validator + r'''
int main(void) {
 struct scenario_structure_bsp_reference ref={0x800,0x100000,(void *)(uintptr_t)(CUSTOM_EDITION_TAG_CACHE_ADDRESS+0x800000)};
 custom_edition_cache_globals.tags_loaded=1;
 custom_edition_cache_globals.file_length=0x2000000;
 custom_edition_cache_globals.loaded_bytes=0x800000;
 custom_edition_cache_globals.tag_cache_bytes=0x01700000;
 assert(custom_edition_structure_bsp_reference_valid(&ref)); /* stock-sized CE cache */
 custom_edition_cache_globals.tag_cache_bytes=0x02280000;
 custom_edition_cache_globals.loaded_bytes=0x02100000;
 ref.base_address=(void *)(uintptr_t)(CUSTOM_EDITION_TAG_CACHE_ADDRESS+0x02100000);
 assert(custom_edition_structure_bsp_reference_valid(&ref)); /* upgraded 34.5 MiB cache */
 ref.base_address=(void *)(uintptr_t)(CUSTOM_EDITION_TAG_CACHE_ADDRESS+0x02180000);
 ref.file_size=0x00200000;
 assert(!custom_edition_structure_bsp_reference_valid(&ref)); /* past upgraded cache */
 ref.file_size=0x18;
 ref.base_address=(void *)(uintptr_t)(CUSTOM_EDITION_TAG_CACHE_ADDRESS+0x02280000);
 assert(!custom_edition_structure_bsp_reference_valid(&ref)); /* at cache end */
 ref.file_size=0x100000; ref.file_offset=0x2000000;
 assert(!custom_edition_structure_bsp_reference_valid(&ref)); /* past map file */
 ref.file_offset=-1;
 assert(!custom_edition_structure_bsp_reference_valid(&ref)); /* negative metadata */
 puts("PASS: CE BSPs fit both selected cache sizes; overrun and file-range references reject");
}
''', encoding="utf-8")
subprocess.run(["clang", "-std=gnu11", "-O1", "-fsanitize=address,undefined", str(ce_reference_source), "-o", str(ce_reference_binary)], check=True)
subprocess.run([str(ce_reference_binary)], check=True)

coop = read("port/linux/game/network_coop.c")
assert "return valid_real_vector3d_axes2(forward, up);" in coop
assert "camera_ready && valid_real_vector3d_axes2(&forward, &up)" in coop
assert "COOP_ENEMIES_MAXIMUM_GROWTH = 8" in read("port/linux/game/coop_enemies.c")
assert "MAXIMUM_VEHICLE_HOMES = 1024" in read("source/game/game_engine.c")
capacity = read("port/linux/include/halo_port_capacity.h")
assert "HALO_PORT_MAXIMUM_WIDGETS 2048" in capacity
assert "HALO_PORT_MAXIMUM_LIGHT_VOLUMES 2048" in capacity
assert "players_coop_bring_to_host" in read("source/game/players.c")
assert 'hs_host_player_command(expression, "bringto")' in read("source/hs/hs.c")
assert "scenario && scenario->players.count > 0 && scenario->players.address" in read("source/game/game_engine_oddball.c")
enemy_scaling = function(read("port/linux/game/coop_enemies.c"), "coop_enemies_extra_count")
assert "COOP_ENEMIES_MAXIMUM_GROWTH" in enemy_scaling

ui = read("source/interface/ui_widget.c")
assert 'ui_mouse_selection_row_tracks_hover' in ui and 'server_item_' in function(ui, "ui_mouse_selection_row_tracks_hover")
print("PASS: Build 147 network/map/capacity/camera/CE-validator integration markers")
