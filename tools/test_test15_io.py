"""Execute production touch input, v9/v10/v11 settings assembly, renderer writes and update policy.
No headset, GPU, live match or installer is exercised by these deterministic checks.
"""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/test15-io';OUT.mkdir(parents=True,exist_ok=True)
def fn(text,name):
 start=text.index(name); start=text.rfind('\n',0,start)+1
 body=text.index('{',start);depth=1;end=body+1
 while depth:
  depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]+'\n'
def run(name,text):
 p=OUT/(name+'.c');p.write_text(text)
 subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Wno-unused-function','-fsanitize=address,undefined','-I',str(ROOT),str(p),'-pthread','-lm','-o',str(OUT/name)],check=True)
 subprocess.run([str(OUT/name)],check=True)
s=(ROOT/'port/android/host/host_sdl.c').read_text();block=s[s.index('static pthread_mutex_t touch_lock'):s.index('#define HANDLE_COUNT')]
run('touch',r'''
#include <assert.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>
#include "port/android/include/halo_touch.h"
typedef void JNIEnv;typedef void* jclass;typedef int jint;typedef int jboolean;typedef float jfloat;typedef unsigned long long Uint64;
#define JNIEXPORT
#define JNICALL
static Uint64 now=1;
static Uint64 SDL_GetTicks(void){return now;}
'''+'#ifndef HALO_VR\n'+block+r'''
int main(void){
 struct halo_touch_state s;assert(sizeof(s)==32);
 Java_com_halo_decomp_TouchControls_nativeState(0,0,99999,-99999,0,0,1,0);
 Java_com_halo_decomp_TouchControls_nativeState(0,0,0,0,0,0,0,0);
 host_touch_read(&s);assert(s.buttons==1);host_touch_read(&s);assert(s.buttons==0);
 Java_com_halo_decomp_TouchControls_nativeLook(0,0,.1f,-.2f);host_touch_read(&s);assert(s.yaw==.1f&&s.pitch==-.2f);
 host_touch_read(&s);assert(s.yaw==0&&s.pitch==0);
 Java_com_halo_decomp_TouchControls_nativeLook(0,0,NAN,INFINITY);host_touch_read(&s);assert(s.yaw==0);
 Java_com_halo_decomp_TouchControls_nativeLook(0,0,100,-100);host_touch_read(&s);assert(s.yaw<1.571&&s.pitch> -1.571);
 Java_com_halo_decomp_TouchControls_nativeLook(0,0,1,1);now+=251;host_touch_read(&s);assert(s.yaw==0&&s.pitch==0);
 Java_com_halo_decomp_TouchControls_nativeLook(0,0,1,1);Java_com_halo_decomp_TouchControls_nativeState(0,0,0,0,0,0,0,1);
 host_touch_read(&s);assert(s.generation==1&&s.yaw==0&&s.buttons==0);
 puts("PASS: touch quick taps, one-shot motion, invalid input, clamping, expiry, cancellation and 32-byte ABI");
}
''')
h=(ROOT/'source/game/game_engine.h').read_text();options=h[h.index('enum\n{\n\t_friendly_fire_on'):h.index('\nstruct game_engine\n{')]
s=(ROOT/'source/networking/network_client_message_handler.c').read_text();assembly=s[s.index('static struct network_game network_game_client_settings_staging;'):s.index('\nstatic boolean network_game_client_handle_message_server_game_settings_update(',s.index('static struct network_game network_game_client_settings_staging;'))]
engine=(ROOT/'source/game/game_engine.c').read_text()
run('wire',r'''
#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "port/linux/include/halo_port_limits.h"
typedef unsigned char byte;typedef unsigned char boolean;typedef unsigned short word;
#define TRUE 1
#define FALSE 0
#define csmemcpy memcpy
#define csmemset memset
#define network_event(...) ((void)0)
#define TEST_FLAG(v,b) ((v)&(1u<<(b)))
#define _game_variant_draw_object_in_motion_sensor_bit 0
'''+options+r'''
struct game_variant {struct {int flags,vehicle_set;}universal_variant;};
struct network_game {struct game_variant variant;byte prefix[HALO_PORT_NETWORK_GAME_VARIANT_OPTIONS_OFFSET-sizeof(struct game_variant)];struct game_variant_options variant_options;byte local_data[4];};
struct network_game_client {int ignored;};
struct message_server_game_settings_update {word total_size,offset,length,pad;byte data[0xE00];};
static int applied;
static struct network_game result;
static boolean network_game_client_game_settings_updated(struct network_game_client*c,struct network_game*g){(void)c;result=*g;applied++;return TRUE;}
'''+fn(engine,'boolean game_variant_options_valid(')+fn(engine,'void game_variant_options_default(')+assembly+r'''
struct network_game_server {int unused;};struct network_game_server_client_machine {int unused;};
static int campaign;
static int network_campaign_game(const void *g){(void)g;return campaign;}
#define MIN(a,b) ((a)<(b)?(a):(b))
#define _message_server_game_settings_update 1
static void *create_network_game_message(int type,void *m,int size){(void)type;(void)size;return m;}
static int network_game_server_send_message_to_client_machine(struct network_game_server*s,struct network_game_server_client_machine*m,void*p){(void)s;(void)m;return network_game_client_receive_game_settings_piece(0,p);}
'''+fn((ROOT/'source/networking/network_server_message_handler.c').read_text(),'boolean network_game_server_send_game_settings_to_client_machine(')+r'''
static void deliver(byte *bytes,int size){
 struct message_server_game_settings_update p={0};int before=applied;
 for(int offset=0;offset<size;offset+=sizeof(p.data)){
  p.total_size=size;p.offset=offset;p.length=size-offset<sizeof(p.data)?size-offset:sizeof(p.data);
  memcpy(p.data,bytes+offset,p.length);assert(network_game_client_receive_game_settings_piece(0,&p));
  assert(applied==before+(offset+p.length==size));
 }
}
int main(void){
 assert(sizeof(struct network_game)==HALO_PORT_NETWORK_GAME_SIZE);
 assert(offsetof(struct network_game,local_data)==HALO_PORT_NETWORK_GAME_LOCAL_DATA_OFFSET);
 struct network_game g={0};game_variant_options_default(&g.variant,&g.variant_options);
 g.variant_options.time_limit=30;g.variant_options.loadout=1;g.local_data[0]=1;
 deliver((byte*)&g,sizeof(g));assert(result.variant_options.time_limit==30&&result.local_data[0]==1);
 campaign=1;assert(network_game_server_send_game_settings_to_client_machine(0,0,&g,sizeof(g)));assert(result.variant_options.time_limit==0&&result.local_data[0]==1);
 campaign=0;assert(network_game_server_send_game_settings_to_client_machine(0,0,&g,sizeof(g)));assert(result.variant_options.time_limit==30);applied=1;
 byte legacy[HALO_PORT_NETWORK_GAME_LEGACY_SIZE];memcpy(legacy,&g,HALO_PORT_NETWORK_GAME_VARIANT_OPTIONS_OFFSET);
 memcpy(legacy+HALO_PORT_NETWORK_GAME_VARIANT_OPTIONS_OFFSET,g.local_data,4);
 deliver(legacy,sizeof(legacy));assert(result.variant_options.time_limit==0&&result.local_data[0]==1);
 struct message_server_game_settings_update p={0};p.total_size=sizeof(g);p.length=1;p.offset=0;assert(network_game_client_receive_game_settings_piece(0,&p));
 p.total_size=sizeof(legacy);p.offset=1;assert(network_game_client_receive_game_settings_piece(0,&p));assert(applied==2);
 p.total_size=65535;assert(!network_game_client_receive_game_settings_piece(0,&p));p.total_size=sizeof(g);p.length=0;assert(!network_game_client_receive_game_settings_piece(0,&p));
 for(int i=0;i<10;i++){g.variant_options.primary_weapon=i;assert(game_variant_options_valid(&g.variant_options));}
 g.variant_options.primary_weapon=255;assert(!game_variant_options_valid(&g.variant_options));g.variant_options.primary_weapon=2;
 g.variant_options.vehicle_counts[1][5]=255;assert(!game_variant_options_valid(&g.variant_options));
 puts("PASS: v11/legacy fragment assembly, local-data tail, defaults, malformed fragments, bounded match options");
}
''')
s=(ROOT/'port/linux/src/d3d8_gl.c').read_text()
run('upload',r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define HALO_ANDROID 1
#define GL_ARRAY_BUFFER 1
#define GL_ELEMENT_ARRAY_BUFFER 2
#define INDEX_BUFFER_SIZE 4096
#define GL_STREAM_DRAW 3
static struct {unsigned long stream_offset,index_offset;int stream_buffer,index_buffer,stream_persistent,index_persistent;} device;
static unsigned long expected;
static char sink[4096];
static void stream_reserve(unsigned long n){assert(n%16==0);}
static void state_array_buffer(int b){(void)b;}
static void state_element_array_buffer(int b){(void)b;}
static void glFinish(void){}
static void glBufferData(int a,int b,void*c,int d){(void)a;(void)b;(void)c;(void)d;}
static void host_gl_buffer_write(int target,unsigned offset,unsigned size,const void*data){(void)target;(void)offset;assert(size==expected);memcpy(sink,data,size);}
static int host_gl_buffer_write_persistent(int b,unsigned o,unsigned n,const void*d){(void)b;(void)o;assert(n==expected);memcpy(sink,d,n);return 1;}
'''+fn(s,'static unsigned long stream_upload(')+fn(s,'static unsigned long index_upload(')+r'''
int main(void){for(int mode=0;mode<2;mode++)for(int n=1;n<257;n++){
 expected=n;char *data=malloc(n);memset(data,42,n);device.stream_persistent=device.index_persistent=mode;device.stream_offset=device.index_offset=0;
 assert(stream_upload(data,n)==0);assert(device.stream_offset==((n+15)&~15));assert(index_upload(data,n)==0);assert(device.index_offset==((n+15)&~15));free(data);
 }puts("PASS: exact payload bytes for 512 stream/index sizes and persistent/fallback paths (ASAN)");}
''')
java=OUT/'MobileCheck.java';java.write_text(r'''
package com.halo.decomp;
public class MobileCheck {
 static void check(boolean b){if(!b)throw new AssertionError();}
 public static void main(String[] args){
  TouchLayout l=new TouchLayout();check(l.swipe&&l.scale==1&&l.opacity==.65f);
  for(float[] screen:new float[][]{{1920,1080},{2400,1080},{2048,1536},{1080,1920}})for(int i=0;i<TouchLayout.COUNT;i++){
   float radius=34*Math.min(screen[0]/1000,screen[1]/500);float x=TouchLayout.position(l.x[i],screen[0],radius),y=TouchLayout.position(l.y[i],screen[1],radius);
   check(x>=radius&&x<=screen[0]-radius&&y>=radius&&y<=screen[1]-radius);
  }
  l.scale=Float.NaN;l.opacity=Float.POSITIVE_INFINITY;l.x[0]=-999;l.y[0]=999;l.sensitivityX=999;l.size[1]=Float.NaN;l.sanitize();
  check(l.scale==1&&l.opacity==.65f&&l.x[0]==0&&l.y[0]==1&&l.sensitivityX==3&&l.size[1]==1);
  check(TouchLayout.axis(1,0,100,.08f)==0);check(TouchLayout.axis(100,0,100,.08f)==1);check(TouchLayout.axis(-100,0,100,.08f)==-1);
  check(Math.abs(TouchLayout.axis(100,100,100,.08f)-.7071)<.0001);check(TouchLayout.axis(Float.NaN,0,100,.08f)==0);
  check(UpdatePolicy.newer("halo-ce-quest-test16","1.0-test15"));check(!UpdatePolicy.newer("halo-ce-quest-test14","1.0-test15"));
  check(UpdatePolicy.asset("halo-ce-quest-test16",true).equals("HaloCE-Quest-test16.apk"));check(UpdatePolicy.asset("build-111",false)==null);
  for(String url:new String[]{"http://github.com/a","https://github.com.evil/a","https://user@github.com/a","file:///tmp/x","https://github.com:99/a"})check(!UpdatePolicy.allowedUrl(url));
  check(UpdatePolicy.upstreamVersion("#define HALO_PORT_NETWORK_VERSION 11\n")==11);
  check(UpdatePolicy.upstreamVersion("#define HALO_PORT_NETWORK_VERSION 12\n")==12);
  check(UpdatePolicy.upstreamVersion("#define HALO_PORT_NETWORK_VERSION 99999\n")==-1);
  check(UpdatePolicy.upstreamVersion("#define HALO_PORT_NETWORK_VERSION 11\n#define HALO_PORT_NETWORK_VERSION 12\n")==-1);
  check(UpdatePolicy.upstreamVersion("#define HALO_PORT_NETWORK_VERSION_MINIMUM 9\n")==-1);
  check(UpdatePolicy.allowedUrl("https://release-assets.githubusercontent.com/a"));check(UpdatePolicy.digest("sha256:"+"a".repeat(64)));check(!UpdatePolicy.digest("sha256:"+"a".repeat(63)));
  System.out.println("PASS: touch screen fractions, clamps, deadzone, diagonal movement; update edition/URL/digest/downgrade policy");
 }
}
''');j=ROOT/'port/android/app/src/main/java/com/halo/decomp'
subprocess.run(['javac','-d',str(OUT),str(j/'TouchLayout.java'),str(j/'UpdatePolicy.java'),str(java)],check=True)
subprocess.run(['java','-cp',str(OUT),'com.halo.decomp.MobileCheck'],check=True)

# Execute the upstream slot-reuse predicate, including bounds and lobby behavior.
s=(ROOT/'source/networking/network_game_manager.c').read_text()
run('slots',r'''
#include <assert.h>
#include <stdio.h>
typedef int boolean;typedef unsigned char byte;
#define FALSE 0
#define TRUE 1
#define NONE (-1)
struct datum_header {short identifier;};
struct player_datum {short identifier;int quit_out_of_game,unit_index;};
static struct player_datum players[128];
static struct {int valid,maximum_count,size;void *data;} pool={1,128,sizeof(struct player_datum),players},*player_data=&pool;
struct network_game_server {int unused;};static struct network_game_server server;
static int active=1,playing=1;
static struct network_game_server *global_network_game_server_get(void){return &server;}
static int game_in_progress(void){return active;}
static int game_engine_running(void){return 1;}
static int network_game_server_playing(struct network_game_server*s){(void)s;return playing;}
'''+fn(s,'static boolean network_game_player_slot_reusable(')+fn(s,'static boolean network_game_player_slot_held(')+r'''
int main(void){
 for(int i=0;i<128;i++){
  players[i].identifier=1;players[i].quit_out_of_game=0;players[i].unit_index=10;assert(network_game_player_slot_held(i));
  players[i].quit_out_of_game=1;assert(network_game_player_slot_held(i));players[i].unit_index=NONE;assert(!network_game_player_slot_held(i));
 }
 assert(!network_game_player_slot_held(-1)&&!network_game_player_slot_held(128));
 players[0].quit_out_of_game=0;playing=0;assert(!network_game_player_slot_held(0));playing=1;assert(network_game_player_slot_held(0));
 pool.valid=0;assert(!network_game_player_slot_held(0));
 puts("PASS: 128 quit-player slots, live-unit retention, bounds, lobby and invalid-pool handling");
}
''')
