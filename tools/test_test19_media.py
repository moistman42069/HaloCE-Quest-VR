"""Production ISO import and world-to-XR reticle regressions; no game data/device.
Run under the Linux build environment with clang and a JDK.
"""
from pathlib import Path
import re, subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test19-media-checks'; OUT.mkdir(parents=True,exist_ok=True)

def fn(s,name):
    m=re.search(r'^(?:static )?[\w *]+\b'+name+r'\s*\([^;{]*\)\s*\{',s,re.M)
    assert m, name
    a=s.index('{',m.start());b=a+1;depth=1
    while depth: depth+=(s[b]=='{')-(s[b]=='}');b+=1
    return s[m.start():b]+'\n'

frame=(ROOT/'port/linux/src/vr_frame.c').read_text()
c=r'''
#include <assert.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#define HEAD_REACH .35f
static struct {int heading_valid,roomscale;float units_per_metre,heading,reticle_distance,reticle_position[3];
 struct {int origin_valid,recentre_pending;float origin[3];} vehicle_seat;
 float room_previous[2],room_now[2];struct {struct {float position[3];} head;} frame;} vr;
static float render_interpolation_fraction(void){return .4f;}
'''+fn(frame,'rotate')+fn(frame,'to_halo')+fn(frame,'head_offset')+fn(frame,'view')+fn(frame,'vr_set_reticle_world')+r'''
int main(void){
 vr.heading_valid=1;vr.units_per_metre=3.048f;
 for(int yaw=-8;yaw<=8;yaw++)for(int room=0;room<2;room++)for(int pose=0;pose<20;pose++){
  vr.heading=yaw*.4f;vr.roomscale=room;vr.room_previous[0]=.4f;vr.room_now[0]=.7f;
  float anchor[]={31,-9,7},local[]={.1f*pose-1,.03f*pose,-2-.8f*pose};
  float offset[3],p[3],f[3],u[3],q[]={0,0,0,1},heading[]={cosf(vr.heading),sinf(vr.heading),0};
  vr.frame.head.position[0]=.15f*pose;vr.frame.head.position[1]=.02f*pose;vr.frame.head.position[2]=-.05f*pose;
  head_offset(offset);
  for(int i=0;i<3;i++)offset[i]+=local[i]-vr.frame.head.position[i];
  view(offset,q,anchor,heading,p,f,u);vr_set_reticle_world(anchor,p);
  assert(vr.reticle_distance>0);
  for(int i=0;i<3;i++)assert(fabsf(vr.reticle_position[i]-local[i])<.00001f);
 }
 float zero[3]={0},bad[3]={NAN,0,0};vr_set_reticle_world(zero,bad);assert(vr.reticle_distance==0);
 vr.heading_valid=0;vr_set_reticle_world(zero,zero);assert(vr.reticle_distance==0);
 vr.heading_valid=1;vr.heading=NAN;vr_set_reticle_world(zero,zero);assert(vr.reticle_distance==0);
 vr.heading=0;vr.units_per_metre=INFINITY;vr_set_reticle_world(zero,zero);assert(vr.reticle_distance==0);
 puts("PASS: 680 world/XR reticle round-trips, headings, room-scale and head clamp, invalid values");
}
'''
(OUT/'reticle.c').write_text(c)
subprocess.run(['clang','-std=c11','-O1','-fsanitize=address,undefined',str(OUT/'reticle.c'),'-lm','-o',str(OUT/'reticle')],check=True)
subprocess.run([str(OUT/'reticle')],check=True)

gl=(ROOT/'port/linux/src/d3d8_gl.c').read_text()
vao=r'''
#include <assert.h>
#include <string.h>
#include <stdio.h>
typedef unsigned GLuint;
static struct {GLuint vertex_array;} gl_state;
static GLuint actual;static int binds;
static void glBindVertexArray(GLuint a){actual=a;binds++;}
'''+fn(gl,'xgpu_gl_state_invalidate')+fn(gl,'state_vertex_array')+r'''
int main(void){
 for(int frame=0;frame<100;frame++){
  actual=0; xgpu_gl_state_invalidate();int before=binds;
  state_vertex_array(7);assert(actual==7&&binds==before+1);
  state_vertex_array(7);assert(binds==before+1);
 }
 puts("PASS: renderer VAO restored after compositor invalidation; repeated binds cached");
}
'''
(OUT/'vao.c').write_text(vao)
subprocess.run(['clang','-std=c11','-fsanitize=address,undefined',str(OUT/'vao.c'),'-o',str(OUT/'vao')],check=True)
subprocess.run([str(OUT/'vao')],check=True)

java=r'''
package com.halo.decomp;
import java.io.*;import java.nio.*;import java.nio.channels.*;import java.nio.file.*;import java.util.*;
public class ImageCheck {
 static final byte[] MAGIC="MICROSOFT*XBOX*MEDIA".getBytes(java.nio.charset.StandardCharsets.US_ASCII);
 static ByteBuffer buf(int n){return ByteBuffer.allocate(n).order(ByteOrder.LITTLE_ENDIAN);}
 static void write(FileChannel c,long p,ByteBuffer b)throws Exception{b.position(0);while(b.hasRemaining())p+=c.write(b,p);}
 static void entry(ByteBuffer b,int at,String name,long sector,int size,boolean directory,int next){
  byte[] n=name.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1);b.putShort(at,(short)0);b.putShort(at+2,(short)next);
  b.putInt(at+4,(int)sector);b.putInt(at+8,size);b.put(at+12,(byte)(directory?16:0));b.put(at+13,(byte)n.length);
  for(int i=0;i<n.length;i++)b.put(at+14+i,n[i]);
 }
 static Path image(Path dir,long partition,int depth,long dataSector)throws Exception{
  Path path=dir.resolve("image.iso");
  try(FileChannel c=FileChannel.open(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE,StandardOpenOption.SPARSE)){
   // Java's SPARSE hint is ignored by WSL drvfs. Mark only this newly created
   // synthetic fixture sparse before writing distant sectors, avoiding GiB of
   // zero-fill and keeping repeated checks inexpensive. Native Linux needs none.
   String absolute=path.toAbsolutePath().toString();
   if(absolute.matches("/mnt/[a-z]/.*") && Files.exists(Paths.get("/mnt/c/Windows/System32/fsutil.exe"))){
    String windows=Character.toUpperCase(absolute.charAt(5))+":"+absolute.substring(6).replace('/','\\');
    int result=new ProcessBuilder("/mnt/c/Windows/System32/fsutil.exe","sparse","setflag",windows)
     .redirectOutput(ProcessBuilder.Redirect.DISCARD).redirectError(ProcessBuilder.Redirect.INHERIT).start().waitFor();
    if(result!=0)throw new IOException("Cannot create sparse WSL test fixture");
   }
   ByteBuffer header=buf(2048);for(int i=0;i<MAGIC.length;i++){header.put(i,MAGIC[i]);header.put(0x7ec+i,MAGIC[i]);}
   header.putInt(20,0x40);header.putInt(24,depth*32);write(c,partition+0x10000,header);
   ByteBuffer root=buf(depth*32);for(int n=0;n<depth;n++)entry(root,n*32,n==depth-1?"MaPs":"other"+n,0x48,64,true,n==depth-1?0:(n+1)*8);
   write(c,partition+0x40*2048,root);
   ByteBuffer maps=buf(64);entry(maps,0,"UI.MAP",dataSector,4,false,8);entry(maps,32,"a10.map",dataSector+1,4,false,0);
   write(c,partition+0x48*2048,maps);write(c,partition+dataSector*2048,ByteBuffer.wrap(new byte[]{1,2,3,4}));
   write(c,partition+(dataSector+1)*2048,ByteBuffer.wrap(new byte[]{5,6,7,8}));
  }return path;
 }
 static void extract(Path p,Path out)throws Exception{try(FileChannel c=FileChannel.open(p)){XisoExtractor.extractMaps(c,out.toFile(),(f,d,t)->{});}}
 static void fail(Path p,Path out,String expected)throws Exception{
  try{extract(p,out);throw new AssertionError("accepted damaged image");}catch(IOException e){if(!e.getMessage().contains(expected))throw new AssertionError(e);}
  if(Files.exists(out.resolve("maps/ui.map")))throw new AssertionError("published partial image");
 }
 static void patch(Path p,long at,int value)throws Exception{try(FileChannel c=FileChannel.open(p,StandardOpenOption.WRITE)){write(c,at,buf(4).putInt(0,value));}}
 public static void main(String[] args)throws Exception{
  Path root=Paths.get(args[0]);Files.createDirectories(root);
  for(long partition:new long[]{0,0x0fd90000L,0x02080000L,0x18300000L}){
   Path d=Files.createTempDirectory(root,"layout-");Path p=image(d,partition,100,0x90);Path out=d.resolve("out");extract(p,out);
   if(!Arrays.equals(Files.readAllBytes(out.resolve("maps/ui.map")),new byte[]{1,2,3,4})||!Files.exists(out.resolve("maps/a10.map")))throw new AssertionError();
  }
  Path d=Files.createTempDirectory(root,"large-");Path p=image(d,0,1,0x200010);extract(p,d.resolve("out"));
  d=Files.createTempDirectory(root,"cycle-");p=image(d,0,2,0x90);patch(p,0x40*2048+32,8<<16);fail(p,d.resolve("out"),"directory tree");
  d=Files.createTempDirectory(root,"short-");p=image(d,0,1,0x90);try(FileChannel c=FileChannel.open(p,StandardOpenOption.WRITE)){c.truncate(0x90*2048);}fail(p,d.resolve("out"),"Truncated");
  d=Files.createTempDirectory(root,"header-");p=image(d,0,1,0x90);patch(p,0x10000+0x7ec,0);fail(p,d.resolve("out"),"header is damaged");
  d=Files.createTempDirectory(root,"bounds-");p=image(d,0,1,0x90);patch(p,0x10000+20,0x7fffffff);fail(p,d.resolve("out"),"Truncated");
  d=Files.createTempDirectory(root,"name-");p=image(d,0,1,0x90);patch(p,0x48*2048+14,0x2e2e);fail(p,d.resolve("out"),"Unsafe filename");
  d=Files.createTempDirectory(root,"cancel-");p=image(d,0,1,0x90);Thread.currentThread().interrupt();
  try{extract(p,d.resolve("out"));throw new AssertionError();}catch(java.io.InterruptedIOException expected){}finally{Thread.interrupted();}
  System.out.println("PASS: all 4 Xbox partition layouts, 100-deep valid tree, mixed case, >4 GiB offsets, cycle/truncation/header/bounds/path/cancellation rejection");
 }
}
'''
(OUT/'ImageCheck.java').write_text(java)
subprocess.run(['javac','-d',str(OUT),str(ROOT/'port/android/app/src/main/java/com/halo/decomp/XisoExtractor.java'),str(OUT/'ImageCheck.java')],check=True)
subprocess.run(['java','-cp',str(OUT),'com.halo.decomp.ImageCheck',str(OUT/'fixtures')],check=True)
