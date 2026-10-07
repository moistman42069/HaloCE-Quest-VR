#!/usr/bin/env python3
"""Execute actual menu filtering, ordering and refresh selection code."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


def function(text,name):
    match=re.search(r'(?m)^(?:static )?(?:boolean|void|int|short|char const \*|struct advertised_game \*)\s*'+name+r'\([^;]*?\)\n\{',text)
    assert match,name
    return text[match.start():text.index('\n}',match.end())+2]


def main():
    menu=(ROOT/'port/linux/game/menu_functions.c').read_text()
    p2p=(ROOT/'port/linux/src/p2p_lobby.c').read_text()
    header=(ROOT/'port/linux/src/p2p.h').read_text()
    listing=re.search(r'struct p2p_listing\n\{.*?\n};',header,re.S).group()
    p2p_enum=re.search(r'enum\n\{\n\s*P2P_LISTING_NAME_SIZE.*?\n};',header,re.S).group()
    filters=menu[menu.index('static struct\n{\n    boolean empty, full, known;'):menu.index('static void browser_filters_read')]
    prefix=r'''
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
typedef unsigned char boolean;
typedef unsigned char byte;
#define TRUE 1
#define FALSE 0
#define NONE -1
#define NUMBEROF(x) (sizeof(x)/sizeof((x)[0]))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define PIN(v,a,b) MIN(MAX(v,a),b)
#define _stricmp strcasecmp
#define NUMBER_OF_SINGLE_PLAYER_LEVELS 2
#define MAXIMUM_ADVERTISED_GAMES 9
#define BROWSER_ROWS 15
#define LOBBY_BROWSER_GAMES 256
enum {_multiplayer_mode_server_browser,_multiplayer_mode_lan,_multiplayer_mode_direct_link};
static int ustrcmp(const wchar_t*a,const wchar_t*b){while(*a&&*a==*b){a++;b++;}return *a-*b;}
static int show_empty=1,show_full=1,filter_engine=-1;
static const char *team_option="all",*password_option="all",*map_option="all";
static int config_boolean(const char*key){return !strcmp(key,"browser.show_empty")?show_empty:show_full;}
static const char *config_string(const char*key){return !strcmp(key,"browser.maps")?map_option:!strcmp(key,"browser.teams")?team_option:password_option;}
static int config_text(const char*k,char*out,unsigned int size){(void)k;snprintf(out,size,"%d",filter_engine);return 1;}
static int custom_edition_level_name(const char*n){return !strncmp(n,"custom_maps\\",12);}
static short custom_edition_maps_display_index(const char*n){return !strcmp(n,"custom_maps\\example")?13:-1;}
static short ui_widget_port_multiplayer_maps(const char *const **out,short*last){static const char*const names[]={"levels\\test\\bloodgulch\\bloodgulch"};*out=names;*last=0;return 1;}
static const char *main_get_solo_level_name(short level){return level?"levels\\a30\\a30":"levels\\a10\\a10";}
struct advertised_game{unsigned char xnaddr[12];wchar_t game_name[16];char map_name[128];short player_count,maximum_player_count,engine_type;boolean open,has_teams,valid,peer;};
static struct advertised_game network_games[9];
static void*global_network_game_client_get(void){return (void*)1;}
static struct advertised_game*network_game_client_get_available_games(void*c){(void)c;return network_games;}
static boolean network_game_client_advertised_game_is_valid(struct advertised_game*g){return g->valid;}
static boolean game_from_peer(struct advertised_game*g){return g->peer;}
static struct{short mode;struct advertised_game*games[9];byte game_identifiers[9][6];short game_count,game_chosen;}multiplayer;
'''
    core='\n'.join(function(menu,name) for name in ['browser_filters_read','browser_map_stem','browser_map_known','browser_filter_match','browser_game_order','browser_games_read'])
    lobby=r'''
static struct p2p_listing fixture[256];
static short fixture_count;
static struct{struct p2p_listing games[256];short count,first,chosen;unsigned char identifier[6];boolean joining,ready;}lobby_browser;
struct widget_instance{short focused;};
static void lobby_browser_focus_row(struct widget_instance*list,short row){list->focused=row;}
static int p2p_lobby_games(struct p2p_listing*out,int capacity){int count=MIN(fixture_count,capacity);memcpy(out,fixture,count*sizeof(*out));qsort(out,count,sizeof(*out),listing_order);return count;}
static boolean player_name_clean(wchar_t*text,long count){(void)count;return text[0]!=0;}
'''
    refresh=menu[menu.index('    byte selected_identifier[6];'):menu.index('\t/* (the first game found takes the focus',menu.index('    byte selected_identifier[6];'))]
    refresh='static void refresh(struct widget_instance*list){short focused=list->focused;\n'+refresh+'\n}\n'
    tests=r'''
static void defaults(void){show_empty=show_full=1;filter_engine=-1;team_option=password_option=map_option="all";browser_filters_read();}
static void listing(short index,byte id,byte players){struct p2p_listing*g=&fixture[index];memset(g,0,sizeof(*g));g->identifier[0]=id;strcpy(g->name,"server");strcpy(g->map,"bloodgulch");g->player_count=players;g->maximum_player_count=128;g->open=1;g->engine_type=2;}
int main(void)
{
    struct widget_instance list;
    short i;
    defaults();
    assert(browser_filter_match(0,16,TRUE,2,FALSE,FALSE,"missing"));
    show_empty=0;browser_filters_read();assert(!browser_filter_match(0,16,TRUE,2,FALSE,FALSE,"bloodgulch"));
    show_full=0;browser_filters_read();assert(!browser_filter_match(16,16,TRUE,2,FALSE,FALSE,"bloodgulch"));
    assert(!browser_filter_match(2,16,FALSE,2,FALSE,FALSE,"bloodgulch"));
    defaults();filter_engine=0;browser_filters_read();assert(browser_filter_match(2,128,TRUE,0,FALSE,FALSE,"a10"));assert(!browser_filter_match(2,128,TRUE,2,FALSE,FALSE,"bloodgulch"));
    defaults();team_option="teams";password_option="locked";browser_filters_read();assert(browser_filter_match(2,16,TRUE,2,TRUE,TRUE,"bloodgulch"));assert(!browser_filter_match(2,16,TRUE,2,FALSE,TRUE,"bloodgulch"));assert(!browser_filter_match(2,16,TRUE,2,TRUE,FALSE,"bloodgulch"));
    defaults();map_option="known";browser_filters_read();assert(browser_map_known("bloodgulch"));assert(browser_map_known("a10"));assert(browser_map_known("custom_maps\\example"));assert(!browser_map_known("custom_maps\\bloodgulch"));assert(!browser_filter_match(2,16,TRUE,2,TRUE,FALSE,"unknown"));
    defaults();
    fixture_count=3;listing(0,1,10);listing(1,2,8);listing(2,3,2);
    list.focused=NONE;refresh(&list);assert(lobby_browser.games[0].identifier[0]==1);
    list.focused=0;lobby_browser.chosen=0;
    fixture[0].player_count=3;fixture[1].player_count=12;
    lobby_browser.joining=TRUE;lobby_browser.identifier[0]=1;
    refresh(&list);assert(lobby_browser.chosen==1&&list.focused==1&&lobby_browser.games[1].identifier[0]==1);
    assert(lobby_browser.joining&&lobby_browser.identifier[0]==1); /* independent pending join */
    list.focused=2;fixture[2].player_count=20;refresh(&list);assert(lobby_browser.chosen==0&&list.focused==0&&lobby_browser.games[0].identifier[0]==3);
    fixture_count=20;for(i=0;i<20;i++)listing(i,(byte)(i+1),(byte)(30-i));
    list.focused=NONE;lobby_browser.count=0;refresh(&list);
    list.focused=14;lobby_browser.first=0;refresh(&list);assert(lobby_browser.first==1&&list.focused==13&&lobby_browser.chosen==14);
    /* A vanished selection is clamped safely, including an empty filter result. */
    filter_engine=0;list.focused=13;refresh(&list);assert(!lobby_browser.count&&lobby_browser.first==0&&lobby_browser.chosen==0);
    defaults();
    multiplayer.mode=_multiplayer_mode_lan;
    for(i=0;i<3;i++){network_games[i].valid=network_games[i].open=1;network_games[i].maximum_player_count=16;network_games[i].engine_type=2;network_games[i].xnaddr[2]=(byte)(i+1);network_games[i].player_count=10-i;strcpy(network_games[i].map_name,"bloodgulch");network_games[i].game_name[0]=L'A'+i;}
    browser_games_read();assert(multiplayer.game_count==3&&multiplayer.games[0]->xnaddr[2]==1);
    multiplayer.game_chosen=1;network_games[1].player_count=16;browser_games_read();assert(multiplayer.game_chosen==0&&multiplayer.games[0]->xnaddr[2]==2);
    assert(multiplayer.game_identifiers[0][0]==2);
    puts("browser: persistent filter predicates, known-map catalog, population order, live host identity, page scroll and LAN refresh passed");
    return 0;
}
'''
    compiler=shutil.which('clang') or shutil.which('cc');assert compiler
    with tempfile.TemporaryDirectory(prefix='test31-browser-') as temp:
        temp=Path(temp); harness=temp/'browser.c';exe=temp/'browser'
        harness.write_text(prefix+p2p_enum+listing+filters+core+function(p2p,'listing_order')+lobby+function(menu,'text_to_wide')+function(menu,'lobby_browser_valid_games')+refresh+tests)
        subprocess.run([compiler,'-std=gnu11','-fshort-wchar','-O1','-g','-fsanitize=address,undefined',str(harness),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
    xml=ET.parse(ROOT/'port/assets/menus/ce/main_menu.multiplayer_type_select.join_game.filters.xml')
    keys={node.get('setting') for node in xml.iter('widget') if node.get('setting')}
    assert keys=={'browser.show_empty','browser.show_full','browser.engine','browser.teams','browser.passwords','browser.maps'}
    assert not any(node.get('event')=='deleted' for node in xml.iter('on')), 'Cancel must not save edits'
    assert 'listing.version != HALO_PORT_NETWORK_VERSION' in p2p
    assert 'game->locked' in function(menu,'lobby_browser_select')
    assert 'p2p_listing_unlock' in function(menu,'password_screen_join')
    assert '!memcmp(games[index].xnaddr + 2, lobby_browser.identifier' in function(menu,'lobby_browser_joined_game')


if __name__=='__main__':
    main()
