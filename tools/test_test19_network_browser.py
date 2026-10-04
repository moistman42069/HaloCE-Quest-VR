"""Test19 production cluster invariant, public browser and updater regressions.
No live server, headset, installer or game assets are exercised.
"""
from pathlib import Path
import re, subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/test19-checks';OUT.mkdir(parents=True,exist_ok=True)
def function(s,name):
 a=s.index(name);a=s.rfind('\n',0,a)+1;b=s.index('{',a)+1;depth=1
 while depth: depth+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[a:b]+'\n'
def run(name,s):
 p=OUT/(name+'.c');p.write_text(s,encoding='utf-8');exe=OUT/name
 subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Wno-unused-function','-fsanitize=address,undefined','-I',str(ROOT),str(p),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
s=(ROOT/'source/objects/objects.c').read_text()
run('clusters',r'''
#include <assert.h>
#include <stdio.h>
typedef int boolean;
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define TEST_FLAG(f,b) (((f)>>(b))&1)
#define SET_FLAG(f,b,v) ((f)=(v)?((f)|(1u<<(b))):((f)&~(1u<<(b))))
enum {_object_header_active_bit,_object_header_automatically_deactivate_bit,_object_header_connected_to_map_bit,_object_cannot_be_activated_bit};
struct object_datum {struct {unsigned flags;long parent_object_index;} object;} object;
struct object_header_datum {unsigned flags;int cluster_index;} header;
static struct object_header_datum *object_header_get(long i){(void)i;return &header;}
static struct object_datum *object_get(long i){(void)i;return &object;}
'''+function(s,'static boolean object_activation_has_cluster(')+function(s,'void object_activate(')+r'''
int main(void){
 for(int automatic=0;automatic<2;automatic++)for(int connected=0;connected<2;connected++)
 for(int cluster=-1;cluster<256;cluster++)for(int parent=-1;parent<2;parent++)for(int forbidden=0;forbidden<2;forbidden++){
  header.flags=(automatic<<_object_header_automatically_deactivate_bit)|(connected<<_object_header_connected_to_map_bit);header.cluster_index=cluster;
  object.object.flags=forbidden<<_object_cannot_be_activated_bit;object.object.parent_object_index=parent;
  object_activate(0);assert(TEST_FLAG(header.flags,_object_header_active_bit)==(!forbidden&&parent==NONE&&!(automatic&&connected&&cluster==NONE)));
 }
 puts("PASS: object activation cluster/parent/automatic/connected/cannot-activate matrix");
}
''')
assert 'if (!VALID_INDEX(object_header->cluster_index, cluster_count))' in s
assert 'object PVS recovery:' in s
# Execute the production browser state machine with native discovery/clock/event stubs.
b=(ROOT/'port/linux/game/network_browser.c').read_text(encoding='utf-8-sig')
b=re.sub(r'^#include "[^\n]+\n','',b,flags=re.M)
b=re.sub(r'^typedef char browser_[^\n]+\n','',b,flags=re.M) # actual 32-bit layout is checked by both APK builds
prefix=r'''
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <wchar.h>
#include <stdarg.h>
typedef unsigned char byte;typedef unsigned short word;typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "port/linux/src/p2p.h"
struct network_game_client {int dummy;};
struct network_advertised_game;
static struct network_game_client client;
struct network_game_client *global_network_game_client_get(void){return &client;}
struct network_advertised_game *network_game_client_get_available_games(struct network_game_client *c);
int network_game_client_advertised_game_is_valid(struct network_advertised_game *g);
void event_manager_post_button(short controller,short button);
'''
stubs=r'''
static unsigned long clock_now=1000;
static struct p2p_listing public[256];static int public_count,started,refreshes,joins,posted,failed;
static struct network_advertised_game lan[9];
unsigned long system_milliseconds(void){return clock_now;}
int config_boolean(char const *name){(void)name;return 1;}
void platform_log(char const *format,...){(void)format;}
void p2p_lobby_browse(int on){started=on;}
void p2p_lobby_refresh(void){refreshes++;}
int p2p_lobby_games(struct p2p_listing *out,int max){assert(max==256);memcpy(out,public,sizeof(public));return public_count;}
void p2p_lobby_mark_failed(const unsigned char *identifier){(void)identifier;failed++;}
int p2p_join_invite(const char *s){assert(!strncmp(s,"halo://join/",12));joins++;return 1;}
struct network_advertised_game *network_game_client_get_available_games(struct network_game_client *c){(void)c;return lan;}
int network_game_client_advertised_game_is_valid(struct network_advertised_game *g){return g->valid;}
void event_manager_post_button(short controller,short button){assert(controller==0&&button==0);posted++;}
int main(void){
 struct network_advertised_game *rows[9];wchar_t text[32];
 network_browser_begin();assert(started&&refreshes==1);assert(network_browser_rows(rows,0,0)==2);
 assert(!network_browser_select(rows[0],0));assert(refreshes==2);
 for(int i=0;i<256;i++){public[i].identifier[0]=i;public[i].identifier[1]=1;snprintf(public[i].name,33,"Host %03d",i);strcpy(public[i].invite,"halo://join/abc");strcpy(public[i].map,"bloodgulch");public[i].player_count=i%128;public[i].maximum_player_count=128;public[i].open=1;}
 public_count=256;clock_now+=1001;assert(network_browser_rows(rows,0,0)==9);assert(browser.count==256);assert(rows[1]->player_count==127);
 int seen=0;while(1){int n=network_browser_rows(rows,1,0);for(int i=1;i<n-1;i++){assert(network_browser_text(i,text,32));seen++;}if((browser.page+1)*7>=browser.count)break;assert(!network_browser_select(rows[n-1],0));}
 assert(seen==256);assert(browser.page==36);network_browser_select(rows[0],0);assert(browser.page==35);
 browser.page=0;network_browser_rows(rows,1,0);struct browser_game target=browser.games[0];
 assert(!network_browser_select(rows[1],0));assert(joins==1&&browser.pending==0);
 public_count=0;clock_now+=1001;network_browser_rows(rows,1,0);assert(browser.count==256&&browser.pending==0); // selection cannot jump
 memcpy(lan[0].xnaddr+2,target.identifier,6);lan[0].valid=1;lan[0].open=1;
 network_browser_rows(rows,1,0);assert(posted==1);network_browser_rows(rows,1,0);assert(posted==1);
 assert(network_browser_select(rows[1],0)==&lan[0]);assert(browser.pending==NONE);
 memset(lan,0,sizeof(lan));network_browser_select(rows[1],0);network_browser_rows(rows,2,0);assert(browser.pending==NONE); // moving cancels
 network_browser_select(rows[1],0);clock_now+=30001;network_browser_rows(rows,1,0);assert(failed==1&&browser.pending==NONE);
 // A newly discovered unrelated LAN host must never be joined for the selected invite.
 lan[0].valid=1;lan[0].xnaddr[2]=42;lan[0].xnaddr[3]=42;
 assert(!network_browser_select(rows[1],0));assert(browser.pending==0);
 network_browser_end();assert(!started&&browser.pending==NONE);
 puts("PASS: 256 listings, population order, every page, refresh, stable selection, exact host, cancel, timeout, one deferred join event");
}
'''
run('browser',prefix+b+stubs)
JAVA=ROOT/'port/android/app/src/main/java/com/halo/decomp';p=OUT/'UpdateCheck.java'
p.write_text('''package com.halo.decomp; public class UpdateCheck { public static void main(String[] a){
 for(int installed=1;installed<=40;installed++)for(int release=1;release<=40;release++)if(UpdatePolicy.newerCode(release,installed)!=(release>installed))throw new AssertionError();
 if(UpdatePolicy.newerCode(0,19)||UpdatePolicy.newerCode(20,0)||UpdatePolicy.newerCode(19,19)||UpdatePolicy.newerCode(19,20))throw new AssertionError();
 if(!UpdatePolicy.asset("v1.0.0",true).equals("HaloCE-Quest-1.0.0.apk"))throw new AssertionError();
 System.out.println("PASS: same-code promotion, newer candidate, upgrade and invalid version codes"); }}''')
subprocess.run(['javac','-d',str(OUT),str(JAVA/'UpdatePolicy.java'),str(p)],check=True)
subprocess.run(['java','-cp',str(OUT),'com.halo.decomp.UpdateCheck'],check=True)
print('PASS: test19 focused regressions')

# Upstream RFC8032 / X25519 binding and signed-listing tests, against production
# algorithms. Only the XDK platform include is replaced for this host harness.
for name in ['p2p_crypto.c','p2p_lobby.c']:
 source=(ROOT/'port/linux/src'/name).read_text()
 source=source.replace('#include "platform.h"', 'void platform_log(const char *, ...);\nvoid platform_translate_path(const char *, char *, unsigned int);')
 (OUT/name).write_text(source,encoding='utf-8')
exe=OUT/'signed-lobby'
subprocess.run(['clang','-std=gnu11','-DHALO_LINUX_PLATFORM_LAYER','-O1','-fsanitize=address','-ffunction-sections','-fdata-sections',
 '-I'+str(ROOT/'port/linux/src'),'-I'+str(ROOT/'port/linux/include'),'-I'+str(ROOT/'port/third_party/monocypher'),
 str(ROOT/'tools/p2p_lobby_check.c'),str(OUT/'p2p_crypto.c'),str(OUT/'p2p_lobby.c'),
 str(ROOT/'port/third_party/monocypher/monocypher.c'),str(ROOT/'port/third_party/monocypher/monocypher-ed25519.c'),
 '-Wl,--gc-sections','-pthread','-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
