"""Focused OpenCE Build 157 port checks; no game/runtime launch."""
from pathlib import Path
import hashlib
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
assert re.search(r"^#define HALO_PORT_NETWORK_VERSION 24$", limits, re.M)
assert re.search(r"^#define HALO_PORT_NETWORK_VERSION_MINIMUM 24$", limits, re.M)
assert re.search(r"^#define HALO_PORT_NETWORK_VERSION_MAXIMUM 24$", limits, re.M)

# Exercise the port helper compiled from the real C function under sanitizers.
source = read("source/input/input_abstraction.c")
trigger = function(source, "input_abstraction_port_primary_trigger")
fixture = r'''
#include <assert.h>
#include <stdio.h>
typedef float real;
enum { _game_control_primary_trigger = 7 };
#define MAXIMUM_GAMEPADS 4
#define NUMBER_OF_GAMEPAD_BUTTONS 16
#define NUMBER_OF_GAMEPAD_ANALOG_BUTTONS 8
struct gamepad_state { unsigned char analog_buttons[8]; unsigned char buttons[16]; };
struct game_input_preferences { unsigned char game_control_to_xbox_buttons[12]; };
struct input_abstraction_runtime_globals { struct game_input_preferences player_control_preferences[MAXIMUM_GAMEPADS]; };
struct input_abstraction_runtime_globals input_abstraction_globals;
static struct gamepad_state pads[MAXIMUM_GAMEPADS];
static struct gamepad_state *states[MAXIMUM_GAMEPADS];
static struct gamepad_state const *input_get_gamepad_state(short index) { return states[index]; }
''' + trigger + r'''
int main(void) {
 input_abstraction_globals.player_control_preferences[0].game_control_to_xbox_buttons[_game_control_primary_trigger]=6;
 states[0]=&pads[0];
 pads[0].analog_buttons[6]=0; assert(input_abstraction_port_primary_trigger(0)==0.0f);
 pads[0].analog_buttons[6]=127;
 assert(input_abstraction_port_primary_trigger(0)>0.49f && input_abstraction_port_primary_trigger(0)<0.50f);
 pads[0].analog_buttons[6]=255; assert(input_abstraction_port_primary_trigger(0)==1.0f);
 input_abstraction_globals.player_control_preferences[0].game_control_to_xbox_buttons[_game_control_primary_trigger]=9;
 pads[0].buttons[9]=1; assert(input_abstraction_port_primary_trigger(0)==1.0f);
 states[0]=0; assert(input_abstraction_port_primary_trigger(0)==0.0f);
 assert(input_abstraction_port_primary_trigger(-1)==0.0f);
 assert(input_abstraction_port_primary_trigger(MAXIMUM_GAMEPADS)==0.0f);
 input_abstraction_globals.player_control_preferences[0].game_control_to_xbox_buttons[_game_control_primary_trigger]=NUMBER_OF_GAMEPAD_BUTTONS;
 states[0]=&pads[0]; assert(input_abstraction_port_primary_trigger(0)==0.0f);
 puts("PASS: analog trigger pressure, binary fallback, invalid controller and mapping bounds");
}
'''
out = ROOT / "build/test36"
out.mkdir(parents=True, exist_ok=True)
cfile, binary = out / "primary_trigger.c", out / "primary_trigger"
cfile.write_text(fixture, encoding="utf-8")
subprocess.run(["clang", "-std=gnu11", "-O1", "-fsanitize=address,undefined", str(cfile), "-o", str(binary)], check=True)
subprocess.run([str(binary)], check=True)

# Build 157 network-24 features. These checks pin the port to the upstream
# semantics without copying host-only code or changing the public network UI.
engine = read("source/game/game_engine.c")
header = read("source/game/game_engine.h")
menu = read("port/linux/game/menu_functions.c")
options_valid = function(engine, "game_variant_options_valid")
placement = function(engine, "game_engine_vehicle_placement_allowed")
remap = function(engine, "game_engine_remap_vehicle")
assert "VARIANT_VEHICLE_SET_PC = 0xFE" in header
assert "o->vehicle_set[side] != VARIANT_VEHICLE_SET_PC" in options_valid
assert "if (set == VARIANT_VEHICLE_SET_PC)\n\t\treturn TRUE" in placement
assert "vehicle_set[0] == VARIANT_VEHICLE_SET_PC" in remap
assert "vehicle_set[1] == VARIANT_VEHICLE_SET_PC" in remap
assert "VEHICLE_PRESET_PC 8" in menu and "VEHICLE_PRESET_CUSTOM 9" in menu
spawn = function(engine, "game_engine_update_item_spawn")
assert "custom_edition_cache_tags_loaded()" in spawn
assert "vector3d_from_angle(&placement_data.forward, equipment->facing)" in spawn

server = read("source/networking/network_server_manager.c")
enough = function(server, "server_has_enough_machines")
countdown = function(server, "server_ok_to_countdown")
can_start = function(server, "network_game_server_game_can_start")
assert "minimum_machine_count = 1" in enough
assert "server_alone(server)" in countdown and "server_needs_more_teams" in countdown
assert "server_alone(server)" in can_start
ui = read("source/interface/ui_widget_game_data_input_functions.c")
directions = function(ui, "multiplayer_game_directions")
assert "game->machine_count < 1" in directions
assert "game->player_count < 1" in directions

# Scope and turret reports are not modified without device logs. The added
# diagnostics describe the current handoff/fallback and do not steer gameplay.
frame = read("port/linux/src/vr_frame.c")
compute = function(frame, "compute_aim_pose")
aim_update = function(frame, "update_aim_pose")
vehicle_aim = function(frame, "vr_aim")
assert "look_rotation(between, up, vr.aim_pose.orientation)" in compute
assert "main-hand to grip-line angle" in aim_update
assert "aim behavior unchanged" in aim_update
assert "two_hand_changed = previous_two_handed != two_handed" in aim_update
assert aim_update.index("if (two_hand_changed || (zoom_changed && two_handed))") < aim_update.index("acosf(dot)")
assert "vr.aim_pose.orientation =" not in aim_update and "look_rotation(" not in aim_update
assert "forward/right/up %.3f/%.3f/%.3f" in aim_update
assert "game zoom transition %d -> %d" in function(frame, "vr_set_zoom_level")
assert "native-facing fallback %s" in frame
assert "if (steering_valid)" in vehicle_aim and "if (hand_may_aim < 0) return 0" in vehicle_aim
assert "int hand = hand_may_aim == 2 ? 1 : 0" in vehicle_aim
assert "else\n\t{\n\t\tprevious_vehicle_source = -99" in frame
assert "scope view gate: %s; enabled %d" in function(frame, "vr_scope_view")
assert "scope layer pose: shape %d" in function(frame, "place_scope")

vr_render = read("port/linux/game/vr_render.c")
mounted_aim = function(vr_render, "vr_vehicle_aim_source")
scope_window = function(vr_render, "scope_window")
assert "mounted aim selection: role %s, seat %d, vehicle object %ld" in mounted_aim
assert "effective source %s (%d)" in mounted_aim
assert "scope camera: zoom %d, shape %d" in scope_window
assert "logged_two_handed != vr_two_handed()" in scope_window

# Keep the original-image recommendation visible both during setup/import and
# on the normal launch screen, without labeling other revisions as unsupported.
help_ui = read("port/android/app/src/main/java/com/halo/decomp/LauncherHelp.java")
launcher = read("port/android/app/src/main/java/com/halo/decomp/LauncherActivity.java")
game_data = read("port/android/app/src/main/java/com/halo/decomp/GameDataManager.java")
assert "original Xbox Halo: Combat Evolved XISO" in help_ui
assert "Rev 1 and Rev 2 images can be imported, but are not recommended" in help_ui
assert "LauncherHelp.RECOMMENDED_ISO_NOTE" in function(launcher, "buildMenu")
assert "LauncherHelp.RECOMMENDED_ISO_NOTE" in function(launcher, "buildInterface")
assert "LauncherHelp.DATA_COMPATIBILITY_NOTE" in game_data

# The optional Halo-inspired typeface is local, licensed, persistent and
# limited to short launcher labels; long setup/help text retains system sans.
font = read("port/android/app/src/main/java/com/halo/decomp/LauncherFont.java")
assert 'getBoolean(KEY_HALO_FONT, true)' in font
assert 'putBoolean(KEY_HALO_FONT, !isHaloEnabled(context)).apply()' in font
assert 'fonts/Orbitron-Regular.ttf' in font
assert 'value.length() <= MAX_DISPLAY_TEXT_LENGTH' in font
assert 'originalTypefaces.put(text, original)' in font and 'text.setTypeface(original)' in font
assert 'static final String SUPPORT_NOTE = "Need help? DM @MeWhenINameMyself on Discord."' in help_ui
assert 'LauncherFont.apply(this, scroll)' in function(launcher, "buildMenu")
assert 'LauncherFont.apply(this, importScroll)' in function(launcher, "buildInterface")
assert 'LauncherHelp.SUPPORT_NOTE' in function(launcher, "buildMenu")
assert 'LauncherHelp.SUPPORT_NOTE' in function(launcher, "buildInterface")
font_asset = ROOT / "port/android/app/src/main/assets/fonts/Orbitron-Regular.ttf"
font_license = ROOT / "port/android/app/src/main/assets/fonts/OFL-Orbitron.txt"
assert hashlib.sha256(font_asset.read_bytes()).hexdigest() == "f8c2b5e8dbd870bb73ad0802b1ffcdff4e053c5c074fe403132b9c1852d962d9"
assert font_asset.read_bytes()[:4] == b"\x00\x01\x00\x00"
assert 'SIL Open Font License, Version 1.1' in font_license.read_text(encoding="utf-8")
assert 'Reserved Font Name: "Orbitron"' in font_license.read_text(encoding="utf-8")
assert "Orbitron Regular" in read("CREDITS.md")
print("PASS: launcher style preference, original-XISO guidance, support contact and licensed font asset")

# Builds 156–157's world-positioned stereo audio path must not touch ordinary
# 2D stereo or the existing mono/3D spatializer.
audio_mixer = read("port/linux/src/dsound_sdl.c")
audio_gains = function(audio_mixer, "voice_gains")
audio_mix = function(audio_mixer, "mix_voice")
audio_manager = function(read("source/sound/sound_manager.c"), "update_channels")
audio_port = function(read("source/sound/sound_dsound_xbox.c"), "dsound_port_set_channel_stereo_position")
assert "stream->channels == 2 && stream->stereo_positioned" in audio_gains
assert "float middle = 0.5f * (sample_left + sample_right)" in audio_mix
assert "dsound_port_set_channel_stereo_position(channel_index, FALSE" in audio_manager
assert "dsound_port_set_channel_stereo_position(channel_index, TRUE" in audio_manager
assert "stereo_occlusion,\n\t\t\t\t\t\t\t\tstereo_obstruction" in audio_manager
assert "dsound_channel_set_I3DL2_properties(channel_index)" in audio_port
assert "dsound_sdl_stream_set_stereo_position(channel->stream" in audio_port
print("PASS: Build 157 network-24 semantics and evidence-only VR diagnostics are present")
