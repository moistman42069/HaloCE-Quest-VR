"""A joined/hosted client must not be reused as the browser's search client."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test33-network-browser-lifecycle'
OUT.mkdir(parents=True, exist_ok=True)

def function(source, name):
    match = re.search(r'^[\w *]+\b' + name + r'\s*\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'

manager = (ROOT/'source/networking/network_client_manager.c').read_text()
handler = (ROOT/'source/interface/ui_widget_event_handler_functions.c').read_text()
initialize = function(handler, 'network_game_server_list_initialize')
browse = function(handler, 'ui_widget_port_browse')
assert initialize.index('dispose_global_network_game_client();') < initialize.index('create_global_network_game_client()')
assert 'game_connection_set(1);' in initialize and 'network_browser_begin();' in initialize
states = re.search(r'enum network_game_client_state\s*\{([^}]+)\}', manager, re.S)
assert states and re.match(r'\s*_network_game_client_state_searching\s*,', states.group(1))

source = r'''
#include <assert.h>
#include <stddef.h>
#include <stdarg.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
enum { _network_game_client_state_searching, _network_game_client_state_joining,
       _network_game_client_state_pregame, _network_game_client_state_ingame,
       _network_game_client_state_postgame };
enum { _port_network_game_client_state_searching = 0 };
struct network_game_client { short state; };
struct widget_instance;
struct event_record;
static struct network_game_client client;
static struct network_game_client *active_client;
static int searches;
static struct network_game_client *global_network_game_client_get(void) { return active_client; }
static short network_game_client_get_state(struct network_game_client *c, short *data) {
    if (data) *data = 0;
    return c->state;
}
static boolean network_game_server_list_initialize(struct widget_instance *w,
        struct event_record *e, boolean *deleted) {
    (void)w; (void)e; (void)deleted;
    searches++;
    client.state = _network_game_client_state_searching;
    active_client = &client;
    return TRUE;
}
static void platform_log(const char *format, ...) { (void)format; }
''' + browse + r'''
int main(void) {
    boolean deleted = FALSE;
    active_client = NULL;
    assert(ui_widget_port_browse(NULL, NULL, &deleted));
    assert(searches == 1 && active_client && active_client->state == _network_game_client_state_searching);
    assert(ui_widget_port_browse(NULL, NULL, &deleted));
    assert(searches == 1); /* an active search stays alive */
    for (short state = _network_game_client_state_joining;
         state <= _network_game_client_state_postgame; state++) {
        client.state = state;
        active_client = &client;
        assert(ui_widget_port_browse(NULL, NULL, &deleted));
        assert(searches == (int)state + 1);
        assert(active_client && active_client->state == _network_game_client_state_searching);
    }
    return 0;
}
'''

cfile = OUT/'network_browser_lifecycle.c'
executable = OUT/'network_browser_lifecycle'
cfile.write_text(source)
subprocess.run(['clang', '-std=gnu11', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                str(cfile), '-o', str(executable)], check=True)
subprocess.run([str(executable)], check=True)
print('PASS: fresh, active-search, joining, pregame, ingame and postgame browser entry states')
