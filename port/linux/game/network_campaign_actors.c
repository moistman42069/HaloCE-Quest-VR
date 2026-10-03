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

void platform_log(char const *format, ...);

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
/* A client has no local actor datum. Keep a bounded lease on the host's
 * controls so unit_update does not erase them as an uncontrolled unit. */
static boolean received[MAXIMUM_TRACKED_OBJECTS];
static boolean seen[MAXIMUM_TRACKED_OBJECTS];
static long received_tick[MAXIMUM_TRACKED_OBJECTS];
static unsigned long received_count, expired_count;
static long diagnostics_tick;
struct campaign_actor_impulse
{
	long round;
	unsigned long seed;
	long object_index;
	short impulse;
	word aligned;
	real_vector2d alignment;
};
typedef char campaign_actor_impulse_size_assert[sizeof(struct campaign_actor_impulse) == 24 ? 1 : -1];
static struct campaign_actor_impulse impulses[256];
static short impulse_count;
static boolean impulse_overflowed;

word network_campaign_actor_impulses_size(void) { return sizeof(struct campaign_actor_impulse); }
void network_campaign_actor_impulses_reset(void) { impulse_count = 0; impulse_overflowed = FALSE; }

void network_campaign_actor_impulse_capture(long object_index, short impulse, real_vector2d const *alignment)
{
	struct unit_datum *unit;
	struct campaign_actor_impulse *entry;
	if (!network_campaign_playing() || game_connection() != _game_connection_network_server ||
		!(unit = unit_try_and_get(object_index)) || unit->unit.player_index != NONE ||
		!unit_animation_impulse_valid(impulse)) return;
	if (impulse_count == NUMBEROF(impulses))
	{
		if (!impulse_overflowed)
			platform_log("campaign: NPC animation event queue full; dropping excess visual events this tick");
		impulse_overflowed = TRUE;
		return;
	}
	entry = &impulses[impulse_count++];
	memset(entry, 0, sizeof(*entry));
	entry->round = network_game_get_number_of_games_played();
	entry->seed = network_game_get_random_seed();
	entry->object_index = object_index;
	entry->impulse = impulse;
	entry->aligned = alignment != NULL;
	if (alignment) entry->alignment = *alignment;
}

static void flush_impulses(void)
{
	struct { struct distributed_message_header header;
		struct campaign_actor_impulse entries[RELIABLE_ENTRIES(struct campaign_actor_impulse)]; } message;
	short offset = 0;
	while (offset < impulse_count)
	{
		short count = MIN(impulse_count - offset, NUMBEROF(message.entries));
		memcpy(message.entries, impulses + offset, count * sizeof(impulses[0]));
		distributed_send(&message, _distributed_message_campaign_actor_impulses, count,
			sizeof(message.header) + count * sizeof(impulses[0]), _distributed_to_clients_reliably);
		offset += count;
	}
	network_campaign_actor_impulses_reset();
}

void network_campaign_actor_impulses_receive(void const *entries, short count)
{
	short index;
	if (!network_campaign_client()) return;
	for (index = 0; index < count; index++)
	{
		struct campaign_actor_impulse entry;
		struct unit_datum *unit;
		real length;
		memcpy(&entry, (byte const *)entries + index * sizeof(entry), sizeof(entry));
		length = entry.alignment.i * entry.alignment.i + entry.alignment.j * entry.alignment.j;
		if (entry.round != network_game_get_number_of_games_played() ||
			entry.seed != (unsigned long)network_game_get_random_seed() ||
			!distributed_object_index_valid(entry.object_index) || !network_objects_client_has(entry.object_index) ||
			!(unit = unit_try_and_get(entry.object_index)) || unit->unit.player_index != NONE ||
			TEST_FLAG(unit->object.damage_flags, _object_dead_bit) || !unit_animation_impulse_valid(entry.impulse) ||
			entry.aligned > 1 || (entry.aligned && !(length >= 0.99f && length <= 1.01f))) continue;
		unit_start_animation_impulse(entry.object_index, entry.impulse, entry.aligned ? &entry.alignment : NULL);
	}
}

static void release_control(long slot)
{
	struct unit_datum *unit = unit_try_and_get(controls[slot].object_index);
	if (unit && unit->unit.player_index == NONE && unit->unit.actor_index == NONE &&
		unit->unit.swarm_actor_index == NONE &&
		!TEST_FLAG(unit->unit.flags, _unit_possessed_by_recording_bit))
	{
		unit_set_actively_controlled(controls[slot].object_index, FALSE);
		unit->unit.throttle = *global_zero_vector3d;
		unit->unit.control_flags = 0;
		unit->unit.primary_trigger = 0.f;
	}
	received[slot] = FALSE;
}

word network_campaign_actors_size(void) { return sizeof(struct campaign_actor_control); }
void network_campaign_actors_reset(void)
{
	long slot;
	for (slot = 0; slot < MAXIMUM_TRACKED_OBJECTS; slot++)
		if (seen[slot]) release_control(slot);
	memset(seen, 0, sizeof(seen));
	memset(captured, 0, sizeof(captured));
	received_count = expired_count = 0;
	diagnostics_tick = 0;
}

void network_campaign_actor_update(long object_index)
{
	long slot = DATUM_INDEX_TO_ABSOLUTE_INDEX(object_index);
	long now, age;
	struct unit_datum *unit;
	if (slot < 0 || slot >= MAXIMUM_TRACKED_OBJECTS || !received[slot] ||
		controls[slot].object_index != object_index) return;
	now = game_time_get();
	age = now - received_tick[slot];
	unit = unit_try_and_get(object_index);
	if (!network_campaign_client() || !network_objects_client_has(object_index) ||
		!unit || unit->unit.player_index != NONE ||
		TEST_FLAG(unit->object.damage_flags, _object_dead_bit) ||
		age < 0 || age > 2 * TICKS_PER_SECOND)
	{
		release_control(slot);
		expired_count++;
	}
	if (now >= diagnostics_tick)
	{
		platform_log("campaign actors: host controls received=%lu expired=%lu (client ownership fix test14)",
			received_count, expired_count);
		diagnostics_tick = now + 10 * TICKS_PER_SECOND;
	}
}

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
	flush_impulses();
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
		long slot;
		real squared;
		memcpy(&entry, (byte const *)entries + index * sizeof(entry), sizeof(entry));
		if (entry.round != network_game_get_number_of_games_played() ||
			entry.seed != (unsigned long)network_game_get_random_seed() ||
			!distributed_object_index_valid(entry.object_index) || !network_objects_client_has(entry.object_index) ||
			!(unit = unit_try_and_get(entry.object_index)) || unit->unit.player_index != NONE ||
			TEST_FLAG(unit->object.damage_flags, _object_dead_bit)) continue;
		squared = control->throttle.i * control->throttle.i + control->throttle.j * control->throttle.j + control->throttle.k * control->throttle.k;
		if (!(squared >= 0.f && squared <= 9.f) || !VALID_INDEX(control->animation_state, NUMBER_OF_UNIT_ANIMATION_STATES) ||
			!VALID_INDEX(control->aiming_speed, NUMBER_OF_UNIT_AIMING_SPEEDS) || !VALID_FLAGS(control->control_flags, NUMBER_OF_UNIT_CONTROL_FLAGS) ||
			(control->weapon_index != NONE && !VALID_INDEX(control->weapon_index, MAXIMUM_WEAPONS_PER_UNIT)) ||
			(control->grenade_index != NONE && !VALID_INDEX(control->grenade_index, NUMBER_OF_UNIT_GRENADE_TYPES)) ||
			control->zoom_level < NONE || control->zoom_level > 2 || !(control->primary_trigger >= 0.f && control->primary_trigger <= 1.f) ||
			!normal_valid(&control->facing_vector) || !normal_valid(&control->aiming_vector) || !normal_valid(&control->looking_vector)) continue;
		slot = DATUM_INDEX_TO_ABSOLUTE_INDEX(entry.object_index);
		controls[slot] = entry;
		received[slot] = TRUE;
		seen[slot] = TRUE;
		received_tick[slot] = game_time_get();
		received_count++;
		if (!TEST_FLAG(unit->unit.flags, _unit_actively_controlled_bit))
			unit_set_actively_controlled(entry.object_index, TRUE);
		unit_control(entry.object_index, control);
	}
}
