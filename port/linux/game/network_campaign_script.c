/* Reliable, ordered campaign presentation. The host runs mission scripts;
 * clients replay only explicitly permitted visual/control effects. */
#include "cseries.h"
#include "game/game.h"
#include "hs/hs.h"
#include "networking/network_game_globals.h"
#include "network_distributed.h"
#include "network_campaign.h"
#include <string.h>

void platform_log(char const *format, ...);
extern long const hs_function_table_count;

/* Wire IDs are positions in this list; append only within a protocol version.
 * Stateful loading/BSP/checkpoint operations belong to the lifecycle protocol,
 * never this presentation stream. */
static char const *presentation_names[] = {
	"camera_control", "camera_set", "player_enable_input", "player_camera_control",
	"fade_in", "fade_out", "cinematic_start", "cinematic_stop",
	"cinematic_show_letterbox", "cinematic_set_title", "cinematic_set_title_delayed",
	"show_hud", "show_hud_help_text", "enable_hud_help_flash", "hud_help_flash_restart",
	"hud_show_health", "hud_blink_health", "hud_show_shield", "hud_blink_shield",
	"hud_show_motion_sensor", "hud_blink_motion_sensor", "hud_show_crosshair",
	"hud_clear_messages", "hud_set_help_text", "hud_set_objective_text",
	"hud_set_timer_time", "hud_set_timer_warning_time", "hud_set_timer_position", "show_hud_timer",
	"numeric_countdown_timer_set", "numeric_countdown_timer_stop", "numeric_countdown_timer_restart",
	"player_effect_set_max_translation", "player_effect_set_max_rotation", "player_effect_set_max_rumble",
	"player_effect_start", "player_effect_stop",
	"cinematic_screen_effect_start", "cinematic_screen_effect_set_convolution",
	"cinematic_screen_effect_set_filter", "cinematic_screen_effect_set_filter_desaturation_tint",
	"cinematic_screen_effect_set_video", "cinematic_screen_effect_stop", "pause_hud_timer",
	"sound_impulse_start", "sound_impulse_stop", "sound_looping_start", "sound_looping_stop",
	"sound_looping_set_scale", "sound_looping_set_alternate", "sound_class_set_gain",
	"camera_set_animation", "camera_set_relative", "camera_set_first_person", "camera_set_dead",
	"custom_animation", "unit_custom_animation_at_frame", "unit_stop_custom_animation",
	"activate_nav_point_flag", "activate_nav_point_object", "activate_team_nav_point_flag",
	"activate_team_nav_point_object", "deactivate_nav_point_flag", "deactivate_nav_point_object",
	"deactivate_team_nav_point_flag", "deactivate_team_nav_point_object",
	"cinematic_set_near_clip_distance", "effect_new", "effect_new_on_object_marker",
	"ai_allegiance", "ai_allegiance_remove", "unit_set_emotion", "unit_set_emotion_animation",
	"unit_suspended", "unit_set_enterable_by_player", "object_set_collideable",
	"cinematic_suppress_bsp_object_creation"
};

struct campaign_presentation
{
	long round;
	unsigned long seed;
	word opcode, count;
	long arguments[8];
	/* Strings are offsets into this bounded buffer, never remote pointers. */
	char strings[256];
};
typedef char campaign_presentation_size_assert[sizeof(struct campaign_presentation) == 300 ? 1 : -1];

static struct campaign_presentation pending[256];
static short pending_count;
static short functions[NUMBEROF(presentation_names)];
static boolean initialized, overflowed;

static void presentation_initialize(void)
{
	short index, function;
	if (initialized) return;
	initialized = TRUE;
	for (index = 0; index < NUMBEROF(presentation_names); index++)
	{
		functions[index] = NONE;
		for (function = 0; function < hs_function_table_count; function++)
			if (!strcmp(hs_function_get(function)->name, presentation_names[index]))
				functions[index] = function;
		if (functions[index] == NONE)
			platform_log("campaign: missing presentation function %s", presentation_names[index]);
	}
}

void network_campaign_script_reset(void)
{
	pending_count = 0;
	overflowed = FALSE;
}

word network_campaign_script_entry_size(void) { return sizeof(struct campaign_presentation); }

static void presentation_capture(short function_index, long const *arguments)
{
	short index, argument, used = 0;
	struct hs_function_definition *function;
	struct campaign_presentation *entry;
	if (game_connection() != _game_connection_network_server || !network_campaign_active() ||
		!network_campaign_playing()) return;
	presentation_initialize();
	for (index = 0; index < NUMBEROF(functions) && functions[index] != function_index; index++) {}
	if (index == NUMBEROF(functions)) return;
	function = hs_function_get(function_index);
	if (function->parameter_count > 8 || !hs_campaign_call_valid(function_index, arguments))
	{
		platform_log("campaign: rejected presentation arguments for %s", function->name);
		return;
	}
	if (pending_count == NUMBEROF(pending))
	{
		if (!overflowed) platform_log("campaign: presentation queue overflow; ending unsynchronized session");
		overflowed = TRUE;
		network_game_abort();
		return;
	}
	entry = &pending[pending_count++];
	memset(entry, 0, sizeof(*entry));
	entry->round = network_game_get_number_of_games_played();
	entry->seed = network_game_get_random_seed();
	entry->opcode = index;
	entry->count = function->parameter_count;
	if (entry->count) memcpy(entry->arguments, arguments, entry->count * sizeof(long));
	for (argument = 0; argument < entry->count; argument++)
	{
		if (function->parameter_types[argument] == _hs_type_string)
		{
			char const *value = (char const *)arguments[argument];
			short length = 0;
			while (length < sizeof(entry->strings) - used && value[length]) length++;
			if (length == sizeof(entry->strings) - used)
			{
				pending_count--;
				platform_log("campaign: presentation string too long for %s", function->name);
				return;
			}
			memcpy(entry->strings + used, value, length + 1);
			entry->arguments[argument] = used;
			used += length + 1;
		}
	}
}

void network_campaign_script_capture(short function_index, long const *arguments)
{
	if (!network_campaign_playing() || game_connection() != _game_connection_network_server) return;
	/* This function is also called directly by AI conversations. Capture at its
	 * native entry so a script call is not sent twice. */
	if (!strcmp(hs_function_get(function_index)->name, "sound_impulse_start")) return;
	presentation_capture(function_index, arguments);
}

void network_campaign_script_capture_named(char const *name, long const *arguments)
{
	short index;
	if (!network_campaign_playing() || game_connection() != _game_connection_network_server) return;
	presentation_initialize();
	for (index = 0; index < NUMBEROF(functions); index++)
		if (!strcmp(name, presentation_names[index]) && functions[index] != NONE)
		{
			presentation_capture(functions[index], arguments);
			return;
		}
}

void network_campaign_script_flush(void)
{
	short offset = 0;
	struct {
		struct distributed_message_header header;
		struct campaign_presentation entries[RELIABLE_ENTRIES(struct campaign_presentation)];
	} message;
	if (!network_campaign_active()) { pending_count = 0; return; }
	while (offset < pending_count)
	{
		short count = MIN(pending_count - offset, NUMBEROF(message.entries));
		memcpy(message.entries, pending + offset, count * sizeof(pending[0]));
		distributed_send(&message, _distributed_message_campaign_presentation, count,
			sizeof(message.header) + count * sizeof(pending[0]), _distributed_to_clients_reliably);
		offset += count;
	}
	pending_count = 0;
}

void network_campaign_script_receive(void const *entries, short count)
{
	short index;
	if (!network_campaign_client()) return;
	presentation_initialize();
	for (index = 0; index < count; index++)
	{
		struct campaign_presentation entry;
		short function, argument;
		boolean valid = TRUE;
		memcpy(&entry, (byte const *)entries + index * sizeof(entry), sizeof(entry));
		if (entry.round != network_game_get_number_of_games_played() ||
			entry.seed != (unsigned long)network_game_get_random_seed() ||
			entry.opcode >= NUMBEROF(functions)) continue;
		function = functions[entry.opcode];
		if (function == NONE || entry.count > 8 || entry.count != hs_function_get(function)->parameter_count) continue;
		for (argument = 0; argument < entry.count; argument++)
			if (hs_function_get(function)->parameter_types[argument] == _hs_type_string)
			{
				long offset = entry.arguments[argument];
				if (offset < 0 || offset >= sizeof(entry.strings) ||
					!memchr(entry.strings + offset, 0, sizeof(entry.strings) - offset))
				{ valid = FALSE; break; }
				entry.arguments[argument] = (long)(entry.strings + offset);
			}
		if (!valid || !hs_campaign_call_valid(function, entry.arguments)) continue;
		hs_campaign_replay(function, entry.arguments);
	}
}
