"""Test31: OpenCE build 145/network 22 and scoped Quest regressions.
Device play is still required; these checks establish protocol/source and logic invariants.
"""
from pathlib import Path
import hashlib, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
def read(p): return (ROOT/p).read_text()
def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'
limits=read('port/linux/include/halo_port_limits.h')
for suffix in ('','_MINIMUM','_MAXIMUM'):
    assert re.search(r'#define HALO_PORT_NETWORK_VERSION%s 22\b' % suffix, limits)
UPSTREAM_145 = [('port/linux/game/coop_enemies.c', '64288778915265ec598613e1bb982f27330953b4b4f5dd7af41244e26c4a7f2a'), ('port/linux/game/coop_enemies.h', '8984e3e416e5f6fa1c743313e57fc5de87fc9a2a47be488be667865808a05a68'), ('port/linux/game/coop_scripts.c', '756652fd7f6bbad39e0accef5fc199748800354ed647c1e218228a346ab80284'), ('port/linux/game/coop_scripts.h', 'a105eef852039f01d80cdde8e1f888c32d723fe0cbd98fd5aa27b6efc2ef3947'), ('port/linux/game/coop_spectate.c', '8ed6ccee0a4881e61b533a93b4621f236ae78b88703fd08203de36fa1bdb5afe'), ('port/linux/game/coop_spectate.h', '6c73fce2dfd2bbb300f784f4ed393053db1978e5b5a984d7dd8c1fa75eb58035'), ('port/linux/game/network_actors.c', 'beaa436a7da1d9e3c9efb83e796a6d7ccbe80d61ac19814b219031577dfdc4f4'), ('port/linux/game/network_coop.h', 'ff29c9fae0f03a3686342766ead3557f0aa7c4b4eaa9932dbf4c3a8724acf1d0'), ('port/linux/game/network_damage.c', 'c00195f62854a8bb8148f1971d13ba0dd53a14275c8f4eb633ff3b01081073d7'), ('source/networking/network_client_manager.h', 'a0b2b1d2ef0245b3cc5f9dfb6b735f1b30ec0ae7dc0fc8df06060e6ee28912f1'), ('source/networking/network_client_message_handler.c', '89cd5d3c8963cfaa0cf5b410e3de66b4d4366bade65059a6b46af6432b03f0a6'), ('source/networking/network_client_message_handler.h', '4e65c098f5319897418237324e40f66a41cafe49df86d968ffdc6c781108691f'), ('source/networking/network_connection.c', '69da59f00b832a23673391de46ce87777f4f1e5bc959b0e8242a748d80704ae5'), ('source/networking/network_connection.h', '9a11ece195c463d5ab7a79395e843a3c0c83d4d26909d6625ce810613723b077'), ('source/networking/network_game_globals.h', 'a28d5c2f842015da03414f031b10bd8f5c34af24190722b1b494f88a4418f95f'), ('source/networking/network_game_manager.c', '661f390bb974d50213d062f31cf2c9ddc2588634b35324c98d4986d31809b92e'), ('source/networking/network_game_manager.h', '204beda14791cc65d729247711af3b61f20e5dbbfd04386cf7bac58e4a61ad1e'), ('source/networking/network_game_preferences.c', '109ea168784432e85e70eee3e86e74107d2c6ec36220982ecde96a0a3a59e68a'), ('source/networking/network_game_protocol.h', 'c7a4ab43c54b02cb96921b04ac670f90d185ab2c60ae58309a616c70d21a8b2e'), ('source/networking/network_game_ui.c', 'd3ed3ab54f1e0ca70e9a64f856f617320a23f3ae26fa75d6dbe6e7e4fb5ef901'), ('source/networking/network_game_ui.h', 'd1bcda47270cd85ff303f0ec1503b38c4900bcd8f01d48410a2997efdb4e4d21'), ('source/networking/network_messages.c', '82846ccd5f3686652e94dee3661b8d5e214d8866da8c1c12e5b62d3b5a8ab1a3'), ('source/networking/network_messages.h', 'daea3a6af2f0a925e27a98f6899c741bf95ed366c9144a689801ba90cdc6aa27'), ('source/networking/network_server_manager_internal.h', '59520fef12c538c7546d9367bc64b8da18d9fff2c07fc65911df249be133b664'), ('source/networking/network_server_message_handler.c', 'e14eb1ed0a60404685d9a0653892d3be327bbaf1c9241804962bae45ad88597d'), ('source/networking/network_server_message_handler.h', '1641cb2ad5ecd9af74ba8e8090eda13aa9fbe3389c83c1c98a1c20ea61c1a6a0'), ('source/networking/telnet_console.c', 'c13de6b6c23b2d2ba8e020bba499b2f7d0afe7baa8117d80ab859a96d1e93372'), ('source/networking/telnet_console.h', '45d366a413de2c53a2781afc79484c90d12ca67847d5ba05dd6d1afa193dedf3')]
for path,digest in UPSTREAM_145:
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
client=read('source/networking/network_client_manager.c')
assert '!cache_files_map_present(message_packet->map.name)' in client
assert 'CUSTOM_EDITION_LEVEL_NAME_PREFIX "%s"' in read('port/linux/game/custom_edition_maps.c')
cache=read('source/cache/cache_files.c')
assert 'custom_edition_level_name(scenario_name) || custom_edition_cache_playable(stripped_scenario_name)' in cache
assert 'pal_tags_loaded(cache_file_globals.header.build)' in cache
assert 'OPENSAUCE_MAP_FILE_EXTENSION' in read('port/linux/game/custom_edition_cache.c')
assert 'display_error_text_when_main_menu_loaded(error_text)' in fn(cache,'cache_files_map_present')
assert 'cache_files_precache_map_loaded(map_name)' in fn(cache,'cache_files_map_present')
assert 'return custom_edition_cache_playable(map_name);' in fn(read('source/cache/cache_files_windows.c'),'cache_files_precache_map_loaded')
assert 'ui_widget_port_text_wrap' in read('source/interface/ui_widget.c')
print('PASS: network 22 exact; %d networking files identical to pinned OpenCE build 145; map namespace/preflight, PAL and legacy loader retained' % len(UPSTREAM_145))
