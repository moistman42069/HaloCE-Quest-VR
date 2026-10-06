"""Exercise production VR math/state helpers without requiring a headset.

The C functions are extracted verbatim from the game sources. The harness
checks geometric invariants and weapon lifecycle transitions, not source text.
Run with python3 tools/test_quest_vr_math.py (requires clang).
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "quest-vr-checks"
OUT.mkdir(parents=True, exist_ok=True)


def function(source, name):
    match = re.search(r"^(?:static )?[\w *]+\b" + re.escape(name) + r"\s*\(", source, re.M)
    if not match:
        raise ValueError(name)
    start = source.index("{", match.start())
    depth = 1
    end = start + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end] + "\n"


render = (ROOT / "port/linux/game/vr_render.c").read_text()
# test26: the finger pose before each joint took its own curl (1.0.7), to
# compare against: one curl for all three joints poses exactly as it did
render_1_0_7 = subprocess.check_output(["git", "show", "9bca3958:port/linux/game/vr_render.c"], cwd=ROOT, text=True)
frame = (ROOT / "port/linux/src/vr_frame.c").read_text()
prelude = r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
typedef float real;
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define MIN(a,b) ((a)<(b)?(a):(b))
#define CEILING(n,c) ((n)>(c)?(c):(n))
#define PIN(n,floor,ceiling) ((n)<(floor) ? (floor) : CEILING((n),(ceiling)))
#define MAXIMUM_NODES_PER_ANIMATION 64
typedef union { struct { float i,j,k; }; float n[3]; } real_vector3d;
typedef union { struct { float x,y,z; }; float n[3]; } real_point3d;
typedef struct { real scale; real_vector3d forward,left,up; real_point3d position; } real_matrix4x3;
struct vr_animation_graph_node { char name[33]; short parent_node_index; };
struct animation_graph { struct { int count; void *address; } nodes; };
#define TAG_BLOCK_GET_ELEMENT(block,index,type) (((type *)(block)->address)+(index))
static real dot_product3d(real_vector3d const*a,real_vector3d const*b) { return a->i*b->i+a->j*b->j+a->k*b->k; }
static void scale_vector3d(real_vector3d const*a,real s,real_vector3d*b) { b->i=a->i*s;b->j=a->j*s;b->k=a->k*s; }
static void normalize3d(real_vector3d *v) { real l=sqrtf(dot_product3d(v,v)); if(l>0)scale_vector3d(v,1/l,v); }
static void cross_product3d(real_vector3d const*a,real_vector3d const*b,real_vector3d*c) {
 real_vector3d t={a->j*b->k-a->k*b->j,a->k*b->i-a->i*b->k,a->i*b->j-a->j*b->i}; *c=t;
}
enum { HAND_LOOSE,HAND_HELD,HAND_EMPTY };
static char const *hand_state_names[] = {"loose","held","empty"};
static struct { long noted_weapon; int pending_state,hand_state,grip_held[2],weapon_hand,gun_held,two_hand_held,support_near;
 double pending_until; float ungripped_seconds; int ungripped_warned; } vr;
static double clock_ms;
static double now_ms(void) { return clock_ms; }
static int physical_weapons(void) { return 1; }
static void platform_log(char const *format, ...) { (void)format; }
'''
helpers = ["vr_length", "vr_point_minus", "vr_rotation_between", "vr_rotate_vector", "vr_carry",
           "vr_node_under", "vr_unit_vector", "vr_turn_subtree", "vr_axis_rotation", "vr_finger_of",
           "vr_finger_nodes", "vr_orient_hand", "vr_pose_finger_joints", "vr_finger_contact_curls"]
tests = r'''
static float determinant(real r[3][3]) {
 return r[0][0]*(r[1][1]*r[2][2]-r[1][2]*r[2][1])-r[0][1]*(r[1][0]*r[2][2]-r[1][2]*r[2][0])+r[0][2]*(r[1][0]*r[2][1]-r[1][1]*r[2][0]);
}
static float distance(real_point3d a,real_point3d b) { real_vector3d d;vr_point_minus(&a,&b,&d);return vr_length(&d); }
int main(void) {
 real_vector3d directions[]={{1,0,0},{-1,0,0},{0,1,0},{0,0,1},{.3f,-.4f,.5f},{.00001f,-1,0}};
 for(int a=0;a<6;a++)for(int b=0;b<6;b++) {
  real r[3][3];real_vector3d u=directions[a],v=directions[b],out;
  normalize3d(&u);normalize3d(&v);vr_rotation_between(&u,&v,r);vr_rotate_vector(r,&u,&out);
  assert(fabsf(determinant(r)-1)<.0001f);
  for(int i=0;i<3;i++)assert(fabsf(out.n[i]-v.n[i])<.0001f);
 }
 real_vector3d invalid={NAN,0,0};assert(!vr_unit_vector(&invalid));
 invalid.i=INFINITY;assert(!vr_unit_vector(&invalid));invalid.i=0;assert(!vr_unit_vector(&invalid));
 for(int mirror=0;mirror<2;mirror++) {
  struct vr_animation_graph_node nodes[16]={0};struct animation_graph graph={{16,nodes}};
  real_matrix4x3 m[16]={0},baseline[16];short joints[5][3];
  char const *names[]={"thumb","index","middle","ring","pinky"};
  nodes[0].parent_node_index=NONE;
  for(int f=0;f<5;f++)for(int d=0;d<3;d++) {
   int i=1+f*3+d;snprintf(nodes[i].name,sizeof(nodes[i].name),"frame l %s%d",names[f],d);
   nodes[i].parent_node_index=d?i-1:0;
   m[i].position=(real_point3d){.08f+.025f*d,(mirror?-1:1)*(-.05f+.025f*f),0};
  }
  for(int i=0;i<16;i++) {m[i].scale=1;m[i].forward.i=1;m[i].left.j=mirror?-1:1;m[i].up.k=1;}
  vr_finger_nodes(&graph,0,"l ",joints);
  assert(joints[2][0]==7 && joints[2][2]==9);
  real_vector3d f={0,1,0},u={0,0,1},palm={1,0,0},actual;
  vr_orient_hand(&graph,m,0,joints,&f,&u);
  vr_point_minus(&m[joints[2][0]].position,&m[0].position,&actual);normalize3d(&actual);
  assert(dot_product3d(&actual,&f)>.9999f);
  vr_point_minus(&m[joints[1][0]].position,&m[joints[4][0]].position,&actual);normalize3d(&actual);
  assert(dot_product3d(&actual,&u)>.9999f);
  memcpy(baseline,m,sizeof(m));
  for(int finger=0;finger<5;finger++)for(int curl=0;curl<=2;curl++) {
   real_point3d tip,old_tip;real_matrix4x3 old[16];real const same[3]={curl*.5f,curl*.5f,curl*.5f};
   memcpy(old,baseline,sizeof(old));
   assert(vr_pose_finger_1_0_7(&graph,old,0,joints[finger],finger,curl*.5f,&palm,&f,&u,&old_tip));
   memcpy(m,baseline,sizeof(m));
   assert(vr_pose_finger_joints(&graph,m,0,joints[finger],finger,same,&palm,&f,&u,&tip));
   /* one curl for every joint: exactly 1.0.7's pose */
   assert(!memcmp(m,old,sizeof(m))&&!memcmp(&tip,&old_tip,sizeof(tip)));
   /* a joint each its own curl: the bones keep their lengths, the base's alone moves the base */
   {real_matrix4x3 n[16];real_point3d t2;real const mixed[3]={curl*.5f,1.f-curl*.5f,.3f};
    memcpy(n,baseline,sizeof(n));assert(vr_pose_finger_joints(&graph,n,0,joints[finger],finger,mixed,&palm,&f,&u,&t2));
    for(int d=0;d<2;d++)assert(fabsf(distance(n[joints[finger][d]].position,n[joints[finger][d+1]].position)-.025f)<.00001f);
    for(int a=0;a<3;a++)assert(isfinite(t2.n[a]));}
   for(int d=0;d<2;d++)assert(fabsf(distance(m[joints[finger][d]].position,m[joints[finger][d+1]].position)-.025f)<.00001f);
   for(int i=0;i<16;i++)for(int a=0;a<3;a++)assert(isfinite(m[i].position.n[a]));
   for(int a=0;a<3;a++)assert(isfinite(tip.n[a]));
   /* Rotation of one finger cannot disturb the wrist or another finger. */
   assert(distance(m[0].position,baseline[0].position)==0);
   int other=joints[(finger+1)%5][2];assert(distance(m[other].position,baseline[other].position)==0);
  }
  nodes[1].parent_node_index=2;nodes[2].parent_node_index=1;
  assert(!vr_node_under(&graph,1,15));assert(!vr_node_under(&graph,63,0));
 }
 /* test26: contact moves a finger's joints continuously, from the curl it wants (t 0) to straight (-1) or
 curled (+1) at t 1, the base first flattening and the tip first buckling, each monotonic; no direction, no change */
 {int checked=0;
  for(int w=0;w<=10;w++)for(int dir=-1;dir<=1;dir++){real wanted=w/10.f,prev[3]={wanted,wanted,wanted};
   for(int k=0;k<=200;k++){real c[3],t=k/200.f;vr_finger_contact_curls(wanted,dir,t,c);checked++;
    for(int d=0;d<3;d++){assert(c[d]>=-1e-6f&&c[d]<=1+1e-6f);
     if(!dir)assert(c[d]==wanted);
     else{assert(dir<0?c[d]<=prev[d]+1e-6f:c[d]>=prev[d]-1e-6f);
      assert(fabsf(c[d]-prev[d])<=(1.f/200.f)/.5f+1e-5f);} /* no jump bigger than the fastest joint's pace */
     prev[d]=c[d];}
    if(k==0)for(int d=0;d<3;d++)assert(fabsf(c[d]-wanted)<1e-6f);
    if(k==200&&dir)for(int d=0;d<3;d++)assert(fabsf(c[d]-(dir<0?0.f:1.f))<1e-6f);
    if(dir<0&&wanted>0&&k>0&&k<100)assert(wanted-c[0]>=wanted-c[2]-1e-6f); /* the base flattens first */
    if(dir>0&&wanted<1&&k>0&&k<100)assert(c[2]-wanted>=c[0]-wanted-1e-6f);}} /* the tip buckles first */
  printf("PASS: %d contact curls continuous and monotonic (flatten base first, buckle tip first)\n",checked);}
 vr.noted_weapon=-1;vr.pending_state=-1;vr.weapon_hand=1;
 vr_note_weapon(42);assert(vr.hand_state==HAND_LOOSE);
 vr.pending_state=HAND_EMPTY;vr_note_weapon(43);assert(vr.hand_state==HAND_EMPTY);
 vr.pending_state=-1;vr.hand_state=HAND_HELD;vr_note_weapon(43);assert(vr.hand_state==HAND_HELD);
 vr_note_weapon(-1);assert(vr.hand_state==HAND_EMPTY);
 vr.hand_state=HAND_HELD;vr_note_weapon(-1);assert(vr.hand_state==HAND_EMPTY && !vr.gun_held);
 vr.pending_state=HAND_HELD;vr_note_weapon(44);assert(vr.hand_state==HAND_HELD && vr.gun_held);
 vr.pending_state=HAND_EMPTY;vr.pending_until=1;clock_ms=2000;vr_note_weapon(44);assert(vr.pending_state==-1);
 puts("PASS: 36 rotations, mirrored wrist frames, 30 finger poses (one curl each: bit-identical to 1.0.7; per-joint curls keep "
      "bone lengths), bounded ancestry, weapon lifecycle");
}
'''
old_pose = function(render_1_0_7, "vr_pose_finger").replace("vr_pose_finger(", "vr_pose_finger_1_0_7(", 1)
code = prelude + "\n".join(function(render, name) for name in helpers) + old_pose + function(frame, "vr_note_weapon") + tests
(OUT / "vr_math.c").write_text(code)
subprocess.run(["clang", "-std=c11", "-O1", "-g", "-fsanitize=address,undefined", str(OUT / "vr_math.c"), "-lm", "-o", str(OUT / "vr_math")], check=True)
subprocess.run([str(OUT / "vr_math")], check=True)
