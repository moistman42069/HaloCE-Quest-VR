"""Test26 (1.0.8): co-op cutscenes and the co-op client's crash, a Quest 2
client's red text, the first Quest's start, the HUD and reticle toggles,
head-gesture reach, the wrist HUD, melee along the gun, and fingers bending
smoothly against walls.

Evidence (kept private): two co-op logs and videos (a phone hosting, a Quest
joined, 2026-10-04) show the client's characters standing where they were
in a cutscene while the host's positions slid them, and the client halting
on unit_dialogue.c #406 as a crewman was shot (symbolized stack:
network_campaign_script_receive -> hs_campaign_replay -> scripted_sound_new
-> unit_notify_impulse_sound). A Quest 2 client's screen filled with "its
host's rules" warnings. A first Quest (Android 10) log: "cannot reserve the
Xbox memory window at 80000000 (No such file or directory)". Production
functions run under ASan/UBSan with small stubs; where a fix answers a
reproduced fault, the 1.0.7 code (9bca3958) is run too and shown to fail.
"""
from pathlib import Path
import re, subprocess
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test26'; OUT.mkdir(parents=True, exist_ok=True)
BEFORE = '9bca3958'  # test25, 1.0.7


def fn(text, name):
    m = re.search(r'^(?:static )?(?:inline )?[\w *]+\b' + re.escape(name) + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert m, name
    a = text.index('{', m.start()); b = a + 1; depth = 1
    while depth:
        depth += (text[b] == '{') - (text[b] == '}'); b += 1
    return text[m.start():b] + '\n'


def between(text, start, end, include_end=True):
    a = text.index(start)
    b = text.index(end, a + len(start))
    return text[a:b + (len(end) if include_end else 0)] + '\n'


def run(name, text, std='gnu11'):
    p = OUT / (name + '.c'); p.write_text(text)
    subprocess.run(['clang', '-std=' + std, '-O1', '-Wall', '-Wextra', '-Wno-unused-function', '-Wno-unused-variable',
                    '-Wno-unused-parameter', '-Wno-missing-field-initializers', '-Wno-missing-braces',
                    '-fsanitize=address,undefined', '-I', str(ROOT), str(p), '-lm', '-o', str(OUT / name)], check=True)
    subprocess.run([str(OUT / name)], check=True)


def read(path, encoding='utf-8'):
    return (ROOT / path).read_text(encoding=encoding)


def git_show(path, commit=BEFORE):
    return subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT, text=True, encoding='latin-1')


frame = read('port/linux/src/vr_frame.c')
render = read('port/linux/game/vr_render.c')
menu = read('port/linux/game/vr_menu.c')
config = read('port/linux/src/port_config.c')
vr_h = read('port/linux/src/vr.h')
units = read('source/units/units.c', 'latin-1')
dialogue = read('source/units/unit_dialogue.c', 'latin-1')
bipeds = read('source/units/bipeds.c', 'latin-1')
obey = read('source/ai/action_obey.c', 'latin-1')
scripting = read('source/units/unit_scripting_commands.c', 'latin-1')
actors = read('port/linux/game/network_campaign_actors.c')
objects_net = read('port/linux/game/network_objects.c')
campaign_h = read('port/linux/game/network_campaign.h')
distributed_h = read('port/linux/game/network_distributed.h')
distributed_c = read('port/linux/game/network_distributed.c')
script_c = read('port/linux/game/network_campaign_script.c')
campaign_objects = read('port/linux/game/network_campaign_objects.c')
breakable = read('source/physics/breakable_surfaces.c', 'latin-1')
cheats = read('source/game/cheats.c', 'latin-1')
graphics = read('port/linux/game/vr_graphics.c')
console_vars = read('source/rasterizer/rasterizer_console_vars.h', 'latin-1')
host_memory = read('port/android/host/host_memory.c')
host_main = read('port/android/host/host_main.c')
host_xr = read('port/android/host/host_xr.c')
abi = read('port/android/include/halo_android_abi.h')
hud = read('source/interface/hud.c', 'latin-1')
hud_weapon = read('source/interface/hud_weapon.c', 'latin-1')
main_c = read('source/main/main.c', 'latin-1')
client_manager = read('source/networking/network_client_manager.c', 'latin-1')
game_state = read('source/saved games/game_state.c', 'latin-1')
gradle = read('port/android/app/build.gradle')
listing = read('port/android/app/src/main/java/com/halo/decomp/ServerListing.java')
browser = read('port/android/app/src/main/java/com/halo/decomp/ServerBrowser.java')
updater = read('port/android/app/src/main/java/com/halo/decomp/Updater.java')
package = read('tools/package-quest.py')

# --- 1. the co-op client's crash: a death scream replayed on a unit already dead here
notify = fn(dialogue, 'unit_notify_impulse_sound')
guard = ('if (unit->unit.speech.current.sound_definition_index != sound_definition_index &&\n'
         '\t\tTEST_FLAG(unit->object.damage_flags, _object_dead_bit))\n\t{\n\t\treturn;\n\t}')
assert guard in notify, 'the dead unit keeps no speech'
assert notify.index('unit_speak(unit_index, play_type, &speech_item);') < notify.index(guard) < notify.index('406,'), \
    'after unit_speak (the sound already plays), before assertion #406'
print('PASS: a co-op client replaying the host\'s death scream on a unit already dead here no longer halts (#406); '
      'the sound plays, the dead unit keeps no speech')

# --- 2. a resting object's teleport goes out at once (cutscene characters placed as on the host)
send = fn(objects_net, 'distributed_host_send_states')
assert 'if (at_rest && !was_moving && !distributed_host_rest_moved(absolute_index, object_index))' in send or (
    'if (at_rest && !distributed_host_rest_state_due(absolute_index) &&\n'
        '\t\t\t!distributed_host_rest_moved(absolute_index, object_index))' in send)  # (test29: with OpenCE build 144's rest repeats)
assert send.count('distributed_host_note_rest_sent(absolute_index, object_index);') == 2, 'each state sent is noted'
tolerances = ''.join(re.findall(r'#define REMOTE_OBJECT_(?:ANGLE_)?TOLERANCE [^\n]+\n', objects_net))
assert tolerances.count('#define') == 2
rest_state = re.search(r'static struct\n\{\n\tlong object_index;\n.*?\} objects_host_rest_sent\[MAXIMUM_TRACKED_OBJECTS\];\n',
                       objects_net, re.S).group(0)
run('rest_resend', r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
typedef int boolean; typedef float real;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
typedef union { struct { real x,y,z; }; real n[3]; } real_point3d;
typedef union { struct { real i,j,k; }; real n[3]; } real_vector3d;
#define MAXIMUM_TRACKED_OBJECTS 4
''' + tolerances + r'''
struct object_datum { struct { real_point3d position; real_vector3d forward, up; } object; };
static struct object_datum objects[4];
static struct object_datum *object_get(long i){ return &objects[i & 3]; }
''' + rest_state + fn(objects_net, 'distributed_host_note_rest_sent') + fn(objects_net, 'distributed_host_rest_moved') + r'''
static void yaw(struct object_datum *o, float degrees){ float r=degrees*3.14159265f/180; o->object.forward=(real_vector3d){{cosf(r),sinf(r),0}}; }
int main(void){
 long a=0x10000, b=0x20000;
 for(int i=0;i<4;i++){objects[i].object.forward.i=1;objects[i].object.up.k=1;}
 /* first seen (its creation carried where it is), then unmoved: nothing more */
 assert(!distributed_host_rest_moved(0,a)); assert(!distributed_host_rest_moved(0,a));
 /* a script's teleport: at once; a nudge within the tolerance: not */
 objects[0].object.position.x=0.04f; assert(!distributed_host_rest_moved(0,a));
 objects[0].object.position.x=3.0f; assert(distributed_host_rest_moved(0,a));
 distributed_host_note_rest_sent(0,a); assert(!distributed_host_rest_moved(0,a));
 /* turned: 8 degrees within, 15 out; tilted 15 out */
 yaw(&objects[0],8); assert(!distributed_host_rest_moved(0,a));
 yaw(&objects[0],15); assert(distributed_host_rest_moved(0,a)); distributed_host_note_rest_sent(0,a);
 { float r=15*3.14159265f/180; objects[0].object.up=(real_vector3d){{sinf(r),0,cosf(r)}}; }
 assert(distributed_host_rest_moved(0,a)); distributed_host_note_rest_sent(0,a);
 /* a position gone wrong goes too */
 objects[0].object.position.y=NAN; assert(distributed_host_rest_moved(0,a)); objects[0].object.position.y=0;
 objects[0].object.position.z=INFINITY; assert(distributed_host_rest_moved(0,a)); objects[0].object.position.z=0;
 distributed_host_note_rest_sent(0,a);
 /* another object in the slot: first seen */
 objects[0].object.position.x=-50; assert(!distributed_host_rest_moved(0,b)); assert(!distributed_host_rest_moved(0,b));
 puts("PASS: a resting object teleported or turned by a script goes out at once (5 cm, 0.98 as the client's own"
      " tolerances; not-a-number too); unmoved, nudged or newly seen ones wait their turn as before");
}
''')

# --- 3-5. (test27) the CE02 co-op these replicated through is retired: OpenCE's co-op
# (network_coop.c, network_actors.c, network 20) replicates the host's custom animations and
# AI user animations, and glass, itself. What remains of test26 here is checked against it.
start = fn(units, 'unit_start_user_animation')
assert 'network_coop_note_unit_animation(unit_index, animation_graph_index, animation_index,' in start
assert 'network_actors_note_user_animation(unit_index, animation_graph_index, animation_index,' in start
assert 'network_campaign_actor_animation_capture(' not in start, "the retired CE02 capture is gone"
assert breakable.count('network_coop_note_surface_broken(') == 2, 'both break sites, as OpenCE'
port_break = fn(breakable, 'breakable_surface_port_break')
assert 'breakable_surface_index < 0 || breakable_surface_index >= structure_bsp->breakable_surfaces.count' in port_break
assert '!breakable_surface_extant(breakable_surface_index)' in port_break
assert '(theirs & 0xFF00) == 0xCE00' in client_manager and 'This version plays co-op as OpenCE does' in client_manager
assert 'isCampaign(version)' in listing and 'Co-op of this app 1.0.8 or older' in listing
print("PASS: (test27) co-op animations and glass replicate through OpenCE's co-op; a 1.0.8 (CE02) host is listed and refused by name")

# --- 6. a Quest 2 client's red text: the enforcer and the medium preset fought every frame
options = between(console_vars, 'struct rasterizer_debug_options\n{', '\n};')
graphics_body = between(graphics, 'enum\n{\n\t_preset_low,', '\n#endif', include_end=False)
graphics_before = git_show('port/linux/game/vr_graphics.c')
assert fn(graphics_before, 'read_settings') == fn(graphics, 'read_settings')
assert between(graphics_before, 'static struct graphics_effect effects[] =', '};') == \
    between(graphics, 'static struct graphics_effect effects[] =', '};'), 'the presets themselves unchanged'
cheats_before = git_show('source/game/cheats.c')
old_enforce = fn(cheats_before, 'cheats_network_client_rasterizer_enforce').replace(
    'cheats_network_client_rasterizer_enforce(', 'old_rasterizer_enforce(', 1)
old_apply = fn(graphics_before, 'vr_graphics_apply').replace('vr_graphics_apply(', 'old_vr_graphics_apply(', 1)
enforce = fn(cheats, 'cheats_network_client_enforce')
assert 'if (changed && !warned)' in enforce and 'warned = FALSE;' in enforce, 'said once a game'
run('red_text', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef unsigned char byte; typedef byte boolean; typedef float real;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
''' + options + r'''
struct rasterizer_debug_options rasterizer_debug_options;
boolean render_shadows, render_particles_enabled, render_particle_systems_enabled, render_contrails_enabled,
 render_weather_particle_systems_enabled, decals_enabled, weather;
static const char *system_name, *user_value="auto";
static int client=1;
static const char *config_string(const char *k){ return !strcmp(k,"graphics.preset") ? "auto" : user_value; }
static const char *vr_system_name(void){ return system_name; }
static int vr_settings_generation(void){ return 1; }
static boolean network_game_distributed_client(void){ return client; }
static void platform_log(const char *f, ...){ (void)f; }
''' + fn(cheats, 'cheats_network_client_switch_free') + fn(cheats, 'cheats_network_client_switch_enforced') +
    fn(cheats, 'cheats_network_client_rasterizer_enforce') + old_enforce + graphics_body + old_apply + r'''
static void game_starts(void){
 memset(&rasterizer_debug_options,0,sizeof(rasterizer_debug_options));
 for(boolean *p=&rasterizer_debug_options.draw_environment_lightmaps;p<=&rasterizer_debug_options.draw_environment_fog_screen;p++) *p=TRUE;
 rasterizer_debug_options.draw_water=rasterizer_debug_options.draw_detail_objects=rasterizer_debug_options.draw_lens_flares=TRUE;
 rasterizer_debug_options.fog_atmospheric_enabled=rasterizer_debug_options.fog_planar_enabled=TRUE;
 rasterizer_debug_options.bump_mapping_enabled=rasterizer_debug_options.active_camouflage_multipass_enabled=TRUE;
 rasterizer_debug_options.draw_environment=2;
 render_shadows=render_particles_enabled=render_particle_systems_enabled=render_contrails_enabled=TRUE;
 render_weather_particle_systems_enabled=decals_enabled=weather=TRUE;
 memset(&vr_graphics,0,sizeof(vr_graphics));
}
/* frames in which the host's rules put something back (each one a warning, before) */
static int fights(int old, int order, int frames){
 int changed_frames=0; game_starts();
 for(int f=0;f<frames;f++){ boolean changed;
  if(order){ old?old_vr_graphics_apply():vr_graphics_apply(); changed=client&&(old?old_rasterizer_enforce():cheats_network_client_rasterizer_enforce()); }
  else{ changed=client&&(old?old_rasterizer_enforce():cheats_network_client_rasterizer_enforce()); old?old_vr_graphics_apply():vr_graphics_apply(); }
  if(f>=2&&changed) changed_frames++; }
 return changed_frames;
}
int main(void){
 const char *systems[]={"Oculus Quest","Oculus Quest 2","Meta Quest 3"}, *values[]={"auto","off","on"};
 /* 1.0.7: the Quest 2's medium preset and the host's rules fought every frame */
 system_name="Oculus Quest 2"; user_value="auto"; client=1;
 int before=fights(1,0,100); assert(before>=95);
 /* now: no fight on any headset, any setting, either order */
 for(int s=0;s<3;s++) for(int v=0;v<3;v++) for(int order=0;order<2;order++){
  system_name=systems[s]; user_value=values[v];
  assert(fights(0,order,100)==0);
  /* what everyone must draw is drawn: water, grass, fog, the world's lightmaps and its other parts */
  assert(rasterizer_debug_options.draw_water&&rasterizer_debug_options.draw_detail_objects&&
   rasterizer_debug_options.fog_atmospheric_enabled&&rasterizer_debug_options.fog_planar_enabled&&rasterizer_debug_options.draw_environment==2);
  for(boolean *p=&rasterizer_debug_options.draw_environment_lightmaps;p<=&rasterizer_debug_options.draw_environment_fog_screen;p++)
   assert(*p||!cheats_network_client_switch_enforced(p));
 }
 /* the Quest 2 client keeps its speed: no shadows, reflections or lens flares */
 system_name="Oculus Quest 2"; user_value="auto"; fights(0,0,10);
 assert(!rasterizer_debug_options.draw_environment_shadows&&!rasterizer_debug_options.draw_environment_reflections&&!rasterizer_debug_options.draw_lens_flares);
 /* alone (not a client), the first Quest's preset leaves grass and screen fog off as before */
 system_name="Oculus Quest"; client=0; fights(0,0,10);
 assert(!rasterizer_debug_options.draw_detail_objects&&!rasterizer_debug_options.draw_environment_fog_screen);
 printf("PASS: a Quest 2 client's preset and its host's rules fought %d of 98 frames in 1.0.7 (a warning each); now none on any headset,"
        " setting or order; water, grass, fog and the world's parts drawn for everyone, shadows, reflections and lens flares the"
        " client's own; warned once a game\n", before);
}
''')

# --- 7. the first Quest: a kernel before 4.17 takes MAP_FIXED_NOREPLACE as a hint
memory_before = git_show('port/android/host/host_memory.c')
old_reserve = fn(memory_before, 'reserve').replace('static int reserve(', 'static int old_reserve(', 1)
assert 'host_memory_failure = ' in host_memory and 'host_memory_failure' in host_main
assert 'could not start on this device' in host_main
run('memory', r'''
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/types.h>
/* an address space, simulated (the build machine's own kernel may be either
kind, or know the flag not at all): a kernel from 4.17 refuses a range in use
with EEXIST; one before takes the address as a hint and maps elsewhere */
static int old_kernel, reclaims, reclaim_fails;
static struct { uint64_t address, size; int used; } ranges[16];
static uint64_t elsewhere = 0x7f0000000000ull;
static int range_count(void){ int n=0; for(int i=0;i<16;i++) n+=ranges[i].used; return n; }
static int in_use(uint64_t a, uint64_t s){ for(int i=0;i<16;i++) if(ranges[i].used&&a<ranges[i].address+ranges[i].size&&ranges[i].address<a+s) return 1; return 0; }
static void *add(uint64_t a, uint64_t s){ for(int i=0;i<16;i++) if(!ranges[i].used){ ranges[i].address=a; ranges[i].size=s; ranges[i].used=1; return (void*)(uintptr_t)a; } assert(0); return MAP_FAILED; }
static void *kernel_mmap(void *where, size_t s, int p, int f, int fd, off_t o){
 uint64_t a=(uint64_t)(uintptr_t)where;
 assert((f&MAP_PRIVATE)&&(f&MAP_ANONYMOUS)&&!(f&MAP_FIXED)&&fd==-1);
 if((f&MAP_FIXED_NOREPLACE)&&!old_kernel){ if(in_use(a,s)){ errno=EEXIST; return MAP_FAILED; } return add(a,s); }
 if(a&&!in_use(a,s)) return add(a,s);
 a=elsewhere; elsewhere+=s+0x100000; return add(a,s); }
static int kernel_munmap(void *where, size_t s){ for(int i=0;i<16;i++) if(ranges[i].used&&ranges[i].address==(uint64_t)(uintptr_t)where){ assert(ranges[i].size==s); ranges[i].used=0; return 0; } assert(0); return -1; }
/* ART's idle large object space in the way, given back (non-zero: something was) */
static int art_slot=-1;
static int reclaim_art_overlap(uint64_t address, uint64_t size){ reclaims++; if(reclaim_fails||art_slot<0) return 0;
 ranges[art_slot].used=0; art_slot=-1; return 1; }
#define mmap kernel_mmap
#define munmap kernel_munmap
''' + fn(host_memory, 'map_fixed_noreplace') + fn(host_memory, 'reserve') + old_reserve + r'''
static void occupy(uint64_t a, uint64_t s){ add(a,s); for(int i=0;i<16;i++) if(ranges[i].used&&ranges[i].address==a) art_slot=i; }
static void clear(void){ memset(ranges,0,sizeof(ranges)); art_slot=-1; }
int main(void){
 const uint64_t address=0x80000000ull, size=0x20000000ull;
 for(old_kernel=0;old_kernel<2;old_kernel++){
  /* free: reserved where asked */
  clear(); assert(reserve(address,size,1)==0&&range_count()==1&&in_use(address,size));
  /* in use by ART's idle space: given back and reserved */
  clear(); occupy(address+0x1000000,0x200000);
  reclaims=0; errno=ENOENT; assert(reserve(address,size,1)==0&&reclaims==1&&range_count()==1&&art_slot<0);
  /* in use by something else: refused, and said so (EEXIST, not a stale error), nothing left mapped elsewhere */
  clear(); occupy(address+0x1000000,0x200000);
  reclaims=0; reclaim_fails=1; errno=ENOENT; assert(reserve(address,size,1)==-1&&errno==EEXIST&&reclaims==1&&range_count()==1);
  errno=ENOENT; assert(reserve(address,size,0)==-1&&errno==EEXIST&&range_count()==1); reclaim_fails=0;
  /* 1.0.7: on the old kernel, refused with the stale error and ART's space never given back (the first Quest's
  log: "No such file or directory"); on a newer one, as now */
  clear(); occupy(address+0x1000000,0x200000); reclaims=0; errno=ENOENT;
  if(old_kernel) assert(old_reserve(address,size,1)==-1&&errno==ENOENT&&reclaims==0&&range_count()==1);
  else assert(old_reserve(address,size,1)==0&&reclaims==1);
 }
 puts("PASS: the first Quest's kernel (MAP_FIXED_NOREPLACE a hint) and newer ones reserve a free range, take back ART's idle"
      " space in the way and refuse others with EEXIST; 1.0.7 refused there with a stale \"No such file or directory\"");
}
''')

# --- 8. buttons: the reticle toggle on the left stick's click; crouch on the turning stick held down
enums = re.search(r'enum\n\{\n\tVR_BUTTON_ACTION_JUMP,.*?VR_BUTTON_SOURCES\n\};\n', vr_h, re.S).group(0)
assert enums.index('VR_BUTTON_ACTION_RETICLE') > enums.index('VR_BUTTON_ACTION_SWITCH_GRENADE'), 'appended'
names = ''.join(between(frame, 'static const %s' % t, '};') for t in
                ['char *const button_action_keys', 'char *const button_source_values', 'int button_defaults']) + \
    ''.join(fn(frame, f) for f in ['vr_button_action_key', 'vr_button_default', 'vr_button_source_value', 'vr_button_source_of'])
init = frame[frame.index('migrate_gun_aim_reset();\n\tmigrate_reticle_button();'):]
assert init.index('migrate_reticle_button();') < init.index('vr_reload_settings();'), 'before settings load'
run('reticle_migration', r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
''' + enums + names + r'''
static char values[VR_BUTTON_ACTIONS][32]; static int applied, fail, writes;
static int key_index(const char *k){for(int a=0;a<VR_BUTTON_ACTIONS;a++) if(!strcmp(k,vr_button_action_key(a))) return a; assert(0); return 0;}
static const char *config_string(const char *k){return values[key_index(k)];}
static boolean config_boolean(const char *k){assert(!strcmp(k,"vr.controls_reticle_applied")); return applied;}
static boolean config_write_string(const char *k, const char *v){if(fail) return FALSE; writes++; strcpy(values[key_index(k)],v); return TRUE;}
static boolean config_write_boolean(const char *k, boolean v){assert(!strcmp(k,"vr.controls_reticle_applied")); if(fail) return FALSE; applied=v; return TRUE;}
static void platform_log(const char *f, ...){(void)f;}
''' + fn(frame, 'migrate_reticle_button') + r'''
static void defaults(void){for(int a=0;a<VR_BUTTON_ACTIONS;a++) strcpy(values[a],vr_button_source_value(vr_button_default(a))); applied=0; fail=0; writes=0;}
#define IS(a,v) (!strcmp(values[a],v))
int main(void){
 /* an old config.toml: crouch written as the left stick (the reticle's key absent: its default) */
 defaults(); strcpy(values[VR_BUTTON_ACTION_CROUCH],"left_stick");
 migrate_reticle_button(); assert(IS(VR_BUTTON_ACTION_CROUCH,"right_stick_down")&&IS(VR_BUTTON_ACTION_RETICLE,"left_stick")&&applied);
 /* once: a crouch put back on the left stick later is the player's choice (the reticle left as set) */
 strcpy(values[VR_BUTTON_ACTION_CROUCH],"left_stick"); writes=0; migrate_reticle_button(); assert(IS(VR_BUTTON_ACTION_CROUCH,"left_stick")&&writes==0);
 /* crouch moved by the player elsewhere: kept; another action on the left stick: the reticle has no button */
 defaults(); strcpy(values[VR_BUTTON_ACTION_CROUCH],"x"); strcpy(values[VR_BUTTON_ACTION_GRENADE],"left_stick");
 migrate_reticle_button(); assert(IS(VR_BUTTON_ACTION_CROUCH,"x")&&IS(VR_BUTTON_ACTION_RETICLE,"none")&&IS(VR_BUTTON_ACTION_GRENADE,"left_stick")&&applied);
 /* the turning stick held down already taken: crouch is left with no button (ducking still crouches) */
 defaults(); strcpy(values[VR_BUTTON_ACTION_CROUCH],"left_stick"); strcpy(values[VR_BUTTON_ACTION_JUMP],"right_stick_down");
 migrate_reticle_button(); assert(IS(VR_BUTTON_ACTION_CROUCH,"none")&&IS(VR_BUTTON_ACTION_RETICLE,"left_stick"));
 /* a new install: nothing to move */
 defaults(); migrate_reticle_button(); assert(IS(VR_BUTTON_ACTION_CROUCH,"right_stick_down")&&IS(VR_BUTTON_ACTION_RETICLE,"left_stick")&&applied);
 /* a save that fails is tried again next start */
 defaults(); strcpy(values[VR_BUTTON_ACTION_CROUCH],"left_stick"); fail=1; migrate_reticle_button(); assert(!applied);
 fail=0; migrate_reticle_button(); assert(applied&&IS(VR_BUTTON_ACTION_CROUCH,"right_stick_down"));
 /* never two actions on one button afterwards */
 for(int a=0;a<VR_BUTTON_ACTIONS;a++) for(int b=a+1;b<VR_BUTTON_ACTIONS;b++)
  assert(strcmp(values[a],values[b])||IS(a,"none")||IS(a,"hold"));
 puts("PASS: crouch moves once from the left stick's click to the turning stick held down, the click becomes the reticle"
      " toggle; players' own choices kept, a taken button left free, a failed save retried; no button does two things");
}
''')
for key, kind, default in [('vr.button_reticle', '_config_string', r'"\"left_stick\""'),
                           ('vr.button_crouch', '_config_string', r'"\"right_stick_down\""'),
                           ('vr.hud_tap_distance', '_config_real', '"0.1"'), ('vr.wrist_hud', '_config_boolean', '"false"'),
                           ('vr.flashlight_distance', '_config_real', '"0.2"'),
                           ('vr.controls_reticle_applied', '_config_boolean', '"false"')]:
    assert ('{ "%s", %s, %s,' % (key, kind, default)) in config, key

# --- 8b. Controls -> L STICK CLICK: RETICLE (default) or CROUCH, the layout before 1.0.8
assert '{ "L STICK CLICK", "buttons", _vr_setting_crouch_click, 2, { { "RETICLE", "reticle" }, { "CROUCH", "crouch" } } },' in \
    between(menu, 'static struct vr_menu_setting const vr_menu_controls[] =', '};')
change = fn(menu, 'vr_menu_setting_change')
click_change = between(change, '\tcase _vr_setting_crouch_click:\n', '\t\tbreak;\n\t}\n\tvr_reload_settings();', include_end=False)
click_change = click_change[click_change.index('\n') + 1:]
click_index = between(fn(menu, 'vr_menu_value_index'), '\t\tcase _vr_setting_crouch_click:\n', '\t\t\tbreak;', include_end=False)
click_index = click_index[click_index.index('\n') + 1:]
run('crouch_click', r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define NONE (-1)
typedef int boolean;
#define TRUE 1
#define FALSE 0
''' + enums + names + r'''
static char values[VR_BUTTON_ACTIONS][32];
static int key_index(const char *k){for(int a=0;a<VR_BUTTON_ACTIONS;a++) if(!strcmp(k,vr_button_action_key(a))) return a; assert(0); return 0;}
static const char *config_string(const char *k){return values[key_index(k)];}
static boolean config_write_string(const char *k, const char *v){strcpy(values[key_index(k)],v); return TRUE;}
static void platform_log(const char *f, ...){(void)f;}
''' + fn(menu, 'vr_menu_button_source') + fn(menu, 'vr_menu_button_set') + r'''
/* the row's value shown: 0 RETICLE, 1 CROUCH, NONE (CUSTOM) */
static int shown(void){ const char *choices[2]={"reticle","crouch"};
 for(int index=0;index<2;index++){ const char *value=choices[index];
''' + click_index + r'''
 } return NONE; }
static void choose(const char *value){ boolean written;
''' + click_change + r'''
 (void)written; }
static void defaults(void){for(int a=0;a<VR_BUTTON_ACTIONS;a++) strcpy(values[a],vr_button_source_value(vr_button_default(a)));}
static void unique(void){for(int a=0;a<VR_BUTTON_ACTIONS;a++) for(int b=a+1;b<VR_BUTTON_ACTIONS;b++){
 int s=vr_menu_button_source(a); if(s!=VR_BUTTON_SOURCE_NONE&&s!=VR_BUTTON_SOURCE_HOLD) assert(vr_menu_button_source(b)!=s);}}
#define IS(a,v) (!strcmp(values[a],v))
int main(void){
 /* the default shows RETICLE */
 defaults(); assert(shown()==0);
 /* CROUCH: 1.0.7's buttons exactly (the left stick's click crouches, the turning stick held down does nothing),
 the reticle's toggle on no button */
 choose("crouch"); assert(shown()==1); unique();
 assert(IS(VR_BUTTON_ACTION_JUMP,"a")&&IS(VR_BUTTON_ACTION_ACTION,"b")&&IS(VR_BUTTON_ACTION_MELEE,"right_stick")&&
  IS(VR_BUTTON_ACTION_CROUCH,"left_stick")&&IS(VR_BUTTON_ACTION_SWITCH_WEAPON,"y")&&IS(VR_BUTTON_ACTION_GRENADE,"x")&&
  IS(VR_BUTTON_ACTION_SWITCH_GRENADE,"hold")&&IS(VR_BUTTON_ACTION_RETICLE,"none"));
 for(int a=0;a<VR_BUTTON_ACTIONS;a++) assert(vr_menu_button_source(a)!=VR_BUTTON_SOURCE_RIGHT_STICK_DOWN);
 /* RETICLE again: the 1.0.8 defaults */
 choose("reticle"); assert(shown()==0); for(int a=0;a<VR_BUTTON_ACTIONS;a++) assert(vr_menu_button_source(a)==vr_button_default(a));
 /* after any BUTTONS changes, either choice leaves no button with two actions and shows itself */
 srand(26);
 for(int i=0;i<20000;i++){ int a=rand()%VR_BUTTON_ACTIONS, s=rand()%VR_BUTTON_SOURCES;
  if(s==VR_BUTTON_SOURCE_HOLD && a!=VR_BUTTON_ACTION_SWITCH_GRENADE) s=VR_BUTTON_SOURCE_NONE;
  vr_menu_button_set(a,s); unique();
  if(i%7==0){ int crouch=rand()&1; choose(crouch?"crouch":"reticle"); unique(); assert(shown()==crouch); } }
 puts("PASS: Controls -> L STICK CLICK: RETICLE (default) or CROUCH, which restores 1.0.7's buttons exactly (the reticle toggle"
      " left without a button); back to RETICLE restores 1.0.8's; after 20,000 random button changes no button does two things");
}
''')

# --- 9. the HUD head tap (the weapon hand to its own temple), the HUD hidden but menus, prompts and the reticle kept
tap = between(frame, '\t/* test26: the HUD tap:', '\n\t/* crouching:', include_end=False)
assert 'vr.hud_tap_distance = ' in fn(frame, 'vr_reload_settings') and 'vr.hud_tap_armed = 1;' in frame
assert 'return vr.active && vr.hud_hidden;' in fn(frame, 'vr_hud_hidden'), 'only in VR'
assert '!vr.reticle_hidden' in fn(frame, 'vr_crosshair_enabled')
for marker in ['if (!VR_HUD_HIDDEN())']:
    assert marker in hud, 'unit interface, nav points and damage indicators'
assert hud_weapon.count('!VR_HUD_HIDDEN()') >= 2, 'weapon and grenade panels; the crosshair kept'
if 'HUD_TAP_HOLD_SECONDS' in frame:
    print('PASS: (test29: the HUD tap is held, not passed through: test_test29 runs it)')
else:
    run('hud_tap', r'''
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include "port/android/include/halo_android_abi.h"
static struct { float hud_tap_distance; struct halo_xr_frame frame; int hud_hidden, hud_tap_armed; } vr;
static int buzzes;
static void vr_haptic(int h, float a, float s){ (void)h; (void)a; (void)s; buzzes++; }
static void platform_log(const char *f, ...){ (void)f; }
''' + fn(frame, 'rotate').replace('static void rotate(', 'static void rotate(', 1) + fn(frame, 'distance3') + r'''
static void hud_tap(int w)
{
''' + tap + r'''
}
static void at(int w, float x, float y, float z){ vr.frame.grip[w].position[0]=x; vr.frame.grip[w].position[1]=y; vr.frame.grip[w].position[2]=z; hud_tap(w); }
int main(void){
 vr.hud_tap_distance=0.1f; vr.hud_tap_armed=1; vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3;
 vr.frame.head.position[1]=1.6f; vr.frame.head.orientation[3]=1;
 /* the right hand to the right temple: hidden, once; held there nothing more */
 at(1,0.1f,1.6f,0.04f); assert(vr.hud_hidden==1&&buzzes==1); at(1,0.09f,1.62f,0.05f); assert(vr.hud_hidden==1&&buzzes==1);
 /* drawn back a little: not again until well away (5 cm past the reach) */
 at(1,0.2f,1.6f,0.04f); at(1,0.1f,1.6f,0.04f); assert(vr.hud_hidden==1);
 at(1,0.3f,1.6f,0.04f); at(1,0.1f,1.6f,0.04f); assert(vr.hud_hidden==0&&buzzes==2); at(1,0.4f,1.6f,0.04f);
 /* not: the right hand at the left temple, a gun at the cheek, the right shoulder's holster, a gun held up to aim */
 at(1,-0.1f,1.6f,0.04f); at(1,0.05f,1.45f,-0.2f); at(1,0.2f,1.35f,0.05f); at(1,0.1f,1.5f,-0.35f); assert(vr.hud_hidden==0&&buzzes==2);
 /* the head turned 90 degrees left: its temple turned with it */
 { float s=sqrtf(0.5f); vr.frame.head.orientation[1]=s; vr.frame.head.orientation[3]=s;
   float side[3]={0.08f,0,0.04f}, temple[3]; rotate(vr.frame.head.orientation,side,temple);
   at(1,0.1f,1.6f,0.04f); assert(vr.hud_hidden==0);
   at(1,temple[0],1.6f+temple[1],temple[2]); assert(vr.hud_hidden==1); at(1,1,1,1);
   vr.frame.head.orientation[1]=0; vr.frame.head.orientation[3]=1; }
 /* the left hand (left-handed) to the left temple */
 at(0,-0.1f,1.6f,0.04f); assert(vr.hud_hidden==0); at(0,1,1,1);
 /* off (0) or the hand untracked: never */
 vr.hud_tap_distance=0; at(1,0.08f,1.6f,0.04f); assert(vr.hud_hidden==0);
 vr.hud_tap_distance=0.1f; vr.frame.hand_valid[1]=0; at(1,0.08f,1.6f,0.04f); assert(vr.hud_hidden==0);
 puts("PASS: the weapon hand brought to its own temple shows or hides the HUD once a tap (re-armed 5 cm past the reach),"
      " following the head's turn; the other temple, a gun at the cheek or held up, the shoulder holster, off or untracked: nothing");
}
''')

# --- 10. the wrist HUD: on the back of the off hand's wrist, read as a watch is
assert re.search(r'#define HALO_XR_SWAPCHAIN_WRIST 6\b', abi) and re.search(r'#define HALO_XR_SWAPCHAIN_COUNT 7\b', abi)
assert re.search(r'#define HALO_XR_LAYER_WRIST 0x200u', abi)
assert 'HALO_XR_LAYER_WRIST' in host_xr and 'HALO_XR_SWAPCHAIN_WRIST' in host_xr
assert 'if (wrist_hud_active() && place_wrist(&layers) && copy_wrist(texture))' in frame
assert ('return vr.wrist_hud && !vr.menus_active && !vr.hud_hidden && !vr.seated &&\n'
        '\t\t(vr.frame.hand_valid[1 - vr.weapon_hand] & 1);') in fn(frame, 'wrist_hud_active'), \
    'seated or the off hand untracked: the HUD ahead whole'
run('wrist', r'''
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "port/android/include/halo_android_abi.h"
static struct { int weapon_hand, two_hand_held, seated; struct halo_xr_frame frame; struct halo_xr_info info;
 float wrist_along, wrist_across, wrist_out, wrist_size; } vr;
''' + ''.join(re.findall(r'#define WRIST_HUD_\w+ [^\n]+\n', frame)) + fn(frame, 'rotate') + fn(frame, 'look_rotation') + fn(frame, 'place_wrist') + r'''
static float dot(const float a[3], const float b[3]){ return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }
static void normalise(float v[3]){ float l=sqrtf(dot(v,v)); for(int i=0;i<3;i++) v[i]/=l; }
static void cross(const float a[3], const float b[3], float o[3]){ o[0]=a[1]*b[2]-a[2]*b[1]; o[1]=a[2]*b[0]-a[0]*b[2]; o[2]=a[0]*b[1]-a[1]*b[0]; }
/* an OpenXR grip from its axes: z (toward the wrist; -z the controller's forward) and x */
static void grip(int hand, const float z[3], const float x[3], const float at[3]){
 float y[3], forward[3]={-z[0],-z[1],-z[2]}; cross(z,x,y);
 look_rotation(forward,y,vr.frame.grip[hand].orientation); memcpy(vr.frame.grip[hand].position,at,sizeof(float)*3); }
int main(void){
 vr.info.width[HALO_XR_SWAPCHAIN_WRIST]=512; vr.info.height[HALO_XR_SWAPCHAIN_WRIST]=384; vr.wrist_size=1;
 vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=3;
 const float hand_at[3]={0,-0.3f,-0.35f}, east[3]={1,0,0}, west[3]={-1,0,0}, right_view[3]={1,0,0};
 float to_eyes[3]={0,0.3f,0.35f}; normalise(to_eyes);
 float away[3]={-to_eyes[0],-to_eyes[1],-to_eyes[2]};
 for(int o=0;o<2;o++){
  struct halo_xr_layers layers; memset(&layers,0,sizeof(layers));
  vr.weapon_hand=1-o; vr.two_hand_held=vr.seated=0;
  /* the watch pose: the forearm across the body, the hand pointing to the other side, its back to the eyes
  (the back of a left hand is the grip's -x, of a right one +x: OpenXR's grip) */
  grip(o, o==0?west:east, o==0?away:to_eyes, hand_at);
  assert(place_wrist(&layers));
  float normal[3], x[3], y[3]; const float qz[3]={0,0,1}, qx[3]={1,0,0}, qy[3]={0,1,0};
  rotate(layers.wrist_pose.orientation,qz,normal); rotate(layers.wrist_pose.orientation,qx,x); rotate(layers.wrist_pose.orientation,qy,y);
  assert(dot(normal,to_eyes)>0.99f);                 /* facing the eyes */
  assert(dot(x,right_view)>0.99f);                   /* read left to right */
  assert(y[1]>0.7f&&y[2]<-0.6f);                     /* its top up and away: upright */
  float d[3]; for(int i=0;i<3;i++) d[i]=layers.wrist_pose.position[i]-hand_at[i];
  assert(sqrtf(dot(d,d))<0.12f&&dot(d,to_eyes)>0.03f); /* at the wrist, out of the back of the hand (test29: 10 cm back) */
  assert(fabsf(layers.wrist_size[0]-0.11f)<1e-6f&&fabsf(layers.wrist_size[1]-0.0825f)<1e-6f);
  /* the palm to the eyes: not shown; the hand holding the gun, seated or untracked: not shown */
  grip(o, o==0?west:east, o==0?to_eyes:away, hand_at); assert(!place_wrist(&layers));
  grip(o, o==0?west:east, o==0?away:to_eyes, hand_at);
  vr.two_hand_held=1; assert(!place_wrist(&layers)); vr.two_hand_held=0;
  vr.seated=1; assert(!place_wrist(&layers)); vr.seated=0;
  vr.frame.hand_valid[o]=0; assert(!place_wrist(&layers)); vr.frame.hand_valid[o]=3;
 }
 puts("PASS: the wrist HUD sits on the back of the off hand's wrist (either hand), facing the eyes upright and read left"
      " to right in the watch pose, 11 x 8 cm; hidden with the palm turned up, two hands on the gun, seated or untracked");
}
''')

# --- 11. menus grouped: HUD + RETICLE and HEAD GESTURES after GAMEPLAY (test25 checks every row's width)
pages = between(menu, '} const vr_menu_pages[] =', '};')
assert pages.index('"GAMEPLAY", vr_menu_vr') < pages.index('"HUD + RETICLE", vr_menu_hud') < \
    pages.index('"HEAD GESTURES", vr_menu_gestures')
hud_page = between(menu, 'static struct vr_menu_setting const vr_menu_hud[] =', '};')
gestures = between(menu, 'static struct vr_menu_setting const vr_menu_gestures[] =', '};')
for key in ['vr.crosshair"', 'vr.crosshair_size', 'vr.crosshair_opacity', 'vr.wrist_hud']:
    assert key in hud_page, key
assert '"FLASHLIGHT", "vr.flashlight_distance"' in gestures and '{ "20 CM", "0.2" }' in gestures and '{ "OFF", "0" }' in gestures
assert '"HUD TAP", "vr.hud_tap_distance"' in gestures and '{ "10 CM", "0.1" }' in gestures
gameplay = between(menu, 'static struct vr_menu_setting const vr_menu_vr[] =', '};')
assert 'vr.crosshair' not in gameplay and 'vr.flashlight_distance' not in gameplay, 'each setting on one page'
assert '{ "RETICLE", "vr.button_reticle", _vr_setting_button, 9,' in menu and '{ "R DOWN", "right_stick_down" }' in menu
print('PASS: settings grouped (HUD + RETICLE: crosshair, size, opacity, wrist HUD; HEAD GESTURES: flashlight and HUD tap'
      ' reach or off; BUTTONS: reticle, R DOWN for the turning stick held down); defaults shown as choices')

# --- 12. melee along the gun with a follow-through; a blow landing inside what it struck counts
melee = fn(render, 'vr_render_impact_melee')
assert re.search(r'#define VR_MELEE_POINTS 3\b', render)
assert 'along[1] = short_gun ? 0.12f : 0.2f;' in melee and 'along[2] = short_gun ? 0.0f : 0.4f;' in melee
assert 'reach = (reach > 0.15f ? 0.15f : reach) * units;' in melee and 'real reach = speed * 0.05f;' in melee
assert '(armed && index ? 0.05f : 0.035f) * units' in melee
impact = fn(units, 'unit_vr_impact_melee')
assert ('if (obstruction.type == _collision_result_object && obstruction.t >= 0.0f && obstruction.t <= 1.0f &&\n'
        '\t\t\t\t!hit)') in impact, 'an object (never a wall) between the eye and the hand is what it struck'
print('PASS: melee sweeps the grip, middle and (long guns) far end, carried on up to 15 cm by the swing\'s speed;'
      ' a hand a fast swing carried inside a character strikes it, a wall still stops the blow')

# --- 13. adopted upstream (OpenCE build 128): the engine's speed-ups, glass, a client never reverting
assert 'cluster_partitions_port_forget' in game_state and 'cluster_partitions_port_forget' in read('source/structures/cluster_partitions.c', 'latin-1')
# (test27: upstream's own form since build 129: the co-op host reverts for everyone, a local game alone)
assert 'else if (game_connection() != _game_connection_network_client)\n\t{\n\t\tgame_state_revert();' in fn(main_c, 'main_revert_map_private')
assert 'else if (skippable && game_connection() == _game_connection_local)' in fn(main_c, 'main_skip_cinematic_private')
may_discard = fn(bipeds, 'biped_port_may_discard')
assert 'network_objects_may_delete(biped_index)' in may_discard and 'noted_biped_index != biped_index' in may_discard
assert bipeds.count('biped_port_may_discard(biped_index)') == 2, 'fallen out of the world, and discarded far below'
print('PASS: OpenCE build 128 adopted where it fits (engine speed-ups, glass, a client never reverting or skipping alone);'
      ' a client\'s fallen copy of the host\'s biped said once, the host\'s to erase')

# --- 14. version, identity and package markers
code = int(re.search(r'versionCode Math\.max\((\d+), buildNumber\)', gradle).group(1))
assert code >= 34 and int(re.search(r': "1\.0\.(\d+)(?:-test\d+[a-z]?)?"', gradle).group(1)) >= 8
identity_match = re.search(
    r'platform_log\("vr: (HaloCE Quest (?:test\d+[a-z]? candidate|\d+\.\d+\.\d+ release)[^"]*)"\);', frame)
assert identity_match, 'VR identity uses either a candidate or stable-release label'
identity = identity_match.group(1)
# The identity banner now explicitly names the candidate's upstream network.
# Keep the history assertion and ensure it identifies Build157/network24.
assert 'test26 candidate 1.0.8' in frame or 'test26:' in frame
assert 'OpenCE Build 157 / network 24' in identity
assert 'candidate_at_least(args.label, 26)' in package
print('PASS: test26 wiring (version 1.0.8 / 34 or later, identity line, package markers)')
