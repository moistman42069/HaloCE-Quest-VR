#!/usr/bin/env python3
"""Execute production generic keyboard and menu text lifecycle with platform stubs."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def function(source, name):
    match = re.search(r"(?m)^(?:static )?(?:boolean|void|long|wchar_t \*)\s*" + re.escape(name) + r"\([^;]*?\)\n\{", source)
    assert match, name
    end = source.index("\n}", match.end()) + 2
    return source[match.start():end]


def main():
    source = (ROOT / "source/interface/virtual_keyboard.c").read_text()
    menus = (ROOT / "port/linux/game/menu_functions.c").read_text()
    constants = source.split("/* ---------- constants */", 1)[1].split("/* ---------- macros */", 1)[0]
    globals_type = re.search(r"struct virtual_keyboard_globals\n\{.*?\n};", source, re.S).group()
    globals_data = source.split("static char const virtual_keyboard_layout_table", 1)[1].split("/* ---------- public code */", 1)[0]
    globals_data = "static char const virtual_keyboard_layout_table" + globals_data
    preamble = r'''
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
typedef unsigned char boolean;
typedef unsigned short word;
typedef unsigned char byte;
typedef struct { short y0, x0, y1, x1; } rectangle2d;
#define TRUE 1
#define FALSE 0
#define NONE -1
#define MIN(a,b) ((a)<(b)?(a):(b))
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define match_assert(file,line,condition) assert(condition)
#define csmemset memset
#define csmemmove memmove
static size_t ustrlen(const wchar_t *p) { size_t n=0; while(p[n])n++; return n; }
static wchar_t *ustrncpy(wchar_t *a,const wchar_t*b,size_t n){size_t i=0;for(;i<n&&b[i];i++)a[i]=b[i];for(;i<n;i++)a[i]=0;return a;}
static wchar_t *ustrcpy(wchar_t*a,const wchar_t*b){size_t i=0;do{a[i]=b[i];}while(b[i++]);return a;}
static int ustrcmp(const wchar_t*a,const wchar_t*b){while(*a&&*a==*b){a++;b++;}return *a-*b;}
static unsigned long now;
static unsigned long system_milliseconds(void){return now;}
static void event_manager_flush(void){}
static void ui_play_audio_feedback_sound(short sound){(void)sound;}
static int unique_calls, unique_name=1, errors;
static boolean saved_game_file_name_unique(wchar_t *name){(void)name;unique_calls++;return unique_name;}
enum {_error_already_a_saved_game_file_with_that_name=1,_error_cannot_create_saved_game_file_with_empty_name};
static void display_error(int code,int player,int modal,int pause){(void)code;(void)player;(void)modal;(void)pause;errors++;}
struct virtual_keyboard_definition {int unused;};
static wchar_t virtual_keyboard_get_current_character(void){return L'k';}
static boolean virtual_keyboard_cancel(void);
static boolean virtual_keyboard_select(void);
'''
    names = ["virtual_keyboard_launch_internal", "virtual_keyboard_launch", "virtual_keyboard_launch_text",
        "virtual_keyboard_active", "virtual_keyboard_last_exit_saved_text", "virtual_keyboard_cancel",
        "virtual_keyboard_close", "virtual_keyboard_display_text", "virtual_keyboard_free_space_in_text_buffer",
        "virtual_keyboard_backspace", "virtual_keyboard_select", "virtual_keyboard_pointer"]
    production = "\n".join(function(source, name) for name in names)
    fields = menus.split("/* ---- a text field", 1)[1]
    fields = fields[fields.index("static struct"):fields.index("static void text_field_insert")]
    adapters = r'''
#define TEXT_FIELD_LENGTH 128
#define SOUND_ERROR 4
struct widget_instance {int unused;};
struct key_stroke {int unused;};
static int input_get_key(struct key_stroke *key){(void)key;return 0;}
static void platform_text_field(int state){(void)state;}
static void platform_log(const char *format,...){(void)format;}
'''
    tests = r'''
static void choose(short key)
{
    rectangle2d bounds = keyboard_rect[key];
    virtual_keyboard_pointer((short)((bounds.x0+bounds.x1)/2),(short)((bounds.y0+bounds.y1)/2),TRUE,FALSE);
}
static int callbacks;
static char result[128];
static void completed(const char *text){callbacks++;snprintf(result,sizeof(result),"%s",text);}
int main(void)
{
    struct virtual_keyboard_definition definition;
    struct widget_instance row;
    wchar_t buffer[128], original[128], masked[128];
    int i;
    virtual_keyboard_globals.keyboard=&definition;
    for(i=0;i<100;i++) buffer[i]=original[i]=L'a';
    buffer[100]=original[100]=0;
    assert(virtual_keyboard_launch_text(buffer,sizeof(buffer),L"INVITE LINK",FALSE));
    assert(virtual_keyboard_globals.buffer_size==sizeof(buffer));
    assert(!virtual_keyboard_launch_text(buffer,sizeof(buffer),L"OVERLAP",FALSE));
    choose(_vkey_a);
    assert(buffer[0]==L'k'&&buffer[1]==0);
    virtual_keyboard_pointer(0,0,FALSE,TRUE);
    assert(!virtual_keyboard_active()&&!virtual_keyboard_last_exit_saved_text());
    assert(!ustrcmp(buffer,original)); /* cancel restores beyond legacy31characters */
    buffer[0]=0;
    assert(virtual_keyboard_launch_text(buffer,sizeof(buffer),L"PASSWORD",TRUE));
    for(i=0;i<180;i++)choose(_vkey_a);
    assert(ustrlen(buffer)==127);
    assert(virtual_keyboard_display_text(masked,128)==masked);
    assert(port_keyboard.display_start==101);
    for(i=0;i<26;i++)assert(masked[i]==L'*');
    assert(masked[26]==0);
    choose(_vkey_done);
    assert(virtual_keyboard_last_exit_saved_text()&&!virtual_keyboard_active());
    assert(unique_calls==0);
    assert(virtual_keyboard_launch_text(buffer,sizeof(buffer),L"PASSWORD",TRUE));
    choose(_vkey_backspace); /* selected initial value -> clear */
    choose(_vkey_done);
    assert(buffer[0]==0&&virtual_keyboard_last_exit_saved_text()&&unique_calls==0);
    /* Profile behavior remains the original31character cap and saved-file policy. */
    ustrcpy(buffer,L"profile");
    assert(virtual_keyboard_launch(buffer,sizeof(buffer),8));
    assert(virtual_keyboard_globals.buffer_size==64&&!port_keyboard.generic);
    choose(_vkey_backspace);choose(_vkey_done);
    assert(errors==1&&!virtual_keyboard_last_exit_saved_text());
    assert(!ustrcmp(buffer,L"profile"));
    assert(virtual_keyboard_launch(buffer,sizeof(buffer),8));
    unique_name=0;choose(_vkey_a);choose(_vkey_done);
    assert(unique_calls==1&&errors==2&&!virtual_keyboard_last_exit_saved_text());
    assert(!ustrcmp(buffer,L"profile"));
    /* Modal menu completion survives arbitrarily long editing and commits once. */
    text_field_begin_masked(&row,"old",32,completed);
    assert(text_field.native_keyboard&&text_field.masked);
    now=300000;choose(_vkey_a);choose(_vkey_done);
    pc_menu_text_input_update();pc_menu_text_input_update();
    assert(callbacks==1&&!strcmp(result,"k")&&!text_field.row);
    text_field_begin_masked(&row,"old",32,completed);
    choose(_vkey_backspace);choose(_vkey_done);pc_menu_text_input_update();
    assert(callbacks==2&&!strcmp(result,""));
    text_field_begin(&row,"before",15,completed);
    choose(_vkey_a);virtual_keyboard_close();pc_menu_text_input_update();
    assert(callbacks==2&&!text_field.row);
    text_field_begin(&row,"before",15,completed);
    choose(_vkey_a);pc_menu_text_input_reset();pc_menu_text_input_update();
    assert(callbacks==2&&!virtual_keyboard_active()&&!text_field.row);
    for(i=0;i<TEXT_FIELD_LENGTH;i++)assert(!text_field.keyboard_text[i]);
    assert(!virtual_keyboard_launch_text(buffer,0,L"bad",FALSE));
    assert(!virtual_keyboard_launch_text(buffer,3,L"bad",FALSE));
    puts("generic keyboard: limits, full cancel, masked rendering, empty password, profile isolation, pointer keys and modal lifecycle passed");
    return 0;
}
'''
    compiler = shutil.which("clang") or shutil.which("cc")
    assert compiler
    with tempfile.TemporaryDirectory(prefix="test31-text-") as temp:
        temp = Path(temp)
        harness = temp / "keyboard.c"
        harness.write_text(preamble + constants + globals_type + globals_data + production + adapters + fields + tests)
        binary = temp / "keyboard"
        subprocess.run([compiler, "-DHALO_ANDROID", "-fshort-wchar", "-std=gnu11", "-O1", "-g",
            "-fsanitize=address,undefined", str(harness), "-o", str(binary)], check=True)
        subprocess.run([str(binary)], check=True)
    # The actual render function must use only its masked display view for
    # glyphs, selection bounds and cursor widths, never the secret's glyphs.
    rendering = function(source, "virtual_keyboard_render_internal")
    assert "virtual_keyboard_display_text(masked_text" in rendering
    assert "rasterizer_draw_unicode_string(&bounds, &bounds, NULL, 0, shown_text)" in rendering
    assert "wchar_t *character = shown_text" in rendering
    assert "pc_menu_text_input_update();" in menus
    assert "!text_field.native_keyboard && system_milliseconds()" in menus


if __name__ == "__main__":
    main()
