"""Production network regressions and managed data imports; no copyrighted fixtures.

Requires JDK17 and clang. Creates isolated synthetic files under ignored build/.
Device UI, real disc completeness and internet matches require owner testing.
"""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test17-checks'
OUT.mkdir(parents=True, exist_ok=True)
JAVA = ROOT / 'port/android/app/src/main/java/com/halo/decomp'


def function(source, name):
    start = source.rfind('\n', 0, source.index(name)) + 1
    end = source.index('{', start) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end] + '\n'


def compile_c(name, code):
    file = OUT / (name + '.c')
    file.write_text(code, encoding='utf-8')
    binary = OUT / name
    subprocess.run(['clang', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-fsanitize=address,undefined', '-I', str(ROOT), str(file),
                    '-o', str(binary)], check=True)
    return binary


players = (ROOT / 'source/game/players.c').read_text(encoding='utf-8')
expression = re.search(r'control_data\.control_flags\s*=\s*([^;]+);', players)[1]
assert '!TEST_FLAG(action->control_flags, UNIT_CONTROL_PORT_ACTION_ONLY_BIT)' in players
units = (ROOT / 'source/units/units.h').read_text(encoding='utf-8')
bit = re.search(r'^#define UNIT_CONTROL_PORT_ACTION_ONLY_BIT\s+(\d+)', units, re.M)[1]
queues = (ROOT / 'source/game/player_queues_new.c').read_text(encoding='utf-8')
queue_fn = function(queues, 'static boolean update_queue_make_room(')
toast_fn = function((ROOT / 'port/android/host/host_sdl.c').read_text(encoding='utf-8'),
                    'int host_sdl_show_simple_message_box(')
binary = compile_c('network', r'''
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
typedef uint8_t byte;
typedef uint16_t word;
typedef uint32_t dword;
#define FALSE 0
#define TRUE 1
#define FLAG(b) (1u << (b))
struct datum_header {short identifier;};
struct data_array {int maximum_count,size;void *data;};
static int deleted; static uint32_t deleted_index;
static void datum_delete(struct data_array *q,long i) {
    deleted++;deleted_index=(uint32_t)i;
    ((struct datum_header*)q->data)[(uint16_t)i].identifier=0;
}
''' + queue_fn + r'''
static int logged,toasted;
#define HOST_LOG_INFO 1
#define host_logf(...) ((void)++logged)
static int SDL_ShowAndroidToast(const char *message,int duration,int gravity,int x,int y){
 assert(!strcmp(message,"reason")&&duration==1&&gravity==-1&&x==0&&y==0);toasted++;return 1;
}
''' + toast_fn.replace('(void)flags;', '(void)flags;(void)title;') +
f'\n#define UNIT_CONTROL_PORT_ACTION_ONLY_BIT {bit}\n' + r'''
int main(void){
 struct {uint32_t control_flags;} storage,*action=&storage;
 for(uint32_t flags=0;flags<=65535;flags++){
  action->control_flags=flags;
  word control=''' + expression + r''';
  assert(control==(flags&0x7fff));assert(!(control&0x8000));
 }
 struct datum_header data[4]={{0}};struct data_array q={4,sizeof(data[0]),data};
 assert(!update_queue_make_room(&q,4));assert(!update_queue_make_room(&q,-1));assert(!deleted);
 assert(!update_queue_make_room(&q,0x10001));assert(!deleted);
 for(uint32_t id=1;id<=65535;id++){
  data[1].identifier=(short)id;deleted=0;
  assert(update_queue_make_room(&q,(long)(id<<16|1)));assert(!deleted);
  assert(!update_queue_make_room(&q,(long)((id==65535?1:id+1)<<16|1)));
  assert(deleted==1&&deleted_index==(id<<16|1)&&data[1].identifier==0);
 }
 assert(host_sdl_show_simple_message_box(0,"title","reason"));assert(logged==1&&toasted==1);
 puts("PASS: 65,536 action words; 65,535 same/stale queue identifiers; bounds; asynchronous logged join notices");
}
''')
subprocess.run([str(binary)], check=True)

profile = compile_c('profile', r'''
#include <stdlib.h>
#include "port/android/host/game_data_profile.h"
int main(int argc,char **argv){
 if(argc!=3)return 2;
 char out[1024]={0};int status=halo_game_data_profile(argv[1],out,sizeof(out));
 if(status!=atoi(argv[2])){fprintf(stderr,"profile status %d, expected %s\n",status,argv[2]);return 1;}
 if(status==1){char tiny[2];if(halo_game_data_profile(argv[1],tiny,sizeof(tiny))!=-1)return 1;puts(out);}
 return 0;
}
''')
harness = OUT / 'DataCheck.java'
harness.write_text(r'''
package com.halo.decomp;
import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
public class DataCheck {
 static File base;static String nativeTool;static int checks;
 static void check(boolean b){checks++;if(!b)throw new AssertionError("check "+checks);}
 interface Job{void run()throws Exception;}
 static void reject(Job job)throws Exception{boolean failed=false;try{job.run();}catch(IOException e){failed=true;}check(failed);}
 static byte[] map(String build,int version,int type,int seed){
  byte[] bytes=new byte[4096];ByteBuffer b=ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN);
  b.putInt(0,0x68656164);b.putInt(4,version);b.putInt(8,4096);b.putInt(2044,0x666f6f74);
  System.arraycopy(build.getBytes(StandardCharsets.US_ASCII),0,bytes,64,build.length());b.putShort(96,(short)type);b.putInt(3000,seed);return bytes;
 }
 static File maps(File root,int seed)throws Exception{
  File dir=new File(root,"maps");dir.mkdirs();
  Files.write(new File(dir,"ui.map").toPath(),map("01.10.12.2276",5,2,seed));
  Files.write(new File(dir,"bloodgulch.map").toPath(),map("01.10.12.2276",5,1,seed));return dir;
 }
 static GameDataLibrary.Profile add(GameDataLibrary lib,File src,String label)throws Exception{
  File stage=lib.stage();try{GameDataLibrary.copyMaps(src,stage);return lib.finish(stage,label);}finally{lib.discard(stage);check(!stage.exists());}
 }
 static void nativeCheck(int status)throws Exception{
  Process p=new ProcessBuilder(nativeTool,base.toString(),""+status).redirectError(ProcessBuilder.Redirect.INHERIT).start();
  String out=new String(p.getInputStream().readAllBytes(),StandardCharsets.UTF_8).trim();check(p.waitFor()==0);
  if(status==1)check(out.equals(GameDataLibrary.activeRoot(base).toString()));
 }
 static void entry(ByteBuffer b,int at,int right,int sector,int length,int attr,String name){
  b.putShort(at,(short)0);b.putShort(at+2,(short)right);b.putInt(at+4,sector);b.putInt(at+8,length);
  b.put(at+12,(byte)attr);b.put(at+13,(byte)name.length());for(int i=0;i<name.length();i++)b.put(at+14+i,(byte)name.charAt(i));
 }
 static byte[] iso(boolean duplicate){
  byte[] image=new byte[50*2048];ByteBuffer b=ByteBuffer.wrap(image).order(ByteOrder.LITTLE_ENDIAN);
  byte[] magic="MICROSOFT*XBOX*MEDIA".getBytes(StandardCharsets.US_ASCII);
  System.arraycopy(magic,0,image,0x10000,magic.length);System.arraycopy(magic,0,image,0x107ec,magic.length);
  b.putInt(0x10014,40);b.putInt(0x10018,2048);entry(b,40*2048,0,41,2048,16,"MAPS");
  entry(b,41*2048,8,42,4096,0,"UI.MAP");entry(b,41*2048+32,0,44,4096,0,duplicate?"ui.map":"bloodgulch.map");
  System.arraycopy(map("01.01.14.2342",5,2,20),0,image,42*2048,4096);
  System.arraycopy(map("01.01.14.2342",5,1,21),0,image,44*2048,4096);return image;
 }
 static GameDataLibrary.Profile extract(GameDataLibrary lib,byte[] bytes)throws Exception{
  File file=new File(base,"synthetic.iso");Files.write(file.toPath(),bytes);File stage=lib.stage();
  try(FileInputStream in=new FileInputStream(file)){XisoExtractor.extractMaps(in.getChannel(),stage,(f,d,t)->{});return lib.finish(stage,"synthetic");}
  finally{lib.discard(stage);check(!stage.exists());}
 }
 public static void main(String[] args)throws Exception{
  base=new File(args[0]);nativeTool=args[1];maps(base,1);Files.writeString(new File(base,"config.toml").toPath(),"original settings");
  File save=new File(base,"save");save.mkdir();Files.writeString(new File(save,"progress").toPath(),"original save");
  GameDataLibrary lib=new GameDataLibrary(base);check(lib.list().size()==1);check(GameDataLibrary.activeRoot(base).equals(base));nativeCheck(0);
  File a=maps(new File(base,"source-a"),2);File b=maps(new File(base,"source-b"),3);
  Files.move(new File(b,"ui.map").toPath(),new File(b,"UI.MAP").toPath());
  GameDataLibrary.Profile p=add(lib,a,"A"),q=add(lib,b,"B");check(lib.list().size()==3);check(!p.fingerprint.equals(q.fingerprint));
  check(p.build.contains("NTSC 01.10.12.2276"));check(p.fingerprint.length()==64);check(GameDataLibrary.idValid(p.id));
  check(add(lib,a,"duplicate").id.equals(p.id));check(lib.list().size()==3);
  lib.select(p.id);nativeCheck(1);check(GameDataLibrary.activeRoot(base).equals(p.root));
  check(Files.readString(new File(p.root,"config.toml").toPath()).equals("original settings"));
  check(!new File(p.root,"save/progress").exists());new File(p.root,"save").mkdir();Files.writeString(new File(p.root,"save/progress").toPath(),"profile save");
  lib.select(q.id);nativeCheck(1);check(!new File(q.root,"save/progress").exists());
  check(new GameDataLibrary(base).list().size()==3);lib.rename(q,"My Rev2 (user label)");check(lib.list().stream().anyMatch(x->x.label.equals("My Rev2 (user label)")));
  reject(()->lib.rename(q,"\n"));reject(()->lib.select("../escape"));
  check(lib.withMap("bloodgulch").size()==3);check(lib.withMap("../bloodgulch").isEmpty());check(lib.withMap("missing").isEmpty());
  lib.select("");nativeCheck(0);check(Files.readString(new File(save,"progress").toPath()).equals("original save"));
  check(Files.readString(new File(base,"config.toml").toPath()).equals("original settings"));
  check(java.util.Arrays.equals(Files.readAllBytes(new File(base,"maps/ui.map").toPath()),map("01.10.12.2276",5,2,1)));
  for(byte[] invalid:new byte[][]{map("01.10.12.2276",7,2,1),map("unrecognized",5,2,1),map("01.10.12.2276",5,1,1),new byte[100]}){
   Files.write(new File(a,"ui.map").toPath(),invalid);reject(()->add(lib,a,"bad"));check(lib.list().size()==3);
  }
  Files.delete(new File(a,"ui.map").toPath());reject(()->add(lib,a,"missing ui"));
  File staging=lib.stage();check(lib.list().size()==3);lib.discard(staging);reject(()->lib.discard(base));
  File duplicate=maps(new File(base,"duplicate"),4);Files.copy(new File(duplicate,"ui.map").toPath(),new File(duplicate,"UI.MAP").toPath());
  if(!Files.isSameFile(new File(duplicate,"ui.map").toPath(),new File(duplicate,"UI.MAP").toPath()))reject(()->add(lib,duplicate,"duplicate name"));
  check(GameDataLibrary.mapName("UI.MAP"));check(!GameDataLibrary.mapName("../ui.map"));check(!GameDataLibrary.mapName("a\\ui.map"));
  Thread.currentThread().interrupt();reject(()->GameDataLibrary.copy(new ByteArrayInputStream(new byte[1]),new File(base,"cancelled"),10));Thread.interrupted();
  reject(()->GameDataLibrary.copy(new ByteArrayInputStream(new byte[2]),new File(base,"oversize"),1));
  File marker=new File(base,"active-data.txt");
  for(String invalid:new String[]{"../escape", "x".repeat(65),p.id+"\0","p-"+"f".repeat(32)}){
   Files.write(marker.toPath(),invalid.getBytes(StandardCharsets.UTF_8));check(GameDataLibrary.activeRoot(base)==null);nativeCheck(-1);
  }
  lib.select(p.id);File ui=new File(p.root,"maps/ui.map");File held=new File(p.root,"maps/ui.held");Files.move(ui.toPath(),held.toPath());
  check(GameDataLibrary.activeRoot(base)==null);nativeCheck(-1);Files.move(held.toPath(),ui.toPath());lib.select("");
  GameDataLibrary.Profile extracted=extract(lib,iso(false));check(extracted.build.contains("PAL 01.01.14.2342"));check(new File(extracted.root,"maps/ui.map").isFile());
  reject(()->extract(lib,iso(true)));reject(()->extract(lib,java.util.Arrays.copyOf(iso(false),43*2048)));reject(()->extract(lib,new byte[32]));
  Thread.currentThread().interrupt();reject(()->extract(lib,iso(false)));Thread.interrupted();
  check(lib.list().size()==4);check(GameDataLibrary.activeRoot(base).equals(base));
  System.out.println("PASS: "+checks+" managed-data checks: Java/native selection agreement, isolated saves/config, fingerprints, deduplication, case normalization, malformed inputs, bounds, cancellation and XDVDFS extraction");
 }
}
''', encoding='utf-8')
subprocess.run(['javac', '-d', str(OUT), *[str(JAVA / (name+'.java')) for name in
                ['MapInfo', 'GameDataLibrary', 'XisoExtractor']], str(harness)], check=True)
with tempfile.TemporaryDirectory(prefix='data-', dir=OUT) as temp:
    subprocess.run(['java', '-cp', str(OUT), 'com.halo.decomp.DataCheck', temp, str(profile)], check=True)
