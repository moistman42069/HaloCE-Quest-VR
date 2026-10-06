"""Execute production co-op actor/physics logic with a small mocked engine.

No game is launched. Wire longs are represented as 32-bit int in this host
harness (Android's real ILP32 ABI is checked by its full native build).
Run from Linux/WSL: python3 tools/test_campaign_actors.py
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/campaign-checks'
OUT.mkdir(parents=True, exist_ok=True)

def body(text, marker):
    start = text.index(marker)
    left = text.index('{', start)
    depth = 1
    end = left + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

def source(path):
    text = (ROOT / path).read_text()
    return re.sub(r'^#include[^\n]*\n', '', text, flags=re.M)

actors = source('port/linux/game/network_campaign_actors.c')
control = body(source('source/units/unit_control_data.h'), 'struct unit_control_data\n') + ';'
neutral = body(source('source/units/units.c'), 'else if (!TEST_FLAG(unit->unit.flags, _unit_actively_controlled_bit))').replace('else if', 'if', 1)
rest = body(source('port/linux/game/network_objects.c'), 'if (network_campaign_client() && object->object.type == _object_type_biped &&')
common = r'''
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
typedef float real;
typedef unsigned char byte;
typedef unsigned short word;
typedef struct { real i,j,k; } real_vector3d;
typedef struct { real i,j; } real_vector2d;
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define FLAG(b) (1u << (b))
#define TEST_FLAG(v,b) (((v) & FLAG(b)) != 0)
#define SET_FLAG(v,b,on) ((v) = ((v) & ~FLAG(b)) | ((on) ? FLAG(b) : 0))
#define VALID_INDEX(i,n) ((i) >= 0 && (i) < (n))
#define VALID_FLAGS(v,n) (((v) & ~((1u << (n))-1)) == 0)
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAXIMUM_TRACKED_OBJECTS 8
#define MAXIMUM_WEAPONS_PER_UNIT 4
#define NUMBER_OF_UNIT_ANIMATION_STATES 10
#define NUMBER_OF_UNIT_AIMING_SPEEDS 5
#define NUMBER_OF_UNIT_CONTROL_FLAGS 12
#define NUMBER_OF_UNIT_GRENADE_TYPES 2
#define TICKS_PER_SECOND 30
#define DATUM_INDEX_TO_ABSOLUTE_INDEX(i) ((i)&65535)
#define DATAGRAM_ENTRIES(t) 2
#define RELIABLE_ENTRIES(t) 2
#define _game_connection_network_server 1
#define _game_connection_network_client 2
#define _unit_actively_controlled_bit 0
#define _unit_controllable_bit 1
#define _unit_possessed_by_recording_bit 2
#define _object_dead_bit 0
#define _object_at_rest_bit 1
#define _object_on_ground_bit 2
#define _biped_airborne_bit 0
#define _object_type_biped 0
#define _distributed_object_at_rest_bit 1
#define _distributed_message_campaign_actors 36
#define _distributed_message_campaign_actor_impulses 39
#define _distributed_message_campaign_actor_animations 40
#define _unit_state_user_animation 5
#define _biped_absolute_movement_bit 3
#define _biped_no_collision_bit 4
#define ANIMATION_GRAPH_TAG 0x616e7472
#define _animation_base 1
#define TAG_BLOCK_GET_ELEMENT(block,index,type) (&((type *)(block)->address)[index])
#define _distributed_to_clients 0
#define _distributed_to_clients_reliably 1
struct distributed_message_header { word h; byte type,count; int time; };
struct obj { int damage_flags,flags,type; real_vector3d forward,translational_velocity,angular_velocity;
 struct { int animation_graph_index; struct { short index,frame_index; } state; } animation; };
struct ud { int player_index,actor_index,swarm_actor_index,flags; real_vector3d throttle,desired_looking_vector,desired_aiming_vector,desired_facing_vector; int control_flags; real primary_trigger;
 struct { int state; } animation; };
struct unit_datum { struct obj object; struct ud unit; };
struct biped_datum { struct obj object; struct ud unit; struct { int flags,airborne_ticks; } biped; };
struct object_datum { struct obj object; };
static struct biped_datum units[8];
static int ids[8],owned[8],now=10,connection=2,active=1,round_id=3,seed=8,logs,sent,aborted,played;
static real_vector3d zero;
static real_vector3d const *global_zero_vector3d=&zero;
struct unit_datum *unit_try_and_get(int id) { int s=DATUM_INDEX_TO_ABSOLUTE_INDEX(id); return s<8 && id==ids[s] ? (struct unit_datum*)&units[s] : 0; }
boolean network_campaign_playing(void) { return active; }
boolean network_campaign_client(void) { return active && connection==2; }
int game_connection(void) { return connection; }
int game_time_get(void) { return now; }
int network_game_get_number_of_games_played(void) { return round_id; }
int network_game_get_random_seed(void) { return seed; }
boolean distributed_object_index_valid(int id) { return id!=NONE && (id>>16)!=0; }
boolean network_objects_client_has(int id) { int s=DATUM_INDEX_TO_ABSOLUTE_INDEX(id); return s<8 && owned[s] && unit_try_and_get(id); }
void platform_log(char const *f, ...) { (void)f; logs++; }
void network_game_abort(void) { aborted++; }
void unit_set_actively_controlled(int id, boolean v) { struct unit_datum *u=unit_try_and_get(id); assert(u); SET_FLAG(u->unit.flags,_unit_actively_controlled_bit,v); SET_FLAG(u->unit.flags,_unit_controllable_bit,v); }
boolean unit_animation_impulse_valid(short i) { return i>=0 && i<14; }
boolean unit_start_animation_impulse(int id, short i, real_vector2d *v) { assert(unit_try_and_get(id)); assert(unit_animation_impulse_valid(i)); if(v) assert(v->i*v->i+v->j*v->j>=.99f); played++; return TRUE; }
static unsigned char animation_wire[256]; static short animation_wire_count; static int animation_sends;
void distributed_send(void *m, byte t, short n, word size, short dest) { assert(n>0 && n<=2); assert(size>sizeof(struct distributed_message_header)); assert((t==36&&dest==0)||(t==39&&dest==1)||(t==40&&dest==1)); sent+=n;
 if(t==40){assert(size<=sizeof(struct distributed_message_header)+sizeof(animation_wire)); memcpy(animation_wire,(byte*)m+sizeof(struct distributed_message_header),size-sizeof(struct distributed_message_header)); animation_wire_count=n; animation_sends++;} }
/* test26: the animation graphs (graph 7: a base animation of 30 frames, an overlay; others no graph) */
struct animation { short type,frame_count; };
struct animation_graph { struct { int count; struct animation *address; } animations; };
static struct animation graph_animations[2]={{_animation_base,30},{2,30}};
static struct animation_graph graph7={{2,graph_animations}};
static boolean tag_index_is_group(int tag, int group) { return group==ANIMATION_GRAPH_TAG && tag==7; }
static struct animation_graph *animation_graph_definition_get(int tag) { assert(tag==7); return &graph7; }
static int started, started_graph, started_frame, started_interpolate; static short started_animation;
static void unit_network_start_user_animation(int id, int graph, short animation, short frame, boolean interpolate)
 { assert(unit_try_and_get(id)); started++; started_graph=graph; started_animation=animation; started_frame=frame; started_interpolate=interpolate; }
struct biped_datum *biped_try_and_get(int id) { return (struct biped_datum*)unit_try_and_get(id); }
'''
stub_control = r'''
static void unit_control(int id, struct unit_control_data const *c) { struct unit_datum *u=unit_try_and_get(id); assert(u); u->unit.throttle=c->throttle; u->unit.control_flags=c->control_flags; u->unit.primary_trigger=c->primary_trigger; }
'''
tests = r'''
static void reset_units(void) { network_campaign_actors_reset(); network_campaign_actor_impulses_reset(); memset(units,0,sizeof(units)); for(int i=0;i<8;i++){ids[i]=65536+i;owned[i]=1;units[i].unit.player_index=units[i].unit.actor_index=units[i].unit.swarm_actor_index=NONE;} connection=2;active=1;now=10; }
static struct campaign_actor_control packet(void) { struct campaign_actor_control p={0}; p.round=round_id;p.seed=seed;p.object_index=ids[0];p.control.throttle.i=1;p.control.primary_trigger=1;p.control.control_flags=1;p.control.weapon_index=p.control.grenade_index=p.control.zoom_level=NONE;p.control.aiming_vector.i=p.control.facing_vector.i=p.control.looking_vector.i=1;return p; }
#define CHECK_REJECT(change) do { reset_units(); struct campaign_actor_control p=packet(); change; network_campaign_actors_receive(&p,1); assert(!received[0]); } while(0)
int main(void) {
 reset_units(); struct campaign_actor_control p=packet();
 network_campaign_actors_receive(&p,1); assert(received[0]); assert(units[0].unit.flags&1);
 native_neutral((struct unit_datum*)&units[0]); assert(units[0].unit.throttle.i==1);
 now=70;network_campaign_actor_update(ids[0]);assert(received[0]);
 now=71;network_campaign_actor_update(ids[0]);assert(!received[0]);assert(units[0].unit.throttle.i==0&&units[0].unit.primary_trigger==0&&!(units[0].unit.flags&1));
 /* Checkpoint restoring a previously borrowed active flag must clear it even after expiry. */
 units[0].unit.flags|=1;network_campaign_actors_reset();assert(!(units[0].unit.flags&1));
 network_campaign_actors_receive(&p,1);assert(received[0]);now=0;network_campaign_actor_update(ids[0]);assert(!received[0]);
 CHECK_REJECT(p.round++); CHECK_REJECT(p.seed++); CHECK_REJECT(p.object_index=-1);
 CHECK_REJECT(p.object_index=65544); CHECK_REJECT(p.object_index=131072); CHECK_REJECT(owned[0]=0);
 CHECK_REJECT(units[0].unit.player_index=0); CHECK_REJECT(units[0].object.damage_flags=1);
 CHECK_REJECT(p.control.throttle.i=NAN); CHECK_REJECT(p.control.throttle.i=4);
 CHECK_REJECT(p.control.aiming_vector.i=INFINITY); CHECK_REJECT(p.control.facing_vector.i=0);
 CHECK_REJECT(p.control.control_flags=0xffff); CHECK_REJECT(p.control.primary_trigger=2);
 CHECK_REJECT(p.control.animation_state=99); CHECK_REJECT(p.control.aiming_speed=99);
 CHECK_REJECT(p.control.weapon_index=4); CHECK_REJECT(p.control.grenade_index=2); CHECK_REJECT(p.control.zoom_level=3);
 CHECK_REJECT(connection=1); CHECK_REJECT(active=0);
 reset_units();p=packet();network_campaign_actors_receive(&p,1);units[0].object.damage_flags=1;network_campaign_actor_update(ids[0]);assert(!received[0]);
 reset_units();connection=1;sent=0;for(int i=0;i<5;i++)network_campaign_actor_capture(ids[i],&p.control);network_campaign_actors_tick();assert(sent==5);network_campaign_actors_tick();assert(sent==5);
 real_vector2d align={1,0};network_campaign_actor_impulse_capture(ids[0],3,&align);assert(impulse_count==1);struct campaign_actor_impulse e=impulses[0];network_campaign_actors_tick();assert(sent==6&&impulse_count==0);
 /* A save/BSP reset preserves events; timeline reset clears them. */
 network_campaign_actor_impulse_capture(ids[0],3,&align);network_campaign_actors_reset();assert(impulse_count==1);network_campaign_actor_impulses_reset();assert(impulse_count==0);
 for(int i=0;i<300;i++)network_campaign_actor_impulse_capture(ids[0],3,&align);assert(impulse_count==256&&impulse_overflowed&&aborted==0);network_campaign_actor_impulses_reset();
 connection=2;played=0;network_campaign_actor_impulses_receive(&e,1);assert(played==1);
 e.impulse=14;network_campaign_actor_impulses_receive(&e,1);assert(played==1);e.impulse=3;e.alignment.i=NAN;network_campaign_actor_impulses_receive(&e,1);assert(played==1);e.alignment.i=1;e.seed++;network_campaign_actor_impulses_receive(&e,1);assert(played==1);
 reset_units(); units[0].biped.flags=1;units[0].biped.airborne_ticks=40;
 apply_rest((struct object_datum*)&units[0],1);assert(!units[0].biped.flags && !units[0].biped.airborne_ticks);assert(units[0].object.flags&FLAG(_object_at_rest_bit));assert(rest_tolerance==0);
 apply_rest((struct object_datum*)&units[0],0);assert(!(units[0].object.flags&FLAG(_object_at_rest_bit)));assert(units[0].object.translational_velocity.i==.2f);
 units[0].unit.player_index=0;units[0].biped.flags=1;apply_rest((struct object_datum*)&units[0],1);assert(units[0].biped.flags==1);
 units[0].unit.player_index=NONE;active=0;apply_rest((struct object_datum*)&units[0],1);assert(units[0].biped.flags==1);
 /* test26: the host's user animations: a start goes as the host played it (its frame at the tick's end), with the
 biped's flags; reliable, once a tick, three in two messages; the client plays it and takes the flags */
 reset_units();connection=1;animation_sends=0;
 for(int i=0;i<3;i++){units[i].unit.animation.state=_unit_state_user_animation;units[i].object.animation.animation_graph_index=7;
  units[i].object.animation.state.index=0;units[i].object.animation.state.frame_index=(short)(4+i);
  network_campaign_actor_animation_capture(ids[i],i==1);}
 units[0].biped.flags=FLAG(_biped_absolute_movement_bit)|FLAG(_biped_no_collision_bit);
 network_campaign_actors_tick();assert(animation_sends==2&&animation_wire_count==1);
 network_campaign_actors_tick();assert(animation_sends==2); /* (sent once) */
 /* one start then the flags alone: the flags and the start in one entry, read at the tick's end */
 network_campaign_actor_animation_capture(ids[0],1);network_campaign_actor_movement_capture(ids[0]);network_campaign_actors_tick();
 assert(animation_sends==3&&animation_wire_count==1);
 {unsigned char wire[256];memcpy(wire,animation_wire,sizeof(wire));
  connection=2;started=0;memset(&units[0].biped,0,sizeof(units[0].biped));
  network_campaign_actor_animations_receive(wire,1);
  assert(started==1&&started_graph==7&&started_animation==0&&started_frame==4&&started_interpolate);
  assert(TEST_FLAG(units[0].biped.flags,_biped_absolute_movement_bit)&&TEST_FLAG(units[0].biped.flags,_biped_no_collision_bit));
  /* refused: another round or game, a unit the client does not have, dead, unknown flags, no graph, a bad index,
  an overlay, a frame past the end; not on the host */
  struct campaign_actor_animation e; memcpy(&e,wire,sizeof(e));
  #define REFUSE(change) do{struct campaign_actor_animation c=e;change;started=0;units[0].biped.flags=0;network_campaign_actor_animations_receive(&c,1);assert(!started&&!units[0].biped.flags);}while(0)
  REFUSE(c.round++);REFUSE(c.seed++);REFUSE(owned[0]=0);REFUSE(c.object_index=131072);REFUSE(units[0].object.damage_flags=1);
  REFUSE(c.flags|=0x10);REFUSE(connection=1);
  owned[0]=1;units[0].object.damage_flags=0;connection=2;
  #define NO_START(change) do{struct campaign_actor_animation c=e;change;started=0;network_campaign_actor_animations_receive(&c,1);assert(!started);}while(0)
  NO_START(c.animation_graph_index=8);NO_START(c.animation_graph_index=NONE);NO_START(c.animation_index=2);NO_START(c.animation_index=-1);
  NO_START(c.animation_index=1);NO_START(c.frame_index=30);NO_START(c.frame_index=-1);
  /* the flags alone (a command list ending): they are cleared */
  units[0].biped.flags=FLAG(_biped_no_collision_bit);{struct campaign_actor_animation c=e;c.flags=0;c.animation_graph_index=NONE;
   started=0;network_campaign_actor_animations_receive(&c,1);assert(!started&&!units[0].biped.flags);}}
 /* host: a start ended the same tick (no longer a user animation) goes not at all, unless its flags changed;
 nothing on a client; a timeline reset forgets the marks */
 reset_units();connection=1;animation_sends=0;units[0].unit.animation.state=0;
 network_campaign_actor_animation_capture(ids[0],0);network_campaign_actors_tick();assert(animation_sends==0);
 network_campaign_actor_animation_capture(ids[0],0);network_campaign_actor_movement_capture(ids[0]);network_campaign_actors_tick();assert(animation_sends==1);
 network_campaign_actor_movement_capture(ids[1]);network_campaign_actor_impulses_reset();network_campaign_actors_tick();assert(animation_sends==1);
 connection=2;network_campaign_actor_movement_capture(ids[1]);connection=1;network_campaign_actors_tick();assert(animation_sends==1);
 puts("PASS: production actor ownership, invalid packets, timeout/death/rewind/reset, host batching, impulses and NPC rest scope");
 puts("PASS: test26 user animations: sent once as the host played them (frame, interpolation, absolute movement, no collision),"
      " batched reliably, applied on the client; another round/game, foreign/dead units, unknown flags, bad graphs, indexes, overlays"
      " and frames refused; ended starts unsent; flags alone cleared; host only; reset forgets");
}
'''
rest_wrapper = '''static float rest_tolerance;
static void apply_rest(struct object_datum *object,int at_rest) {
 struct { byte flags; } s = {at_rest ? 2 : 0}, *state=&s;
 real_vector3d velocity={.2f,0,0},angular_velocity={0,0,0};
 real tolerance=.1f,blend_distance=1.f;
''' + rest + '\n rest_tolerance=tolerance; (void)blend_distance; }\n'
unit = common + control + stub_control + actors + '\nstatic void native_neutral(struct unit_datum *unit) {\n' + neutral + '\n}\n' + rest_wrapper + tests
unit = re.sub(r'\blong\b','int',unit)
p=OUT/'actors.c';p.write_text(unit)
subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-Wno-sign-compare','-fsanitize=address,undefined',str(p),'-o',str(OUT/'actors')],check=True)
subprocess.run([str(OUT/'actors')],check=True)
