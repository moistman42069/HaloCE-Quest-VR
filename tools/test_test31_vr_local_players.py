#!/usr/bin/env python3
"""Actual menu entry guards preserve Quest stereo and flat local split-screen."""
from pathlib import Path
import re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]

def function(source,name):
    m=re.search(r'(?m)^static boolean '+name+r'\([^;]*?\)\n\{',source)
    assert m,name
    return source[m.start():source.index('\n}',m.end())+2]

def main():
    source=(ROOT/'port/linux/game/menu_functions.c').read_text()
    preamble=r'''
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <wchar.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE -1
#define MAXIMUM_LOCAL_PLAYERS 4
#define BUTTON_START 7
#define _client_state_pregame 3
struct player_profile{int unused;};
struct widget_instance{int unused;};
struct network_game{int maximum_players;};
static int player_spawn_count=1,reset_calls,profile_calls,profile_ok=1,errors,dispatches,failures;
static int playing=1,local_count=1,lobby_player_count=1,client_exists=1,state=3;
static struct network_game game={16};
static struct {int adding;short controller;}lobby_join={0,NONE};
static void display_error_text_deferred(const wchar_t *message,int controller){(void)controller;assert(message[0]==L'Q');errors++;}
static void player_ui_reset_single_player_local_player_controllers(void){reset_calls++;}
static boolean campaign_profile(short controller,struct player_profile *p){(void)controller;(void)p;profile_calls++;return profile_ok;}
static boolean campaign_fail(void){failures++;return FALSE;}
static int lobby_local_player_count(void){return local_count;}
static void *global_network_game_client_get(void){return client_exists?&game:NULL;}
static struct network_game *network_game_client_get_game(void *client){return client;}
static boolean lobby_controller_playing(short controller){(void)controller;return playing;}
static void ui_widget_port_dispatch_event(struct widget_instance*w,int button,int controller,boolean *deleted){(void)w;assert(button==BUTTON_START);assert(controller==0);*deleted=FALSE;dispatches++;}
static struct widget_instance *focused_leaf(struct widget_instance*w){return w;}
static int network_game_client_get_state(void*c,short*s){(void)c;*s=0;return state;}
'''
    body='\n'.join(function(source,n) for n in ['local_split_screen_allowed','coop_begin','lobby_add_player','lobby_join_start'])
    checks=r'''
int main(void){struct widget_instance widget;boolean deleted=0;
#ifdef HALO_VR
 assert(!coop_begin(0));assert(player_spawn_count==1&&reset_calls==0&&profile_calls==0&&errors==1);
 assert(!lobby_add_player());assert(!lobby_join.adding&&errors==2);
 playing=0;assert(!lobby_join_start(&widget,1,&deleted));
 assert(lobby_join.controller==NONE&&errors==3&&dispatches==0);
 // Even a disconnected or full lobby cannot mutate local ownership via this path.
 client_exists=0;assert(!lobby_join_start(&widget,1,&deleted));
 assert(lobby_join.controller==NONE&&errors==4);
 playing=1;assert(!lobby_join_start(&widget,0,&deleted));
 assert(dispatches==1&&errors==4&&!deleted); // existing player START still activates focus
 puts("Quest: local campaign, ADD PLAYER and new-controller START blocked before mutation; existing-player START preserved");
#else
 assert(coop_begin(0));assert(player_spawn_count==2&&reset_calls==1&&profile_calls==1&&!errors);
 profile_ok=0;assert(!coop_begin(0));assert(player_spawn_count==1&&reset_calls==2&&profile_calls==2&&failures==1);
 assert(lobby_add_player());assert(lobby_join.adding&&!errors);
 local_count=4;lobby_join.adding=0;assert(!lobby_add_player());assert(!lobby_join.adding&&failures==2);
 playing=0;assert(lobby_join_start(&widget,1,&deleted));assert(lobby_join.controller==1&&!errors);
 playing=1;assert(!lobby_join_start(&widget,0,&deleted));assert(dispatches==1&&!errors);
 client_exists=0;playing=0;lobby_join.controller=NONE;assert(!lobby_join_start(&widget,1,&deleted));
 assert(lobby_join.controller==NONE&&failures==3);
 puts("Flat: original two-player campaign/profile, lobby capacity, join and existing-player START behavior preserved");
#endif
}
'''
    with tempfile.TemporaryDirectory(prefix='test31-local-players-') as name:
        out=Path(name);c=out/'local.c';c.write_text(preamble+body+checks)
        cc=shutil.which('clang') or shutil.which('gcc');assert cc
        for mode in ['vr','flat']:
            binary=out/mode
            subprocess.run([cc,'-std=c11','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',*(['-DHALO_VR'] if mode=='vr' else []),str(c),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)
    render=(ROOT/'port/linux/game/vr_render.c').read_text()
    assert 'if (window_count != 2 ||' in render
    assert 'local_player_index != local_player_get_next(NONE)' in render
    for marker in ['CREATE GAME > INTERNET or LAN','then SINGLEPLAYER.']:
        assert marker in source
    print('Quest local-player boundary matches actual stereo/render ownership and provides network co-op instructions')

if __name__=='__main__':main()
