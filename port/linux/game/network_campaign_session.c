/* The launcher's co-op hosting (test27: OpenCE's co-op, network_coop.c).

The launcher (CoopLauncher) writes a one-shot coop_host.txt in the game data
root: "2 <mission 0..9> <difficulty 0..3> <public 0/1> <most players 2..128>"
(format 1, the four before the most players, still reads: 16 players). With
the main menu up, this opens a native network lobby (as the Xbox's Create
Game does), adds the local player, and sets it up as upstream's Create Game
does for a SINGLEPLAYER map (ui_widget_port_cooperative_level_choose): the
campaign level, the difficulty and a gametype with no game engine, which is
what makes a network game co-op on every machine, this app's and OpenCE's.
A public game is listed through the signed lobby (p2p_lobby.c), which the
in-game server browsers (this app's System Link list, OpenCE's Server
Browser) and the community directory read; a private one by its invite.
The host starts it from the lobby, or it starts as the lobby fills; players
may join it under way, as OpenCE's do.

(The CE01/CE02 campaign protocol this file started before 1.0.9 is retired:
network_campaign_game is never true now.) */
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
void p2p_set_hosting_public(int value);
/* source/interface/ui_widget_event_handler_functions.c */
boolean ui_widget_port_cooperative_level_choose(char const *map_name, short difficulty);

static char const *missions[] = {"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"};
enum
{
	COOP_MINIMUM_PLAYERS = 2,
	/* (OpenCE's Server Setup offers co-op games of 2 to 128 players,
	MAXIMUM_NETWORK_PLAYER_COUNT; test28: this was 16) */
	COOP_MAXIMUM_PLAYERS = 128,
	/* (the 1.0.8 launcher's format, without the most players: Server Setup's default) */
	COOP_FORMAT_1_PLAYERS = 16,
};
static boolean requested, booted, configured, player_added, start_requested, list_publicly;
static short mission, difficulty, most_players;
static real settle_seconds;
static unsigned long last_poll, request_time;

boolean network_campaign_host_requested(void) { return requested; }
boolean network_coop_host_public(void) { return requested && list_publicly; }
/* (the retired CE campaign's settings: never asked for now) */
boolean network_campaign_host_settings(struct network_game *game) { (void)game; return FALSE; }

void network_campaign_session_end(void)
{
	if (requested)
		p2p_set_hosting_public(FALSE);
	requested = booted = configured = player_added = start_requested = list_publicly = FALSE;
	settle_seconds = 0.0f;
	remove("d:\\coop_status.txt");
}

/* (the retired CE campaign's level change: upstream's, main.c, ends a won
co-op round and sets up the next level) */
boolean network_campaign_change_level(boolean next)
{
	(void)next;
	return FALSE;
}

/* a request's fields; FALSE if malformed */
static boolean coop_request_read(char const *text)
{
	int version = 0, selected = -1, level = -1, publish = -1, players = COOP_MAXIMUM_PLAYERS;
	char extra;
	int read = sscanf(text, "%d %d %d %d %d %c", &version, &selected, &level, &publish, &players, &extra);

	if (version == 2 && read == 5)
	{
	}
	else if (version == 1 && read == 4)
	{
		players = COOP_FORMAT_1_PLAYERS;
	}
	else
		return FALSE;
	if (!VALID_INDEX(selected, NUMBEROF(missions)) || level < 0 || level > 3 || (publish != 0 && publish != 1) ||
		players < COOP_MINIMUM_PLAYERS || players > COOP_MAXIMUM_PLAYERS)
	{
		return FALSE;
	}
	mission = (short)selected;
	difficulty = (short)level;
	list_publicly = publish;
	most_players = (short)players;
	return TRUE;
}

void network_campaign_session_update(boolean menu_loaded, real seconds)
{
	unsigned long now = system_milliseconds();
	struct network_game_server *server;
	struct network_game *game;

	if (!requested && menu_loaded && game_connection() == _game_connection_local && now - last_poll >= 1000UL)
	{
		FILE *file;

		last_poll = now;
		file = fopen("d:\\coop_host.txt", "rb");
		if (file)
		{
			char text[128];
			size_t count = fread(text, 1, sizeof(text) - 1, file);
			boolean failed = ferror(file) != 0 || !feof(file);

			fclose(file);
			text[count] = 0;
			remove("d:\\coop_host.txt");
			if (!failed && coop_request_read(text))
			{
				requested = TRUE;
				request_time = now;
				settle_seconds = 0.0f;
				platform_log("co-op: host requested: %s, difficulty %d, up to %d players, %s", missions[mission],
					difficulty, most_players, list_publicly ? "public" : "private");
			}
			else
				platform_log("co-op: ignored a malformed launcher host request");
		}
	}
	if (!requested)
		return;
	if (!booted)
	{
		if (!menu_loaded)
			return;
		settle_seconds += seconds;
		if (settle_seconds < 1.0f)
			return;
		booted = TRUE;
		player_ui_fast_setup_network_server();
		if (!global_network_game_server_get())
		{
			platform_log("co-op: could not open the host's lobby");
			network_game_abort();
		}
		return;
	}
	server = global_network_game_server_get();
	if (!server)
	{
		network_campaign_session_end();
		return;
	}
	game = network_game_get_game();
	if (!configured)
	{
		short level = main_get_solo_level_from_name(missions[mission]);
		char const *map_name = main_get_solo_level_name(level);

		configured = map_name && ui_widget_port_cooperative_level_choose(map_name, difficulty);
		if (!configured)
		{
			if (now - request_time > 30000UL)
			{
				platform_log("co-op: the lobby could not be set up for %s", missions[mission]);
				network_game_abort();
			}
			return;
		}
		network_game_server_port_set_cooperative_players(most_players);
		p2p_set_hosting_public(list_publicly);
		platform_log("co-op: lobby open: %s (%s), difficulty %d, up to %d players, %s", missions[mission], map_name,
			difficulty, most_players, list_publicly ? "listed publicly" : "private (invite)");
	}
	if (!player_added && menu_loaded && global_network_game_client_get())
		player_added = network_game_client_add_player(global_network_game_client_get(), 0);
	if (!player_added && now - request_time > 30000UL)
	{
		platform_log("co-op: the local player could not enter the lobby");
		network_game_abort();
		return;
	}
	/* (the lobby full: started for the host, who can start it sooner) */
	if (!start_requested && menu_loaded && game && game->player_count >= game->maximum_players &&
		network_game_server_port_in_pregame())
	{
		start_requested = TRUE;
		network_game_client_request_immediate_start();
		platform_log("co-op: the lobby is full (%d players); starting", game->player_count);
	}
	if (start_requested && network_game_server_port_in_pregame() && game &&
		game->player_count < game->maximum_players)
	{
		/* (back in the lobby, for the next level, with room again) */
		start_requested = FALSE;
	}
}

/* (the retired CE campaign's clock hooks, network_campaign_lifecycle.c: no
game is a CE campaign's now, so nothing reaches them) */
void network_game_client_campaign_clock(long time) { (void)time; }
void network_game_server_campaign_clock(long time) { (void)time; }
