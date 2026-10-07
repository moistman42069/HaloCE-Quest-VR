/* The launcher's co-op hosting (test27: OpenCE's co-op, network_coop.c).

The launcher (CoopLauncher) writes a one-shot coop_host.txt in the game data
root: "2 <mission 0..9> <difficulty 0..3> <public 0/1> <most players 2..128>"
(format 1, the four before the most players, still reads: 16 players;
test30's format 3 is format 2's line, then the server's name on a line of
its own: printable ASCII, COOP_NAME_LENGTH at most, empty for the
machine's name as before). With
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
	/* (the server's name: a network game's name holds 15, as the launcher's PvP host) */
	COOP_NAME_LENGTH = 15,
};
static boolean requested, booted, configured, player_added, start_requested, list_publicly;
static short mission, difficulty, most_players;
/* test30: the server's name asked for (empty: the machine's) */
static char host_name[COOP_NAME_LENGTH + 1];
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
	host_name[0] = 0;
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

/* a request's fields; FALSE if malformed (test30: format 3, the server's
name on the second line; nothing else after the fields) */
static boolean coop_request_read(char const *text)
{
	int version = 0, selected = -1, level = -1, publish = -1, players = COOP_MAXIMUM_PLAYERS;
	char line[64], extra;
	char const *rest = strchr(text, '\n');
	size_t length = rest ? (size_t)(rest - text) : strlen(text);
	char const *after;
	int read;

	if (length >= sizeof(line))
		return FALSE;
	memcpy(line, text, length);
	line[length] = 0;
	read = sscanf(line, "%d %d %d %d %d %c", &version, &selected, &level, &publish, &players, &extra);
	if ((version == 2 || version == 3) && read == 5)
	{
	}
	else if (version == 1 && read == 4)
	{
		players = COOP_FORMAT_1_PLAYERS;
	}
	else
		return FALSE;
	after = rest ? rest + 1 : "";
	host_name[0] = 0;
	if (version == 3)
	{
		size_t name_length = strcspn(after, "\r\n"), index;

		if (name_length > COOP_NAME_LENGTH)
			return FALSE;
		for (index = 0; index < name_length; index++)
		{
			if (after[index] < ' ' || after[index] > '~')
				return FALSE;
		}
		memcpy(host_name, after, name_length);
		host_name[name_length] = 0;
		after += name_length;
	}
	if (after[strspn(after, " \t\r\n")])
	{
		host_name[0] = 0;
		return FALSE;
	}
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
		/* test30: the server's name as the launcher asked (none: the
		machine's, as before); the players' count below sends it to any
		client already in, the listing reads it (network_game_server_list) */
		if (host_name[0] && game)
		{
			int index;

			for (index = 0; host_name[index] && index < (int)NUMBEROF(game->name) - 1; index++)
				game->name[index] = (wchar_t)(unsigned char)host_name[index];
			game->name[index] = 0;
		}
		network_game_server_port_set_cooperative_players(most_players);
		p2p_set_hosting_public(list_publicly);
		platform_log("co-op: lobby open: %s (%s), difficulty %d, up to %d players, %s, named %s", missions[mission], map_name,
			difficulty, most_players, list_publicly ? "listed publicly" : "private (invite)",
			host_name[0] ? host_name : "(the device's name)");
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
