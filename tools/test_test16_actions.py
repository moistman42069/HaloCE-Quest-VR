"""Exercise test16 production config migration and native action math/state.
No headset/GPU or rendered-animation acceptance is claimed by these checks.
"""
from pathlib import Path
import os, re, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test16-checks';OUT.mkdir(parents=True,exist_ok=True)
def fn(s,name):
 m=re.search(r'^(?:static )?[\w *]+\b'+re.escape(name)+r'\s*\(',s,re.M)
 assert m,name
 start=s.index('{',m.start());end=start+1;depth=1
 while depth:
  depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]+'\n'
def compile_run(name,code,extra=()):
 p=OUT/(name+'.c');p.write_text(code)
 subprocess.run(['clang','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-missing-braces','-fno-sanitize-recover=all','-fsanitize=address,undefined','-I',str(ROOT),str(p),*extra,'-lm','-pthread','-o',str(OUT/name)],check=True)
 subprocess.run([str(OUT/name)],check=True)
# Compile complete config implementation; stub only platform logging / unused SDL include.
s=(ROOT/'port/linux/src/port_config.c').read_text().replace('#include "platform.h"','static void platform_log(const char *s, ...) {(void)s;}').replace('#include <SDL3/SDL.h>','')
for vr in (False,True):
 name='config-vr' if vr else 'config-flat'
 p=OUT/(name+'.c');p.write_text('#define HALO_ANDROID 1\n'+('#define HALO_VR 1\n' if vr else '')+s+'\n#include <assert.h>\nint main(int argc,char **argv){assert(argc==2);assert(config_boolean("renderer.safe_geometry")==atoi(argv[1]));return 0;}\n')
 subprocess.run(['clang','-std=gnu11','-fno-sanitize-recover=all','-fsanitize=address,undefined','-I',str(ROOT/'port/linux/src'),'-I',str(ROOT/'port/third_party/tomlc17'),str(p),str(ROOT/'port/third_party/tomlc17/tomlc17.c'),'-pthread','-o',str(OUT/name)],check=True)
 cases=[('fresh',None,vr),('legacy','# retain\n[renderer]\nsafe_geometry = false # old\n[vr]\nbody = "legs"\n',vr),
 ('safe','[renderer]\nsafe_geometry=true\n',True),('missing','# keep\n[network]\nonline=false\n',vr),
 ('optout','[renderer]\nsafe_geometry=false\nvr_geometry_revision=1\n',False),
 ('old-revision','[renderer]\nsafe_geometry=false\nvr_geometry_revision=0\n',vr),
 ('crlf','[renderer]\r\nsafe_geometry = false\r\n[network]\r\nonline=false\r\n',vr),
 ('malformed','[renderer]\nsafe_geometry = nope\n',vr),
 ('inline','renderer={safe_geometry=false}\n',vr)]
 for case,initial,expected in cases:
  with tempfile.TemporaryDirectory(dir=OUT) as folder:
   config=Path(folder)/'config.toml'
   if initial is not None:config.write_bytes(initial.encode())
   env=dict(os.environ,HALO_DATA_ROOT=folder);env.pop('HALO_SAFE_GEOMETRY',None)
   # Process-local reload twice, to check persistence / opt-out stability.
   for repeat in range(2):subprocess.run([str(OUT/name),str(int(expected))],env=env,check=True)
   saved=config.read_text()
   if case=='malformed' or (vr and case=='inline'):assert saved==initial
   if case=='legacy':
    assert '# retain' in saved and 'body = "legs"' in saved
    if vr:assert (Path(folder)/'config.toml.pre-safe-geometry').read_text()==initial
   if case in ('missing','crlf'):assert 'online=false' in saved
   if vr and case not in ('malformed','inline'):assert re.search(r'vr_geometry_revision\s*=\s*1',saved)
   if not vr and case=='fresh':assert 'vr_geometry_revision' not in saved
 print('PASS:',name,'fresh/upgrade/reload/opt-out/CRLF/malformed/inline config (18 loads)')
# Exercise a write failure without relying on privileged filesystem permissions.
with tempfile.TemporaryDirectory(dir=OUT) as folder:
 root=Path(folder);original=b'# retained\n[renderer]\nsafe_geometry=false\n[vr]\nbody="legs"\n'
 config=root/'config.toml';config.write_bytes(original)
 blocked=root/'config.toml.safe-geometry.tmp';blocked.mkdir();(blocked/'keep').write_text('blocks replacement')
 env=dict(os.environ,HALO_DATA_ROOT=folder);env.pop('HALO_SAFE_GEOMETRY',None)
 for _ in range(2):
  subprocess.run([str(OUT/'config-vr'),'1'],env=env,check=True)
  assert config.read_bytes()==original
  assert (root/'config.toml.pre-safe-geometry').read_bytes()==original
print('PASS: failed migration writes preserve original config/backup; Safe in memory across retries')
fp=(ROOT/'source/interface/first_person_weapons.c').read_text()
enum=fp[fp.index('enum first_person_weapon_state'):fp.index('enum first_person_weapon_state')+fp[fp.index('enum first_person_weapon_state'):].index('};')+2]
compile_run('action-states',r'''
#include <assert.h>
#include <stdio.h>
#include "port/linux/game/vr_action_blend.h"
'''+enum+'\n'+fn(fp,'first_person_weapon_vr_action_mask')+r'''
int main(void){
 unsigned expected[]={0,3,3,3,0,0,0,0,0,0,3,3,3,3,3,3,3,3,3,3,1,3,3,3};
 assert(sizeof(expected)/sizeof(*expected)==NUMBER_OF_FIRST_PERSON_WEAPON_STATES);
 for(int i=0;i<NUMBER_OF_FIRST_PERSON_WEAPON_STATES;i++)assert(first_person_weapon_vr_action_mask(i)==expected[i]);
 assert(!first_person_weapon_vr_action_mask(-1)&&!first_person_weapon_vr_action_mask(999));
 for(int hz=30;hz<=144;hz++){
  struct vr_action_blend a={0};double t=1,dt=1./hz;
  vr_action_blend_update(&a,t,0,0);assert(a.weight[0]==0);
  for(int i=0;i<hz;i++){
   t+=dt;vr_action_blend_update(&a,t,3,0);float prior=a.weight[0];
   vr_action_blend_update(&a,t,3,0);assert(a.weight[0]==prior); /* other eye */
  }
  assert(a.weight[0]==1&&a.weight[1]==1);
  for(int i=0;i<hz;i++){t+=dt;vr_action_blend_update(&a,t,1,0);}
  assert(a.weight[0]==1&&a.weight[1]==0); /* throw uses support arm */
  t+=dt;vr_action_blend_update(&a,t,0,0);assert(a.weight[0]<1&&a.weight[0]>0);
  t+=dt;float prior=a.weight[0];vr_action_blend_update(&a,t,3,0);assert(a.weight[0]>=prior); /* interrupt */
  vr_action_blend_update(&a,t,0,1);assert(a.weight[0]==0&&a.weight[1]==0); /* swap/unit/hand/config reset */
  vr_action_blend_update(&a,t+1,3,0);assert(a.weight[0]==1); /* frame gap */
  vr_action_blend_update(&a,t-1,0,0);assert(a.weight[0]==0); /* clock reset */
  vr_action_blend_update(&a,NAN,3,0);assert(!a.valid&&a.weight[0]==0);
 }
 puts("PASS: all 24 native action states, 30-144Hz blends, both eyes, interrupts, identity/time resets");
}
''')
# Exact production matrix/quaternion helpers, including left-hand reflection.
m=(ROOT/'source/math/matrix_math.c').read_text();r=(ROOT/'source/math/real_math.c').read_text();v=(ROOT/'port/linux/game/vr_render.c').read_text()
pre=r'''
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
typedef float real;typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAXIMUM_NODES_PER_ANIMATION 64
struct vr_animation_graph_node {short parent_node_index;};
struct animation_graph {struct {int count;struct vr_animation_graph_node *address;} nodes;};
#define TAG_BLOCK_GET_ELEMENT(b,i,t) (((t*)(b)->address)+(i))
typedef union {struct {float i,j,k;};float n[3];} real_vector3d;
typedef union {struct {float x,y,z;};float n[3];} real_point3d;
typedef struct {real_vector3d v;float w;} real_quaternion;
typedef struct {float scale;union{struct{real_vector3d forward,left,up;};float n[3][3];};real_point3d position;} real_matrix4x3;
#define square_root sqrtf
#define reciprocal_square_root(x) (1.f/sqrtf(x))
static void set_real_quaternion(real_quaternion*q,real i,real j,real k,real w){q->v.i=i;q->v.j=j;q->v.k=k;q->w=w;}
static const short matrix4x3_next[]={1,2,0};
static void scale_vector3d(real_vector3d const*a,real s,real_vector3d*b){b->i=a->i*s;b->j=a->j*s;b->k=a->k*s;}
static void cross_product3d(real_vector3d const*a,real_vector3d const*b,real_vector3d*c){real_vector3d t={a->j*b->k-a->k*b->j,a->k*b->i-a->i*b->k,a->i*b->j-a->j*b->i};*c=t;}
static float dot_product3d(real_vector3d const*a,real_vector3d const*b){return a->i*b->i+a->j*b->j+a->k*b->k;}
'''
# quaternion_normalize pulls in square_root + global identity for a zero quaternion.
normalize=fn(r,'quaternion_normalize')

compile_run('action-matrices',pre+normalize+fn(r,'quaternions_interpolate')+fn(r,'quaternions_interpolate_and_normalize')+fn(m,'matrix4x3_rotation_to_quaternion')+fn(m,'matrix4x3_rotation_from_quaternion')+fn(v,'vr_action_matrix_valid')+fn(v,'vr_blend_action_matrix')+fn(v,'vr_node_under')+fn(v,'vr_blend_action_arm')+r'''
int main(void){
 for(int mirror=0;mirror<2;mirror++)for(int degrees=-180;degrees<=180;degrees+=15){
  float theta=degrees*3.141592653589793f/360;
  real_quaternion q={{{0,0,sinf(theta)}},cosf(theta)};
  real_matrix4x3 a={1,{{{1,0,0},{0,1,0},{0,0,1}}},{{0,0,0}}},b;
  matrix4x3_rotation_from_quaternion(&b,&q);b.position.x=1;b.position.y=2;b.position.z=3;
  if(mirror){scale_vector3d(&a.left,-1,&a.left);scale_vector3d(&b.left,-1,&b.left);}
  for(int i=0;i<=100;i++){
   float w=i/100.f;real_matrix4x3 t=a;vr_blend_action_matrix(&t,&b,w);
   if(i==0)assert(!memcmp(&t,&a,sizeof(t)));
   if(i==100)assert(!memcmp(&t,&b,sizeof(t)));
   real_vector3d cross;cross_product3d(&t.forward,&t.left,&cross);
   assert(fabsf(dot_product3d(&cross,&t.up)-(mirror?-1:1))<.0001f);
   assert(fabsf(dot_product3d(&t.forward,&t.left))<.0001f);
   assert(fabsf(dot_product3d(&t.forward,&t.forward)-1)<.0001f);
   if(i==99)assert(dot_product3d(&t.forward,&b.forward)>.999f);
   assert(fabsf(t.position.x-w)<.00001f&&fabsf(t.position.z-3*w)<.00001f);
  }
 }
 real_matrix4x3 valid={1,{{{1,0,0},{0,1,0},{0,0,1}}},{{0,0,0}}},bad=valid,out=valid;
 bad.position.x=NAN;vr_blend_action_matrix(&out,&bad,.5f);assert(!memcmp(&out,&valid,sizeof(out)));
 out=bad;vr_blend_action_matrix(&out,&valid,.5f);assert(!memcmp(&out,&valid,sizeof(out)));
 vr_blend_action_matrix(&out,&valid,NAN);assert(!memcmp(&out,&valid,sizeof(out)));
 struct vr_animation_graph_node nodes[]={{-1},{0},{1},{2},{2},{4},{-1}};
 struct animation_graph graph={{7,nodes}};
 real_matrix4x3 tracked[7],native[7];
 for(int i=0;i<7;i++){tracked[i]=valid;native[i]=valid;native[i].position.x=10+i;}
 vr_blend_action_arm(&graph,tracked,native,0,4,1);
 for(int i=0;i<7;i++)assert(tracked[i].position.x==(i<4?10+i:0));
 for(int i=0;i<7;i++)tracked[i]=valid;
 vr_blend_action_arm(&graph,tracked,native,-1,4,1);
 for(int i=0;i<7;i++)assert(tracked[i].position.x==0);
 vr_blend_action_arm(&graph,tracked,native,0,4,0);
 for(int i=0;i<7;i++)assert(tracked[i].position.x==0);
 puts("PASS: native arm/finger descendants, gun/attachment exclusion, invalid root and zero-ownership no-op");
 puts("PASS: 5050 native/tracked rotation blends, exact endpoints, reflected left hand, no shear");
}
''')
