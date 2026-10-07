"""Production scoreboard presentation/settings/paging; no game or device."""
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test31-menu-presentation'
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return (ROOT / path).read_text()


def fn(text, name):
    m = re.search(r'^(?:static )?[\w *]+\b' + name + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    i = text.index('{', m.start()) + 1
    depth = 1
    while depth:
        depth += (text[i] == '{') - (text[i] == '}')
        i += 1
    return text[m.start():i] + '\n'


game = read('source/game/game_engine.c')
text = read('source/rasterizer/rasterizer_text.c')
hires = read('port/linux/src/text_hires.c')
platform = read('port/linux/src/sdl_platform.c')
xinput = read('port/linux/src/xinput_sdl.c')
xml = ET.fromstring(read('port/assets/menus/ce/main_menu.settings_select.player_setup.player_profile_edit.audio_settings.xml'))
assert any('SOUND (RESTART)' in n.get('text', '') for n in xml.iter('string'))
assert any('restarting' in n.get('text', '') for n in xml.iter('string'))
assert 'game_variant_options_valid' in game
assert 'statistic_buffer_in_game_only && player->quit_out_of_game' in fn(game, 'populate_statistic_buffer')
assert 'game_engine_scoreboard_closed();' in fn(game, 'game_engine_post_rasterize_in_game')
assert 'memset(fonts, 0, sizeof(fonts));' in fn(text, 'hires_text_font_get')
assert 'read_at != config_changes()' in fn(text, 'hires_text_font_get')
pad = fn(xinput, 'XInputGetState')
assert pad.index('platform_scoreboard_gamepad') > pad.index('vr_gamepad_state')
assert pad.index('platform_scoreboard_gamepad') < pad.index('memcmp(&state->Gamepad')
assert text.count('viewport_bounds.x0 - text_scale_origin_x) / text_scale') == 2

header = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <wchar.h>
typedef int boolean;
typedef float real;
typedef uint32_t pixel32;
typedef uint64_t Uint64;
typedef struct {short x0,y0,x1,y1;} rectangle2d;
typedef struct {real alpha,red,green,blue;} real_argb_color;
#define TRUE 1
#define FALSE 0
#define NONE -1
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define PIN(a,lo,hi) MIN(MAX(a,lo),hi)
#define MULTIPLAYER_MAXIMUM_PLAYERS 128
#define NUMBER_OF_VERTICES_PER_QUADRILATERAL 4
#define DATUM_INDEX_TO_ABSOLUTE_INDEX(x) (x)
#define csmemset memset
#define csstrcmp strcmp
static unsigned long generation;
static int background=1, enabled=1, reads;
static const char *color_string="16,16,16,150", *layout="teams";
unsigned long config_changes(void){return generation;}
int config_boolean(const char *key){reads++;return !strcmp(key,"display.high_res_text")?enabled:background;}
const char *config_string(const char *key){return strstr(key,"team_layout")?layout:color_string;}
static struct {struct {rectangle2d window_bounds,viewport_bounds;} camera;} render;
struct font_header {int leading_height,descending_height,ascending_height;};
static struct font_header font={0,0,14};
static long hud_get_font_index(void){return 0;}
static struct font_header *font_definition_get(long n){(void)n;return &font;}
static void offset_rectangle2d(rectangle2d *r,int x,int y){r->x0+=x;r->x1+=x;r->y0+=y;r->y1+=y;}
struct statistic_buffer {long player_index;};
struct player_datum {short team_index;int quit_out_of_game;wchar_t name[32];};
static struct player_datum players[128];
static struct statistic_buffer input[128];
static long count;static int teams,connection;
enum {_postgame_statistic_ranking,_game_connection_network_client,_game_connection_network_server};
static struct player_datum *player_try_and_get(long i){return i<0||i>=count?NULL:&players[i];}
static int game_engine_has_teams(void){return teams;}
static int game_connection(void){return connection;}
static boolean statistic_buffer_in_game_only;
static long populate_statistic_buffer(struct statistic_buffer *out,int stat,int flag){(void)stat;(void)flag;memcpy(out,input,count*sizeof(*out));return count;}
static long populate_campaign_player_buffer(struct statistic_buffer *out){memcpy(out,input,count*sizeof(*out));return count;}
static void format_name(wchar_t *s){s[0]=0;}
static void format_player(long i,wchar_t *s){(void)i;s[0]=0;}
static struct {void (*format_score_name)(wchar_t*);void (*format_player_score)(long,wchar_t*);} engine={format_name,format_player}, *game_engine=&engine;
static void game_engine_generate_title_string(wchar_t *s,long i){(void)i;s[0]=0;}
static int game_engine_player_is_out_of_lives(long i){(void)i;return 0;}
static wchar_t *get_place_string(struct statistic_buffer *e){(void)e;return L"";}
static long tag_loaded(int id,const char *name){(void)id;(void)name;return NONE;}
static wchar_t *unicode_string_list_get_string(long i,int j){(void)i;(void)j;return L"";}
static void usprintf(wchar_t *out,const wchar_t *format,...){(void)format;out[0]=0;}
static real_argb_color *hud_get_text_color(real_argb_color *c){*c=(real_argb_color){1,1,1,1};return c;}
long distributed_player_ping(short i){return i;}
static int panels,drawn_rows;static rectangle2d panel;static pixel32 panel_color;
void draw_quad(rectangle2d *r,pixel32 c){panels++;panel=*r;panel_color=c;}
static void scoreboard_draw_row(const wchar_t *s,boolean b,const real_argb_color *c,long row,short top,short left,boolean tabs){
 (void)s;(void)b;(void)c;(void)top;(void)left;if(tabs&&row>=2)drawn_rows++;
}
struct dynamic_screen_vertex {struct {float x,y,z,w;} position;float uv[2];};
static struct dynamic_screen_vertex captured[4];static const void *original;
static real text_scale=1,text_scale_origin_x,text_scale_origin_y;
static void rasterizer_text_draw_character(const struct dynamic_screen_vertex *v){original=v;memcpy(captured,v,sizeof(captured));}
static int input_lock,locked;static Uint64 now;
static struct {int menus,focused;} input_state={0,1};
static void pthread_mutex_lock(int *p){(void)p;assert(!locked);locked=1;}
static void pthread_mutex_unlock(int *p){(void)p;assert(locked);locked=0;}
static Uint64 SDL_GetTicks(void){return now;}
#define SCOREBOARD_OPEN_MS 250
static Uint64 scoreboard_open_until_ms,scoreboard_pad_repeat_ms;
static float scoreboard_wheel;
static long scoreboard_notches,scoreboard_pages;
static int scoreboard_pad_direction;
static long scoreboard_scroll;
static boolean scoreboard_open;
'''
sdk = read('port/include/xdk/xdk_xbox.h')
header += '\n'.join(re.search(r'^#define ' + name + r' .*$', sdk, re.M).group()
                    for name in ('XINPUT_GAMEPAD_BACK', 'XINPUT_GAMEPAD_DPAD_UP', 'XINPUT_GAMEPAD_DPAD_DOWN')) + '\n'
start = game.index('enum\n{', game.index('/* port: the scoreboard of a full-screen'))
end = game.index('/* network_distributed.c', start)
header += game[start:end]
body = fn(hires, 'text_enabled') + fn(text, 'rasterizer_text_set_scale') + fn(text, 'rasterizer_text_draw_scaled_character')
body += fn(platform, 'platform_scoreboard_scroll') + fn(platform, 'platform_scoreboard_gamepad')
body += fn(game, 'scoreboard_background_color') + fn(game, 'scoreboard_team_columns')
body += fn(game, 'game_engine_scoreboard_closed') + fn(game, 'game_engine_rasterize_scoreboard')
tests = r'''
static void test_settings(void){
 assert(text_enabled()==1);int old=reads;assert(text_enabled()==1&&reads==old);
 enabled=0;generation++;assert(!text_enabled());enabled=1;generation++;assert(text_enabled());
 assert(scoreboard_background_color()==0x96101010);
 color_string="999999999999999999999999999999999999999999999999, 1, 2, 255";generation++;
 assert(scoreboard_background_color()==0xffff0102);
 background=0;generation++;assert(!scoreboard_background_color());background=1;generation++;
 assert(scoreboard_team_columns());layout="score";generation++;assert(!scoreboard_team_columns());
 layout="teams";generation++;
 puts("PASS: live text/layout/background settings; color parsing saturates without overflow");
}
static void test_scale(void){
 struct dynamic_screen_vertex v[4]={0};for(int i=0;i<4;i++){v[i].position.x=10+i;v[i].position.y=20+i;v[i].uv[0]=i;}
 rasterizer_text_set_scale(1,0,0);rasterizer_text_draw_scaled_character(v);assert(original==v&&!memcmp(v,captured,sizeof(v)));
 rasterizer_text_set_scale(0.75f,10,20);rasterizer_text_draw_scaled_character(v);
 assert(captured[3].position.x==12.25f&&captured[3].position.y==22.25f&&captured[3].uv[0]==3);
 rasterizer_text_set_scale(INFINITY,NAN,INFINITY);assert(text_scale==1&&text_scale_origin_x==0&&text_scale_origin_y==0);
 puts("PASS: scaled text geometry, UV preservation, default identity and finite fallback");
}
static void test_input(void){
 unsigned short b=XINPUT_GAMEPAD_BACK|XINPUT_GAMEPAD_DPAD_DOWN;short y=20000;long n,p;
 platform_scoreboard_gamepad(&b,&y);assert(y==20000&&(b&XINPUT_GAMEPAD_DPAD_DOWN));
 platform_scoreboard_scroll(1,&n,&p);platform_scoreboard_gamepad(&b,&y);
 assert(y==0&&!(b&XINPUT_GAMEPAD_DPAD_DOWN));platform_scoreboard_scroll(1,&n,&p);assert(p==1);
 b=XINPUT_GAMEPAD_BACK|XINPUT_GAMEPAD_DPAD_DOWN;platform_scoreboard_gamepad(&b,&y);
 platform_scoreboard_scroll(1,&n,&p);assert(p==0);now=200;platform_scoreboard_scroll(1,&n,&p);
 now=351;b=XINPUT_GAMEPAD_BACK|XINPUT_GAMEPAD_DPAD_DOWN;platform_scoreboard_gamepad(&b,&y);
 platform_scoreboard_scroll(1,&n,&p);assert(p==1);
 b=XINPUT_GAMEPAD_BACK;y=20000;platform_scoreboard_gamepad(&b,&y);platform_scoreboard_scroll(1,&n,&p);assert(p==-1);
 b=0;y=21000;platform_scoreboard_gamepad(&b,&y);assert(y==21000);
 now+=300;b=XINPUT_GAMEPAD_BACK|XINPUT_GAMEPAD_DPAD_UP;y=22000;platform_scoreboard_gamepad(&b,&y);assert(y==22000&&(b&XINPUT_GAMEPAD_DPAD_UP));
 platform_scoreboard_scroll(0,&n,&p);assert(!p&&!n);
 puts("PASS: controller/mapped touch/VR paging gated by visible score hold; repeat, release and expiry");
}
static void test_lists(void){
 render.camera.window_bounds=(rectangle2d){0,0,640,480};render.camera.viewport_bounds=render.camera.window_bounds;
 count=128;for(int i=0;i<128;i++){input[i].player_index=i;players[i].team_index=i%2;}
 for(int mode=0;mode<3;mode++){
  teams=mode==0;game_engine=mode==2?NULL:&engine;game_engine_scoreboard_closed();
  drawn_rows=panels=0;game_engine_rasterize_scoreboard(127,0.5f);
  assert(drawn_rows>0&&drawn_rows<128&&panels==1&&panel.x0>=0&&panel.x1<=640);
  assert(text_scale==1&&scoreboard_scroll>0);
  scoreboard_pages=100000;game_engine_rasterize_scoreboard(127,1);assert(scoreboard_scroll>=0&&scoreboard_scroll<128);
  scoreboard_pages=-100000;game_engine_rasterize_scoreboard(127,1);assert(scoreboard_scroll==0);
 }
 count=0;game_engine_rasterize_scoreboard(0,1);assert(text_scale==1);
 game_engine_scoreboard_closed();assert(!scoreboard_open&&!scoreboard_open_until_ms);
 puts("PASS: 128-player team/score/co-op pages, own-player opening page, bounds, empty list and text-scale restoration");
}
int main(void){test_settings();test_scale();test_input();test_lists();return 0;}
'''
(OUT / 'presentation.c').write_text(header + body + tests)
subprocess.run(['clang', '-std=gnu11', '-O1', '-Wno-multichar', '-fsanitize=address,undefined',
                str(OUT / 'presentation.c'), '-lm', '-o', str(OUT / 'presentation')], check=True)
subprocess.run([str(OUT / 'presentation')], check=True)
