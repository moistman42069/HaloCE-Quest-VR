/* Campaign session identity and negotiation. Gameplay synchronization is kept
 * separate from the competitive v9/v10 protocol. See COOP-FEASIBILITY.md. */
#include "cseries.h"
#include "game/game.h"
#include "networking/network_game_manager.h"
#include "networking/network_game_globals.h"
#include "network_campaign.h"
#include <stdio.h>
#include <string.h>

static char const *campaign_maps[] = {
	"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"
};

static boolean campaign_map_valid(char const *map)
{
	short index;
	char path[128];
	for (index = 0; index < NUMBEROF(campaign_maps); index++)
	{
		snprintf(path, sizeof(path), "levels\\%s\\%s", campaign_maps[index], campaign_maps[index]);
		if (!strcmp(map, path)) return TRUE;
	}
	return FALSE;
}

boolean network_campaign_game(struct network_game const *game)
{
	return game && game->map.version == HALO_CAMPAIGN_MAP_VERSION &&
		game->variant.game_engine_index == game_engine_none &&
		game->minimum_players == 2 && game->maximum_players == 2 &&
		game->difficulty >= 0 && game->difficulty < 4 &&
		memchr(game->map.name, 0, sizeof(game->map.name)) && campaign_map_valid(game->map.name);
}

boolean network_campaign_active(void)
{
	short connection = game_connection();
	return (connection == _game_connection_network_client || connection == _game_connection_network_server) &&
		network_campaign_game(network_game_get_game());
}

boolean network_campaign_playing(void)
{
	return network_campaign_active() && network_game_get_game()->local_data.game_objects_loaded && game_in_progress();
}

boolean network_campaign_client(void)
{
	return game_connection() == _game_connection_network_client && network_campaign_active() &&
		network_game_get_game()->local_data.game_objects_loaded;
}

boolean network_campaign_advertised(word version, byte flags)
{
	return version == HALO_CAMPAIGN_NETWORK_VERSION &&
		(flags & (HALO_CAMPAIGN_ADVERTISED_FLAG | HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG)) ==
		(HALO_CAMPAIGN_ADVERTISED_FLAG | HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG);
}

void network_campaign_join_token(byte *token)
{
	/* Capability echo, NOT authentication. Old clients return the raw nonce and
	 * are rejected by a campaign host, even if their UI skips version checking.
	 * Keep the fixed join packet and the hardware identity completely intact. */
	static byte const domain[16] = {'H','a','l','o','C','a','m','p','a','i','g','n','V','0','0','1'};
	short index;
	for (index = 0; index < 16; index++) token[index] ^= domain[index];
}

boolean network_campaign_prepare(struct network_game *game, char const *map, short difficulty)
{
	if (!game || !map || !campaign_map_valid(map) || difficulty < 0 || difficulty > 3)
		return FALSE;
	memset(&game->variant, 0, sizeof(game->variant));
	strncpy(game->map.name, map, sizeof(game->map.name) - 1);
	game->map.name[sizeof(game->map.name) - 1] = 0;
	game->map.version = HALO_CAMPAIGN_MAP_VERSION;
	game->minimum_players = game->maximum_players = 2;
	game->maximum_teams = 1;
	game->difficulty = difficulty;
	return TRUE;
}
