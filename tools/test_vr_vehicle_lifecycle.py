"""Replay the stale-seat map-transition failure using production VR helpers.
No headset/game assets required. ASan/UBSan; clang required.
"""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/vr-vehicle-checks';OUT.mkdir(parents=True,exist_ok=True)
def fn(source,name):
 start=source.rfind('\n',0,source.index(name))+1;end=source.index('{',start)+1;depth=1
 while depth:
  depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]+'\n'
source=(ROOT/'port/linux/game/vr_render.c').read_text(encoding='utf-8')
game=(ROOT/'source/game/game.c').read_text(encoding='utf-8')
for function,before in [('void game_initialize_for_new_map(', 'game_state_initialize_for_new_map();'),('void game_dispose_from_old_map(', 'objects_dispose_from_old_map();')]:
 body=fn(game,function);assert body.index('vr_render_reset_vehicle_view();')<body.index(before)
code=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define csmemset memset
#define platform_log(...) ((void)0)
#define vr_head_look_reset() ((void)0)
typedef struct {float x,y,z;} real_point3d;
struct render_camera {real_point3d position;};
struct object_marker {struct {real_point3d position;} matrix;};
struct unit_datum {struct {long parent_object_index;} object;struct {short parent_seat_index;} unit;};
static struct {int valid;} pool={1},*object_header_data=&pool;
static struct {struct {int seated,driver,gunner;long unit_index,vehicle_index;short seat_index;float offset,heading;}seat;
 int cinematic_view;real_point3d cinematic_position;}vr_render;
static struct unit_datum unit={{200},{2}},vehicle={{NONE},{NONE}};
static long unit_id=100,vehicle_id=200;
static int lookups,markers,first_person=1;
static int vr_first_person_vehicles(void){return first_person;}
static struct unit_datum *unit_try_and_get(long id){
 assert(object_header_data&&object_header_data->valid);lookups++;
 return id==unit_id?&unit:id==vehicle_id?&vehicle:NULL;
}
static int object_get_marker_by_name(long id,const char *name,struct object_marker *m,int count){
 assert(id==unit_id&&object_header_data&&object_header_data->valid);assert(!strcmp(name,"head")&&count==1);
 markers++;m->matrix.position=(real_point3d){7,8,9};return 1;
}
static void unit_get_camera_position(long id,real_point3d *p){assert(id==unit_id);*p=(real_point3d){7,8,9};}
static void vr_vehicle_adjust_anchor(real_point3d *p){(void)p;}
/* test22: the steadied seat anchor (tested in test_test22) */
static void vr_seat_steady_anchor(real_point3d *p){(void)p;}
''' + fn(source,'void vr_render_reset_vehicle_view(')+fn(source,'static boolean vr_seat_view(')+fn(source,'static void view_anchor(')+r'''
static void seat(void){
 pool.valid=1;object_header_data=&pool;unit_id=100;vehicle_id=200;unit.object.parent_object_index=200;unit.unit.parent_seat_index=2;
 vr_render.seat.seated=1;vr_render.seat.unit_index=100;vr_render.seat.vehicle_index=200;vr_render.seat.seat_index=2;vr_render.seat.heading=1.25f;
 vr_render.cinematic_view=0;first_person=1;lookups=markers=0;
}
static void anchor(int expected){
 struct render_camera camera={{1,2,3}};real_point3d point;view_anchor(&camera,&point);
 assert(point.x==(expected?7:1)&&point.y==(expected?8:2)&&point.z==(expected?9:3));
}
int main(void){
 seat();anchor(1);assert(markers==1&&vr_render.seat.heading==1.25f&&vr_seat_view());
 seat();unit_id=0x10064;anchor(0);assert(!markers&&!vr_render.seat.seated&&vr_render.seat.unit_index==NONE);
 seat();vehicle_id=0x100c8;anchor(0);assert(!markers&&!vr_render.seat.seated);
 seat();unit.object.parent_object_index=NONE;anchor(0);assert(!markers&&!vr_render.seat.seated);
 seat();unit.unit.parent_seat_index=3;anchor(0);assert(!markers&&!vr_render.seat.seated);
 seat();vr_render.seat.seat_index=NONE;anchor(0);assert(!markers&&!vr_render.seat.seated);
 seat();pool.valid=0;anchor(0);assert(!lookups&&!markers&&!vr_render.seat.seated);
 seat();object_header_data=NULL;anchor(0);assert(!lookups&&!markers&&!vr_render.seat.seated);
 seat();vr_render_reset_vehicle_view();anchor(0);assert(!lookups&&!markers);
 /* Reused identical handles in a new map are not a license to retain a seat. */
 pool.valid=1;anchor(0);assert(!lookups&&!markers);
 seat();first_person=0;anchor(0);assert(!lookups&&!markers&&vr_render.seat.seated);
 first_person=1;anchor(1);assert(markers==1);
 seat();vr_render.cinematic_view=1;vr_render.cinematic_position=(real_point3d){4,5,6};
 struct render_camera camera={{1,2,3}};real_point3d point;view_anchor(&camera,&point);assert(point.x==4&&point.y==5&&point.z==6&&!lookups&&!markers);
 for(int i=0;i<10000;i++){seat();anchor(1);vr_render_reset_vehicle_view();pool.valid=0;anchor(0);pool.valid=1;anchor(0);assert(markers==1);}
 puts("PASS: stale/deleted/reused seat handles, invalid pool, detach/seat changes, map lifecycle ordering, valid vehicle/cinematic/chase views and 10,000 transition cycles");
}
'''
file=OUT/'vehicle.c';file.write_text(code,encoding='utf-8')
subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(file),'-o',str(OUT/'vehicle')],check=True)
subprocess.run([str(OUT/'vehicle')],check=True)
