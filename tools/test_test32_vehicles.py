#!/usr/bin/env python3
"""Replay production seat lifecycle, 6DOF camera and independent turret aim.

Runs native source helpers with bounded engine/XR endpoints under ASan/UBSan.
No game files or headset are required; physical co-op acceptance is separate.
"""
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]

def fn(source,name):
    m=re.search(r'^(?:static )?[\w *]+\b'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',source,re.M)
    assert m,name
    end=m.end();depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]+'\n'


def main():
    frame=(ROOT/'port/linux/src/vr_frame.c').read_text()
    render=(ROOT/'port/linux/game/vr_render.c').read_text()
    code=r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define csmemset memset
#define HEAD_REACH .35f
#define ROOM_STEP_LIMIT .5f
#define HALO_XR_FRAME_SHOULD_RENDER 1
#define HALO_XR_FRAME_VIEWS_VALID 2
#define HALO_XR_FRAME_FOCUSED 4
#define HALO_XR_FRAME_RECENTRED 8
#define HALO_XR_BUTTON_LEFT_THUMB 1
#define HALO_XR_BUTTON_RIGHT_THUMB 2
typedef int boolean;typedef float real;
typedef union {struct {float i,j,k;};float n[3];} real_vector3d;
struct halo_xr_pose {float position[3],orientation[4];};
static struct {
 int active,seated,roomscale,room_held,heading_valid,stereo,stereo_enabled,force_render;
 int aiming,aiming_last_frame,hand_aiming,hand_aim,recentre_held,recentre_source;
 float heading,last_aim_yaw,head_yaw,aim_yaw,diag_yaw,diag_walk_speed,comfort_move,comfort_turn,run_push;
 float room_previous[2],room_now[2],units_per_metre;
 struct {int known,index,role,origin_valid,recentre_pending;long unit,vehicle;float origin[3];}vehicle_seat;
 struct {struct halo_xr_pose head,eye[2],aim[2];float fov[2][4],thumb[4];unsigned flags,buttons,hand_valid[2];long long predicted_display_period;}frame;
}vr;
static struct {struct {int seated,driver,gunner;long unit_index,vehicle_index;short seat_index;float offset,heading;}seat;}vr_render;
static struct {int valid;}pool={1},*object_header_data=&pool;
struct unit_datum {long definition_index;struct {long parent_object_index;real_vector3d forward;}object;struct {short parent_seat_index;}unit;};
struct unit_seat {unsigned long flags;};
static struct unit_seat seats[3]={{1},{0},{2}};
struct unit_definition {struct {struct {int count;struct unit_seat *address;}seats;}unit;};
static struct unit_definition definition={{{3,seats}}};
static struct unit_datum unit={1,{200,{1,0,0}},{1}},vehicle={2,{-1,{1,0,0}},{-1}};
static long unit_id=100,vehicle_id=200;
static int lookups,requests,logs,generation;
static const char *turret="right",*steering="right";
static int vr_settings_generation(void){return generation;}
static const char *config_string(const char *key){if(!strcmp(key,"vr.turret_aim"))return turret;assert(!strcmp(key,"vr.vehicle_steering"));return steering;}
static struct unit_datum *unit_try_and_get(long id){assert(object_header_data&&object_header_data->valid);lookups++;return id==unit_id?&unit:id==vehicle_id?&vehicle:NULL;}
static struct unit_definition *unit_definition_get(long id){assert(id==2);return &definition;}
static const char *tag_get_name(long id){assert(id==2);return "vehicles/test/vehicle";}
#define TAG_BLOCK_GET_ELEMENT(block,index,type) ((type*)&(block)->address[index])
#define TEST_FLAG(flags,bit) (((flags)&(1ul<<(bit)))!=0)
#define _unit_seat_driver_bit 0
#define _unit_seat_gunner_bit 1
enum {_vr_steering_stick,_vr_steering_head,_vr_steering_right,_vr_steering_left};
static void platform_log(const char *fmt,...){(void)fmt;logs++;}
static void host_xr_recenter(void){requests++;}
static void vr_head_look_reset(void){}
static void reset_hud_tap(void){}
static int vr_first_person_vehicles(void){return 1;}
static float render_interpolation_fraction(void){return .5f;}
static int frame_begin(void){return 1;}
static void synthesize_views(void){}
static void update_aim_pose(void){}
static int hand_forward(float f[3]){f[0]=1;f[1]=f[2]=0;return 1;}
static void turn(void){}
static float comfort_stick(float x,float y){(void)x;(void)y;return 0;}
static void comfort_update(double s){(void)s;}
static void aim_diagnostics(float g,int s,int h,const float *b,float p){(void)g;(void)s;(void)h;(void)b;(void)p;}
void vr_room_hold(void);
'''
    code+=''.join(fn(frame,n) for n in ['rotate','to_halo','wrap_angle','head_forward','vehicle_recentered','vr_vehicle_seat','head_offset','view','vr_eye_view','vr_room_hold','vr_room_step','vr_aim'])
    code+=''.join(fn(render,n) for n in ['vr_vehicle_steering','vr_turret_aim','vr_vehicle_aim_source','vr_yaw','vr_update_seat','vr_render_reset_vehicle_view'])
    code+=r'''
static void near(float a,float b){assert(fabsf(a-b)<.00001f);}
static void reset(void){
 memset(&vr,0,sizeof(vr));memset(&vr_render,0,sizeof(vr_render));
 vr.active=vr.stereo=vr.stereo_enabled=vr.heading_valid=vr.hand_aim=1;vr.units_per_metre=1;vr.frame.flags=7;
 vr.frame.head.orientation[3]=vr.frame.eye[0].orientation[3]=vr.frame.eye[1].orientation[3]=1;
 vr.frame.aim[0].orientation[1]=sinf(.4f);vr.frame.aim[0].orientation[3]=cosf(.4f);vr.frame.aim[1].orientation[3]=1;
 vr.frame.hand_valid[0]=vr.frame.hand_valid[1]=2;
 pool.valid=1;object_header_data=&pool;unit_id=100;vehicle_id=200;unit.object.parent_object_index=200;unit.unit.parent_seat_index=1;
 definition.unit.seats.count=3;unit.object.forward=(real_vector3d){1,0,0};vehicle.object.forward=(real_vector3d){1,0,0};
 requests=logs=lookups=0;turret=steering="right";generation++;
}
static void runtime_recenter(void){
 memset(vr.frame.head.position,0,sizeof(vr.frame.head.position));
 vr.room_previous[0]=vr.room_previous[1]=vr.room_now[0]=vr.room_now[1]=0;vr.room_held=1;
 vehicle_recentered();
}
static void check_lean(void){
 float offset[3],position[3]={8,9,10},heading[3]={1,0,0},p[2][3],f[3],u[3],bounds[4];
 for(int eye=0;eye<2;eye++){
  memcpy(vr.frame.eye[eye].position,vr.frame.head.position,12);vr.frame.eye[eye].position[0]+=eye?.032f:-.032f;
  assert(vr_eye_view(eye,position,heading,1,p[eye],f,u,bounds));near(f[0],1);near(u[2],1);
 }
 head_offset(offset);near(p[0][0],8-offset[2]);near(p[0][1],9-offset[0]+.032f);near(p[0][2],10+offset[1]);near(p[0][1]-p[1][1],.064f);
}
int main(void){
 float offset[3],step[2],f[3],heading=.3f;
 reset();unit.object.parent_object_index=NONE;vr_update_seat(100);assert(requests==0&&!vr.seated); /* no startup recenter loop */
 unit.object.parent_object_index=200;vr.room_now[0]=-80;vr.room_now[1]=100;vr.roomscale=1;
 vr.frame.head.position[0]=5;vr.frame.head.position[1]=1.2f;vr.frame.head.position[2]=3;
 vr_update_seat(100);assert(requests==1&&vr.seated&&vr.vehicle_seat.role==0&&vr.vehicle_seat.index==1&&vr.recentre_source==3);
 head_offset(offset);near(offset[0],0);near(offset[1],0);near(offset[2],0);
 vr.frame.head.position[0]+=.10f;vr.frame.head.position[1]+=.08f;vr.frame.head.position[2]-=.12f;
 for(int room=0;room<2;room++){vr.roomscale=room;head_offset(offset);near(offset[0],.1f);near(offset[1],.08f);near(offset[2],-.12f);check_lean();}
 for(int i=0;i<1000;i++)vr_update_seat(100);assert(requests==1);head_offset(offset);near(offset[0],.1f); /* never rebase each frame */
 vr.heading_valid=1;assert(!vr_room_step(step)); /* pending recenter cannot become walking */
 runtime_recenter();assert(!vr.vehicle_seat.recentre_pending&&vr.vehicle_seat.origin_valid);
 vr.frame.head.position[0]=.16f;vr.frame.head.position[1]=-.05f;head_offset(offset);near(offset[0],.16f);near(offset[1],-.05f);check_lean();
 /* Both eye translation and head rotation survive without any facing-input callback. */
 vr.frame.eye[0].orientation[1]=sinf(.35f);vr.frame.eye[0].orientation[3]=cosf(.35f);
 {float p[3],u[3],bounds[4],anchor[3]={0},forward[3]={1,0,0};assert(vr_eye_view(0,anchor,forward,1,p,f,u,bounds));assert(fabsf(f[1])>.6f);near(p[2],-.05f);}
 /* Explicit/manual runtime recenter while seated reanchors once, then lean resumes. */
 runtime_recenter();vr.frame.head.position[2]=-.2f;head_offset(offset);near(offset[2],-.2f);assert(requests==1);
 unit.object.parent_object_index=NONE;vr_update_seat(100);assert(requests==2&&!vr.seated&&vr.recentre_source==4);head_offset(offset);near(offset[2],0);
 vr_update_seat(100);vr_render_reset_vehicle_view();assert(requests==2);runtime_recenter();assert(!vr.vehicle_seat.origin_valid&&!vr.vehicle_seat.recentre_pending);
 /* Entry/seat transfer/deleted or salted handles/map reset: exactly one request per transition. */
 unit.object.parent_object_index=200;unit.unit.parent_seat_index=0;vr_update_seat(100);assert(requests==3&&vr_render.seat.driver);
 unit.unit.parent_seat_index=2;vr_update_seat(100);assert(requests==4&&vr_render.seat.gunner&&vr.recentre_source==5);
 unit_id=100+65536;vr_update_seat(unit_id);assert(requests==5&&vr_render.seat.unit_index==unit_id);
 unit.unit.parent_seat_index=99;vr_update_seat(unit_id);assert(requests==6&&!vr.seated);vr_update_seat(unit_id);assert(requests==6);
 unit.unit.parent_seat_index=1;vr_update_seat(unit_id);assert(requests==7);vehicle_id+=65536;vr_update_seat(unit_id);assert(requests==8&&!vr.seated);
 unit.object.parent_object_index=vehicle_id;vr_update_seat(unit_id);assert(requests==9);vr_render_reset_vehicle_view();vr_render_reset_vehicle_view();assert(requests==10);
 pool.valid=0;lookups=0;vr_update_seat(unit_id);assert(lookups==0&&requests==10);object_header_data=NULL;vr_update_seat(unit_id);assert(lookups==0);
 /* Preserve passenger seat orientation, independently from selected gun controls. */
 reset();unit.object.forward=(real_vector3d){0,1,0};vr_update_seat(100);near(vr_render.seat.offset,1.57079632679f);assert(vr_vehicle_aim_source()==0);
 unit.object.parent_object_index=NONE;vr_update_seat(100);assert(vr_vehicle_aim_source()==1);
 unit.object.parent_object_index=200;unit.unit.parent_seat_index=2;vr_update_seat(100);
 const char *modes[]={"right","left","head","stick","invalid"};int expected[]={2,3,0,-1,2};
 for(int i=0;i<5;i++){turret=modes[i];generation++;assert(vr_vehicle_aim_source()==expected[i]);}
 turret="left";generation++;unit.unit.parent_seat_index=0;vr_update_seat(100);assert(vr_vehicle_aim_source()==2); /* driver stays right */
 steering="head";generation++;assert(vr_vehicle_aim_source()==0);
 steering="left";generation++;assert(vr_vehicle_aim_source()==3);
 unit.unit.parent_seat_index=2;vr_update_seat(100);turret="right";generation++;
 assert(vr_aim(0,1,vr_vehicle_aim_source(),&heading,f));near(f[0],cosf(heading));near(f[1],sinf(heading));assert(!vr.hand_aiming);
 turret="left";generation++;assert(vr_aim(0,1,vr_vehicle_aim_source(),&heading,f));assert(fabsf(f[1]-sinf(heading))>.4f);
 turret="right";generation++;vr.frame.hand_valid[1]=0;assert(!vr_aim(0,1,vr_vehicle_aim_source(),&heading,f));assert(vr.aiming&&vr.heading_valid); /* native facing held, camera alive */
 turret="stick";generation++;assert(!vr_aim(0,1,vr_vehicle_aim_source(),&heading,f)&&vr.seated);
 puts("PASS: production seat identity + stereo positional/rotational lean, entry/exit/transfer recenters, invalid handles, independent turret source and lost tracking");
}
'''
    with tempfile.TemporaryDirectory(prefix='test32-vehicles-') as tmp:
        path=Path(tmp)/'vehicles.c';path.write_text(code)
        binary=Path(tmp)/'vehicles'
        subprocess.run(['clang','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-missing-braces','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(path),'-lm','-o',str(binary)],check=True)
        subprocess.run([str(binary)],check=True)
    windows=fn(render,'vr_render_windows')
    assert windows.index('vr_update_seat(')<windows.index('eye_camera(')
    assert 'director_inhibited_facing' not in windows
    facing=fn(render,'vr_player_control_facing')
    assert 'vr_vehicle_aim_source()' in facing
    begin=fn(frame,'frame_begin')
    assert 'vehicle_recentered();' in begin.split('HALO_XR_FRAME_RECENTRED',1)[1]
    host=(ROOT/'port/android/host/host_xr.c').read_text()
    assert 'xr.recentre_pending = 1;' in fn(host,'host_xr_recenter')
    print('PASS: render refresh precedes eye cameras independently of facing, runtime recenter wiring and turret source routing')

if __name__=='__main__':main()
