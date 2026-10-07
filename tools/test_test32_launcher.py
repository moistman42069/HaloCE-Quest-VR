#!/usr/bin/env python3
"""Check current launcher routes against the real OpenCE menus and compile its Java.

No Android app, clipboard, live server, game or APK is started. Menu UI and
clipboard behavior still require device validation.
"""
from pathlib import Path
import base64
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'port/android/app/src/main/java/com/halo/decomp'
MENUS = ROOT / 'port/assets/menus/ce'


def java_method(source, name):
    match = re.search(r'    static [\w<> ,]+\b' + name + r'\([^;{]*\)(?: throws \w+)? \{', source)
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end]


def check_launch_storage_and_geometry(help_source):
    methods = '\n'.join(java_method(help_source, name) for name in
        ['geometryMigrationKey', 'geometrySafe', 'saveGeometry'])
    check = '''package com.halo.decomp;
import java.io.*;
import java.nio.file.*;
import java.util.*;
class LauncherStateCheck {
 static int checks;
 static void check(boolean ok){checks++;if(!ok)throw new AssertionError("check "+checks);}
 interface Op {void run() throws Exception;}
 static void fails(Op op)throws Exception{boolean failed=false;try{op.run();}catch(IOException e){failed=true;}check(failed);}
 METHODS
 public static void main(String[] args)throws Exception{
  Path base=Path.of(args[0]),root=Files.createDirectory(base.resolve("active"));
  File folder=root.toFile();Path other=Files.createDirectory(base.resolve("other-set"));
  byte[] command={0,1,2,100,-1};
  Files.writeString(root.resolve("config.toml"),"# preserved\\n[vr]\\nbody=\\"legs\\"\\n");
  Files.createDirectories(root.resolve("save"));Files.writeString(root.resolve("save/progress"),"save");
  check(LauncherRequests.retire(folder)==0);check(!Files.exists(root.resolve("launcher-history")));
  for(String name:new String[]{"coop_host.txt","pvp_host.txt","join_link.txt"}){
   Files.write(root.resolve(name),command);Files.write(other.resolve(name),command);
  }
  check(LauncherRequests.retire(folder)==3);
  Path history=root.resolve("launcher-history"),batch;
  try(var entries=Files.list(history)){batch=entries.findFirst().orElseThrow();}
  for(String name:new String[]{"coop_host.txt","pvp_host.txt","join_link.txt"}){
   check(!Files.exists(root.resolve(name)));check(Arrays.equals(Files.readAllBytes(batch.resolve(name)),command));
   check(Arrays.equals(Files.readAllBytes(other.resolve(name)),command));
  }
  check(Files.readString(root.resolve("save/progress")).equals("save"));
  check(Files.readString(root.resolve("config.toml")).contains("body=\\"legs\\""));
  check(LauncherRequests.retire(folder)==0);
  try(var entries=Files.list(history)){check(entries.count()==1);}
  Files.write(root.resolve("join_link.txt"),new byte[]{42});check(LauncherRequests.retire(folder)==1);
  check(Arrays.equals(Files.readAllBytes(batch.resolve("join_link.txt")),command));
  Files.createDirectory(root.resolve("coop_host.txt"));fails(()->LauncherRequests.retire(folder));
  check(Files.isDirectory(root.resolve("coop_host.txt")));Files.delete(root.resolve("coop_host.txt"));
  fails(()->LauncherRequests.retire(null));
  Path blocked=Files.createDirectory(base.resolve("blocked"));Files.write(blocked.resolve("pvp_host.txt"),command);
  Files.writeString(blocked.resolve("launcher-history"),"not a directory");fails(()->LauncherRequests.retire(blocked.toFile()));
  check(Arrays.equals(Files.readAllBytes(blocked.resolve("pvp_host.txt")),command));
  Path linked=Files.createDirectory(base.resolve("linked"));Files.write(linked.resolve("pvp_host.txt"),command);
  Files.createSymbolicLink(linked.resolve("launcher-history"),other);fails(()->LauncherRequests.retire(linked.toFile()));
  check(Files.exists(linked.resolve("pvp_host.txt")));
  Path cfg=root.resolve("config.toml");
  for(boolean vr:new boolean[]{false,true}){
   String key=geometryMigrationKey(vr),otherKey=geometryMigrationKey(!vr);
   for(String revision:new String[]{"0","-1","oops","\\"1\\""}){
    Files.writeString(cfg,"[renderer]\\nsafe_geometry=false\\n"+key+"="+revision+"\\n");check(geometrySafe(folder,vr));
   }
   Files.writeString(cfg,"[renderer]\\nsafe_geometry=false\\n"+otherKey+"=1\\n");check(geometrySafe(folder,vr));
   for(String revision:new String[]{"1","2"}){
    Files.writeString(cfg,"[renderer]\\nsafe_geometry=false\\n"+key+"="+revision+"\\n");check(!geometrySafe(folder,vr));
   }
   Files.writeString(cfg,"[renderer]\\n"+key+"=1\\n");check(geometrySafe(folder,vr));
   Files.writeString(cfg,"# preserved\\n[vr]\\nbody=\\"legs\\"\\n");check(geometrySafe(folder,vr));
   saveGeometry(folder,vr,false);check(!geometrySafe(folder,vr));
   check(ConfigSettings.read(folder,"renderer",key,"0").equals("1"));
   check(Files.readString(cfg).contains("body=\\"legs\\""));
   saveGeometry(folder,vr,true);check(geometrySafe(folder,vr));
   String duplicate="[renderer]\\nsafe_geometry=false\\nsafe_geometry=true\\n";
   Files.writeString(cfg,duplicate);fails(()->saveGeometry(folder,vr,false));check(Files.readString(cfg).equals(duplicate));
  }
  System.out.println("PASS: "+checks+" launch-request archive and actual launcher geometry policy/save checks");
 }
}
'''.replace('METHODS', methods)
    with tempfile.TemporaryDirectory(prefix='test32-launcher-state-') as temp:
        out = Path(temp)
        java = out/'LauncherStateCheck.java'
        java.write_text(check)
        subprocess.run(['javac', '-d', str(out), str(java), str(JAVA/'ConfigSettings.java'),
            str(JAVA/'LauncherRequests.java')], check=True)
        subprocess.run(['java', '-cp', str(out), 'com.halo.decomp.LauncherStateCheck', str(out)], check=True)


def main():
    widgets, strings = {}, {}
    for path in MENUS.glob('*.xml'):
        for e in ET.parse(path).getroot().iter():
            if e.get('platform') == 'desktop':
                continue
            if e.tag == 'widget' and e.get('name'):
                widgets[e.get('name')] = e
            if e.tag == 'strings':
                strings[e.get('name')] = [s.get('text', '') for s in e.findall('string')]

    def widget(suffix):
        found = [e for name, e in widgets.items() if name.endswith('/' + suffix)]
        assert len(found) == 1, (suffix, len(found))
        return found[0]

    def caption(e):
        return e.get('text') or strings[e.get('string_list')][int(e.get('string_index', '0'))].strip()

    def callback(suffix, name):
        assert any(e.get('run') == name for e in widget(suffix).findall('on')), (suffix, name)

    expected = {
        'multiplayer_type_join_item': 'JOIN GAME',
        'multiplayer_type_join_internet_item': 'SERVER BROWSER',
        'multiplayer_type_join_lan_item': 'LAN',
        'multiplayer_type_join_direct_item': 'DIRECT LINK',
        'multiplayer_type_create_item': 'CREATE GAME',
        'multiplayer_type_create_internet_item': 'INTERNET',
        'multiplayer_type_create_lan_item': 'LAN',
        'multiplayer_type_coop_item': 'CO-OP CAMPAIGN',
        'multiplayer_type_gametypes_item': 'EDIT GAMETYPES',
        'network_settings_profile_item': 'NETWORK SETUP',
        'join_game_button_refresh': 'REFRESH',
        'join_game_button_join': 'JOIN GAME',
        'join_game_button_filters': 'FILTERS',
        'button_edit_link': 'ENTER LINK',
        'button_clipboard': 'PASTE LINK',
        'lobby_button_start': 'START NOW',
    }
    for suffix, text in expected.items():
        assert caption(widget(suffix)) == text, suffix
    callback('button_edit_link', 'port direct link edit')
    callback('button_clipboard', 'direct ip connect go')
    callback('filters_apply', 'port browser filters apply')
    callback('op_invite', 'ss copy invite')
    password = widgets['main_menu/multiplayer_type_select/server_settings/op_password']
    assert any(e.get('run') == 'ss edit server password' for e in password.findall('on'))
    setup = widgets['main_menu/multiplayer_type_select/server_settings/button_ok']
    assert setup.get('text') == 'START GAME'
    assert setup.find('on').get('run') == 'ss start game'
    assert any('SINGLEPLAYER' in v for v in strings.values())
    assert 'CO-OP' in widget('engine_spinner').get('strings')
    assert widget('engine_spinner').get('setting') == 'browser.engine'
    assert widget('max_players_spinner').get('strings').split('|')[-1] == '128'

    launcher = (JAVA / 'LauncherActivity.java').read_text()
    help_source = (JAVA / 'LauncherHelp.java').read_text()
    network = (JAVA / 'NetworkSettings.java').read_text()
    main_menu = launcher[launcher.index('private void buildMenu()'):launcher.index('private void selectMod(')]
    for name in ['new ServerBrowser', 'new PvpLauncher', 'new CoopLauncher']:
        assert name not in main_menu, name
    assert 'LauncherHelp.network(this)' in main_menu
    assert 'if(item==0) { network(activity); return; }' in help_source
    for essential in ['"Play"', '"Versions & updates"', '"Network settings"',
                      '"Controller & touch settings"', '"Game files & versions"',
                      '"Game data & compatibility"', '"Geometry compatibility"',
                      '"Reset settings to defaults"', 'RunLog.destination()', 'ModInstaller.SPV1']:
        assert essential in main_menu, essential
    assert 'passOnInvite(getIntent())' in launcher and 'writeInvite(intent.getData().toString())' in launcher
    assert 'play.setOnClickListener(v -> startFromMenu())' in main_menu
    assert re.search(r'if \(isInvite\(getIntent\(\)\)\)\s*startGame\(\)', launcher)
    play = launcher[launcher.index('private void startFromMenu()'):launcher.index('File baseRoot()')]
    assert play.index('LauncherRequests.retire(gameRoot())') < play.index('startGame();')
    assert re.search(r'catch \(java.io.IOException e\).*?return;.*?startGame\(\);', play, re.S)
    assert play.index('LauncherRequests.retire(gameRoot())') < play.index('if (isInvite(getIntent()))') < play.index('!writeInvite(invite)')
    saved = help_source[help_source.index('private static void savedInvites'):help_source.index('static void show(')]
    for retained in ['"server_browser"', '"coop_browser"', 'getString("saved","[]")',
                     'ServerInvite.normalize', 'ServerInvite.displayName', '"Copy invite"',
                     'ClipboardManager', 'newPlainText', 'i<512', '1024*1024']:
        assert retained in saved, retained
    for prohibited in ['.edit(', '.delete(', '.remove(', 'new URL', 'writeInvite(', 'startGame(']:
        assert prohibited not in saved, prohibited
    assert 'stored data is unchanged' in saved
    assert 'System Link' not in help_source + network
    assert 'boolean current=geometrySafe(root,vr)' in help_source and 'saveGeometry(root,vr,!current)' in help_source
    check_launch_storage_and_geometry(help_source)

    with tempfile.TemporaryDirectory(prefix='test32-launcher-') as temp:
        out = Path(temp)
        config = out / 'BuildConfig.java'
        config.write_text('package com.halo.decomp; final class BuildConfig { static final int HALO_NETWORK_VERSION=997; }')
        check = out / 'GuideCheck.java'
        check.write_text('''package com.halo.decomp;
import java.util.Base64;
import java.nio.charset.StandardCharsets;
class GuideCheck { public static void main(String[] args) {
 String[] pages={InGameNetworkGuide.BROWSE,InGameNetworkGuide.HOST_PVP,InGameNetworkGuide.COOP,
   InGameNetworkGuide.INVITES,InGameNetworkGuide.COMPATIBILITY};
 for(String page:pages) System.out.println(Base64.getEncoder().encodeToString(page.getBytes(StandardCharsets.UTF_8)));
}}
''')
        subprocess.run(['javac', '-d', str(out), str(config), str(JAVA/'InGameNetworkGuide.java'), str(check)], check=True)
        result = subprocess.run(['java', '-cp', str(out), 'com.halo.decomp.GuideCheck'], check=True, capture_output=True, text=True)
        pages = [base64.b64decode(line).decode() for line in result.stdout.splitlines()]
        assert len(pages) == 5 and all(500 < len(p) < 3500 for p in pages)
        for page in pages:
            assert 'System Link' not in page and '\ufffd' not in page
        for route in ['Multiplayer > Join Game > Server Browser', 'Multiplayer > Join Game > LAN', 'most populated games first', 'APPLY']:
            assert route in pages[0], route
        assert 'list auto-scrolls as you move through rows' in pages[0]
        assert 'scroll arrows' not in pages[0]
        for text in ['Create Game > Internet', 'SINGLEPLAYER', 'FRIENDLY FIRE', 'EXTRA ENEMIES', 'PLAYER COLLISIONS',
                     'START GAME', 'START NOW', '128', 'local split screen', 'blocked on Quest']:
            assert text in pages[2], text
        for text in ['Direct Link', 'PASTE LINK', 'ENTER LINK', 'PASSWORDS', 'does not ask', 'Saved invites', 'not automatically imported']:
            assert text in pages[3], text
        assert 'network 997' in pages[4], 'network version must come from BuildConfig'
        for text in ['ISO/revision', 'Versions & updates', 'no relay', 'Download/HaloCE', 'discord.gg/S9uSCKxKx', '@MeWhenINameMyself']:
            assert text in pages[4], text

    # Full Java type check against the real Android API. This does not configure
    # Gradle or package an APK. SDK and SDL are already used by the other suites.
    sdk = Path(os.environ.get('ANDROID_HOME', os.environ.get('ANDROID_SDK_ROOT', str(Path.home()/'Android/Sdk'))))
    jars = sorted((sdk/'platforms').glob('android-*/android.jar'))
    assert jars, 'Android SDK is required for the launcher Java API check'
    sdl = ROOT/'build/android/third_party/SDL3/android-project/app/src/main/java'
    assert (sdl/'org/libsdl/app/SDLActivity.java').is_file(), 'Stage SDL dependencies first'
    with tempfile.TemporaryDirectory(prefix='test32-launcher-api-') as temp:
        out = Path(temp)
        config = out/'BuildConfig.java'
        version = re.search(r'^#define HALO_PORT_NETWORK_VERSION (\d+)', (ROOT/'port/linux/include/halo_port_limits.h').read_text(), re.M).group(1)
        config.write_text('package com.halo.decomp; public final class BuildConfig {'
            'public static final String APPLICATION_ID="com.halo.decomp",VERSION_NAME="test";'
            'public static final int VERSION_CODE=0,HALO_BUILD_NUMBER=0,'
            f'HALO_NETWORK_VERSION={version},HALO_NETWORK_MINIMUM={version},HALO_NETWORK_MAXIMUM={version};'
            'public static final boolean DEBUG=true;}')
        subprocess.run(['javac', '-encoding', 'UTF-8', '-classpath', str(jars[-1]), '-d', str(out),
            str(config), *map(str, JAVA.glob('*.java')), *map(str, sdl.rglob('*.java'))], check=True)
    print('PASS: real OpenCE captions/routes and 5 compiled guide pages; launcher duplicates removed, essentials/invites preserved; full Android+SDL Java compiles')


if __name__ == '__main__':
    main()
