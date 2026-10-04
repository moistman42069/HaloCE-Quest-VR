/* Production host bootstrap. One-shot coop_host.txt format:
 * version (1), mission index (0..9), difficulty (0..3), public listing (0/1). */
#include "cseries.h"
#include "game/game.h"
#include "interface/player_ui.h"
#include "main/main.h"
#include "networking/network_game_globals.h"
#include "networking/network_game_manager.h"
#include "networking/network_client_manager.h"
#include "networking/network_server_manager.h"
#include "network_campaign.h"
#include <stdio.h>
#include <string.h>

void platform_log(char const *format, ...);
unsigned long system_milliseconds(void);
int p2p_hosting_invite(char *text, int size);
void p2p_set_hosting_public(int value);
static char const *missions[] = {"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"};
static boolean requested, booted, player_added, start_requested, list_publicly;
static short mission, difficulty;
static real settle_seconds;
static unsigned long last_poll, request_time;
static unsigned long last_status;

/* Atomic, bounded launcher status. The Android publisher checks freshness and
 * only announces while the native lobby really exists and the host opted in. */
static void session_status(struct network_game const *game, unsigned long now)
{
	char invite[256];
	FILE *file;
	if (now - last_status < 1000UL) return;
	last_status = now;
	if (!p2p_hosting_invite(invite, sizeof(invite))) return;
	file = fopen("d:\\coop_status.txt.tmp", "wb");
	if (file)
	{
		int result = fprintf(file, "1 %d %d %d %d %d %s\n", list_publicly, mission, difficulty,
			game->player_count, !start_requested && game->player_count < 2, invite);
		boolean ok = result > 0 && !ferror(file);
		if (fclose(file) != 0) ok = FALSE;
		if (ok) rename("d:\\coop_status.txt.tmp", "d:\\coop_status.txt");
		else remove("d:\\coop_status.txt.tmp");
	}
}

boolean network_campaign_host_requested(void) { return requested; }
boolean network_campaign_host_settings(struct network_game *game)
{
	char path[128];
	if (!requested || !VALID_INDEX(mission, NUMBEROF(missions))) return FALSE;
	snprintf(path, sizeof(path), "levels\\%s\\%s", missions[mission], missions[mission]);
	return network_campaign_prepare(game, path, difficulty);
}
void network_campaign_session_end(void)
{
	p2p_set_hosting_public(FALSE);
	requested = booted = player_added = start_requested = list_publicly = FALSE;
	settle_seconds = 0.0f;
	remove("d:\\coop_status.txt");
}
boolean network_campaign_change_level(boolean next)
{
	struct network_game_server *server;
	if (!network_campaign_active()) return FALSE;
	if (game_connection() != _game_connection_network_server) return TRUE;
	server = global_network_game_server_get();
	if (!server || !requested) { network_game_abort(); return TRUE; }
	if (next && ++mission >= NUMBEROF(missions))
	{
		platform_log("campaign: final mission completed; closing co-op session");
		network_game_server_switch_to_postgame(server);
		network_game_server_graceful_shutdown(server);
		network_game_abort();
		return TRUE;
	}
	network_campaign_level_wait();
	network_game_server_switch_to_postgame(server);
	if (!network_game_server_reset_to_pregame(server))
	{
		platform_log("campaign: could not return both machines to the loading lobby");
		network_game_abort();
		return TRUE;
	}
	start_requested = FALSE;
	settle_seconds = 0.0f;
	platform_log("campaign: %s mission %s at difficulty %d", next ? "advancing to" : "restarting", missions[mission], difficulty);
	return TRUE;
}
void network_campaign_session_update(boolean menu_loaded, real seconds)
{
	unsigned long now = system_milliseconds();
	struct network_game *game;
	if (!requested && menu_loaded && game_connection() == _game_connection_local && now - last_poll >= 1000UL)
	{
		FILE *file;
		last_poll = now;
		file = fopen("d:\\coop_host.txt", "rb");
		if (file)
		{
			char text[128], extra;
			int version, selected, level, publish;
			size_t count = fread(text, 1, sizeof(text) - 1, file);
			boolean failed = ferror(file) != 0 || !feof(file);
			fclose(file);
			text[count] = 0;
			remove("d:\\coop_host.txt");
			if (!failed && sscanf(text, "%d %d %d %d %c", &version, &selected, &level, &publish, &extra) == 4 &&
				version == 1 && VALID_INDEX(selected, NUMBEROF(missions)) && level >= 0 && level <= 3 &&
				(publish == 0 || publish == 1))
			{
				mission = selected; difficulty = level; list_publicly = publish;
				requested = TRUE; request_time = now; settle_seconds = 0.f;
				platform_log("campaign: requested host mission %s difficulty %d public %d", missions[mission], difficulty, publish);
			}
			else platform_log("campaign: ignored malformed launcher host request");
		}
	}
	if (!requested) return;
	if (!booted)
	{
		if (!menu_loaded) return;
		settle_seconds += seconds;
		if (settle_seconds < 1.0f) return;
		booted = TRUE;
		player_ui_fast_setup_network_server();
		if (!global_network_game_server_get())
		{ platform_log("campaign: could not open host lobby"); network_game_abort(); }
		return;
	}
	if (!global_network_game_server_get()) { network_campaign_session_end(); return; }
	game = network_game_get_game();
	if (!network_campaign_game(game))
	{ platform_log("campaign: host settings lost their campaign identity"); network_game_abort(); return; }
	session_status(game, now);
	if (!player_added && menu_loaded && global_network_game_client_get())
		player_added = network_game_client_add_player(global_network_game_client_get(), 0);
	if (!start_requested && menu_loaded && game->player_count == 2 && game->machine_count == 2)
	{
		start_requested = TRUE;
		network_game_client_request_immediate_start();
		platform_log("campaign: both players joined; starting mission");
	}
	/* A reconnect needs cinematic/checkpoint history; refuse late join for now. */
	if (network_campaign_playing() && game->player_count != 2)
	{ platform_log("campaign: partner disconnected"); network_game_abort(); }
	if (!player_added && now - request_time > 30000UL)
	{ platform_log("campaign: local player could not enter the lobby"); network_game_abort(); }
}
