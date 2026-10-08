"""Exercise host-24/client-target profiles and mode-aware native join gates."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def function(source, name):
    match = re.search(r"^(?:static )?(?:inline )?[\w *]+\b" + re.escape(name) + r"\s*\([^;{]*\)\s*\{", source, re.M)
    assert match, name
    start = source.index("{", match.start())
    depth, end = 1, start + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end]


limits = read("port/linux/include/halo_port_limits.h")
assert re.search(r"^#define HALO_PORT_NETWORK_VERSION 24$", limits, re.M)
assert re.search(r"^#define HALO_PORT_NETWORK_VERSION_MINIMUM 11$", limits, re.M)
assert re.search(r"^#define HALO_PORT_NETWORK_VERSION_MAXIMUM 24$", limits, re.M)
assert re.search(r"^#define HALO_PORT_CAMPAIGN_NETWORK_VERSION_MINIMUM 23$", limits, re.M)
assert re.search(r"^#define HALO_PORT_CUSTOM_EDITION_NETWORK_VERSION_MINIMUM 23$", limits, re.M)
assert "int halo_port_active_network_version(void);" in limits

config = read("port/linux/src/port_config.c")
assert '{ "network.protocol_version", _config_integer, "24"' in config
assert "pthread_mutex_lock(&active_network_version_lock)" in config
assert "active_network_version_initialized" in config
assert "configured == 0" in function(config, "network_protocol_version_resolve")
resolve = function(config, "network_protocol_version_resolve")
initialize = function(config, "active_network_version_initialize")
active_getter = function(config, "halo_port_active_network_version")

p2p = read("port/linux/src/p2p_lobby.c")
listing_make = function(p2p, "listing_make")
listing_filter = function(p2p, "listing_version_matches_target")
assert "HALO_PORT_NETWORK_VERSION >> 8" in listing_make
assert "bytes[size++] = (unsigned char)HALO_PORT_NETWORK_VERSION;" in listing_make
assert "halo_port_active_network_version()" not in listing_make
assert "target == 0 || version == target" in listing_filter
assert "HALO_PORT_NETWORK_VERSION_MINIMUM" in listing_filter
assert "HALO_PORT_NETWORK_VERSION_MAXIMUM" in listing_filter
assert "0=all compatible" in p2p

server_handler = read("source/networking/network_server_message_handler.c")
advertise = function(server_handler, "network_game_server_handle_message_client_broadcast_game_search")
assert "HALO_PORT_NETWORK_VERSION & 0xFF" in advertise
assert "HALO_PORT_NETWORK_VERSION >> 8" in advertise
assert "halo_port_active_network_version()" not in advertise
assert "network_game_settings_protocol_valid" not in server_handler

client = read("source/networking/network_client_manager.c")
target_match = function(client, "network_protocol_target_allows_version")
custom_map_match = function(client, "network_advertised_map_is_custom_edition")
compatibility = function(client, "network_game_client_advertised_game_compatible")
assert "HALO_PORT_CAMPAIGN_NETWORK_VERSION_MINIMUM" in compatibility
assert "HALO_PORT_CUSTOM_EDITION_NETWORK_VERSION_MINIMUM" in compatibility
assert "game->engine_type == game_engine_none" in compatibility
assert "game->map.version != 0" in compatibility
assert '"custom_maps\\\\"' in custom_map_match
assert "network protocol target" not in compatibility.lower() or "target" in compatibility
assert "halo_port_active_network_version()" in compatibility
settings_updated = function(client, "network_game_client_game_settings_updated")
assert "game_variant_options_valid" not in settings_updated
assert "halo_port_active_network_version()" not in settings_updated
transition_gate = function(client, "network_game_client_settings_version_compatible")
assert "HALO_PORT_CAMPAIGN_NETWORK_VERSION_MINIMUM" in transition_gate
assert "HALO_PORT_CUSTOM_EDITION_NETWORK_VERSION_MINIMUM" in transition_gate
assert "network_game_client_joined_host_version" in settings_updated
assert settings_updated.index("network_game_client_settings_version_compatible") < settings_updated.index("cache_files_map_present")
assert "network_game_abort()" in settings_updated and "network_game_client_reset(client, TRUE)" in settings_updated
assert "platform_show_message" in settings_updated
join_host_version = function(client, "network_game_client_host_version_for_join")
record_join = function(client, "network_game_client_record_joined_host_version")
clear_join = function(client, "network_game_client_clear_joined_host_version")
initiate_join = function(client, "network_game_client_initiate_join_game")
reset_client = function(client, "network_game_client_reset")
dispose_client = function(client, "network_game_client_dispose")
assert "network_game_client_advertised_versions[index].version" in join_host_version
assert "global_network_game_server_get() ? HALO_PORT_NETWORK_VERSION : 0" in join_host_version
assert "network_game_client_clear_joined_host_version()" in initiate_join
assert "network_game_client_record_joined_host_version(client, game)" in initiate_join
assert initiate_join.index("if (success == TRUE)") < initiate_join.index("network_game_client_record_joined_host_version")
assert "network_game_client_clear_joined_host_version()" in reset_client
assert "network_game_client_clear_joined_host_version()" in dispose_client

engine = read("source/game/game_engine.c")
variant_validation = function(engine, "game_variant_options_valid")
assert "halo_port_active_network_version()" not in variant_validation
assert "VARIANT_VEHICLE_SET_PC" in variant_validation
server_manager = read("source/networking/network_server_manager.c")
assert "halo_port_active_network_version()" not in function(server_manager, "network_game_server_start_network_game")
menu = read("port/linux/game/menu_functions.c")
assert "vehicle_preset_is_unsupported_for_network23" not in menu

fixture = r'''#include <assert.h>
#include <ctype.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define HALO_PORT_NETWORK_VERSION 24
#define HALO_PORT_NETWORK_VERSION_MINIMUM 11
#define HALO_PORT_NETWORK_VERSION_MAXIMUM 24
#define HALO_PORT_CAMPAIGN_NETWORK_VERSION_MINIMUM 23
#define HALO_PORT_CUSTOM_EDITION_NETWORK_VERSION_MINIMUM 23
#define HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG 0x01
#define HALO_PORT_ADVERTISED_IN_PROGRESS_FLAG 0x02
typedef int boolean;
typedef unsigned char byte;
typedef unsigned short word;
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define MAXIMUM_NETWORK_ADVERTISED_GAMES 4
#define csprintf sprintf
#define network_event(...) ((void)0)
enum { game_engine_none = 0 };
struct network_game_map { char name[32]; unsigned long version; };
struct network_game { struct network_game_map map; struct { int game_engine_index; } variant; };
struct network_advertised_game { int unused; short engine_type; struct network_game_map map; };
struct network_game_client { struct network_advertised_game available_games[4]; };
static struct { unsigned int version, flags; } network_game_client_advertised_versions[4];
static unsigned int network_game_client_joined_host_version;
static pthread_mutex_t active_network_version_lock = PTHREAD_MUTEX_INITIALIZER;
static int active_network_version = HALO_PORT_NETWORK_VERSION;
static int active_network_version_initialized;
static long configured_profile = HALO_PORT_NETWORK_VERSION;
static int logs, messages;
static char last_message[400];
static int thread_targets[10];
static int local_host_present;
int halo_port_active_network_version(void);
void *global_network_game_server_get(void) { return local_host_present ? (void *)1 : NULL; }
static void platform_log(const char *format, ...) { (void)format; ++logs; }
static long config_integer(const char *name) { assert(strcmp(name, "network.protocol_version") == 0); return configured_profile; }
static void platform_show_message(const char *title, const char *message) { (void)title; ++messages; snprintf(last_message, sizeof(last_message), "%s", message); }
static int _strnicmp(const char *a,const char *b,size_t n){for(size_t i=0;i<n;i++){int x=tolower((unsigned char)a[i]),y=tolower((unsigned char)b[i]);if(x!=y||!x||!y)return x-y;}return 0;}
static void *target_thread(void *arg){long i=(long)arg;thread_targets[i]=halo_port_active_network_version();return NULL;}
''' + resolve + "\n" + initialize + "\n" + active_getter + "\n" + listing_filter + "\n" + custom_map_match + "\n" + target_match + "\n" + compatibility + "\n" + join_host_version + "\n" + record_join + "\n" + clear_join + "\n" + transition_gate + r'''
int main(int argc, char **argv) {
    long requested = argc > 1 ? atol(argv[1]) : HALO_PORT_NETWORK_VERSION;
    configured_profile = requested;
    int expected_target = requested == 0 || (requested >= HALO_PORT_NETWORK_VERSION_MINIMUM && requested <= HALO_PORT_NETWORK_VERSION_MAXIMUM)
        ? (int)requested : HALO_PORT_NETWORK_VERSION;
    int before_resolve = logs;
    assert(network_protocol_version_resolve(requested) == expected_target);
    assert(logs == before_resolve + (expected_target == requested ? 0 : 1));
    pthread_t threads[10];
    for (long i = 0; i < 10; i++) assert(pthread_create(&threads[i], NULL, target_thread, (void *)i) == 0);
    for (long i = 0; i < 10; i++) { assert(pthread_join(threads[i], NULL) == 0); assert(thread_targets[i] == expected_target); }
    assert(halo_port_active_network_version() == expected_target);
    int startup_logs = logs;
    assert(startup_logs == before_resolve + (expected_target == requested ? 1 : 3));
    configured_profile = expected_target == HALO_PORT_NETWORK_VERSION ? 11 : HALO_PORT_NETWORK_VERSION;
    assert(halo_port_active_network_version() == expected_target);
    assert(logs == startup_logs); /* selected client target is immutable until restart */

    for (long version = 0; version <= 26; version++) {
        int expected = version >= HALO_PORT_NETWORK_VERSION_MINIMUM && version <= HALO_PORT_NETWORK_VERSION_MAXIMUM &&
            (expected_target == 0 || version == expected_target);
        assert(listing_version_matches_target((int)version) == expected);
        assert(network_protocol_target_allows_version((unsigned)expected_target, (unsigned)version) == expected);
    }
    assert(!listing_version_matches_target(0xCE01));
    assert(!network_protocol_target_allows_version(0, 0));
    assert(!network_protocol_target_allows_version(25, 24));
    for (long bad = -1; bad <= 26; bad++) {
        int supported = bad == 0 || (bad >= HALO_PORT_NETWORK_VERSION_MINIMUM && bad <= HALO_PORT_NETWORK_VERSION_MAXIMUM);
        assert(network_protocol_version_resolve(bad) == (supported ? bad : HALO_PORT_NETWORK_VERSION));
    }

    struct network_game_client client = {0};
    for (int remote = 0; remote <= 28; remote++) for (int flags = 0; flags < 4; flags++)
        for (int engine = 0; engine < 3; engine++) for (int custom = 0; custom < 2; custom++) {
            client.available_games[0].engine_type = (short)engine;
            client.available_games[0].map.version = custom ? 1234 : 0;
            network_game_client_advertised_versions[0].version = (unsigned)remote;
            network_game_client_advertised_versions[0].flags = (unsigned)flags;
            int target_match = remote >= HALO_PORT_NETWORK_VERSION_MINIMUM && remote <= HALO_PORT_NETWORK_VERSION_MAXIMUM &&
                (expected_target == 0 || remote == expected_target);
            int expected = target_match && (flags & HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG) &&
                (engine != game_engine_none || remote >= HALO_PORT_CAMPAIGN_NETWORK_VERSION_MINIMUM) &&
                (!custom || remote >= HALO_PORT_CUSTOM_EDITION_NETWORK_VERSION_MINIMUM);
            assert(network_game_client_advertised_game_compatible(&client, &client.available_games[0], FALSE) == expected);
        }
    for (int retired = 0xCE01; retired <= 0xCE02; retired++) for (int flags = 0; flags < 4; flags++) {
        network_game_client_advertised_versions[0].version = (unsigned)retired;
        network_game_client_advertised_versions[0].flags = (unsigned)flags;
        assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[0], FALSE));
    }
    network_game_client_advertised_versions[0].version = 22;
    network_game_client_advertised_versions[0].flags = HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG;
    client.available_games[0].engine_type = 2;
    client.available_games[0].map.version = 1234;
    int before;
    if (expected_target == 0 || expected_target == 22) {
        before = messages;
        assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[0], TRUE));
        assert(messages == before + 1 && strstr(last_message, "Custom Edition map requires network version 23"));
        client.available_games[0].map.version = 0;
        snprintf(client.available_games[0].map.name, sizeof(client.available_games[0].map.name), "CUSTOM_MAPS\\legacy");
        before = messages;
        assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[0], TRUE));
        assert(messages == before + 1 && strstr(last_message, "Custom Edition map requires network version 23"));
        client.available_games[0].map.name[0] = 0;
        client.available_games[0].map.version = 0;
        client.available_games[0].engine_type = game_engine_none;
        before = messages;
        assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[0], TRUE));
        assert(messages == before + 1 && strstr(last_message, "Campaign co-op requires network version 23"));
    }
    network_game_client_advertised_versions[0].version = 0;
    client.available_games[0].engine_type = 2;
    before = messages;
    assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[0], TRUE));
    assert(messages == before + 1 && strstr(last_message, "does not advertise a supported network version"));
    assert(!network_game_client_advertised_game_compatible(NULL, NULL, FALSE));
    assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[4], FALSE));

    /* The host version is captured for the selected slot at join start, not
       read back from the mutable browser list during lobby settings updates. */
    network_game_client_clear_joined_host_version();
    network_game_client_advertised_versions[1].version = 22;
    network_game_client_record_joined_host_version(&client, &client.available_games[1]);
    assert(network_game_client_joined_host_version == 22);
    network_game_client_clear_joined_host_version();
    assert(network_game_client_joined_host_version == 0);
    struct network_game local_game = {0};
    local_host_present = 1;
    network_game_client_record_joined_host_version(&client, (struct network_advertised_game *)&local_game);
    assert(network_game_client_joined_host_version == HALO_PORT_NETWORK_VERSION);
    local_host_present = 0;
    network_game_client_record_joined_host_version(&client, (struct network_advertised_game *)&local_game);
    assert(network_game_client_joined_host_version == 0);

    /* Transition checks preserve old-host PvP, reject old-host campaign/CE,
       and retain exact version-23/24 behavior. */
    struct network_game update = {0};
    update.variant.game_engine_index = 2;
    snprintf(update.map.name, sizeof(update.map.name), "bloodgulch");
    for (int remote = 0; remote <= 24; remote++) {
        int campaign_allowed = remote >= HALO_PORT_CAMPAIGN_NETWORK_VERSION_MINIMUM;
        int ce_allowed = remote >= HALO_PORT_CUSTOM_EDITION_NETWORK_VERSION_MINIMUM;
        assert(network_game_client_settings_version_compatible((unsigned)remote, &update));
        update.variant.game_engine_index = game_engine_none;
        assert(network_game_client_settings_version_compatible((unsigned)remote, &update) == campaign_allowed);
        update.variant.game_engine_index = 2;
        snprintf(update.map.name, sizeof(update.map.name), "CUSTOM_MAPS\\legacy");
        update.map.version = 0; /* old CE advertisements have no checksum field */
        assert(network_game_client_settings_version_compatible((unsigned)remote, &update) == ce_allowed);
        update.map.name[0] = 0;
        update.map.version = 1234;
        assert(network_game_client_settings_version_compatible((unsigned)remote, &update) == ce_allowed);
        update.map.version = 0;
    }
    puts("PASS: config cache, host-24 advertising, PvP 11..24, campaign/CE 23+ admission and post-join transition guard with fresh host-version capture");
}
'''

out = ROOT / "build/test37"
out.mkdir(parents=True, exist_ok=True)
cfile, binary = out / "native_profiles.c", out / "native_profiles"
cfile.write_text(fixture, encoding="utf-8")
subprocess.run(["clang", "-std=gnu11", "-O1", "-Wall", "-Wextra", "-Wno-unused-function",
                "-Wno-unused-parameter", "-fsanitize=address,undefined", str(cfile), "-pthread", "-o", str(binary)], check=True)
for target in [0, *range(11, 25), -1, 10, 25, 65535]:
    subprocess.run([str(binary), str(target)], check=True)

print("PASS: native discovery and admission use client target selection while the host remains protocol 24")
