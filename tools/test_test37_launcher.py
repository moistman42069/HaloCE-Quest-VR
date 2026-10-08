"""Execute the production launcher profile persistence and launch preparation.

Uses tiny Android storage interfaces; no APK installation or game launch.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'port/android/app/src/main/java/com/halo/decomp'

def block(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

with tempfile.TemporaryDirectory(prefix='halo-network-profile-') as temp:
    out = Path(temp)
    sources = {
        'Context.java': '''package android.content;
public abstract class Context {
 public static final int MODE_PRIVATE=0;
 public abstract SharedPreferences getSharedPreferences(String name,int mode);
}''',
        'SharedPreferences.java': '''package android.content;
public interface SharedPreferences {
 int getInt(String key,int fallback); Editor edit();
 interface Editor { Editor putInt(String key,int value); boolean commit(); }
}''',
        'RunLog.java': '''package com.halo.decomp;
final class RunLog { static void line(String line) {} }''',
        'ProfileCheck.java': r'''package com.halo.decomp;
import android.content.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
class ProfileCheck {
 static void check(boolean value) { if(!value) throw new AssertionError(); }
 static class Prefs implements SharedPreferences {
  Map<String,Integer> data=new HashMap<>(); boolean fail;
  public int getInt(String k,int fallback) { return data.getOrDefault(k,fallback); }
  public Editor edit() { return new Editor() {
   String key; int value;
   public Editor putInt(String k,int v) { key=k;value=v;return this; }
   public boolean commit() { if(fail)return false;data.put(key,value);return true; }
  }; }
 }
 static class App extends Context {
  Prefs prefs=new Prefs();
  public SharedPreferences getSharedPreferences(String name,int mode) { return prefs; }
 }
 public static void main(String[] args) throws Exception {
  check(ServerListing.customEditionMap("CUSTOM_MAPS\\test"));
  check(ServerListing.customEditionMap("custom_maps/test"));
  check(!ServerListing.customEditionMap("levels/test") && !ServerListing.customEditionMap(null));
  String listing="a".repeat(64)+"\tserver\tcustom_maps/test\t2\t1\t16\t1\t22";
  check(ServerListing.parse(listing).get(0).customEdition);
  check(!ServerListing.parse(listing.replace("custom_maps/test","bloodgulch")).get(0).customEdition);
  App app=new App(); File root=Files.createTempDirectory(Path.of(args[0]),"data").toFile();
  File other=Files.createTempDirectory(Path.of(args[0]),"other-data").toFile();
  Files.writeString(new File(root,"config.toml").toPath(),"[vr]\nbody = 2\n[network]\nonline = true\n");
  check(NetworkProfile.selected(app)==24);
  NetworkProfile.prepare(app,root); check(NetworkProfile.configured(root)==24);
  NetworkProfile.select(app,root,23); check(NetworkProfile.selected(app)==23);
  check(NetworkProfile.configured(root)==23);
  NetworkProfile.prepare(app,other); check(NetworkProfile.configured(other)==23);
  check(ConfigSettings.read(root,"vr","body","").equals("2"));
  check(ConfigSettings.read(root,"network","online","").equals("true"));
  String before=ConfigSettings.contents(root);
  for(int bad:new int[]{1,5,10,25,65535,-1}) {
   try {NetworkProfile.select(app,root,bad);throw new AssertionError();}catch(IOException expected){}
   check(ConfigSettings.contents(root).equals(before));
  }
  app.prefs.fail=true;
  try {NetworkProfile.select(app,root,24);throw new AssertionError();}catch(IOException expected){}
  check(NetworkProfile.selected(app)==23);
  NetworkProfile.prepare(app,root);check(NetworkProfile.configured(root)==23);
  app.prefs.fail=false;
  NetworkProfile.select(app,root,24);check(NetworkProfile.selected(app)==24);
  app.prefs.data.put("version",10);check(NetworkProfile.selected(app)==24);
  ConfigSettings.write(root,"network",Collections.singletonMap("protocol_version","10"));
  check(NetworkProfile.configured(root)==24);
  NetworkProfile.prepare(app,root);check(ConfigSettings.read(root,"network","protocol_version","").equals("24"));
  File invalid=new File(root,"not-a-directory");Files.writeString(invalid.toPath(),"keep");
  try {NetworkProfile.select(app,invalid,23);throw new AssertionError();}catch(IOException expected){}
  check(NetworkProfile.selected(app)==24);
  for(int version:NetworkProfile.SUPPORTED){NetworkProfile.select(app,root,version);check(NetworkProfile.configured(root)==version);}
  NetworkProfile.select(app,root,0);check(NetworkProfile.selected(app)==0);
  NetworkProfile.gameStarted(root);
  try {NetworkProfile.select(app,root,23);throw new AssertionError();}catch(IOException expected){}
  NetworkProfile.prepare(app,root);check(NetworkProfile.configured(root)==0);
  System.out.println("PASS: all14 targets and auto persistence, per-data handoff, live-game switch blocked, invalid versions, write failures and config preservation");
 }
}'''
    }
    browser = (JAVA/'ServerBrowser.java').read_text(encoding='utf-8')
    sources['PopulationCheck.java'] = '''package com.halo.decomp;
import java.util.*;
class PopulationCheck {
 static class Entry { int version,players; boolean customEdition; Entry(int v,int p){version=v;players=p;} }
 List<Entry> directory=new ArrayList<>(); int selectedNetworkVersion; boolean campaign;
''' + '\n'.join(block(browser, signature) for signature in [
        'private static final class NetworkPopulation',
        'private List<NetworkPopulation> networkPopulations()',
        'private int compatibleReportedPlayers()',
        'private int totalReportedPlayers()',
        'private List<Entry> filteredDirectory()']) + '''
 static void check(boolean b){if(!b)throw new AssertionError();}
 public static void main(String[] args){
  PopulationCheck b=new PopulationCheck();
  b.directory.add(new Entry(24,10));b.directory.add(new Entry(11,8));
  b.directory.add(new Entry(24,4));b.directory.add(new Entry(11,8));
  b.directory.add(new Entry(22,14));
  var groups=b.networkPopulations();
  check(groups.get(0).version==11 && groups.get(0).players==16 && groups.get(0).servers==2);
  check(groups.get(1).version==24 && groups.get(1).players==14 && groups.get(1).servers==2);
  check(groups.get(2).version==22 && groups.get(2).servers==1);
  check(groups.stream().anyMatch(g->g.version==23 && g.players==0 && g.servers==0));
  check(groups.get(0).compatible && groups.get(1).compatible);
  b.selectedNetworkVersion=24;var rows=b.filteredDirectory();
  check(rows.size()==2 && rows.get(0).players==10 && rows.get(1).players==4);
  b.selectedNetworkVersion=0;check(b.filteredDirectory().size()==5);
  check(b.compatibleReportedPlayers()==44);
  b.directory.add(new Entry(25,9));check(b.totalReportedPlayers()==53 && b.compatibleReportedPlayers()==44);
  b.directory.get(1).customEdition=true;check(b.compatibleReportedPlayers()==36);
  b.campaign=true;check(b.compatibleReportedPlayers()==14);
  b.directory.clear();check(b.networkPopulations().stream().allMatch(g->g.players==0 && g.servers==0));
  System.out.println("PASS: production population totals, busiest-first ordering, tie breaks, zero-population supported profiles and filtering");
 }
}'''
    for name, source in sources.items():
        (out/name).write_text(source, encoding='utf-8')
    subprocess.run(['javac','-d',str(out),*[str(out/name) for name in sources],
                    str(JAVA/'ConfigSettings.java'),str(JAVA/'NetworkProfile.java'),str(JAVA/'ServerInvite.java'),str(JAVA/'ServerListing.java')],check=True)
    subprocess.run(['java','-cp',str(out),'com.halo.decomp.ProfileCheck',str(out)],check=True)
    subprocess.run(['java','-cp',str(out),'com.halo.decomp.PopulationCheck'],check=True)
