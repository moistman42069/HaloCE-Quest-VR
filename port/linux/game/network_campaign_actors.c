/* Host actor controls drive the client's native animation/fire presentation.
 * Actor decisions, encounters, hits and mission scripts remain host-owned. */
#include "cseries.h"
#include "game/game.h"
#include "units/units.h"
#include "units/unit_control_data.h"
#include "networking/network_game_globals.h"
#include "network_campaign.h"
#include "network_distributed.h"
#include <string.h>

struct campaign_actor_control
{
	long round;
	unsigned long seed;
	long object_index;
	struct unit_control_data control;
};
typedef char campaign_actor_control_size_assert[sizeof(struct campaign_actor_control) == 76 ? 1 : -1];
static struct campaign_actor_control controls[MAXIMUM_TRACKED_OBJECTS];
static boolean captured[MAXIMUM_TRACKED_OBJECTS];

word network_campaign_actors_size(void) { return sizeof(struct campaign_actor_control); }
void network_campaign_actors_reset(void) { memset(captured, 0, sizeof(captured)); }

void network_campaign_actor_capture(long object_index, struct unit_control_data const *control)
{
	long slot = DATUM_INDEX_TO_ABSOLUTE_INDEX(object_index);
	struct unit_datum *unit;
	struct campaign_actor_control *entry;
	if (!network_campaign_playing() || game_connection() != _game_connection_network_server ||
		slot < 0 || slot >= MAXIMUM_TRACKED_OBJECTS || !(unit = unit_try_and_get(object_index)) ||
		unit->unit.player_index != NONE) return;
	entry = &controls[slot];
	memset(entry, 0, sizeof(*entry));
	entry->round = network_game_get_number_of_games_played();
	entry->seed = network_game_get_random_seed();
	entry->object_index = object_index;
	entry->control = *control;
	entry->control.pad = 0;
	captured[slot] = TRUE;
}

void network_campaign_actors_tick(void)
{
	struct { struct distributed_message_header header;
		struct campaign_actor_control entries[DATAGRAM_ENTRIES(struct campaign_actor_control)]; } message;
	long slot;
	short count = 0;
	if (!network_campaign_playing() || game_connection() != _game_connection_network_server) return;
	for (slot = 0; slot < MAXIMUM_TRACKED_OBJECTS; slot++)
	{
		struct unit_datum *unit;
		if (!captured[slot]) continue;
		captured[slot] = FALSE;
		unit = unit_try_and_get(controls[slot].object_index);
		if (!unit || unit->unit.player_index != NONE) continue;
		message.entries[count++] = controls[slot];
		if (count == NUMBEROF(message.entries))
		{
			distributed_send(&message, _distributed_message_campaign_actors, count,
				sizeof(message.header) + count * sizeof(message.entries[0]), _distributed_to_clients);
			count = 0;
		}
	}
	if (count) distributed_send(&message, _distributed_message_campaign_actors, count,
		sizeof(message.header) + count * sizeof(message.entries[0]), _distributed_to_clients);
}

static boolean normal_valid(real_vector3d const *v)
{
	real squared = v->i * v->i + v->j * v->j + v->k * v->k;
	return squared >= 0.99f && squared <= 1.01f;
}

void network_campaign_actors_receive(void const *entries, short count)
{
	short index;
	if (!network_campaign_client()) return;
	for (index = 0; index < count; index++)
	{
		struct campaign_actor_control entry;
		struct unit_control_data *control = &entry.control;
		struct unit_datum *unit;
		real squared;
		memcpy(&entry, (byte const *)entries + index * sizeof(entry), sizeof(entry));
		if (entry.round != network_game_get_number_of_games_played() ||
			entry.seed != (unsigned long)network_game_get_random_seed() ||
			!distributed_object_index_valid(entry.object_index) || !network_objects_client_has(entry.object_index) ||
			!(unit = unit_try_and_get(entry.object_index)) || unit->unit.player_index != NONE) continue;
		squared = control->throttle.i * control->throttle.i + control->throttle.j * control->throttle.j + control->throttle.k * control->throttle.k;
		if (!(squared >= 0.f && squared <= 9.f) || !VALID_INDEX(control->animation_state, NUMBER_OF_UNIT_ANIMATION_STATES) ||
			!VALID_INDEX(control->aiming_speed, NUMBER_OF_UNIT_AIMING_SPEEDS) || !VALID_FLAGS(control->control_flags, NUMBER_OF_UNIT_CONTROL_FLAGS) ||
			(control->weapon_index != NONE && !VALID_INDEX(control->weapon_index, MAXIMUM_WEAPONS_PER_UNIT)) ||
			(control->grenade_index != NONE && !VALID_INDEX(control->grenade_index, NUMBER_OF_UNIT_GRENADE_TYPES)) ||
			control->zoom_level < NONE || control->zoom_level > 2 || !(control->primary_trigger >= 0.f && control->primary_trigger <= 1.f) ||
			!normal_valid(&control->facing_vector) || !normal_valid(&control->aiming_vector) || !normal_valid(&control->looking_vector)) continue;
		unit_control(entry.object_index, control);
	}
}
