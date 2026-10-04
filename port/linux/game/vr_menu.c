/*
VR_MENU.C

The pause menu's VR settings, in the VR build (HALO_VR): the headset's
options changed in play, in the pause menu's own boxes, font and buttons.

Halo's menus are widget tags in each map. When a level's tags load, this
adds a "VR SETTINGS" item to the solo pause menu's list (its button hints
move from under the list to under the mission objectives, making room). It
opens a screen of categories (CONTROLS, VR, GRAPHICS, EFFECTS), each opening
a page of settings. Every screen is cloned from the pause menu: the same
dimmed backdrop and boxes, with its list where the pause menu's list and the
mission objectives were (a page's settings in two columns). Each setting is
a button cloned from "RESUME GAME": A or right steps it to its next value,
left to its previous; B goes back a screen. The settings are written into
config.toml as they change, and the VR layer takes them up at once
(vr_reload_settings).

The widget code calls back here for the text of these buttons (a game data
input function: VR_MENU_GAME_DATA_FUNCTION) and for their changes (event
handler functions: VR_MENU_NEXT_FUNCTION, VR_MENU_PREVIOUS_FUNCTION).
*/

#ifdef HALO_VR

#include "cseries.h"
#include "math/integer_math.h"
#include "math/real_math.h"
#include "tag_files/tag_groups.h"
#include "tag_files/tag_files.h"

#include "halo_vr.h"
#include "../src/vr.h"
#include "../src/port_config.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* port/linux/src/platform.h (a variadic call needs its prototype in scope
on the Android guest's ABI) */
void platform_log(const char *format, ...);
/* source/cache/cache_files.c */
long cache_file_add_tag(unsigned long group_tag, unsigned long parent_group_tag, char *name, void *base_address);

/* ---------- the widget definition tag ('DeLa'), as ui_widget.c views it */

#define VR_MENU_WIDGET_TAG 0x44654C61 /* 'DeLa' */

struct vr_menu_event_handler
{
	long flags;
	short event_type;
	short function;
	struct tag_reference widget_tag;
	struct tag_reference sound_effect;
	char script[32];
};

struct vr_menu_child
{
	struct tag_reference widget_tag;
	char name[32];
	long flags;
	short custom_controller_index;
	short vertical_offset;
	short horizontal_offset;
	byte unknown03A[0x50 - 0x3A];
};

struct vr_menu_game_data_input
{
	short function;
	byte unknown002[0x24 - 0x02];
};

struct vr_menu_widget
{
	short type;
	short controller_index;
	char name[32];
	rectangle2d bounds;
	long flags;
	long milliseconds_to_auto_close;
	long auto_close_fade_time;
	struct tag_reference background_bitmap;
	struct tag_block game_data_inputs;
	struct tag_block event_handlers;
	struct tag_block search_and_replace_functions;
	byte unknown06C[0xEC - 0x6C];
	struct tag_reference text_label_string_list;
	byte unknown0FC[0x3E0 - 0xFC];
	struct tag_block child_widgets;
};

typedef char vr_menu_event_handler_size[sizeof(struct vr_menu_event_handler) == 0x48 ? 1 : -1];
typedef char vr_menu_child_size[sizeof(struct vr_menu_child) == 0x50 ? 1 : -1];
typedef char vr_menu_game_data_input_size[sizeof(struct vr_menu_game_data_input) == 0x24 ? 1 : -1];
typedef char vr_menu_widget_size[sizeof(struct vr_menu_widget) == 0x3EC ? 1 : -1];
typedef char vr_menu_widget_bounds[offsetof(struct vr_menu_widget, bounds) == 0x24 ? 1 : -1];
typedef char vr_menu_widget_game_data_inputs[offsetof(struct vr_menu_widget, game_data_inputs) == 0x48 ? 1 : -1];
typedef char vr_menu_widget_event_handlers[offsetof(struct vr_menu_widget, event_handlers) == 0x54 ? 1 : -1];
typedef char vr_menu_widget_text[offsetof(struct vr_menu_widget, text_label_string_list) == 0xEC ? 1 : -1];

/* event handler flags and events (ui_widget.c) */
#define VR_MENU_CLOSE_CURRENT 0x1
#define VR_MENU_CLOSE_ALL 0x4
#define VR_MENU_OPEN_WIDGET 0x8
#define VR_MENU_RUN_FUNCTION 0x80
#define VR_MENU_EVENT_A 0
#define VR_MENU_EVENT_B 1
#define VR_MENU_EVENT_DPAD_LEFT 10
#define VR_MENU_EVENT_DPAD_RIGHT 11
#define VR_MENU_EVENT_START 12
#define VR_MENU_EVENT_BACK 13

/* ---------- the settings */

enum
{
	_vr_setting_boolean,
	_vr_setting_real,
	_vr_setting_real_choice,
	_vr_setting_string,
	_vr_setting_degrees,
	_vr_setting_centimetres,
	_vr_setting_vehicle_centimetres,
	_vr_setting_reset_alignment,
	_vr_setting_flip_alignment,
};

#define VR_MENU_MAXIMUM_VALUES 12

struct vr_menu_setting
{
	char const *label, *key;
	short type, value_count;
	struct
	{
		char const *label, *value;
	} values[VR_MENU_MAXIMUM_VALUES];
};

/* an effect's setting (vr_graphics.c): as the preset, or on or off */
#define VR_MENU_EFFECT(label, key) \
	{ label, key, _vr_setting_string, 3, { { "AUTO", "auto" }, { "ON", "on" }, { "OFF", "off" } } }

static struct vr_menu_setting const vr_menu_controls[] =
{
	{ "CONTROLS", "vr.controls", _vr_setting_string, 2, { { "VR", "vr" }, { "XBOX", "pad" } } },
	{ "AIM", "vr.aim", _vr_setting_string, 2, { { "HAND", "hand" }, { "HEAD", "head" } } },
	{ "GUN HAND", "vr.left_handed", _vr_setting_boolean, 2, { { "RIGHT", "false" }, { "LEFT", "true" } } },
	{ "TURNING", "vr.snap_turn", _vr_setting_real, 3, { { "SMOOTH", "0" }, { "SNAP 30", "30" }, { "SNAP 45", "45" } } },
	{ "TURN SPEED", "vr.smooth_turn_speed", _vr_setting_real, 12, { { "45", "45" }, { "60", "60" }, { "75", "75" }, { "90", "90" }, { "105", "105" }, { "120", "120" }, { "150", "150" }, { "180", "180" }, { "210", "210" }, { "240", "240" }, { "270", "270" }, { "300", "300" } } },
	{ "MOVE WITH", "vr.move_relative", _vr_setting_string, 3, { { "HEAD", "head" }, { "LEFT HAND", "left" }, { "RIGHT HAND", "right" } } },
	{ "TWO HANDS", "vr.two_handed", _vr_setting_string, 3, { { "GRIP", "grip" }, { "AUTO", "auto" }, { "OFF", "off" } } },
	{ "WEAPONS", "vr.weapons", _vr_setting_string, 2, { { "LOCKED", "locked" }, { "PHYSICAL", "physical" } } },
	{ "HOLSTERS", "vr.holsters", _vr_setting_boolean, 2, { { "OFF", "false" }, { "ON", "true" } } },
};

static struct vr_menu_setting const vr_menu_body[] =
{
	{ "BODY", "vr.body", _vr_setting_string, 4, { { "ARMS + HANDS", "arms" }, { "FULL", "full" }, { "LEGS + ARMS", "legs" }, { "HANDS ONLY", "hands" } } },
	{ "ARMS", "vr.arms", _vr_setting_string, 3, { { "IK", "ik" }, { "HIDDEN", "hidden" }, { "ANIMATED", "animated" } } },
	{ "FINGERS", "vr.fingers", _vr_setting_boolean, 2, { { "OFF", "false" }, { "TRACKED", "true" } } },
	{ "ROOM-SCALE", "vr.roomscale", _vr_setting_boolean, 2, { { "OFF", "false" }, { "ON", "true" } } },
	{ "CROUCH DEPTH", "vr.crouch_height", _vr_setting_real, 9, { { "OFF", "0" }, { "5 CM", "0.05" }, { "10 CM", "0.1" }, { "15 CM", "0.15" }, { "20 CM", "0.2" }, { "25 CM", "0.25" }, { "30 CM", "0.3" }, { "35 CM", "0.35" }, { "40 CM", "0.4" } } },
	{ "ARM RUN", "vr.arm_run", _vr_setting_boolean, 2, { { "OFF", "false" }, { "ON", "true" } } },
	{ "RUN EFFORT", "vr.arm_run_speed", _vr_setting_real, 11, { { "0.2", "0.2" }, { "0.3", "0.3" }, { "0.4", "0.4" }, { "0.45", "0.45" }, { "0.5", "0.5" }, { "0.6", "0.6" }, { "0.7", "0.7" }, { "0.8", "0.8" }, { "0.9", "0.9" }, { "1.0", "1.0" }, { "1.2", "1.2" } } },
	{ "MELEE", "vr.melee", _vr_setting_string, 2, { { "IMPACT", "impact" }, { "SWING", "swing" } } },
	{ "MELEE SPEED", "vr.melee_speed", _vr_setting_real, 12, { { "OFF", "0" }, { "1.0", "1.0" }, { "1.2", "1.2" }, { "1.4", "1.4" }, { "1.6", "1.6" }, { "1.8", "1.8" }, { "2.0", "2.0" }, { "2.3", "2.3" }, { "2.6", "2.6" }, { "2.9", "2.9" }, { "3.2", "3.2" }, { "3.6", "3.6" } } },
};

static struct vr_menu_setting const vr_menu_vr[] =
{
	{ "HAPTICS", "vr.haptics", _vr_setting_real, 11, { { "0%", "0.0" }, { "10%", "0.1" }, { "20%", "0.2" }, { "30%", "0.3" }, { "40%", "0.4" }, { "50%", "0.5" }, { "60%", "0.6" }, { "70%", "0.7" }, { "80%", "0.8" }, { "90%", "0.9" }, { "100%", "1.0" } } },
	{ "FLASHLIGHT", "vr.flashlight_distance", _vr_setting_real_choice, 2, { { "GESTURE", "0.2" }, { "BUTTON", "0" } } },
	{ "HOLSTER SIZE", "vr.holster_size", _vr_setting_real, 6, { { "10 CM", "0.1" }, { "15 CM", "0.15" }, { "20 CM", "0.2" }, { "25 CM", "0.25" }, { "30 CM", "0.3" }, { "40 CM", "0.4" } } },
	{ "SCOPE", "vr.scope", _vr_setting_boolean, 2, { { "OFF", "false" }, { "ON", "true" } } },

	{ "CUTSCENES", "vr.cutscenes", _vr_setting_string, 3, { { "IMMERSIVE", "immersive" }, { "3D SCREEN", "screen" }, { "FLAT", "flat" } } },
	{ "MP PHYSICAL", "vr.physical_multiplayer", _vr_setting_boolean, 2, { { "OFF", "false" }, { "ON", "true" } } },
	{ "CLOSE CONTACT", "vr.close_contact", _vr_setting_boolean, 2, { { "OFF", "false" }, { "ON", "true" } } },
};

static struct vr_menu_setting const vr_menu_vehicles[] =
{
	{ "VIEW", "vr.vehicle_view", _vr_setting_string, 2, { { "THIRD PERSON", "chase" }, { "FIRST PERSON", "first_person" } } },
	{ "STEERING", "vr.vehicle_steering", _vr_setting_string, 4, { { "RIGHT HAND", "right" }, { "LEFT HAND", "left" }, { "HEAD", "head" }, { "STICK", "stick" } } },
	{ "ALL UP", "vr.vehicle_all_up", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "ALL FORWARD", "vr.vehicle_all_forward", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "ALL RIGHT", "vr.vehicle_all_right", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "HOG UP", "vr.vehicle_warthog_up", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "HOG FORWARD", "vr.vehicle_warthog_forward", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "HOG RIGHT", "vr.vehicle_warthog_right", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "GHOST UP", "vr.vehicle_ghost_up", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "GHOST FORWARD", "vr.vehicle_ghost_forward", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "GHOST RIGHT", "vr.vehicle_ghost_right", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "BANSHEE UP", "vr.vehicle_banshee_up", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "BANSHEE FORWARD", "vr.vehicle_banshee_forward", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "BANSHEE RIGHT", "vr.vehicle_banshee_right", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "TANK UP", "vr.vehicle_scorpion_up", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "TANK FORWARD", "vr.vehicle_scorpion_forward", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "TANK RIGHT", "vr.vehicle_scorpion_right", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "PELICAN UP", "vr.vehicle_pelican_up", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "PELICAN FORWARD", "vr.vehicle_pelican_forward", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
	{ "PELICAN RIGHT", "vr.vehicle_pelican_right", _vr_setting_vehicle_centimetres, 0, { { NULL, NULL } } },
};

static struct vr_menu_setting const vr_menu_crosshair[] =
{
	{ "CROSSHAIR", "vr.crosshair", _vr_setting_string, 2, { { "NATIVE", "native" }, { "OFF", "off" } } },
	{ "SIZE", "vr.crosshair_size", _vr_setting_real, 8, { { "25%", "0.25" }, { "50%", "0.5" }, { "75%", "0.75" }, { "100%", "1" }, { "125%", "1.25" }, { "150%", "1.5" }, { "200%", "2" }, { "300%", "3" } } },
	{ "OPACITY", "vr.crosshair_opacity", _vr_setting_real, 11, { { "0%", "0" }, { "10%", "0.1" }, { "20%", "0.2" }, { "30%", "0.3" }, { "40%", "0.4" }, { "50%", "0.5" }, { "60%", "0.6" }, { "70%", "0.7" }, { "80%", "0.8" }, { "90%", "0.9" }, { "100%", "1" } } },
};

static struct vr_menu_setting const vr_menu_graphics[] =
{
	{ "PRESET", "graphics.preset", _vr_setting_string, 5, { { "AUTO", "auto" }, { "LOW", "low" }, { "MEDIUM", "medium" }, { "HIGH", "high" }, { "MAX", "max" } } },
	{ "RESOLUTION", "vr.resolution_scale", _vr_setting_real, 6, { { "AUTO", "0" }, { "70%", "0.7" }, { "85%", "0.85" }, { "100%", "1" }, { "115%", "1.15" }, { "130%", "1.3" } } },
	VR_MENU_EFFECT("SHADOWS", "graphics.shadows"),
	VR_MENU_EFFECT("LIGHTS", "graphics.dynamic_lights"),
	VR_MENU_EFFECT("SPECULAR", "graphics.specular"),
	VR_MENU_EFFECT("REFLECTIONS", "graphics.reflections"),
	VR_MENU_EFFECT("BUMP MAPS", "graphics.bump_mapping"),
	VR_MENU_EFFECT("GRASS", "graphics.detail_objects"),
	VR_MENU_EFFECT("FOG LAYERS", "graphics.fog_screen"),
};

static struct vr_menu_setting const vr_menu_effects[] =
{
	VR_MENU_EFFECT("DECALS", "graphics.decals"),
	VR_MENU_EFFECT("PARTICLES", "graphics.particles"),
	VR_MENU_EFFECT("CONTRAILS", "graphics.contrails"),
	VR_MENU_EFFECT("WEATHER", "graphics.weather"),
	VR_MENU_EFFECT("LENS FLARES", "graphics.lens_flares"),
	VR_MENU_EFFECT("CAMO", "graphics.camouflage_multipass"),
	{ "REFRESH", "vr.refresh_rate", _vr_setting_real, 4, { { "72 HZ", "72" }, { "80 HZ", "80" }, { "90 HZ", "90" }, { "120 HZ", "120" } } },
};

static struct vr_menu_setting const vr_menu_align_left[] =
{
    { "PITCH", "vr.align_left_pitch", _vr_setting_degrees, 0, { { NULL,NULL } } },
    { "YAW", "vr.align_left_yaw", _vr_setting_degrees, 0, { { NULL,NULL } } },
    { "ROLL", "vr.align_left_roll", _vr_setting_degrees, 0, { { NULL,NULL } } },
    { "RIGHT", "vr.align_left_right", _vr_setting_centimetres, 0, { { NULL,NULL } } },
    { "UP", "vr.align_left_up", _vr_setting_centimetres, 0, { { NULL,NULL } } },
    { "BACK", "vr.align_left_back", _vr_setting_centimetres, 0, { { NULL,NULL } } },
    { "AIM POSE", "vr.align_left_grip_aim", _vr_setting_boolean, 2, { { "NATIVE", "false" }, { "GRIP", "true" } } },
    { "FLIP ROLL 180", "vr.align_left_roll", _vr_setting_flip_alignment, 0, { { NULL,NULL } } },
    { "RESET LEFT", "left", _vr_setting_reset_alignment, 0, { { NULL,NULL } } },
};

static struct vr_menu_setting const vr_menu_align_right[] =
{
    { "PITCH", "vr.align_right_pitch", _vr_setting_degrees, 0, { { NULL,NULL } } },
    { "YAW", "vr.align_right_yaw", _vr_setting_degrees, 0, { { NULL,NULL } } },
    { "ROLL", "vr.align_right_roll", _vr_setting_degrees, 0, { { NULL,NULL } } },
    { "RIGHT", "vr.align_right_right", _vr_setting_centimetres, 0, { { NULL,NULL } } },
    { "UP", "vr.align_right_up", _vr_setting_centimetres, 0, { { NULL,NULL } } },
    { "BACK", "vr.align_right_back", _vr_setting_centimetres, 0, { { NULL,NULL } } },
    { "AIM POSE", "vr.align_right_grip_aim", _vr_setting_boolean, 2, { { "NATIVE", "false" }, { "GRIP", "true" } } },
    { "FLIP ROLL 180", "vr.align_right_roll", _vr_setting_flip_alignment, 0, { { NULL,NULL } } },
    { "RESET RIGHT", "right", _vr_setting_reset_alignment, 0, { { NULL,NULL } } },
};

/* a page of settings, opened from the categories: its first `left_count`
settings in the left column, the rest in the right */
static struct vr_menu_page
{
	char const *label;
	struct vr_menu_setting const *settings;
	long count;
} const vr_menu_pages[] =
{
	{ "CONTROLS", vr_menu_controls, NUMBEROF(vr_menu_controls) },
	{ "BODY", vr_menu_body, NUMBEROF(vr_menu_body) },
	{ "VR", vr_menu_vr, NUMBEROF(vr_menu_vr) },
	{ "VEHICLES", vr_menu_vehicles, NUMBEROF(vr_menu_vehicles) },
	{ "GRAPHICS", vr_menu_graphics, NUMBEROF(vr_menu_graphics) },
	{ "DISPLAY", vr_menu_effects, NUMBEROF(vr_menu_effects) },
	{ "CROSSHAIR", vr_menu_crosshair, NUMBEROF(vr_menu_crosshair) },
	{ "ALIGN LEFT", vr_menu_align_left, NUMBEROF(vr_menu_align_left) },
	{ "ALIGN RIGHT", vr_menu_align_right, NUMBEROF(vr_menu_align_right) },
};

#define VR_MENU_PAGE_COUNT ((long)NUMBEROF(vr_menu_pages))
/* Four rows per column. The fifth left row is reserved for navigation;
 * the fifth right row belongs to the stock button hints. Capacity derives
 * from the definitions, so new settings/categories create further screens. */
#define VR_MENU_SETTINGS_PER_SCREEN 8
#define VR_MENU_PAGES(n) (((n) + VR_MENU_SETTINGS_PER_SCREEN - 1) / VR_MENU_SETTINGS_PER_SCREEN)


/* the setting's value now, as an index into its values (NONE: none of them) */
static long vr_menu_value_index(
	struct vr_menu_setting const *setting)
{
	long index;

	for (index = 0; index < setting->value_count; index++)
	{
		char const *value = setting->values[index].value;

		switch (setting->type)
		{
		case _vr_setting_boolean:
			if (config_boolean(setting->key) == !strcmp(value, "true"))
				return index;
			break;
		case _vr_setting_real:
		case _vr_setting_real_choice:
			if (fabs(config_real(setting->key) - atof(value)) < 0.001)
				return index;
			break;
		case _vr_setting_string:
			if (!strcmp(config_string(setting->key), value))
				return index;
			break;
		}
	}
	return NONE;
}

/* ---------- the tags */

struct vr_menu_navigation { long tag, next, total; };

static struct
{
	/* the tags this made for the map loaded, and what they point at: the
	pause menu's item, the categories' screen and its buttons, and each
	page's screen and buttons */
	long button_tag_index, categories_tag_index;
	long category_tag_indices[NUMBEROF(vr_menu_pages)];
	long page_tag_indices[NUMBEROF(vr_menu_pages)];
	long *setting_tag_indices[NUMBEROF(vr_menu_pages)];
 struct vr_menu_navigation *navigation;
 long navigation_count, navigation_capacity;
 void **allocations;
 long allocation_count, allocation_capacity;
} vr_menu;

/* Track lifetime without a fixed allocation/name ceiling. All allocations
 * are made while map tags load, never in the render loop. */
static void *vr_menu_allocate(long size)
{
    void *memory;
    if (size <= 0) return NULL;
    if (vr_menu.allocation_count == vr_menu.allocation_capacity) {
        long capacity = vr_menu.allocation_capacity ? vr_menu.allocation_capacity * 2 : 128;
        void **grown;
        if (capacity <= vr_menu.allocation_capacity || capacity > 32768) return NULL;
        grown = malloc(capacity * sizeof(*grown));
        if (!grown) return NULL;
        if (vr_menu.allocations) {
            memcpy(grown, vr_menu.allocations, vr_menu.allocation_count * sizeof(*grown));
            free(vr_menu.allocations);
        }
        vr_menu.allocations = grown; vr_menu.allocation_capacity = capacity;
    }
    memory = malloc((size_t)size);
    if (memory) {
        memset(memory, 0, (size_t)size);
        vr_menu.allocations[vr_menu.allocation_count++] = memory;
    }
    return memory;
}

/* Each tag retains its own name until map teardown. */
static char *vr_menu_name(char const *format, long a, long b)
{
    char *name = vr_menu_allocate(64);
    if (name) snprintf(name, 64, format, a, b);
    return name;
}

static struct vr_menu_widget *vr_menu_widget_get(
	long tag_index)
{
	return tag_index != NONE ? tag_get(VR_MENU_WIDGET_TAG, tag_index) : NULL;
}

static void vr_menu_reference(
	struct tag_reference *reference,
	long tag_index)
{
	reference->group_tag = VR_MENU_WIDGET_TAG;
	reference->name = tag_index != NONE ? tag_get_name(tag_index) : "";
	reference->name_length = (long)strlen(reference->name);
	reference->index = tag_index;
}

/* a widget cloned from `template_index`, named, added as a tag of its own */
static long vr_menu_clone(
	long template_index,
	char *tag_name,
	char const *widget_name,
	struct vr_menu_widget **out_widget)
{
	struct vr_menu_widget *widget = tag_name ? vr_menu_allocate(sizeof(*widget)) : NULL;
	long tag_index;

	*out_widget = NULL;
	if (!widget)
		return NONE;
	memcpy(widget, vr_menu_widget_get(template_index), sizeof(*widget));
	memset(widget->name, 0, sizeof(widget->name));
	strncpy(widget->name, widget_name, sizeof(widget->name) - 1);
	tag_index = cache_file_add_tag(VR_MENU_WIDGET_TAG, (unsigned long)NONE, tag_name, widget);
	if (tag_index != NONE)
		*out_widget = widget;
	return tag_index;
}

static boolean vr_menu_handlers(
	struct vr_menu_widget *widget,
	struct vr_menu_event_handler const *handlers,
	long count)
{
	struct vr_menu_event_handler *copy = vr_menu_allocate(count * (long)sizeof(*copy));

	if (!copy)
		return FALSE;
	memcpy(copy, handlers, (size_t)count * sizeof(*copy));
	widget->event_handlers.count = count;
	widget->event_handlers.address = copy;
	return TRUE;
}

/* a button cloned from the pause menu's "RESUME GAME", its text from code */
static long vr_menu_button(
	long template_index,
	char *tag_name,
	char const *widget_name,
	struct vr_menu_event_handler const *handlers,
	long handler_count)
{
	struct vr_menu_widget *widget;
	struct vr_menu_game_data_input *input;
	long tag_index = vr_menu_clone(template_index, tag_name, widget_name, &widget);

	if (tag_index == NONE || !(input = vr_menu_allocate(sizeof(*input))) ||
		!vr_menu_handlers(widget, handlers, handler_count))
	{
		return NONE;
	}
	input->function = VR_MENU_GAME_DATA_FUNCTION;
	widget->game_data_inputs.count = 1;
	widget->game_data_inputs.address = input;
	widget->text_label_string_list.index = NONE;
	widget->text_label_string_list.name = "";
	widget->text_label_string_list.name_length = 0;
	return tag_index;
}

/* one handler, opening `widget_index` on A (NONE: the handler set later) */
static void vr_menu_open_handler(
	struct vr_menu_event_handler *handler,
	long widget_index)
{
	memset(handler, 0, sizeof(*handler));
	handler->flags = VR_MENU_OPEN_WIDGET;
	handler->event_type = VR_MENU_EVENT_A;
	vr_menu_reference(&handler->widget_tag, widget_index);
	vr_menu_reference(&handler->sound_effect, NONE);
}

/* a screen cloned from the pause menu: its backdrop and boxes, a list of
`buttons` (each `column_count` to a row of five down, the second column
`column_x` across), and the button hints at `hints_x`; B (or back) closes
it, start resumes the game */
static long vr_menu_screen(
	long pause_index,
	long list_index,
	char *screen_name,
	char *list_name,
	char const *widget_name,
	long const *buttons,
	long button_count,
	long left_count,
	short column_x,
	short hints_x)
{
	struct vr_menu_widget *pause = vr_menu_widget_get(pause_index);
	struct vr_menu_widget *pause_list = vr_menu_widget_get(list_index);
	struct vr_menu_widget *screen, *list;
	struct vr_menu_child *children;
	struct vr_menu_event_handler handlers[3];
	long list_tag_index, screen_tag_index, index;

	list_tag_index = vr_menu_clone(list_index, list_name, "vr settings list", &list);
	if (list_tag_index == NONE || !(children = vr_menu_allocate(button_count * (long)sizeof(*children))))
		return NONE;
	for (index = 0; index < button_count; index++)
	{
		boolean navigation = index == VR_MENU_SETTINGS_PER_SCREEN;
        long row = navigation ? 4 : (index < left_count ? index : index - left_count);

		memcpy(&children[index], (struct vr_menu_child *)pause_list->child_widgets.address, sizeof(children[index]));
		vr_menu_reference(&children[index].widget_tag, buttons[index]);
		snprintf(children[index].name, sizeof(children[index].name), "vr_button_%ld", index);
		children[index].vertical_offset = (short)(row * 28);
		children[index].horizontal_offset = navigation || index < left_count ? 0 : column_x;
	}
	if (button_count > left_count)
		list->bounds.x1 = (short)(list->bounds.x1 + column_x);
	list->bounds.y1 = MAX(list->bounds.y1, list->bounds.y0 + 5 * 28);
	list->child_widgets.count = button_count;
	list->child_widgets.address = children;

	screen_tag_index = vr_menu_clone(pause_index, screen_name, widget_name, &screen);
	if (screen_tag_index == NONE || !(children = vr_menu_allocate(3 * (long)sizeof(*children))))
		return NONE;
	memcpy(&children[0], (struct vr_menu_child *)pause->child_widgets.address + 0, sizeof(children[0]));
	memcpy(&children[1], (struct vr_menu_child *)pause->child_widgets.address + 1, sizeof(children[1]));
	memcpy(&children[2], (struct vr_menu_child *)pause->child_widgets.address + 4, sizeof(children[2]));
	vr_menu_reference(&children[1].widget_tag, list_tag_index);
	strcpy(children[1].name, "vr_settings_list");
	children[2].horizontal_offset = hints_x;
	screen->child_widgets.count = 3;
	screen->child_widgets.address = children;
	memset(handlers, 0, sizeof(handlers));
	handlers[0].flags = VR_MENU_CLOSE_CURRENT;
	handlers[0].event_type = VR_MENU_EVENT_B;
	handlers[1] = handlers[0];
	handlers[1].event_type = VR_MENU_EVENT_BACK;
	handlers[2].flags = VR_MENU_CLOSE_ALL;
	handlers[2].event_type = VR_MENU_EVENT_START;
	for (index = 0; index < 3; index++)
	{
		vr_menu_reference(&handlers[index].widget_tag, NONE);
		vr_menu_reference(&handlers[index].sound_effect, NONE);
	}
	if (!vr_menu_handlers(screen, handlers, 3))
		return NONE;
	return screen_tag_index;
}

/* Build back-to-front so each NEXT button references an existing screen.
 * The native widget stack makes B return to the preceding page, then the
 * categories. No looping links or unbounded history growth. */
static long vr_menu_paged(long pause, long list, long resume, long group,
    long const *buttons, long count, short column_x, short hints_x)
{
    long pages = VR_MENU_PAGES(count), next = NONE, sub;
    for (sub = pages - 1; sub >= 0; --sub) {
        long visible[VR_MENU_SETTINGS_PER_SCREEN + 1];
        long length = MIN(VR_MENU_SETTINGS_PER_SCREEN, count - sub * VR_MENU_SETTINGS_PER_SCREEN);
        struct vr_menu_event_handler handler;
        memcpy(visible, buttons + sub * VR_MENU_SETTINGS_PER_SCREEN, length * sizeof(long));
        if (next != NONE) {
            long slot = vr_menu.navigation_count;
            if (slot >= vr_menu.navigation_capacity) return NONE;
            vr_menu_open_handler(&handler, next);
            visible[length] = vr_menu_button(resume,
                vr_menu_name("ui\\shell\\solo_game\\pause_game\\vr_next_%ld_%ld", group, sub),
                "vr_next_page", &handler, 1);
            if (visible[length] == NONE) return NONE;
            vr_menu.navigation[slot].tag = visible[length++];
            vr_menu.navigation[slot].next = sub + 2;
            vr_menu.navigation[slot].total = pages;
            vr_menu.navigation_count++;
        }
        next = vr_menu_screen(pause, list,
            vr_menu_name("ui\\shell\\solo_game\\pause_game\\vr_page_%ld_%ld", group, sub),
            vr_menu_name("ui\\shell\\solo_game\\pause_game\\vr_list_%ld_%ld", group, sub),
            "vr_settings_page", visible, length, 4, column_x, hints_x);
        if (next == NONE) return NONE;
    }
    return next;
}

void vr_menu_tags_loaded(
	void)
{
	/* the button hints, centred under the mission objectives (from under the
	list); the right column of settings above them, as wide as the list's
	buttons (the list is 72 from the screen's left) */
	static short const hints_x = 328, right_column_x = 328 - 72;
	long pause_index = tag_loaded(VR_MENU_WIDGET_TAG, "ui\\shell\\solo_game\\pause_game\\pause_game");
	long list_index = tag_loaded(VR_MENU_WIDGET_TAG, "ui\\shell\\solo_game\\pause_game\\pause_list");
	long resume_index = tag_loaded(VR_MENU_WIDGET_TAG, "ui\\shell\\solo_game\\pause_game\\resume_game_button");
	struct vr_menu_widget *pause, *pause_list;
	struct vr_menu_child *children;
	struct vr_menu_event_handler handlers[3];
	long page, index;

	/* (the last map's) */
	for (index = 0; index < vr_menu.allocation_count; index++)
		free(vr_menu.allocations[index]);
    if (vr_menu.allocations) free(vr_menu.allocations);
    memset(&vr_menu, 0, sizeof(vr_menu));
    vr_menu.navigation_capacity = VR_MENU_PAGES(VR_MENU_PAGE_COUNT);
    for (page = 0; page < VR_MENU_PAGE_COUNT; page++)
        vr_menu.navigation_capacity += VR_MENU_PAGES(vr_menu_pages[page].count);
    vr_menu.navigation = vr_menu_allocate(vr_menu.navigation_capacity * sizeof(*vr_menu.navigation));
    if (!vr_menu.navigation) return;
	vr_menu.button_tag_index = vr_menu.categories_tag_index = NONE;
	for (page = 0; page < VR_MENU_PAGE_COUNT; page++)
	{
		vr_menu.category_tag_indices[page] = vr_menu.page_tag_indices[page] = NONE;
		vr_menu.setting_tag_indices[page] = vr_menu_allocate(vr_menu_pages[page].count * sizeof(long));
		if (!vr_menu.setting_tag_indices[page]) return;
		for (index = 0; index < vr_menu_pages[page].count; index++)
			vr_menu.setting_tag_indices[page][index] = NONE;
	}
	if (pause_index == NONE || list_index == NONE || resume_index == NONE)
		return;
	pause = vr_menu_widget_get(pause_index);
	pause_list = vr_menu_widget_get(list_index);
	/* the pause menu as this expects it: its backdrop's boxes, its list
	(four buttons, 28 apart), the mission objectives and the button hints */
	if (pause->child_widgets.count != 5 || pause_list->child_widgets.count != 4)
	{
		platform_log("vr: the pause menu is not as expected; no VR settings in it");
		return;
	}

	/* each setting: A or right steps on, left back */
	memset(handlers, 0, sizeof(handlers));
	handlers[0].flags = VR_MENU_RUN_FUNCTION;
	handlers[0].event_type = VR_MENU_EVENT_A;
	handlers[0].function = VR_MENU_NEXT_FUNCTION;
	handlers[1] = handlers[0];
	handlers[1].event_type = VR_MENU_EVENT_DPAD_RIGHT;
	handlers[2] = handlers[0];
	handlers[2].event_type = VR_MENU_EVENT_DPAD_LEFT;
	handlers[2].function = VR_MENU_PREVIOUS_FUNCTION;
	for (index = 0; index < 3; index++)
	{
		vr_menu_reference(&handlers[index].widget_tag, NONE);
		vr_menu_reference(&handlers[index].sound_effect, NONE);
	}

	/* each page: its settings' buttons and its screen */
	for (page = 0; page < VR_MENU_PAGE_COUNT; page++)
	{
		struct vr_menu_page const *definition = &vr_menu_pages[page];

		for (index = 0; index < definition->count; index++)
		{
			char widget_name[32];

			snprintf(widget_name, sizeof(widget_name), "vr_setting_%ld_%ld", page, index);
			vr_menu.setting_tag_indices[page][index] = vr_menu_button(resume_index,
				vr_menu_name("ui\\shell\\solo_game\\pause_game\\vr_setting_%ld_%ld", page, index),
				widget_name, handlers, 3);
			if (vr_menu.setting_tag_indices[page][index] == NONE)
				return;
		}
		vr_menu.page_tag_indices[page] = vr_menu_paged(pause_index, list_index, resume_index,
            page, vr_menu.setting_tag_indices[page], definition->count, right_column_x, hints_x);
		if (vr_menu.page_tag_indices[page] == NONE)
			return;
	}

	/* the categories, each opening its page, in one column */
	for (page = 0; page < VR_MENU_PAGE_COUNT; page++)
	{
		vr_menu_open_handler(&handlers[0], vr_menu.page_tag_indices[page]);
		vr_menu.category_tag_indices[page] = vr_menu_button(resume_index,
			vr_menu_name("ui\\shell\\solo_game\\pause_game\\vr_category_%ld", page, 0),
			"vr_category_button", handlers, 1);
		if (vr_menu.category_tag_indices[page] == NONE)
			return;
	}
	vr_menu.categories_tag_index = vr_menu_paged(pause_index, list_index, resume_index,
        VR_MENU_PAGE_COUNT, vr_menu.category_tag_indices, VR_MENU_PAGE_COUNT, right_column_x, hints_x);
	if (vr_menu.categories_tag_index == NONE)
		return;

	/* the pause menu's new item, opening the categories */
	vr_menu_open_handler(&handlers[0], vr_menu.categories_tag_index);
	vr_menu.button_tag_index = vr_menu_button(resume_index,
		vr_menu_name("ui\\shell\\solo_game\\pause_game\\vr_settings_button", 0, 0),
		"vr_settings_button", handlers, 1);
	if (vr_menu.button_tag_index == NONE || !(children = vr_menu_allocate(5 * (long)sizeof(*children))))
		return;
	/* (the map's own tags changed last, when nothing can fail) */
	memcpy(children, pause_list->child_widgets.address, 4 * sizeof(*children));
	children[4] = children[3];
	vr_menu_reference(&children[4].widget_tag, vr_menu.button_tag_index);
	strcpy(children[4].name, "vr_settings_button");
	children[4].vertical_offset = (short)(children[3].vertical_offset + 28);
	pause_list->child_widgets.count = 5;
	pause_list->child_widgets.address = children;
	((struct vr_menu_child *)pause->child_widgets.address)[4].horizontal_offset = hints_x;
	platform_log("vr: VR settings added: %ld categories, %ld pages, four rows per column; paged capacity", VR_MENU_PAGE_COUNT, vr_menu.navigation_capacity);
}

/* ---------- the widgets' callbacks */

enum
{
	_vr_menu_none,
	_vr_menu_pause_item,
	_vr_menu_category,
    _vr_menu_navigation,
	_vr_menu_setting,
};

/* what the widget's definition is: the pause menu's item, a category
(its page in *page) or a setting (its page and index) */
static int vr_menu_widget_kind(
	long definition_tag_index,
	long *page,
	long *setting)
{
	long index;

	if (definition_tag_index == NONE)
		return _vr_menu_none;
	if (definition_tag_index == vr_menu.button_tag_index)
        return _vr_menu_pause_item;
    for (index = 0; index < vr_menu.navigation_count; index++)
        if (vr_menu.navigation[index].tag == definition_tag_index) {
            *setting = index;
            return _vr_menu_navigation;
        }
	for (*page = 0; *page < VR_MENU_PAGE_COUNT; (*page)++)
	{
		if (vr_menu.category_tag_indices[*page] == definition_tag_index)
			return _vr_menu_category;
		for (index = 0; vr_menu.setting_tag_indices[*page] && index < vr_menu_pages[*page].count; index++)
		{
			if (vr_menu.setting_tag_indices[*page][index] == definition_tag_index)
			{
				*setting = index;
				return _vr_menu_setting;
			}
		}
	}
	return _vr_menu_none;
}

boolean vr_menu_is_setting(long definition_tag_index)
{
	long page = NONE, setting = NONE;
	return vr_menu_widget_kind(definition_tag_index, &page, &setting) == _vr_menu_setting;
}

boolean vr_menu_setting_text(
	long definition_tag_index,
	wchar_t *text,
	long size)
{
	long page = NONE, setting_index = NONE;
	int kind = vr_menu_widget_kind(definition_tag_index, &page, &setting_index);
	char line[64];
	long index;

	if (kind == _vr_menu_none || size <= 0)
		return FALSE;
	if (kind == _vr_menu_pause_item)
	{
		snprintf(line, sizeof(line), "VR SETTINGS");
	}
	else if (kind == _vr_menu_navigation)
    {
        snprintf(line, sizeof(line), "NEXT PAGE (%ld/%ld)",
            vr_menu.navigation[setting_index].next, vr_menu.navigation[setting_index].total);
    }
    else if (kind == _vr_menu_category)
	{
		snprintf(line, sizeof(line), "%s", vr_menu_pages[page].label);
	}
	else
	{
		struct vr_menu_setting const *setting = &vr_menu_pages[page].settings[setting_index];
		long value_index = vr_menu_value_index(setting);

        if(setting->type == _vr_setting_degrees || setting->type == _vr_setting_centimetres || setting->type == _vr_setting_vehicle_centimetres) {
            double value=config_real(setting->key); if(!isfinite(value)) value=0;
            snprintf(line,sizeof(line),"%s: < %.0f %s >",setting->label,
                setting->type!=_vr_setting_degrees?value*100:value,
                setting->type!=_vr_setting_degrees?"CM":"DEG");
        } else if((setting->type == _vr_setting_reset_alignment || setting->type == _vr_setting_flip_alignment))
            snprintf(line,sizeof(line),"%s: APPLY",setting->label);
        else
		snprintf(line, sizeof(line), setting->type == _vr_setting_real ? "%s: < %s >" : "%s: %s", setting->label,
			value_index != NONE ? setting->values[value_index].label : "CUSTOM");
	}
	for (index = 0; line[index] && index < size - 1; index++)
		text[index] = (wchar_t)(unsigned char)line[index];
	text[index] = 0;
	return TRUE;
}

boolean vr_menu_setting_change(
	long definition_tag_index,
	long step)
{
	long page = NONE, setting_index = NONE;
	struct vr_menu_setting const *setting;
	long value_index;
	char const *value;
	boolean written = FALSE;

	if (vr_menu_widget_kind(definition_tag_index, &page, &setting_index) != _vr_menu_setting)
		return FALSE;
	setting = &vr_menu_pages[page].settings[setting_index];
    if(setting->type == _vr_setting_degrees || setting->type == _vr_setting_centimetres || setting->type == _vr_setting_vehicle_centimetres) {
        double value=config_real(setting->key), unit=setting->type==_vr_setting_degrees?5.0:0.01;
        double limit=setting->type==_vr_setting_degrees?180.0:setting->type==_vr_setting_vehicle_centimetres?0.50:0.20;
        if(!isfinite(value)) value=0.0;
        value=step>0?(floor(value/unit+0.00001)+1)*unit:(ceil(value/unit-0.00001)-1)*unit;
        value=fmax(-limit,fmin(limit,value)); written=config_write_real(setting->key,value);
        vr_reload_settings(); platform_log("vr: %s %.3f%s",setting->key,value,written?"":" (save failed)");
        return TRUE;
    }
    if(setting->type == _vr_setting_flip_alignment) {
        double roll=config_real(setting->key);
        if(!isfinite(roll)) roll=0.0;
        roll=roll>0.0?roll-180.0:roll+180.0;
        roll=fmax(-180.0,fmin(180.0,roll));
        written=config_write_real(setting->key,roll); vr_reload_settings();
        platform_log("vr: %s flipped to %.1f%s",setting->key,roll,written?"":" (save failed)"); return TRUE;
    }
    if(setting->type == _vr_setting_reset_alignment) {
        const char *axes[]={"pitch","yaw","roll","right","up","back"}; char key[64]; int a;
        written=TRUE;
        for(a=0;a<6;a++) { snprintf(key,sizeof(key),"vr.align_%s_%s",setting->key,axes[a]);
            written=config_write_real(key,0.0)&&written; }
        snprintf(key,sizeof(key),"vr.align_%s_grip_aim",setting->key);
        written=config_write_boolean(key,FALSE)&&written; vr_reload_settings();
        platform_log("vr: reset %s controller calibration%s",setting->key,written?"":" (save failed)"); return TRUE;
    }
	value_index = vr_menu_value_index(setting);
	if (setting->type == _vr_setting_real)
	{
		/* Move in the requested direction even from a custom numeric value;
         * nearest-then-step skipped valid thresholds (e.g. 0.34 -> 0.40). */
        double current = config_real(setting->key);
        long i;
        if (step > 0) {
            value_index = setting->value_count - 1;
            for (i = 0; i < setting->value_count; i++)
                if (atof(setting->values[i].value) > current + 0.00001) { value_index = i; break; }
        } else {
            value_index = 0;
            for (i = setting->value_count - 1; i >= 0; i--)
                if (atof(setting->values[i].value) < current - 0.00001) { value_index = i; break; }
        }
	}
	else
		value_index = value_index == NONE ? 0 : (value_index + step + setting->value_count) % setting->value_count;
	value = setting->values[value_index].value;
	switch (setting->type)
	{
	case _vr_setting_boolean:
		written = config_write_boolean(setting->key, !strcmp(value, "true"));
		break;
	case _vr_setting_real:
	case _vr_setting_real_choice:
		written = config_write_real(setting->key, atof(value));
		break;
	case _vr_setting_string:
		written = config_write_string(setting->key, value);
		/* Older configs may have disabled the old 3D screen toggle. Selecting
		the new 3D SCREEN mode explicitly enables that screen. */
		if (!strcmp(setting->key, "vr.cutscenes") && !strcmp(value, "screen"))
			written = config_write_boolean("vr.cinema_3d", TRUE) && written;
		break;
	}
	vr_reload_settings();
	platform_log("vr: %s set to %s%s", setting->key, value, written ? "" : " (not saved to config.toml)");
	return TRUE;
}

#endif
