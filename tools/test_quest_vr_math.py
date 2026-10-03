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
           "vr_finger_nodes", "vr_orient_hand", "vr_pose_finger"]
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
   real_point3d tip;memcpy(m,baseline,sizeof(m));
   assert(vr_pose_finger(&graph,m,0,joints[finger],finger,curl*.5f,&palm,&f,&u,&tip));
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
 vr.noted_weapon=-1;vr.pending_state=-1;vr.weapon_hand=1;
 vr_note_weapon(42);assert(vr.hand_state==HAND_LOOSE);
 vr.pending_state=HAND_EMPTY;vr_note_weapon(43);assert(vr.hand_state==HAND_EMPTY);
 vr.pending_state=-1;vr.hand_state=HAND_HELD;vr_note_weapon(43);assert(vr.hand_state==HAND_HELD);
 vr_note_weapon(-1);assert(vr.hand_state==HAND_EMPTY);
 vr.hand_state=HAND_HELD;vr_note_weapon(-1);assert(vr.hand_state==HAND_EMPTY && !vr.gun_held);
 vr.pending_state=HAND_HELD;vr_note_weapon(44);assert(vr.hand_state==HAND_HELD && vr.gun_held);
 vr.pending_state=HAND_EMPTY;vr.pending_until=1;clock_ms=2000;vr_note_weapon(44);assert(vr.pending_state==-1);
 puts("PASS: 36 rotations, mirrored wrist frames, 30 finger poses, bounded ancestry, weapon lifecycle");
}
'''
code = prelude + "\n".join(function(render, name) for name in helpers) + function(frame, "vr_note_weapon") + tests
(OUT / "vr_math.c").write_text(code)
subprocess.run(["clang", "-std=c11", "-O1", "-g", "-fsanitize=address,undefined", str(OUT / "vr_math.c"), "-lm", "-o", str(OUT / "vr_math")], check=True)
subprocess.run([str(OUT / "vr_math")], check=True)
