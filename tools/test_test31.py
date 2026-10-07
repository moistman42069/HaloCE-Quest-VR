"""Test31: OpenCE build 145/network 22 and scoped Quest regressions.
Device play is still required; these checks establish protocol/source and logic invariants.
"""
from pathlib import Path
import hashlib, re, subprocess
ROOT = Path(__file__).resolve().parents[1]
def read(p): return (ROOT/p).read_text()
def run(name, source):
    out=ROOT/'build/test31'; out.mkdir(parents=True,exist_ok=True)
    p=out/(name+'.c'); p.write_text(source)
    subprocess.run(['clang','-std=gnu11','-O1','-fsanitize=address,undefined',str(p),'-lm','-o',str(out/name)],check=True)
    subprocess.run([str(out/name)],check=True)
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

# Exercise the production range helpers against both allocation layouts.
run('cache_bounds', r'''
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <limits.h>
typedef int boolean;
#define TRUE 1
#define TAG_CACHE_SIZE 4096
#define CUSTOM_EDITION_TAG_CACHE_BYTES_UPGRADED 8192
static int custom, missing;
static unsigned char storage[16384];
static void *physical_memory_get_tag_cache_base_address(void){return missing?0:storage;}
static void *halo_custom_edition_tag_cache(void){return missing?0:storage;}
static int custom_edition_cache_tags_loaded(void){return custom;}
''' + fn(cache,'cache_file_region_contains') + fn(cache,'cache_file_tag_cache_contains') + r'''
int main(void){
 for(custom=0;custom<2;custom++){
  int size=custom?CUSTOM_EDITION_TAG_CACHE_BYTES_UPGRADED:TAG_CACHE_SIZE;
  assert(cache_file_tag_cache_contains(storage,size));
  assert(cache_file_tag_cache_contains(storage+size-1,1));
  assert(!cache_file_tag_cache_contains(storage+size,1));
  assert(!cache_file_tag_cache_contains(storage,size+1));
  assert(!cache_file_tag_cache_contains(storage,0));
  assert(!cache_file_tag_cache_contains(storage,-1));
  assert(!cache_file_tag_cache_contains(storage,LONG_MAX));
  assert(!cache_file_tag_cache_contains((void *)((uintptr_t)storage-1),1));
  assert(!cache_file_tag_cache_contains((void *)UINTPTR_MAX,1));
  missing=1;assert(!cache_file_tag_cache_contains(storage,1));missing=0;
 }
 puts("PASS: production tag-cache bounds, both layouts: edges, missing allocation, zero/negative/overflow lengths and out-of-region addresses");
}
''')
assert 'CUSTOM_EDITION_TAG_CACHE_BYTES_UPGRADED' in fn(cache,'cache_file_tag_cache_contains')
assert 'cache_file_tag_cache_contains' in read('source/hs/hs.c')

config=read('port/linux/src/port_config.c')
assert '"vr.vehicle_warthog_hide_glass", _config_boolean, "true"' in config
assert '"vr.vehicle_warthog_hide_glass", _vr_setting_boolean' in read('port/linux/game/vr_menu.c')
glass=fn(read('port/linux/game/vr_render.c'),'vr_render_seat_transparent')
for guard in ('!vr_first_person_vehicles()', '!vr_seat_view()', 'object_get_ultimate_parent(object_index)', 'vr_settings_generation()', 'strcmp(profile, "warthog") || hide_warthog_glass'):
    assert guard in glass,guard
assert 'return shader_type == glass_type && hide_glass;' in glass
print('PASS: Warthog glass defaults to prior hidden behavior; persisted VR setting and own first-person seat scope')

frame=read('port/linux/src/vr_frame.c')
layout=fn(frame,'layout_controls')
fire=layout[layout.index('\tvr.pad_trigger[1] ='):layout.rindex('}')]
run('seated_fire', r'''
#include <assert.h>
#include <stdio.h>
#define HAND_EMPTY 0
static struct { int seated, hand_state, weapon_hand; float pad_trigger[2]; struct {float trigger[2];} frame; } vr;
static int physical; static int physical_weapons(void){return physical;}
static void fire(void){
''' + fire + r'''
}
int main(void){
 for(int seat=0;seat<2;seat++) for(int empty=0;empty<2;empty++)
 for(physical=0;physical<2;physical++) for(int hand=0;hand<2;hand++){
  vr.seated=seat; vr.hand_state=empty?HAND_EMPTY:1; vr.weapon_hand=hand;
  vr.frame.trigger[hand]=0.65f; vr.pad_trigger[0]=0.4f; fire();
  assert(vr.pad_trigger[1]==(!seat && physical && empty ? 0.0f:0.65f));
  assert(vr.pad_trigger[0]==0.4f);
 }
 puts("PASS: real trigger path: both hands, seated/foot, physical/classic, empty/held; secondary untouched");
}
''')

raster=read('source/rasterizer/xbox/rasterizer_xbox.c')
part=fn(raster,'rasterizer_vr_part_winding')
run('display_winding', r'''
#include <assert.h>
#include <string.h>
#include <stdio.h>
typedef unsigned char byte; typedef int boolean;
#define _rasterizer_vertex_type_model_compressed 5
struct vertex_buffer {int type;long count;}; struct triangle_buffer {int unused;};
static byte vertices[513*32];
static signed char vr_node_winding[44]; static short vr_node_winding_count=8;
static boolean vr_root_mirrored=1;static int mirrored=1,selected=-1,reads;
static int halo_vr_model_mirrored(void){return mirrored;}
static void halo_vr_skinning_mirrored(int n){selected=n;}
static int rasterizer_model_buffer_data(const struct vertex_buffer *v,const struct triangle_buffer *t,const void **data,const void **indices){reads++;*data=vertices;*indices=vertices;return 1;}
''' + part + r'''
static void v(int i,int node,int second,int weight){vertices[i*32+28]=node*3;vertices[i*32+29]=second*3;short w=weight;memcpy(vertices+i*32+30,&w,2);}
int main(void){
 struct vertex_buffer buffer={5,4};struct triangle_buffer triangles={0};
 for(int i=0;i<8;i++)vr_node_winding[i]=-1;vr_node_winding[7]=1;
 for(int i=0;i<4;i++)v(i,7,0,32767);
 rasterizer_vr_part_winding(&buffer,&triangles);assert(selected==0); /* display node 7, root mirrored */
 for(int i=0;i<4;i++)v(i,0,7,32767);
 rasterizer_vr_part_winding(&buffer,&triangles);assert(selected==1); /* body remains mirrored */
 for(int i=0;i<4;i++)v(i,0,7,0);
 rasterizer_vr_part_winding(&buffer,&triangles);assert(selected==0); /* zero influence ignored */
 v(3,0,7,10000);rasterizer_vr_part_winding(&buffer,&triangles);assert(selected==1); /* mixed: existing fallback */
 v(3,43,0,32767);rasterizer_vr_part_winding(&buffer,&triangles);assert(selected==1); /* bounds */
 selected=0;buffer.count=513;int before=reads;rasterizer_vr_part_winding(&buffer,&triangles);assert(selected==1 && reads==before);
 mirrored=0;selected=0;buffer.count=4;rasterizer_vr_part_winding(&buffer,&triangles);assert(selected==0 && reads==before);
 puts("PASS: actual part-winding helper: unmirrored display on mirrored root; both influences, bounds, per-part reset and right-hand no-op");
}
''')

weapons=read('source/items/weapons.c')
aim=read('source/game/aim_assist.c')
preview=fn(weapons,'weapon_vr_preview_primary_ray')
assert 'player_aim_projectile_internal(player_index, position, direction, TRUE)' in fn(aim,'player_aim_projectile')
assert 'player_aim_projectile_internal(player_index, position, direction, FALSE)' in fn(aim,'vr_preview_player_projectile')
assert 'if (record_target)' in fn(aim,'player_aim_projectile_internal')
render=fn(read('port/linux/game/vr_render.c'),'vr_render_windows')
assert 'weapon_vr_preview_primary_ray(weapon, player_index, &origin, &direction)' in render
assert 'aiming != unit_index' in render
assert 'world_reticle = vr.reticle_distance > 0.0f && (vr.hand_aiming || vr.seated)' in frame
run('turret_ray', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef int boolean; typedef float real;
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define TEST_FLAG(v,b) ((v)&(1u<<(b)))
#define MAXIMUM_MARKERS_PER_OBJECT 16
enum {_object_dead_bit=0,_weapon_trigger_projectiles_cannot_be_aimed_bit=1,
 _unit_fires_from_camera_bit=2,_weapon_trigger_uses_weapon_origin_bit=3};
typedef struct {float x,y,z;} real_point3d;
typedef struct {float i,j,k;} real_vector3d;
struct object_marker {struct {real_point3d position;real_vector3d forward;} matrix;};
struct weapon_trigger_definition {unsigned flags;real_point3d first_person_weapon_offset;};
struct block {int count; struct weapon_trigger_definition *address;};
struct weapon_definition {struct {struct block triggers;} weapon;};
struct weapon_datum {long definition_index;};
struct unit_datum {long definition_index;struct{unsigned damage_flags;}object;struct{long gunner_object_index;}unit;};
struct unit_definition {struct{unsigned flags;}unit;};
static struct weapon_datum gun;
static struct unit_datum body;
static struct unit_definition bodydef;
static struct weapon_trigger_definition trigger;
static struct weapon_definition def;
static real_vector3d up={0,0,1},left={0,1,0};
static real_vector3d *global_up3d=&up,*global_left3d=&left;
static int marker_present=1,assist_calls,adjust_calls,adjusted_origin,used_aim;
#define TAG_BLOCK_GET_ELEMENT(b,i,t) ((b)->address+(i))
static struct weapon_datum *weapon_get(long w){assert(w==7);return &gun;}
static struct weapon_definition *weapon_definition_get(long d){return &def;}
static long weapon_get_owner_object_index(long w){return 5;}
static long weapon_get_effect_object_index(long w){return 6;}
static struct unit_datum *unit_try_and_get(long u){assert(u==5);return &body;}
static struct unit_definition *unit_definition_get(long u){return &bodydef;}
static int object_get_marker_by_name(long w,const char *name,struct object_marker *m,int count){
 assert(w==6);m[0].matrix.position=(real_point3d){1,2,3};m[0].matrix.forward=(real_vector3d){0,1,0};return marker_present;}
static void unit_adjust_projectile_ray(long u,real_point3d *o,real_vector3d *f,real *v,int a,int b){
 assert(u==5);adjust_calls++;adjusted_origin=a!=0;used_aim=b!=0;if(a)o->z+=10;if(b)*f=(real_vector3d){1,0,0};}
static void cross_product3d(const real_vector3d *a,const real_vector3d *b,real_vector3d *c){
 *c=(real_vector3d){a->j*b->k-a->k*b->j,a->k*b->i-a->i*b->k,a->i*b->j-a->j*b->i};}
static float normalize3d(real_vector3d *v){float l=sqrtf(v->i*v->i+v->j*v->j+v->k*v->k);if(l>0){v->i/=l;v->j/=l;v->k/=l;}return l;}
static void point_from_line3d(const real_point3d *p,const real_vector3d *d,real a,real_point3d *o){
 *o=(real_point3d){p->x+d->i*a,p->y+d->j*a,p->z+d->k*a};}
static void vr_preview_player_projectile(long p,const real_point3d *o,real_vector3d *d){assert(p==9);assist_calls++;}
''' + preview + r'''
int main(void){
 real_point3d o;real_vector3d f;def.weapon.triggers=(struct block){1,&trigger};
 trigger.first_person_weapon_offset=(real_point3d){1,2,3};body.unit.gunner_object_index=8;
 assert(weapon_vr_preview_primary_ray(7,9,&o,&f));
 assert(!used_aim && !adjusted_origin && assist_calls==1);
 assert(o.x==-1 && o.y==3 && o.z==6 && f.i==0 && f.j==1);
 body.unit.gunner_object_index=NONE;bodydef.unit.flags=1u<<_unit_fires_from_camera_bit;
 assert(weapon_vr_preview_primary_ray(7,9,&o,&f));assert(used_aim && adjusted_origin);
 assert(o.x==2 && o.y==4 && o.z==16 && f.i==1 && f.j==0);
 trigger.flags=1u<<_weapon_trigger_uses_weapon_origin_bit;
 assert(weapon_vr_preview_primary_ray(7,9,&o,&f));assert(o.x==1 && o.y==2 && o.z==3);
 trigger.flags=1u<<_weapon_trigger_projectiles_cannot_be_aimed_bit;int calls=assist_calls;
 assert(weapon_vr_preview_primary_ray(7,9,&o,&f));assert(assist_calls==calls && f.i==0 && f.j==1);
 marker_present=0;assert(!weapon_vr_preview_primary_ray(7,9,&o,&f));
 marker_present=1;body.object.damage_flags=1;assert(!weapon_vr_preview_primary_ray(7,9,&o,&f));
 body.object.damage_flags=0;def.weapon.triggers.count=0;assert(!weapon_vr_preview_primary_ray(7,9,&o,&f));
 puts("PASS: real turret ray helper: gunner muzzle, driver aim, native offsets/origin flags, missing marker/dead/absent trigger guards");
}
''')

# The real update_peers/prediction code sends through a deterministic NAT
# model. Crypto is outside this simulation: delivery is an already authenticated
# peer packet, as peer_heard receives after the unchanged tunnel receive checks.
p2p=read('port/linux/src/p2p.c')
assert 'p2p.stun[i].mapped.address != p2p.stun[first].mapped.address' in fn(p2p,'stun_classify_mapping')
run('nat_punch', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define P2P_MAXIMUM_PEERS 8
#define P2P_IDENTIFIER_SIZE 16
#define P2P_JOIN_FAILED 4
#define P2P_JOIN_CONNECTED 3
#define PEER_TIMEOUT 20000
#define PING_INTERVAL 1000
#define PUNCH_TIMEOUT 30000
#define PUNCH_INTERVAL 200
#define ENDPOINT_SWITCH_TIME 3000
struct p2p_candidate {unsigned long address; unsigned short port;};
struct peer {int used,connected,is_host,rejected,candidate_count; unsigned int predicted_attempts;
 unsigned long offered_time,heard_time,sent_time,endpoint_heard_time;
 unsigned char identifier[16]; char name[33];
 struct p2p_candidate candidates[4],endpoint;};
static struct {struct peer peers[8]; int nat_strict,joining,join_stage; unsigned char join_host[16]; char join_failure[400];} p2p;
static unsigned long now; static int sends,extra,max_extra,full_cone,delivered;
static unsigned long actual_ip; static unsigned short actual_port;
static unsigned long p2p_now(void){return now;}
static int elapsed(unsigned long then,unsigned long delay){return now-then>=delay;}
static void platform_log(const char *format,...){(void)format;}
static void p2p_signal_stop_joining(void){}
static const char *address_text(unsigned long ip,unsigned short port,char *s){return "simulation";}
static void drop_peer(struct peer *p,const char *why){p->used=0;}
''' + fn(p2p,'network_long') + fn(p2p,'network_short') + fn(p2p,'peer_heard') + r'''
/* The remote has already sent to our stable public socket. Full cone accepts
   any source; port-restricted accepts only a tuple we have punched. Symmetric
   remote maps use actual_port rather than their STUN port. Two-egress uses
   actual_ip; only an advertised IP can be tried. */
static void peer_ping(struct peer *p,const struct p2p_candidate *c){
 sends++; int advertised=0;
 for(int i=0;i<p->candidate_count;i++) if(c->address==p->candidates[i].address && c->port==p->candidates[i].port) advertised=1;
 if(!advertised && !p->connected){extra++; assert(network_short(c->port)>=1024);}
 if(full_cone || (c->address==actual_ip && c->port==actual_port)){
  peer_heard(p,actual_ip,actual_port,1); delivered++;
 }
}
''' + fn(p2p,'prediction_public_address') + fn(p2p,'peer_predict_punch') + fn(p2p,'update_peers') + r'''
static void scenario(int strict,int cone,int delta,int egress,int advertised_second,int expected){
 memset(&p2p,0,sizeof(p2p)); sends=extra=delivered=0; full_cone=cone; now=0;
 struct peer *p=&p2p.peers[0]; p->used=1; p->is_host=1; p->candidate_count=1;
 p2p.nat_strict=strict; p2p.joining=1;
 p->candidates[0]=(struct p2p_candidate){network_long(0x08080808),network_short(40000)};
 if(advertised_second){p->candidates[1]=(struct p2p_candidate){network_long(0x09090909),network_short(41000)};p->candidate_count++;}
 actual_ip=network_long(egress?0x09090909:0x08080808);
 actual_port=network_short((egress?41000:40000)+delta);
 for(now=0;now<=30000 && p->used && !p->connected;now+=10){
  int previous=extra; update_peers(); assert(extra-previous<=2);
 }
 assert(p->connected==expected); assert(extra<=256);
 if(strict || cone || (!delta && !egress)) assert(extra==0);
 if(expected){int previous=extra;now+=1000;update_peers();assert(extra==previous);}
 else assert(strstr(p2p.join_failure,"VPN") && strstr(p2p.join_failure,"no relay"));
}
int main(void){
 scenario(0,1,15000,0,0,1); /* full cone receives symmetric peer's first packet */
 scenario(0,0,0,0,0,1); /* endpoint-independent mapping, port-restricted filter */
 scenario(0,0,7,0,0,1); /* sequential symmetric remote: bounded prediction succeeds */
 scenario(0,0,-9,0,0,1); /* negative port delta */
 scenario(0,0,12000,0,0,0); /* random symmetric remote: honest failure */
 scenario(1,0,7,0,0,0); /* no spray from a strict local NAT */
 scenario(-1,0,7,0,0,0); /* no spray before local mapping is measured */
 scenario(0,0,4,1,1,1); /* two egress IPs, actual route among advertised candidates */
 scenario(0,0,4,1,0,0); /* unadvertised egress cannot be guessed */
 assert(!prediction_public_address(network_long(0x7f000001)));
 assert(!prediction_public_address(network_long(0x0a000001)));
 assert(!prediction_public_address(network_long(0xc0a80001)));
 assert(!prediction_public_address(network_long(0xe0000001)));
 puts("PASS: real punching and endpoint adoption under full-cone, restricted, symmetric and two-egress NAT models; bounds/timeouts/stop-on-connect");
}
''')

assert 'stun_classify_mapping();' in fn(p2p,'stun_received')
run('nat_mapping_refresh', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <netinet/in.h>
struct candidate {unsigned long address;unsigned short port;};
struct stun_server {int has_mapped;struct candidate mapped;
 unsigned long address;unsigned short port;unsigned char transaction[12];const char *host;};
static struct {int nat_strict,reported_symmetric,reported_lenient,stun_count;
 struct stun_server stun[4];} p2p;
static void platform_log(const char *s,...){(void)s;}
static const char *address_text(unsigned long ip,unsigned short port,char *text){return "simulated";}
''' + fn(p2p,'stun_classify_mapping') + fn(p2p,'stun_received') + r'''
static void reply(int index,int ip,int port,int xor_mapped,int invalid){
 unsigned char packet[32]={1,1,0,12,0x21,0x12,0xa4,0x42};
 struct sockaddr_in from={0};
 struct stun_server *s=&p2p.stun[index];
 s->address=htonl(0x08080808+index);s->port=htons(3478);s->transaction[0]=index+1;s->host="test";
 from.sin_addr.s_addr=s->address;from.sin_port=s->port;
 memcpy(packet+8,s->transaction,12);
 packet[21]=xor_mapped?0x20:1;packet[23]=8;packet[25]=1;
 unsigned short np=htons(port);unsigned int ni=htonl(ip);
 memcpy(packet+26,&np,2);memcpy(packet+28,&ni,4);
 if(xor_mapped){for(int i=0;i<2;i++)packet[26+i]^=packet[4+i];for(int i=0;i<4;i++)packet[28+i]^=packet[4+i];}
 if(invalid==1)packet[8]^=0x80;
 if(invalid==2)from.sin_addr.s_addr++;
 stun_received(packet,invalid==3?31:32,&from);
}
int main(void){
 p2p.stun_count=4;stun_classify_mapping();assert(p2p.nat_strict==-1);
 p2p.stun[0].has_mapped=1;p2p.stun[0].mapped=(struct candidate){1,100};
 stun_classify_mapping();assert(p2p.nat_strict==-1);
 p2p.stun[1]=p2p.stun[0];stun_classify_mapping();assert(p2p.nat_strict==0);
 p2p.stun[1].mapped.address=2;stun_classify_mapping();assert(p2p.nat_strict==1);
 p2p.stun[0].mapped.address=2;stun_classify_mapping();assert(p2p.nat_strict==0);
 p2p.stun[1].mapped.port++;stun_classify_mapping();assert(p2p.nat_strict==1);
 p2p.stun[2]=p2p.stun[1];stun_classify_mapping();assert(p2p.nat_strict==1);
 p2p.stun[0]=p2p.stun[1];stun_classify_mapping();assert(p2p.nat_strict==0);
 p2p.stun[3]=p2p.stun[0];p2p.stun[3].mapped.address=3;
 stun_classify_mapping();assert(p2p.nat_strict==1);
 memset(&p2p,0,sizeof(p2p));p2p.stun_count=2;p2p.nat_strict=-1;
 reply(0,0x01020304,40000,1,0);assert(p2p.nat_strict==-1);
 reply(1,0x01020304,40000,0,0);assert(p2p.nat_strict==0);
 /* The response that changes a mapping must also change classification. */
 reply(1,0x05060708,40000,1,0);assert(p2p.nat_strict==1);
 reply(0,0x05060708,40000,1,0);assert(p2p.nat_strict==0);
 for(int bad=1;bad<=3;bad++){
  reply(1,0x01020304,45000,1,bad);assert(p2p.nat_strict==0);
 }
 reply(1,0x05060708,45000,1,0);assert(p2p.nat_strict==1);
 reply(0,0x05060708,45000,0,0);assert(p2p.nat_strict==0);
 puts("PASS: production STUN parser/classification: XOR/legacy mapping, immediate IP/port refresh, invalid source/transaction/length, all destinations and repeated changes");
}
''')
