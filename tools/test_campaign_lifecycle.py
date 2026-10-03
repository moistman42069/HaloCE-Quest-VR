"""Run the production co-op barrier state machine with mocked engine/transport.
No game, device or network connection is started. This checks orchestration,
not whether a mission's assets and scripts behave correctly at runtime.
"""
from pathlib import Path
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/campaign-checks';OUT.mkdir(parents=True,exist_ok=True)
s=(ROOT/'port/linux/game/network_campaign_lifecycle.c').read_text()
s=re.sub(r'^#include[^\n]*\n','',s,flags=re.M)
prefix=r'''
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <limits.h>
typedef int boolean;
typedef unsigned char byte;
typedef unsigned short word;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define MAX(a,b) ((a)>(b)?(a):(b))
#define VALID_INDEX(i,n) ((i)>=0&&(i)<(n))
#define _game_connection_network_server 1
#define _game_connection_network_client 2
#define _distributed_message_campaign_lifecycle 34
#define _distributed_to_clients_reliably 1
#define _distributed_to_host_reliably 2
static int active=1,conn=1,tick=10,round_id=2,seed=3,global_structure_bsp_index=0;
static unsigned int ms=100;
static int aborts,saves,restores,restarts,snapshots,resets,sync_ready=1,checkpoint=1,io_ok=1,hash_ok=1,sent,op,client_clock,server_clock,script_resets;
static struct { struct { char name[32]; } map; } game;
static struct { struct { int count; } structure_bsp_references; } scenario={{3}};
struct distributed_message_header { word h;byte type,count;int time; };
#define network_game_get_game() (&game)
#define global_scenario_get() (&scenario)
int game_time_get(void) { return tick; }
int game_connection(void) { return conn; }
int network_game_get_number_of_games_played(void) { return round_id; }
int network_game_get_random_seed(void) { return seed; }
boolean network_campaign_active(void) { return active; }
boolean network_campaign_playing(void) { return active; }
boolean network_campaign_held(void);
void platform_log(char const*f,...) { (void)f; }
unsigned int system_milliseconds(void) { return ms; }
void network_game_abort(void) { aborts++; }
void game_time_set_distributed(int t) { tick=t; }
void render_interpolation_reset(void) { }
void update_queues_reset_and_fill_with_lies(void) { }
void network_distributed_resynchronize(void) { resets++; }
void network_campaign_script_reset(void) { script_resets++; }
boolean cache_files_campaign_digest(char const *m,byte *d) { (void)m;memset(d,7,32);return hash_ok; }
int distributed_client_machines(int *m,int n) { assert(n==2);m[0]=1;return 1; }
boolean network_objects_synchronized(void) { return sync_ready; }
boolean game_state_campaign_has_checkpoint(void) { return checkpoint; }
boolean game_state_campaign_save(void) { saves++;return io_ok; }
boolean game_state_campaign_restore(void) { restores++;tick=5;return io_ok; }
boolean scenario_switch_structure_bsp(short bsp) { global_structure_bsp_index=bsp;return io_ok; }
boolean network_campaign_change_level(boolean next) { assert(!next);restarts++;return TRUE; }
void network_game_client_campaign_clock(int t) { client_clock=t; }
void network_game_server_campaign_clock(int t) { server_clock=t; }
void network_distributed_campaign_snapshot(int m) { assert(m==1);snapshots++; }
void distributed_send(void*m,byte type,short count,word size,short dest);
'''
suffix=r'''
void distributed_send(void*m,byte type,short count,word size,short dest) { assert(type==34&&count==1);assert(size==64);assert(dest==(conn==1?1:2));sent++;op=((struct campaign_barrier*)((byte*)m+8))->operation; }
static void begin(void) { conn=1;active=1;epoch=0;tick=10;ms=100;aborts=0;hash_ok=io_ok=sync_ready=checkpoint=1;network_campaign_loaded();assert(phase==PHASE_HOST_WAIT&&epoch==1);network_campaign_frame();assert(op==CAMPAIGN_READY); }
static struct campaign_barrier client_ready(void) { begin();struct campaign_barrier offer=barrier;memcpy(offer.digest,local_digest,32);conn=2;network_campaign_loaded();assert(phase==PHASE_CLIENT_WAIT);network_campaign_lifecycle_receive(NONE,&offer,sizeof(offer));assert(phase==PHASE_CLIENT_APPLY);network_campaign_frame();assert(phase==PHASE_CLIENT_SNAPSHOT&&op==CAMPAIGN_ACK);return offer; }
int main(void) {
 struct campaign_barrier e=client_ready();e.operation=CAMPAIGN_RELEASE;
 network_campaign_lifecycle_receive(NONE,&e,sizeof(e));assert(phase==PHASE_IDLE&&client_clock==10&&!aborts);
 int time=network_campaign_encode_time(123);assert(network_campaign_decode_time(&time)&&time==123);time=0;assert(!network_campaign_decode_time(&time));
 e=client_ready();e.operation=CAMPAIGN_RELEASE;sync_ready=0;network_campaign_lifecycle_receive(NONE,&e,sizeof(e));assert(aborts==1);
 begin();e=barrier;memcpy(e.digest,local_digest,32);e.operation=CAMPAIGN_ACK;network_campaign_lifecycle_receive(9,&e,sizeof(e));assert(!peer_ack);network_campaign_lifecycle_receive(1,&e,sizeof(e));assert(peer_ack);network_campaign_frame();assert(phase==PHASE_IDLE&&op==CAMPAIGN_RELEASE&&snapshots>0);
 assert(network_campaign_checkpoint_request(FALSE));assert(phase==PHASE_HOST_WAIT&&barrier.operation==CAMPAIGN_SAVE);network_campaign_frame();assert(saves>0);e=barrier;memcpy(e.digest,local_digest,32);e.operation=CAMPAIGN_ACK;network_campaign_lifecycle_receive(1,&e,sizeof(e));network_campaign_frame();assert(checkpoint_valid&&phase==PHASE_IDLE);
 assert(network_campaign_checkpoint_request(TRUE));network_campaign_frame();assert(restores>0&&barrier.time==5&&script_resets>0);
 /* An in-flight save/restore defers subsequent requests, restore takes priority. */
 network_campaign_checkpoint_request(TRUE);network_campaign_checkpoint_request(FALSE);assert(deferred_checkpoint==2);
 e=client_ready();e.operation=CAMPAIGN_RELEASE;e.seed++;network_campaign_lifecycle_receive(NONE,&e,sizeof(e));assert(phase==PHASE_CLIENT_SNAPSHOT);e.seed--;e.digest[0]++;network_campaign_lifecycle_receive(NONE,&e,sizeof(e));assert(aborts==1);
 begin();ms+=120001;network_campaign_frame();assert(aborts==1);
 begin();phase=PHASE_IDLE;checkpoint_valid=0;network_campaign_checkpoint_request(TRUE);assert(restarts==1);
 begin();phase=PHASE_IDLE;epoch=255;network_campaign_checkpoint_request(FALSE);assert(aborts==1);
 begin();phase=PHASE_IDLE;network_campaign_bsp_switched(2);assert(barrier.bsp==2&&barrier.operation==CAMPAIGN_BSP);
 conn=2;phase=PHASE_IDLE;saves=0;network_campaign_checkpoint_request(FALSE);assert(saves==0&&phase==PHASE_IDLE);
 active=0;time=99;assert(network_campaign_encode_time(time)==99&&network_campaign_decode_time(&time));assert(!network_campaign_checkpoint_request(FALSE));
 puts("PASS: production campaign ready/ACK/release, snapshots, save/restore, deferred requests, clocks, bad sender/digest, timeout, generation and PvP isolation");
}
'''
unit=re.sub(r'\blong\b','int',prefix+s+suffix)
p=OUT/'lifecycle.c';p.write_text(unit)
subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-sign-compare','-fsanitize=address,undefined',str(p),'-o',str(OUT/'lifecycle')],check=True)
subprocess.run([str(OUT/'lifecycle')],check=True)
