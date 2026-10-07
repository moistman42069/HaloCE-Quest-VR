"""Compile production menu Save/Defaults and playlist option persistence helpers.

No device, graphics context, real profile or game data is opened.
"""
from pathlib import Path
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test31-menu-settings'
OUT.mkdir(parents=True, exist_ok=True)


def fn(text, name):
    match = re.search(r'^(?:static )?[\w *]+\b' + name + r'\s*\([^;{}]*\)\s*\{', text, re.M)
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end] + '\n'


def run(name, text, extra=(), env=None):
    path = OUT / (name + '.c')
    path.write_text(text)
    subprocess.run(['clang', '-std=gnu11', '-fsanitize=address,undefined',
                    '-fno-sanitize-recover=all', '-g', '-I', str(ROOT/'port/linux/src'),
                    '-I', str(ROOT/'port/third_party/tomlc17'), str(path), *extra,
                    '-pthread', '-lm', '-o', str(OUT/name)], check=True)
    subprocess.run([str(OUT/name)], env=env, check=True)


menu = (ROOT/'port/linux/game/menu_functions.c').read_text()
ui = (ROOT/'source/interface/ui_widget.c').read_text()
dispatch = fn(ui, 'event_handler_dispatch')
assert 'function_failed = TRUE;' in dispatch
assert re.search(r'else if \(!strcmp\(name, "port settings save"\)\)\s*\{\s*return settings_save\(widget\);', menu)
profile = menu[menu.index('static struct\n{\n\tchar const *name;'):menu.index('static byte *profile_setting_field')]
setting = menu[menu.index('struct pc_menu_setting\n{'):menu.index('struct pc_menu_setting *pc_menu_setting_get')]
prefix = r'''
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <wchar.h>
typedef unsigned char boolean, byte;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define MAXIMUM_STRINGS 64
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define _stricmp strcasecmp
#define platform_log(...) ((void)0)
struct widget_instance { int type; long definition_tag_index; struct widget_instance *child,*next,*parent;
 struct {struct {short selected_index;unsigned short number_of_items;}list;} parameters; };
struct player_profile_controller_settings {byte look_sensitivity,invert_look,flight_stick_aircraft_controls,
 autocenter,button_preset,joystick_preset,vibration_disabled,ingame_help_disabled;};
struct player_profile {struct player_profile_controller_settings controller_settings;};
static struct player_profile edit_profile, *current_profile=&edit_profile;
static struct player_profile *player_ui_get_edit_player_profile(void){return current_profile;}
static int writes, errors, applied, error_sounds, fail_write;
static char saved[32]="0.7";
static boolean config_write(const char *name,const char *value){writes++;if(fail_write&&!strcmp(name,"audio.volume"))return FALSE;snprintf(saved,sizeof(saved),"%s",value);return TRUE;}
static boolean config_default(const char *name,char *value,unsigned int size){snprintf(value,size,"%s",!strcmp(name,"display.mode")||!strcmp(name,"display.window_size")?"":!strcmp(name,"display.window_scale")?"2":"1");return TRUE;}
static boolean config_text(const char *name,char *value,unsigned int size){snprintf(value,size,"%s",saved);return TRUE;}
static boolean config_boolean(const char *name){return FALSE;}
static void platform_display_apply(void){applied++;}
static void display_error_text_deferred(const wchar_t *text,int controller){assert(wcsstr(text,L"try OK again"));errors++;}
static boolean campaign_fail(void){error_sounds++;return FALSE;}
'''
run('settings', prefix + setting + r'''
static struct pc_menu_setting settings[3] = {
 {1,"audio.volume",3,{"0","0.5","1"},0},
 {2,"profile.vibration",2,{"false","true"},0},
 {3,"profile.look_sensitivity",4,{"1","2","3","4"},0}};
static struct pc_menu_setting *pc_menu_setting_get(long tag){return tag>0&&tag<=3?&settings[tag-1]:NULL;}
''' + profile + ''.join(fn(menu, name) for name in [
    'text_is_number', 'spinner_item', 'setting_value_index', 'profile_setting_field',
    'profile_setting_boolean', 'setting_text', 'setting_write', 'setting_load',
    'settings_each', 'screen_of', 'setting_changed_save', 'settings_save', 'setting_default_show']) + r'''
int main(void){
 struct widget_instance root={0},group={0},a={.type=2,.definition_tag_index=1},
 b={.type=2,.definition_tag_index=2},c={.type=2,.definition_tag_index=3},
 item={.type=2,.definition_tag_index=1};
 a.parameters.list.number_of_items=3;b.parameters.list.number_of_items=2;c.parameters.list.number_of_items=4;
 root.child=&group;group.parent=&root;group.child=&a;a.parent=&group;a.next=&b;
 b.parent=&group;b.next=&c;c.parent=&group;a.child=&item;item.parent=&a;
 assert(setting_load(&a)&&a.parameters.list.selected_index==1&&settings[0].loaded_index==1);
 assert(setting_load(&b)&&b.parameters.list.selected_index==1);
 assert(setting_load(&item)&&item.parameters.list.selected_index==0); /* item must not load/save */
 /* Defaults only changes UI; backing config/profile and loaded indices are untouched. */
 edit_profile.controller_settings.vibration_disabled=1;
 int before=writes;assert(settings_each(&root,setting_default_show));
 assert(writes==before&&!strcmp(saved,"0.7")&&edit_profile.controller_settings.vibration_disabled==1);
 assert(a.parameters.list.selected_index==2&&b.parameters.list.selected_index==1&&c.parameters.list.selected_index==2);
 assert(settings[0].loaded_index==1&&item.parameters.list.selected_index==0);
 /* A failed first row must not short circuit later rows; retry remains possible. */
 settings[1].loaded_index=0;fail_write=1;
 assert(!settings_save(&a)&&errors==1&&error_sounds==1&&applied==0);
 assert(settings[0].loaded_index==1&&settings[1].loaded_index==1&&settings[2].loaded_index==2);
 assert(edit_profile.controller_settings.vibration_disabled==0&&edit_profile.controller_settings.look_sensitivity==3);
 fail_write=0;assert(settings_save(&a)&&applied==1&&!strcmp(saved,"1")&&settings[0].loaded_index==2);
 before=writes;assert(settings_save(&a)&&writes==before); /* unchanged is not rewritten */
 a.parameters.list.selected_index=-1;c.parameters.list.selected_index=99;
 assert(settings_save(&root)&&writes==before); /* absent/unselected rows retain prior behavior */
 current_profile=NULL;b.parameters.list.selected_index=0;
 assert(!settings_save(&root)&&settings[1].loaded_index==1&&errors==2);
 current_profile=&edit_profile;assert(settings_save(&root)&&edit_profile.controller_settings.vibration_disabled==1);
 char text[40];assert(setting_text("display.mode",text,sizeof(text),TRUE)&&!strcmp(text,"borderless"));
 assert(setting_text("display.window_size",text,sizeof(text),TRUE)&&!strcmp(text,"1280x960"));
 puts("PASS: production settings nested traversal, failed save/retry, defaults staging, unchanged/skipped rows, profile inversion");
}
''')

# Full production config code, changing only its external platform logger and
# a write primitive wrapper so ENOSPC can be injected before any actual write.
# This tests cache/generation publication; it does not claim atomic disk saves.
config_source = (ROOT/'port/linux/src/port_config.c').read_text()
writer = fn(config_source, 'config_write_file')
config_source = config_source.replace(writer.rstrip(), writer.replace('config_write_file(', 'config_write_file_actual(', 1) + r'''
static int config_test_fail_write, config_test_attempts;
static int config_write_file(const char *path, const char *text)
{
 config_test_attempts++;
 if(config_test_fail_write){errno=ENOSPC;return 0;}
 return config_write_file_actual(path,text);
}
''', 1).replace('#include "platform.h"', 'static void platform_log(const char *text, ...) {(void)text;}').replace('#include <SDL3/SDL.h>', '')
config_test = r'''
#include <assert.h>
static void reject_and_retry(const char *name,const char *changed,const char *expected)
{
 char value[200],path[1024];size_t before_size,after_size;
 unsigned long generation=config_changes();int attempts=config_test_attempts;
 config_path(path,sizeof(path));char *before=config_file_read(path,&before_size);assert(before);
 config_test_fail_write=1;assert(!config_write(name,changed));
 assert(config_test_attempts==attempts+1&&config_changes()==generation);
 assert(config_text(name,value,sizeof(value))&&!strcmp(value,expected));
 char *after=config_file_read(path,&after_size);assert(after&&after_size==before_size&&!memcmp(before,after,before_size));
 free(before);free(after);
 config_test_fail_write=0;assert(config_write(name,changed));
 assert(config_changes()==generation+1&&config_text(name,value,sizeof(value))&&!strcmp(value,changed));
}
int main(void)
{
 assert(config_write("audio.music_volume","0.375"));
 assert(config_write("browser.engine","2"));
 assert(config_write("browser.show_empty","true"));
 assert(config_write("browser.teams","any"));
 reject_and_retry("audio.music_volume","0.5","0.375");assert(config_real("audio.music_volume")==0.5);
 reject_and_retry("browser.engine","5","2");assert(config_integer("browser.engine")==5);
 reject_and_retry("browser.show_empty","false","true");assert(!config_boolean("browser.show_empty"));
 reject_and_retry("browser.teams","teams","any");assert(!strcmp(config_string("browser.teams"),"teams"));
 puts("PASS: production config failed writes retain live values/generation for real/integer/boolean/string; successful retry publishes both");
}
'''
for vr in (False, True):
    with tempfile.TemporaryDirectory(dir=OUT) as folder:
        run('config-failure-vr' if vr else 'config-failure-flat',
            '#define HALO_ANDROID 1\n' + ('#define HALO_VR 1\n' if vr else '') + config_source + config_test,
            [str(ROOT/'port/third_party/tomlc17/tomlc17.c')], dict(os.environ, HALO_DATA_ROOT=folder))

# Generated page Cancel/back handlers must never write their staged values.
pages = 0
for path in (ROOT/'port/assets/menus/ce').glob('*.xml'):
    xml = ET.parse(path).getroot()
    if not any(n.get('run') == 'port settings save' for n in xml.iter('on')):
        continue
    pages += 1
    for widget in xml.iter('widget'):
        for event in widget.findall('on'):
            if event.get('event') in ('b', 'back'):
                assert event.get('run') not in ('port settings save', 'port setting save'), path
            if event.get('run') == 'port settings save':
                assert event.get('back') == 'true', path
assert pages >= 5, pages
common = ET.parse(ROOT/'port/assets/menus/ce/shell.xml').getroot()
cancel = next(w for w in common.iter('widget') if w.get('name') == 'common_button_cancel')
assert all(n.get('run') == 'mouse emit back event' for n in cancel.findall('on'))
print(f'PASS: {pages} settings pages stage Defaults, close only after successful Save, Cancel has no write handler')

# Audit every XML name against its actual dispatch table, including inherited
# entries deliberately handled by shared widgets or replaced menu paths.
tags = (ROOT/'port/linux/game/menu_tags.c').read_text()
stock = (ROOT/'source/interface/ui_widget_event_handler_functions.c').read_text()


def table(name):
    body = tags.split('static char const *const ' + name + '[] =', 1)[1].split('};', 1)[0]
    return set(re.findall(r'"([^"\n]+)"', body))


event_names, data_names, opened = set(), set(), set()
config = (ROOT/'port/linux/src/port_config.c').read_text()
setting_keys = set()
for path in (ROOT/'port/assets/menus/ce').glob('*.xml'):
    for el in ET.parse(path).getroot().iter():
        if el.tag == 'widget' and el.get('setting'):
            key = el.get('setting')
            setting_keys.add(key)
            assert '"' + key + '"' in (profile if key.startswith('profile.') else config), key
            assert len(el.get('strings', '').split('|')) == len(el.get('values', '').split('|')), key
        if el.tag == 'on' and el.get('run'):
            event_names.add(el.get('run'))
        if el.tag == 'on' and el.get('open'):
            opened.add(el.get('open'))
        if el.tag == 'data' and el.get('input'):
            data_names.add(el.get('input'))
port_events = table('port_function_names')
port_data = table('port_game_data_input_names')
stock_events = set(re.findall(r'"([^"\n]+)"', stock.split('event_handler_function_list =', 1)[1].split('\n};', 1)[0]))
assert event_names <= port_events | stock_events
assert data_names <= port_data | table('game_data_input_names')
event_code = fn(menu, 'pc_menu_event_function_invoke')
data_code = fn(menu, 'pc_menu_game_data_function_invoke')
direct_events = set(re.findall(r'!strcmp\(name, "([^"\n]+)"\)', event_code))
direct_data = set(re.findall(r'!strcmp\(name, "([^"\n]+)"\)', data_code))
enum_events = {'port quit game', 'port setting load', 'port setting save'}
lifecycle_noops = {'color picker menu dispose', 'dispose sp level list', 'load game menu dispose',
                   'mp level list dispose', 'mp profiles list dispose', 'player profile list dispose'}
shared_or_replaced = {'mouse spinner 1wide click', 'gamespy select header',
                      'direct ip connect init', 'direct ip edit field'}
prefix_events = {n for n in event_names if n.startswith(('mp profile init ', 'mp profile set '))}
assert '!strncmp(name, "mp profile init ", 16)' in event_code
assert '!strncmp(name, "mp profile set ", 15)' in event_code
assert event_names & port_events <= direct_events | enum_events | lifecycle_noops | shared_or_replaced | prefix_events
assert data_names & port_data <= direct_data | {'common button bar update', 'direct ip connect update'}
assert not any('direct_ip_screen' in path for path in opened)  # replaced by direct-link browser
assert 'child->disabled = !browser_item_usable(child);' in fn(menu, 'browser_initialize')
assert 'visible_set(named(screen, "header_sort_arrows", index), FALSE);' in fn(menu, 'browser_initialize')
assert 'ui_widgets_process_mouse' in ui  # native shared pointer path, also covers spinners
assert 'event_manager_post_button(controller, BUTTON_B);' in event_code
print(f'PASS: every XML handler name mapped ({len(event_names)} event names, {len(data_names)} data names); inherited no-ops are explicitly classified')
print(f'PASS: {len(setting_keys)} XML setting keys present in configuration/profile tables with matched label/value counts')

playlist = (ROOT/'source/saved games/playlist_profile.c').read_text()
engine = (ROOT/'source/game/game_engine.c').read_text()
header = (ROOT/'source/game/game_engine.h').read_text()
options = header[header.index('enum\n{\n\t_friendly_fire_on'):header.index('\nstruct game_engine\n{')]
extension_header = playlist[playlist.index('struct playlist_profile_options_header\n{'):playlist.index('static boolean playlist_profile_options_from_block(', playlist.index('struct playlist_profile_options_header\n{'))]
# Guest/XDK unsigned long is 32-bit; the host harness gives this disk field the exact guest width.
extension_header = extension_header.replace('unsigned long magic;', 'uint32_t magic;')
constants = 'enum {\n' + '\n'.join(line for line in playlist.splitlines() if re.match(r'\s+PLAYLIST_PROFILE_OPTIONS_\w+ =', line)) + '\n};'
run('playlist', r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef unsigned char byte,boolean;typedef unsigned short word;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define csmemcpy memcpy
#define csmemset memset
#define csmemcmp memcmp
#define TEST_FLAG(v,b) ((v)&(1u<<(b)))
#define PIN(v,a,b) ((v)<(a)?(a):((v)>(b)?(b):(v)))
#define _game_variant_draw_object_in_motion_sensor_bit 0
#define _saved_game_file_index_valid_bit 5
#define SAVED_GAME_FILE_BLOCK_SIZE 4096
#define match_assert(path,line,value) assert(value)
typedef struct {byte bytes[20];} XCALCSIG_SIGNATURE;
struct game_variant {struct {int flags,vehicle_set;}universal_variant;};
/* Deterministic checksum mock tests framing/tamper/fallback; it does not replace the production checksum algorithm. */
static void saved_game_file_generate_checksum(byte *data,unsigned long size,XCALCSIG_SIGNATURE *result){
 uint32_t h=2166136261u;for(unsigned long i=0;i<size;i++)h=(h^data[i])*16777619u;
 for(int i=0;i<20;i++)result->bytes[i]=(byte)(h>>(8*(i%4)));
}
''' + options + constants + '\n' + extension_header + ''.join(fn(engine, name) for name in ['game_variant_options_valid', 'game_variant_options_default']) + ''.join(fn(playlist, name) for name in ['playlist_profile_options_from_block', 'playlist_profile_options_to_block']) + r'''
static byte disk[SAVED_GAME_FILE_BLOCK_SIZE];static int read_ok=1,read_count;
static boolean playlist_profile_read_block(long index,byte *block){read_count++;if(!read_ok)return FALSE;memcpy(block,disk,sizeof(disk));return TRUE;}
static struct {void *thread;} playlist_profile_globals;
static struct game_variant_options playlist_profile_write_options, written;
static int polls,disposed,write_count,cleanup_count;
static boolean thread_has_exited(void *thread){assert(thread);assert(playlist_profile_write_options.time_limit==7);return ++polls>=2;}
static void dispose_thread(void *thread){assert(thread);disposed++;}
static void game_engine_variant_cleanup(struct game_variant *v){assert(v);cleanup_count++;}
static void playlist_profile_write(long index,struct game_variant *variant){assert(index==32&&variant&&!playlist_profile_globals.thread);written=playlist_profile_write_options;write_count++;}
''' + ''.join(fn(playlist, name) for name in ['playlist_profile_get_options', 'playlist_profile_save_with_options', 'playlist_profile_save']) + r'''
static void put(struct game_variant_options *o){memset(disk,0,sizeof(disk));((struct game_variant*)disk)->universal_variant.vehicle_set=3;playlist_profile_options_to_block(disk,o);}
int main(void){
 struct game_variant_options original,loaded;struct game_variant variant={0};
 assert(sizeof(struct playlist_profile_options_header)==8&&sizeof(original)==28);
 game_variant_options_default(NULL,&original);original.time_limit=12;original.friendly_fire_penalty=30;
 original.vehicle_respawn_time=90;original.vehicle_set[1]=255;original.vehicle_counts[1][5]=4;
 put(&original);assert(playlist_profile_options_from_block(disk,&loaded)&&!memcmp(&original,&loaded,sizeof(loaded)));
 assert(playlist_profile_get_options(32,&loaded)&&loaded.time_limit==12);
 disk[PLAYLIST_PROFILE_OPTIONS_OFFSET+8]^=1;assert(!playlist_profile_options_from_block(disk,&loaded));
 assert(playlist_profile_get_options(32,&loaded)&&loaded.time_limit==0&&loaded.vehicle_set[0]==3);
 put(&original);disk[PLAYLIST_PROFILE_OPTIONS_OFFSET+4]=99;assert(!playlist_profile_options_from_block(disk,&loaded));
 put(&original);disk[PLAYLIST_PROFILE_OPTIONS_OFFSET+6]=0;assert(!playlist_profile_options_from_block(disk,&loaded));
 put(&original);disk[PLAYLIST_PROFILE_OPTIONS_OFFSET]=0;assert(!playlist_profile_options_from_block(disk,&loaded));
 memset(disk,0,sizeof(disk));assert(playlist_profile_get_options(32,&loaded)&&game_variant_options_valid(&loaded)); /* legacy */
 int reads=read_count;assert(!playlist_profile_get_options(NONE,&loaded)&&read_count==reads&&loaded.primary_weapon==2);
 assert(!playlist_profile_get_options(0,&loaded)&&read_count==reads);read_ok=0;assert(!playlist_profile_get_options(32,&loaded));read_ok=1;
 /* Valid checksums must not bypass production bounds. */
 for(int fault=0;fault<6;fault++){
  struct game_variant_options bad=original;
  if(fault==0)bad.time_limit=-1;if(fault==1)bad.friendly_fire_penalty=601;
  if(fault==2)bad.vehicle_respawn_time=3601;if(fault==3)bad.vehicle_counts[0][5]=5;
  if(fault==4)bad.vehicle_set[1]=8;if(fault==5)bad.auto_team_balance=255;
  put(&bad);assert(!playlist_profile_options_from_block(disk,&loaded));
  assert(playlist_profile_get_options(32,&loaded)&&game_variant_options_valid(&loaded)&&loaded.time_limit==0);
 }
 struct game_variant_options legacy=original;legacy.primary_weapon=255;legacy.secondary_weapon=255;
 legacy.friendly_fire=99;legacy.radar_players=255;legacy.loadout=255;legacy.no_map_weapons=255;
 put(&legacy);assert(playlist_profile_options_from_block(disk,&loaded)&&game_variant_options_valid(&loaded));
 assert(loaded.primary_weapon==6&&loaded.secondary_weapon==6&&loaded.no_map_weapons==1);
 playlist_profile_write_options.time_limit=7;playlist_profile_globals.thread=(void*)1;
 playlist_profile_save_with_options(32,&variant,&original);
 assert(polls==2&&disposed==1&&write_count==1&&cleanup_count==1&&!memcmp(&original,&written,sizeof(written)));
 playlist_profile_save_with_options(NONE,&variant,&original);assert(write_count==1&&cleanup_count==1);
 put(&original);playlist_profile_save(32,&variant);assert(write_count==2&&written.time_limit==12);
 puts("PASS: production playlist option roundtrip, legacy defaults, corruption/version/size, normalized legacy values, invalid fields and serialized writer handoff");
}
''')
