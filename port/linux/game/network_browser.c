/* Upstream build-84 signed public discovery, presented in the existing Xbox
 * System Link widgets. No PC menu replacement, disk tag changes or co-op changes.
 * Layout follows ui_widget_game_data_input_functions.c and upstream
 * menu_functions.c's advertised_game. All native joins resolve a live record. */
#include "cseries.h"
#include "networking/network_client_manager.h"
#include "networking/network_game_manager.h"
#include "interface/event_manager.h"
#include "network_browser.h"
#include "../src/p2p.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

unsigned long system_milliseconds(void);
int config_boolean(char const *name);
void platform_log(char const *format, ...);
struct network_advertised_game {
    byte key_id[8], key[16], xnaddr[12], nonce[8];
    unsigned long update_time;
    wchar_t game_name[16]; long map_version; char map_name[128];
    short engine_type; word machine_count, player_count;
    short maximum_player_count, score_limit, platform;
    boolean open, valid, has_teams, oddball_variant;
};
typedef char browser_advertised_size[sizeof(struct network_advertised_game)==0xe4?1:-1];
typedef char browser_identifier_offset[offsetof(struct network_advertised_game,xnaddr)==0x18?1:-1];
#define PUBLIC_GAMES 256
#define LAN_GAMES 9
#define PAGE_SIZE 7
struct browser_game {
    struct network_advertised_game display;
    char invite[P2P_LISTING_INVITE_SIZE];
    unsigned char locked;
    char name[33]; byte identifier[6];
};
static struct {
    struct browser_game games[PUBLIC_GAMES+LAN_GAMES];
    struct network_advertised_game rows[9];
    int count, page, pending, controller, ready;
    unsigned long joined, refreshed;
    boolean active, dirty;
    char status[160];
} browser;

static void wide(wchar_t *out, long size, char const *text) {
    long n; if(size<=0)return;
    for(n=0;n<size-1 && text[n];n++)out[n]=(unsigned char)text[n];out[n]=0;
}
static struct network_advertised_game *find_game(byte const *identifier) {
    struct network_game_client *client=global_network_game_client_get();
    struct network_advertised_game *games=client?network_game_client_get_available_games(client):NULL;
    int i;for(i=0;games && i<LAN_GAMES;i++)
        if(network_game_client_advertised_game_is_valid(&games[i]) && !memcmp(games[i].xnaddr+2,identifier,6))return &games[i];
    return NULL;
}
static int order(void const *a,void const *b) {
    struct browser_game const *x=a,*y=b;
    if(x->display.player_count!=y->display.player_count)return (int)y->display.player_count-x->display.player_count;
    if(x->display.open!=y->display.open)return (int)y->display.open-x->display.open;
    return strcmp(x->name,y->name);
}
static void snapshot(void) {
    struct p2p_listing listings[PUBLIC_GAMES];
    struct network_game_client *client=global_network_game_client_get();
    struct network_advertised_game *lan=client?network_game_client_get_available_games(client):NULL;
    int count=p2p_lobby_games(listings,PUBLIC_GAMES),i,j;
    browser.count=0;
    for(i=0;i<count;i++) {
        struct p2p_listing *p=&listings[i];
        struct browser_game *g=&browser.games[browser.count++];
        memset(g,0,sizeof(*g)); memcpy(g->identifier,p->identifier,6);
        memcpy(g->invite,p->invite,sizeof(g->invite));snprintf(g->name,sizeof(g->name),"%s",p->name);
        /* test27: a password-protected game (OpenCE build 138): its invite is sealed;
        this app has no password entry, so it is marked and not joined */
        g->locked=p->locked;if(g->locked){char locked[sizeof(g->name)];snprintf(locked,sizeof(locked),"LOCK %s",g->name);snprintf(g->name,sizeof(g->name),"%s",locked);}
        wide(g->display.game_name,16,g->name);snprintf(g->display.map_name,sizeof(g->display.map_name),"%s",p->map);
        g->display.engine_type=p->engine_type;g->display.player_count=p->player_count;
        g->display.maximum_player_count=p->maximum_player_count;g->display.open=p->open;
        g->display.valid=TRUE;g->display.has_teams=p->has_teams;g->display.score_limit=NONE;
    }
    for(i=0;lan && i<LAN_GAMES;i++) {
        struct browser_game *g;
        if(!network_game_client_advertised_game_is_valid(&lan[i]) || lan[i].platform!=0)continue;
        for(j=0;j<browser.count;j++)if(!memcmp(lan[i].xnaddr+2,browser.games[j].identifier,6))break;
        if(j<browser.count)continue;
        g=&browser.games[browser.count++];memset(g,0,sizeof(*g));g->display=lan[i];
        memcpy(g->identifier,lan[i].xnaddr+2,6);
        for(j=0;j<15 && lan[i].game_name[j];j++)g->name[j]=lan[i].game_name[j]>=32 && lan[i].game_name[j]<127?(char)lan[i].game_name[j]:'?';
        g->name[j]=0;
    }
    qsort(browser.games,browser.count,sizeof(browser.games[0]),order);
    if(browser.page*PAGE_SIZE>=browser.count)browser.page=0;
    browser.refreshed=system_milliseconds();browser.dirty=FALSE;
}
void network_browser_begin(void) {
    memset(&browser,0,sizeof(browser));browser.active=browser.dirty=TRUE;browser.pending=NONE;
    p2p_lobby_browse(TRUE);p2p_lobby_refresh();
    snprintf(browser.status,sizeof(browser.status),"Public OpenCE + LAN. Most players first. A: join; B: back.");
    platform_log("browser: signed public discovery started; stock System Link UI");
}
void network_browser_end(void) {
    browser.active=FALSE;browser.pending=NONE;p2p_lobby_browse(FALSE);
}
long network_browser_rows(struct network_advertised_game **rows, short selected, short controller) {
    int i, n; unsigned long now=system_milliseconds();
    if(controller==NONE)controller=0;
    if(!browser.active)network_browser_begin();
    if(browser.pending!=NONE) {
        int chosen=browser.page*PAGE_SIZE+selected-1;
        if(chosen!=browser.pending || controller!=browser.controller) {
            browser.pending=NONE;browser.ready=FALSE;
            snprintf(browser.status,sizeof(browser.status),"Join cancelled. Select a game to connect.");
        } else if(!browser.ready && find_game(browser.games[browser.pending].identifier)) {
            browser.ready=TRUE;
            event_manager_post_button(controller,0);
        } else if(!browser.ready) {
            /* test20e: follow the join's stages (p2p_join_status) instead of a
             * fixed 30 s, and say why it failed */
            char failure[160];int tries=0,active=0,stage=p2p_join_status(failure,sizeof(failure),&tries,&active);
            char const *give_up=NULL;
            if(active || now-browser.joined<2000) {
                if(stage==P2P_JOIN_REACHING)snprintf(browser.status,sizeof(browser.status),
                    "Host answered. Opening a direct connection (try %d)... B: cancel.",tries);
                else if(stage==P2P_JOIN_FAILED)snprintf(browser.status,sizeof(browser.status),
                    "Try %d found no direct path; asking again... B: cancel.",tries);
                else if(stage==P2P_JOIN_CONNECTED)snprintf(browser.status,sizeof(browser.status),
                    "Connected. Waiting for the host's game to appear...");
                else snprintf(browser.status,sizeof(browser.status),"Asking the host... B: cancel.");
                if(now-browser.joined>=120000)give_up="The join took too long. Refresh and try again.";
            } else if(stage==P2P_JOIN_FAILED)give_up=failure[0]?failure:"Could not reach the host. Refresh and try again.";
            else if(stage==P2P_JOIN_CONNECTED) {
                snprintf(browser.status,sizeof(browser.status),"Connected. Waiting for the host's game to appear...");
                if(now-browser.joined>=45000)give_up="Connected, but the host's game did not appear. It may be closed or loading.";
            } else if(now-browser.joined>=30000)give_up="Host did not answer. A: retry; refresh to find other games.";
            if(give_up) {
                p2p_lobby_mark_failed(browser.games[browser.pending].identifier);
                browser.pending=NONE;browser.ready=FALSE;
                snprintf(browser.status,sizeof(browser.status),"%s",give_up);
                platform_log("browser: join of the selected public host ended after %lu ms at stage %d (%d direct tries): %s",
                    now-browser.joined,stage,tries,give_up);
            }
        }
    }
    /* Freeze nonempty snapshots until refresh/navigation: rows never jump under
     * the player's pointer as listings arrive, expire or change population. */
    if(browser.pending==NONE && (browser.dirty || (!browser.count && now-browser.refreshed>=1000)))snapshot();
    memset(browser.rows,0,sizeof(browser.rows));
    for(i=0;i<9;i++){browser.rows[i].open=TRUE;rows[i]=&browser.rows[i];}
    n=MIN(PAGE_SIZE,browser.count-browser.page*PAGE_SIZE);
    for(i=0;i<n;i++)browser.rows[i+1]=browser.games[browser.page*PAGE_SIZE+i].display;
    return n+2;
}
struct network_advertised_game *network_browser_select(struct network_advertised_game *row, short controller) {
    int r,n=MIN(PAGE_SIZE,browser.count-browser.page*PAGE_SIZE),index;
    struct browser_game *g;struct network_advertised_game *live;
    if(controller==NONE)controller=0;
    for(r=0;r<9;r++)if(row==&browser.rows[r])break;
    if(!browser.active || r==9)return row; /* untouched legacy callers */
    if(r==0 || r==n+1) {
        if(r==0 && browser.page>0)browser.page--;
        else if(r==n+1 && (browser.page+1)*PAGE_SIZE<browser.count)browser.page++;
        else {browser.page=0;browser.dirty=TRUE;p2p_lobby_refresh();}
        browser.pending=NONE;browser.ready=FALSE;
        snprintf(browser.status,sizeof(browser.status),"Public OpenCE + LAN. ISO/revision or map differences may prevent joining.");
        return NULL;
    }
    index=browser.page*PAGE_SIZE+r-1;if(index<0||index>=browser.count)return NULL;
    g=&browser.games[index]; live=find_game(g->identifier);
    if(live){browser.pending=NONE;browser.ready=FALSE;return live;}
    if(!g->display.open || g->display.player_count>=g->display.maximum_player_count) {
        snprintf(browser.status,sizeof(browser.status),"This game is closed or full. Refresh to check again.");return NULL;
    }
    if(g->locked) {
        snprintf(browser.status,sizeof(browser.status),"This game has a password. Ask its host for an invite link instead.");return NULL;
    }
    if(browser.pending==index)return NULL;
    if(!g->invite[0] || !config_boolean("network.online") || !p2p_join_invite(g->invite)) {
        snprintf(browser.status,sizeof(browser.status),"Host unavailable or Internet play is off. Refresh and try again.");return NULL;
    }
    browser.pending=index;browser.ready=FALSE;browser.controller=controller;browser.joined=system_milliseconds();
    snprintf(browser.status,sizeof(browser.status),"Asking the host... Move selection or B to cancel.");
    platform_log("browser: joining public listing '%s'",g->name);return NULL;
}
boolean network_browser_text(long row,wchar_t *text,long capacity) {
    char line[64];int n=MIN(PAGE_SIZE,browser.count-browser.page*PAGE_SIZE);
    if(!browser.active || row<0 || row>=n+2)return FALSE;
    if(row==0)snprintf(line,sizeof(line),browser.page?"< PREVIOUS PAGE":"REFRESH PUBLIC + LAN");
    else if(row==n+1)snprintf(line,sizeof(line),(browser.page+1)*PAGE_SIZE<browser.count?"NEXT PAGE > (%d/%d)":"REFRESH (%d/%d)",browser.page+1,MAX(1,(browser.count+PAGE_SIZE-1)/PAGE_SIZE));
    else {struct browser_game *g=&browser.games[browser.page*PAGE_SIZE+row-1];
        snprintf(line,sizeof(line),"%3u/%d %.19s%s",g->display.player_count,g->display.maximum_player_count,g->name,g->display.open?"":" [X]");}
    wide(text,capacity,line);return TRUE;
}
char const *network_browser_status(void){return browser.status;}
/* the stock list's "start server if none advertised" declines while this
 * browser owns the list (it always has rows); its warning is noise then */
boolean network_browser_active(void){return browser.active;}
