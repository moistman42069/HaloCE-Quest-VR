/* Production PvP bootstrap. No debug network-test behavior is enabled. */
#include "cseries.h"
#include "cache/cache_files.h"
#include "game/game.h"
#include "game/game_engine.h"
#include "interface/player_ui.h"
#include "networking/network_game_globals.h"
#include "networking/network_game_manager.h"
#include "networking/network_client_manager.h"
#include "networking/network_server_manager.h"
#include "network_campaign.h"
#include "network_pvp_session.h"
#include "network_pvp_request.h"
void platform_log(char const *format, ...);
long config_integer(char const *name);
int config_boolean(char const *name);
unsigned long system_milliseconds(void);
int p2p_hosting_invite(char *text, int size);
void p2p_set_hosting_public(int value);
boolean network_game_server_game_is_open(struct network_game_server *server);
static struct pvp_request request;
static boolean requested, booted, player_added;
static real settle;
static unsigned long last_poll, last_status, request_time;

boolean network_pvp_host_requested(void) { return requested; }
boolean network_pvp_host_settings(struct network_game *game)
{
    int i;
    if(!requested) return FALSE;
    game_engine_get_variant_by_name(&game->variant, request.variant);
    if(request.score) game->variant.universal_variant.score_to_win=request.score;
    snprintf(game->map.name,sizeof(game->map.name),"levels\\test\\%s\\%s",request.map,request.map);
    p2p_set_hosting_public(request.publish);
    game->map.version=(long)cache_files_map_version(game->map.name); game->minimum_players=2; game->maximum_players=(byte)request.maximum;
    game->maximum_teams=game->variant.universal_variant.teams ? 2 : 1;
    for(i=0;i<15 && request.name[i];i++) game->name[i]=(unsigned char)request.name[i];
    game->name[i]=0;
    game_variant_options_default(&game->variant, &game->variant_options);
    game->variant_options.time_limit=PIN(config_integer("pvp.time_limit"),0,1440);
    game->variant_options.friendly_fire=PIN(config_integer("pvp.friendly_fire"),0,3);
    game->variant_options.vehicle_respawn_time=PIN(config_integer("pvp.vehicle_respawn_time"),0,3600);
    game->variant_options.auto_team_balance=config_boolean("pvp.auto_team_balance");
    game->variant_options.radar_players=PIN(config_integer("pvp.radar_players"),0,2);
    game->variant_options.loadout=config_boolean("pvp.custom_loadout") ? _loadout_custom : _loadout_category;
    game->variant_options.primary_weapon=PIN(config_integer("pvp.primary_weapon"),0,9);
    game->variant_options.secondary_weapon=PIN(config_integer("pvp.secondary_weapon"),0,9);
    SET_FLAG(game->variant.universal_variant.flags,_game_variant_draw_object_in_motion_sensor_bit,game->variant_options.radar_players!=_radar_players_none);
    SET_FLAG(game->variant.universal_variant.flags,_game_variant_infinite_grenades_bit,config_boolean("pvp.infinite_grenades"));
    player_ui_set_game_variant(&game->variant);
    return TRUE;
}
void network_pvp_session_end(void)
{
    p2p_set_hosting_public(FALSE);
    requested=booted=player_added=FALSE; settle=0.f;
    remove("d:\\pvp_status.txt");
}
static void pvp_status(struct network_game_server *server, struct network_game *game, unsigned long now)
{
    char invite[256], name[16]; const char *map; FILE *file; int i, result; boolean ok;
    if(now-last_status<1000UL) return;
    last_status=now;
    if(!p2p_hosting_invite(invite,sizeof(invite))) return;
    for(i=0;i<15 && game->name[i];i++) name[i]=game->name[i]>=32 && game->name[i]<127 ? (char)game->name[i] : '?';
    name[i]=0; map=strrchr(game->map.name,'\\'); map=map ? map+1 : game->map.name;
    file=fopen("d:\\pvp_status.txt.tmp","wb"); if(!file) return;
    result=fprintf(file,"1 %d %d %d %d %d %d %ld %s %s\n%s\n", request.publish,game->player_count,
        game->maximum_players,network_game_server_game_is_open(server) && game->player_count<game->maximum_players,
        game->variant.game_engine_index,game->variant.universal_variant.teams,
        (long)game->variant.universal_variant.score_to_win,map,invite,name);
    ok=result>0 && !ferror(file); if(fclose(file)!=0) ok=FALSE;
    if(ok) rename("d:\\pvp_status.txt.tmp","d:\\pvp_status.txt"); else remove("d:\\pvp_status.txt.tmp");
}
void network_pvp_session_update(boolean menu_loaded, real seconds)
{
    unsigned long now=system_milliseconds(); struct network_game_server *server;
    if(!requested && !network_campaign_host_requested() && menu_loaded && game_connection()==_game_connection_local && now-last_poll>=1000UL)
    {
        FILE *file; last_poll=now; file=fopen("d:\\pvp_host.txt","rb");
        if(file)
        {
            char text[256]; size_t count=fread(text,1,sizeof(text)-1,file);
            boolean failed=ferror(file)!=0 || !feof(file);
            fclose(file); text[count]=0; remove("d:\\pvp_host.txt");
            if(!failed && !memchr(text,0,count) && pvp_request_parse(text,&request))
            {
                char path[64]; FILE *map;
                snprintf(path,sizeof(path),"d:\\maps\\%s.map",request.map); map=fopen(path,"rb");
                if(map) { fclose(map); requested=TRUE; request_time=now; settle=0.f;
                    platform_log("PvP: host requested map=%s variant=%s maximum=%d public=%d", request.map,request.variant,request.maximum,request.publish); }
                else platform_log("PvP: selected map is missing; host request rejected");
            }
            else platform_log("PvP: malformed host request rejected");
        }
    }
    if(!requested) return;
    if(!booted)
    {
        if(!menu_loaded) return; settle+=seconds; if(settle<1.f) return;
        booted=TRUE; player_ui_fast_setup_network_server();
        if(!global_network_game_server_get()) { platform_log("PvP: lobby creation failed"); network_game_abort(); }
        return;
    }
    server=global_network_game_server_get();
    if(!server) { network_pvp_session_end(); return; }
    if(!player_added && menu_loaded && global_network_game_client_get())
        player_added=network_game_client_add_player(global_network_game_client_get(),0);
    pvp_status(server,network_game_get_game(),now);
    if(!player_added && now-request_time>30000UL) { platform_log("PvP: local player failed to join lobby"); network_game_abort(); }
    /* Host starts the game through the normal lobby, retaining stock late join. */
}
