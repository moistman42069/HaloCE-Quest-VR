/* Doors, elevators, switches and other devices follow the campaign host.
 * Object creation/deletion precedes these reliable state records. */
#include "cseries.h"
#include "game/game.h"
#include "objects/objects.h"
#include "networking/network_game_globals.h"
#include "network_campaign.h"
#include "network_distributed.h"
#include <string.h>

typedef char campaign_device_size_assert[sizeof(struct campaign_device_state) == 52 ? 1 : -1];
static struct campaign_device_state last[MAXIMUM_TRACKED_OBJECTS];
static boolean valid[MAXIMUM_TRACKED_OBJECTS];
static boolean force_refresh;

void network_campaign_devices_reset(void) { memset(valid, 0, sizeof(valid)); force_refresh = TRUE; }

void network_campaign_devices_tick(void)
{
	struct object_iterator iterator;
	struct {
		struct distributed_message_header header;
		struct campaign_device_state entries[RELIABLE_ENTRIES(struct campaign_device_state)];
	} message;
	short count = 0;
	boolean refresh;
	if (game_connection() != _game_connection_network_server || !network_campaign_playing() ||
		(!force_refresh && game_time_get() % 3)) return;
	refresh = force_refresh || game_time_get() % (3 * TICKS_PER_SECOND) == 0;
	force_refresh = FALSE;
	object_iterator_new(&iterator, _object_mask_device, 0);
	while (object_iterator_next(&iterator))
	{
		struct campaign_device_state state;
		long slot = DATUM_INDEX_TO_ABSOLUTE_INDEX(iterator.index);
		if (slot < 0 || slot >= MAXIMUM_TRACKED_OBJECTS || !device_campaign_read(iterator.index, &state)) continue;
		state.round = network_game_get_number_of_games_played();
		state.seed = network_game_get_random_seed();
		if (!refresh && valid[slot] && !memcmp(&state, &last[slot], sizeof(state))) continue;
		last[slot] = state;
		valid[slot] = TRUE;
		message.entries[count++] = state;
		if (count == NUMBEROF(message.entries))
		{
			distributed_send(&message, _distributed_message_campaign_devices, count,
				sizeof(message.header) + count * sizeof(state), _distributed_to_clients_reliably);
			count = 0;
		}
	}
	if (count) distributed_send(&message, _distributed_message_campaign_devices, count,
		sizeof(message.header) + count * sizeof(message.entries[0]), _distributed_to_clients_reliably);
}

void network_campaign_devices_receive(void const *entries, short count)
{
	short index;
	if (!network_campaign_client()) return;
	for (index = 0; index < count; index++)
	{
		struct campaign_device_state state;
		memcpy(&state, (byte const *)entries + index * sizeof(state), sizeof(state));
		if (state.round != network_game_get_number_of_games_played() ||
			state.seed != (unsigned long)network_game_get_random_seed() ||
			!distributed_object_index_valid(state.object_index) || !network_objects_client_has(state.object_index)) continue;
		device_campaign_apply(&state);
	}
}
