"""Execute production calibration, host request, map header and config helpers.
Requires clang and JDK17; no game/device/server connection.
"""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test15-checks'
OUT.mkdir(parents=True,exist_ok=True)
source=OUT/'check.c'
source.write_text(r'''
#include <assert.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include "port/linux/src/vr_alignment.h"
#include "port/linux/game/network_pvp_request.h"
int main(void) {
 float p[3]={1,2,3},q[4]={0,0,0,1},zero[3]={0},rot[4],offset[3]={0};
 vr_alignment_rotation(zero,rot); assert(vr_alignment_apply(p,q,rot,offset));
 assert(p[0]==1&&p[1]==2&&p[2]==3&&q[3]==1&&q[0]==0);
 float roll[3]={0,0,180}; vr_alignment_rotation(roll,rot);
 assert(vr_alignment_apply(p,q,rot,offset)); assert(fabsf(q[2]-1)<1e-5&&fabsf(q[3])<1e-5);
 assert(vr_alignment_apply(p,q,rot,offset)); assert(fabsf(q[3]+1)<1e-5);
 float yaw[3]={0,90,0}; vr_alignment_rotation(yaw,q); vr_alignment_rotation(zero,rot);
 offset[0]=.1f; p[0]=p[1]=p[2]=0; assert(vr_alignment_apply(p,q,rot,offset));
 assert(fabsf(p[0])<1e-5&&fabsf(p[2]+.1f)<1e-5);
 assert(vr_alignment_bound(NAN,180)==0&&vr_alignment_bound(INFINITY,180)==0);
 assert(vr_alignment_bound(999,180)==180&&vr_alignment_bound(-999,.2f)==-.2f);
 q[0]=NAN; assert(!vr_alignment_apply(p,q,rot,offset)); q[0]=0;q[1]=0;q[2]=0;q[3]=0;
 assert(!vr_alignment_apply(p,q,rot,offset)); q[3]=1;p[0]=INFINITY;assert(!vr_alignment_apply(p,q,rot,offset));
 struct pvp_request request;
 assert(pvp_request_parse("1 128 1 0 bloodgulch slayer\nPublic host\n",&request));
 assert(request.maximum==128&&request.publish==1&&!strcmp(request.name,"Public host"));
 for(int i=0;i<14;i++) { char text[256];snprintf(text,sizeof(text),"1 2 0 9999 wizard %s\nHost\n",pvp_variants[i]);assert(pvp_request_parse(text,&request)); }
 const char *bad[]={"1 129 1 0 bloodgulch slayer\nHost\n","1 1 1 0 bloodgulch slayer\nHost\n",
 "1 16 2 0 bloodgulch slayer\nHost\n","1 16 1 -1 bloodgulch slayer\nHost\n",
 "1 16 1 0 ../ui slayer\nHost\n","1 16 1 0 bloodgulch fake\nHost\n",
 "1 16 1 0 bloodgulch slayer\n\n","1 16 1 0 bloodgulch slayer\n0123456789012345\n",
 "1 16 1 0 bloodgulch slayer\nHost\ntrailing","1 16 1 0 bloodgulch slayer\nHost",
 "2 16 1 0 bloodgulch slayer\nHost\n"};
 for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++) assert(!pvp_request_parse(bad[i],&request));
 puts("PASS: calibration no-op, rotations, local translation, invalid tracking; 14 PvP variants, capacity and malformed requests");
}
''')
subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(ROOT),str(source),'-lm','-o',str(OUT/'check')],check=True)
subprocess.run([str(OUT/'check')],check=True)
java=OUT/'RefinementCheck.java'
java.write_text(r'''
package com.halo.decomp;
import java.io.*;import java.nio.*;import java.nio.file.*;import java.util.*;
public class RefinementCheck {
 static void check(boolean b) {if(!b)throw new AssertionError();}
 public static void main(String[] args)throws Exception {
  File root=new File(args[0],"fixture");root.mkdirs();File config=new File(root,"config.toml");
  Files.writeString(config.toPath(),"# keep\n[vr]\nbody = \"legs\"\n[network]\nonline = false # old\naddress = \"1.2.3.4\"\n[display]\nvsync = true\n");
  Map<String,String> change=new LinkedHashMap<>();change.put("online","true");change.put("tunnel_port","11777");
  ConfigSettings.write(root,"network",change);String edited=Files.readString(config.toPath());
  check(edited.contains("body = \"legs\"")&&edited.contains("address = \"1.2.3.4\"")&&edited.contains("vsync = true"));
  check(ConfigSettings.read(root,"network","online","").equals("true"));
  check(ConfigSettings.read(root,"network","tunnel_port","").equals("11777"));
  check(!ConfigSettings.read(root,"display","tunnel_port","absent").equals("11777"));
  ConfigSettings.write(root,"renderer",Collections.singletonMap("safe_geometry","false"));
  check(ConfigSettings.read(root,"renderer","safe_geometry","").equals("false"));
  ConfigSettings.write(root,"network",Collections.singletonMap("online","false"));
  check(ConfigSettings.read(root,"network","online","").equals("false"));
  File clean=new File(root,"clean");clean.mkdirs();ConfigSettings.write(clean,"network",change);
  check(ConfigSettings.read(clean,"network","tunnel_port","").equals("11777"));
  Files.writeString(config.toPath(),"[network]\nonline=true\n[network]\nonline=false\n");
  try {ConfigSettings.write(root,"network",change);throw new AssertionError();}catch(IOException expected){}
  File map=new File(root,"bloodgulch.map");byte[] header=new byte[2048];ByteBuffer b=ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN);
  b.putInt(0,0x68656164);b.putInt(4,5);b.putInt(2044,0x666f6f74);b.putShort(96,(short)1);
  for(String build:new String[]{"01.01.14.2342","01.10.12.2276","01.08.15.1749"}) {
   Arrays.fill(header,64,96,(byte)0);System.arraycopy(build.getBytes(),0,header,64,build.length());Files.write(map.toPath(),header);
   check(MapInfo.read(map).multiplayer);check(MapInfo.read(map).build.equals(build));check(MapInfo.sha256(map).length()==64);
  }
  b.putShort(96,(short)0);Files.write(map.toPath(),header);check(!MapInfo.read(map).multiplayer);
  b.putShort(96,(short)1);b.putInt(4,7);Files.write(map.toPath(),header);check(!MapInfo.read(map).multiplayer);
  b.putInt(4,5);b.putInt(2044,0);Files.write(map.toPath(),header);check(!MapInfo.read(map).multiplayer);
  Files.write(map.toPath(),new byte[100]);check(!MapInfo.read(map).multiplayer);
  System.out.println("PASS: clean/upgrade config preservation, duplicate rejection, PAL/NTSC header fixtures, format/type/truncation, fingerprints");
 }
}
''')
JAVA=ROOT/'port/android/app/src/main/java/com/halo/decomp'
subprocess.run(['javac','-d',str(OUT),str(JAVA/'MapInfo.java'),str(JAVA/'ConfigSettings.java'),str(java)],check=True)
subprocess.run(['java','-cp',str(OUT),'com.halo.decomp.RefinementCheck',str(OUT)],check=True)
