"""Exercise vehicle glass from the production queued owner to its VR consumer.

The previous helper-only fixture passed an object directly and therefore hid
the wrong renderer field. This test executes the real queue assignments,
consumer call, view/config predicates and profile matching. Object storage and
GPU submission are fixtures; this does not establish headset appearance.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test31-vehicle-glass'
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return (ROOT / path).read_text()


def function(text, name):
    match = re.search(r'^(?:static )?[\w *]+\b' + name + r'\s*\([^;{]*\)\s*\{', text, re.M)
    assert match, name
    end, depth = match.end(), 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end] + '\n'


render = read('port/linux/game/vr_render.c')
models = read('source/rasterizer/xbox/rasterizer_xbox_models.c')
transparent = read('source/rasterizer/xbox/rasterizer_xbox_transparent_geometry.c')
model_definition = read('source/models/models.c')
render_objects = read('source/render/render_objects.c')
consumer = re.search(r'vr_render_seat_transparent\(group->\w+,\s*group->shader->base.type,\s*_shader_type_transparent_glass\)', transparent).group()
# The hook runs for pass zero too: the `pass > 0` break branch is closed
# before HALO_VR, and the cull precedes the complete glass shader switch.
loop_start = transparent.index('for (pass = 0;')
switch_start = transparent.index('switch (group->shader->base.type)', loop_start)
prefix = transparent[loop_start:switch_start]
assert re.search(r'else if \(pass > 0\)\s*\{\s*break;\s*\}\s*#ifdef HALO_VR', prefix)
assert prefix.count('vr_render_seat_transparent(') == 1
assert re.search(r'vr_render_seat_transparent\([^;]+\)\s*continue;\s*#endif\s*$', prefix)
start = models.index('group->object_index = local_parameters->unique_identifier;')
queue = models[start:models.index('group->shader_permutation_index =', start)]
model_owner = re.search(r'model_parameters.unique_identifier = unique_identifier;', model_definition).group()
# The object renderer passes the object handle as render_model's unique ID.
assert re.search(r'&model_effect,\s*object_index,\s*object->object.forced_shader_permutation_index', render_objects)
assert 'long unique_identifier,' in function(model_definition, 'render_model')
hook = transparent.index(consumer)
assert transparent.rindex('#ifdef HALO_VR', 0, hook) > transparent.rindex('else if (pass > 0)', 0, hook)
assert hook < transparent.index('switch (group->shader->base.type)', hook)
assert transparent[hook:hook+len(consumer)+40].count('continue;') == 1
shader_enum_start = transparent.index('enum\n{\n\t_shader_type_screen')
shader_enum = transparent[shader_enum_start:transparent.index('\n};', shader_enum_start)+3]
source = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1L)
#define NUMBEROF(a) (sizeof(a)/sizeof(*(a)))
#define match_assert(file,line,condition) assert(condition)
typedef struct {float x,y,z;} real_point3d;
struct object_datum {long definition_index;struct {long parent_object_index;} object;};
struct unit_datum {long definition_index;struct {long parent_object_index;} object;struct {short parent_seat_index;} unit;};
static struct {int valid;} pool={1},*object_header_data=&pool;
static struct {struct {int seated;long unit_index,vehicle_index;short seat_index;} seat;} vr_render;
static struct unit_datum player,vehicle;
static struct object_datum attachment,other;
static const long player_id=0x12340001L,vehicle_id=0x12340007L,attached_id=0x12340009L,other_id=0x12340003L;
static const char *view="first_person",*vehicle_name="vehicles\\warthog\\warthog";
static int generation,hide_glass=1,active=1,logs,object_reads,unit_reads,resets;
static int vr_settings_generation(void){return generation;}
static const char *config_string(const char *key){assert(!strcmp(key,"vr.vehicle_view"));return view;}
static int config_boolean(const char *key){assert(!strcmp(key,"vr.vehicle_warthog_hide_glass"));return hide_glass;}
static int vr_active(void){return active;}
static void platform_log(const char *fmt,...){(void)fmt;logs++;}
static void vr_render_reset_vehicle_view(void){vr_render.seat.seated=0;vr_render.seat.vehicle_index=NONE;resets++;}
static struct unit_datum *unit_try_and_get(long id){
 assert(object_header_data&&object_header_data->valid);unit_reads++;
 return id==player_id?&player:id==vehicle_id?&vehicle:NULL;
}
static struct object_datum *object_try_and_get(long id){
 assert(object_header_data&&object_header_data->valid);object_reads++;
 return id==vehicle_id?(struct object_datum*)&vehicle:id==player_id?(struct object_datum*)&player:
  id==attached_id?&attachment:id==other_id?&other:NULL;
}
static struct object_datum *object_get(long id){struct object_datum *p=object_try_and_get(id);assert(p);return p;}
static long object_get_ultimate_parent(long id){
 struct object_datum *p;long result=NONE;
 while(id!=NONE){result=id;p=object_get(id);id=p->object.parent_object_index;}
 return result;
}
static char *tag_get_name(long id){assert(id==101);return (char*)vehicle_name;}
static struct shader {struct {short type;} base;} glass_shader;
enum {_render_model_effect_type_none,_render_model_effect_type_modifier,_render_model_effect_type_active_camouflage};
struct effect {short type;long source_object_index;real_point3d source_object_centroid;};
struct model_parameters {long unique_identifier;struct effect effect;};
struct transparent_geometry_group {long object_index,source_object_index;real_point3d centroid;struct shader *shader;};
'''+shader_enum+'\n'+''.join(function(render,n) for n in (
    'vr_vehicle_profile','vr_first_person_vehicles','vr_seat_view','vr_render_seat_transparent'))+r'''
static void queue_group(struct transparent_geometry_group *group,long unique_identifier,short effect,long effect_owner,short shader_type){
 struct model_parameters model_parameters={0};const struct model_parameters *local_parameters=&model_parameters;
 real_point3d point={0};const real_point3d *centroid=&point;struct shader *shader=&glass_shader;
 OWNER
 model_parameters.effect.type=effect;model_parameters.effect.source_object_index=effect_owner;
 shader->base.type=shader_type;
 QUEUE
}
static int cull_checks;
static int culled(const struct transparent_geometry_group *group){cull_checks++;return CONSUMER;}
static void seated(short seat){
 object_header_data=&pool;pool.valid=1;view="first_person";generation++;active=1;
 player.definition_index=100;player.object.parent_object_index=vehicle_id;player.unit.parent_seat_index=seat;
 vehicle.definition_index=101;vehicle.object.parent_object_index=NONE;
 attachment.object.parent_object_index=vehicle_id;other.object.parent_object_index=NONE;
 vr_render.seat.seated=1;vr_render.seat.vehicle_index=vehicle_id;vr_render.seat.unit_index=player_id;vr_render.seat.seat_index=seat;
}
int main(void){
 struct transparent_geometry_group group={0};assert(_shader_type_transparent_glass==8);
 for(short seat=0;seat<3;seat++){
  seated(seat);vehicle_name="vehicles\\warthog\\warthog";hide_glass=1;generation++;
  queue_group(&group,vehicle_id,_render_model_effect_type_none,0,_shader_type_transparent_glass);
  assert(group.object_index==vehicle_id&&group.source_object_index==0);
  assert(culled(&group)); /* This fails with the previously shipped callsite. */
  int before=logs;assert(culled(&group)&&logs==before);
  hide_glass=0;generation++;assert(!culled(&group));
  hide_glass=1;generation++;assert(culled(&group));
  view="chase";generation++;assert(!culled(&group));
  view="first_person";generation++;assert(culled(&group));
  active=0;assert(!culled(&group));active=1;
  queue_group(&group,attached_id,_render_model_effect_type_none,0,_shader_type_transparent_glass);assert(culled(&group));
  queue_group(&group,other_id,_render_model_effect_type_modifier,vehicle_id,_shader_type_transparent_glass);assert(!culled(&group));
  queue_group(&group,vehicle_id,_render_model_effect_type_modifier,other_id,_shader_type_transparent_glass);assert(culled(&group));
  queue_group(&group,NONE,_render_model_effect_type_none,0,_shader_type_transparent_glass);assert(!culled(&group));
  queue_group(&group,0,_render_model_effect_type_none,0,_shader_type_transparent_glass);assert(!culled(&group));
  queue_group(&group,vehicle_id,_render_model_effect_type_none,0,_shader_type_transparent_chicago);assert(!culled(&group));
  queue_group(&group,vehicle_id,_render_model_effect_type_none,0,_shader_type_transparent_meter);assert(!culled(&group));
  queue_group(&group,vehicle_id,_render_model_effect_type_none,0,_shader_type_model);assert(!culled(&group));
  queue_group(&group,vehicle_id,_render_model_effect_type_none,0,_shader_type_transparent_glass);
  vehicle_name="vehicles\\warthog\\mp_warthog";hide_glass=0;generation++;assert(!culled(&group));
  vehicle_name="vehicles\\rwarthog\\rwarthog";assert(!culled(&group));
  vehicle_name="vehicles\\ghost\\ghost";assert(culled(&group)); /* prior other-vehicle policy */
  vr_render.seat.seated=0;assert(!culled(&group));
 }
 /* Teardown and deleted/stale seat state fail before strict object reads. */
 queue_group(&group,vehicle_id,_render_model_effect_type_none,0,_shader_type_transparent_glass);
 seated(0);object_header_data=NULL;int before=object_reads,unit_before=unit_reads;
 assert(!culled(&group)&&object_reads==before&&unit_reads==unit_before&&!vr_render.seat.seated);
 seated(0);pool.valid=0;before=object_reads;unit_before=unit_reads;
 assert(!culled(&group)&&object_reads==before&&unit_reads==unit_before);
 seated(0);player.object.parent_object_index=other_id;before=object_reads;assert(!culled(&group)&&object_reads==before);
 seated(0);player.unit.parent_seat_index=1;before=object_reads;assert(!culled(&group)&&object_reads==before);
 seated(0);vr_render.seat.unit_index=other_id;before=object_reads;assert(!culled(&group)&&object_reads==before);
 assert(resets==5);
 assert(cull_checks==62);
 puts("PASS: 62 production model owner/queue/consumer checks: occupied glass, live toggle, 3 seats, attachments, effects, outside views and 5 teardown guards");
}
'''
source=source.replace('OWNER',model_owner).replace('QUEUE',queue).replace('CONSUMER',consumer)
compiler=['clang','-std=gnu11','-O1','-fsanitize=address,undefined','-fno-strict-aliasing']
cfile=OUT/'glass.c';exe=OUT/'glass';cfile.write_text(source)
subprocess.run(compiler+[str(cfile),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
old=source.replace('vr_render_seat_transparent(group->object_index,','vr_render_seat_transparent(group->source_object_index,')
assert old!=source
badfile=OUT/'glass_old_owner.c';badexe=OUT/'glass_old_owner';badfile.write_text(old)
subprocess.run(compiler+[str(badfile),'-o',str(badexe)],check=True)
result=subprocess.run([str(badexe)],capture_output=True,text=True)
assert result.returncode!=0 and 'culled(&group)' in result.stderr,result.stderr
print('PASS: negative control using the shipped effect-source field fails ordinary Warthog glass culling')
