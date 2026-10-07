"""Test31: queued transparent first-person winding survives and restores its scope.

Runs production state/capture/wrapper/part helpers with a synthetic draw body.
This proves queue and recursive scope behavior, not an AR shader/device result.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test31-transparency'
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return (ROOT / path).read_text()


def fn(text, name):
    matches = list(re.finditer(r'^(?:static )?[\w *]+\b' + re.escape(name) +
                              r'\s*\([^;{]*\)\s*\{', text, re.M))
    assert matches, name
    # The public draw signature also appears inside the #else before the
    # original body. Its last definition is the VR scope wrapper.
    match = matches[-1]
    start = text.index('{', match.start())
    end, depth = start + 1, 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end] + '\n'


gl = read('port/linux/src/d3d8_gl.c')
raster = read('source/rasterizer/xbox/rasterizer_xbox.c')
models = read('source/rasterizer/xbox/rasterizer_xbox_models.c')
transparent = read('source/rasterizer/xbox/rasterizer_xbox_transparent_geometry.c')
header = read('source/rasterizer/xbox/rasterizer_xbox.h')
flag = re.search(r'^#define RASTERIZER_VR_MIRRORED_GEOMETRY_FLAG .+$', header, re.M).group()
assert flag.endswith('(1ul << 9)')
assert 'rasterizer_vr_capture_geometry_flags(geometry_flags,\n\t\t\t\tTEST_FLAG(geometry_flags, _rasterizer_geometry_first_person_bit))' in models
assert models.index('rasterizer_vr_capture_geometry_flags') < models.index('group->geometry_flags = geometry_flags')
assert transparent.count('csmemcpy(&layer_group, group, sizeof(layer_group))') == 2
# Existing render records retain their stock layout: the new bit fits even a
# 16-bit copy, while all transparent group declarations use unsigned long.
for path in ('source/rasterizer/rasterizer_transparent_geometry.c',
             'source/rasterizer/xbox/rasterizer_xbox_models.c',
             'source/rasterizer/xbox/rasterizer_xbox_transparent_geometry.c',
             'source/rasterizer/xbox/rasterizer_xbox_active_camouflage.c',
             'source/rasterizer/xbox/rasterizer_xbox_water.c'):
    assert re.search(r'struct transparent_geometry_group\s*\{\s*unsigned long geometry_flags;', read(path)), path
assert 'sizeof(struct transparent_geometry_group) == 0xA0' in read('source/rasterizer/rasterizer_transparent_geometry.c')

source = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
typedef unsigned char byte;
''' + flag + r'''
#define FIRST_PERSON (1ul << 7)
#define _rasterizer_vertex_type_model_compressed 4
static int vr_mirror_winding, vr_skinning_mirrored = 1;
static signed char vr_node_winding[44];
static short vr_node_winding_count;
static boolean vr_root_mirrored;
struct vertex_buffer {int type;long count;void *data;};
struct triangle_buffer {int valid;};
static int rasterizer_model_buffer_data(const struct vertex_buffer *v, const struct triangle_buffer *t,
    const void **data,const void **indices){*data=v->data;*indices=t;return t->valid && v->data!=0;}
struct transparent_geometry_group {
 unsigned long geometry_flags;
 int early, panel, calls;
 struct transparent_geometry_group *child;
};
static void rasterizer_transparent_geometry_group_draw_scoped(struct transparent_geometry_group *, boolean);
''' + ''.join(fn(gl, name) for name in (
    'halo_vr_mirror_winding', 'halo_vr_model_mirrored', 'halo_vr_winding_state',
    'halo_vr_restore_winding_state', 'halo_vr_skinning_mirrored')) + \
    fn(raster, 'rasterizer_vr_capture_geometry_flags') + \
    fn(raster, 'rasterizer_vr_part_winding') + \
    fn(transparent, 'rasterizer_transparent_geometry_group_draw') + r'''
/* Synthetic GPU/shader body; scope and per-part helpers above are production.
   This models a queued model root, then an unmirrored display-node part. */
static void rasterizer_transparent_geometry_group_draw_scoped(struct transparent_geometry_group *g,boolean dirty){
 assert(g);g->calls++;
 assert(halo_vr_model_mirrored()==!!(g->geometry_flags&RASTERIZER_VR_MIRRORED_GEOMETRY_FLAG));
 if(g->early)return;
 vr_node_winding_count=halo_vr_model_mirrored()?2:0;
 vr_root_mirrored=halo_vr_model_mirrored();
 vr_node_winding[0]=-1;vr_node_winding[1]=1;
 halo_vr_skinning_mirrored(vr_root_mirrored);
 unsigned char data[32]={0};short weight=32767;
 data[28]=g->panel?3:0;memcpy(data+30,&weight,2);
 struct vertex_buffer vertices={4,1,data};struct triangle_buffer triangles={1};
 rasterizer_vr_part_winding(&vertices,&triangles);
 if(halo_vr_model_mirrored())assert(vr_skinning_mirrored==!g->panel);
 int before=halo_vr_winding_state();
 if(g->child)rasterizer_transparent_geometry_group_draw(g->child,dirty);
 assert(halo_vr_winding_state()==before);
}
int main(void){
 struct transparent_geometry_group panel={0},root={0},right={0},world={0},early={0};
 halo_vr_mirror_winding(1);
 panel.geometry_flags=rasterizer_vr_capture_geometry_flags(FIRST_PERSON,1);panel.panel=1;
 root.geometry_flags=rasterizer_vr_capture_geometry_flags(FIRST_PERSON,1);root.child=&panel;
 world.geometry_flags=rasterizer_vr_capture_geometry_flags(0,0);
 assert(!(world.geometry_flags&RASTERIZER_VR_MIRRORED_GEOMETRY_FLAG));
 halo_vr_mirror_winding(0); /* submitting first-person model ended */
 right.geometry_flags=rasterizer_vr_capture_geometry_flags(FIRST_PERSON,1);right.child=&panel;
 assert(!(right.geometry_flags&RASTERIZER_VR_MIRRORED_GEOMETRY_FLAG));
 assert(panel.geometry_flags&RASTERIZER_VR_MIRRORED_GEOMETRY_FLAG);
 assert((unsigned short)panel.geometry_flags==panel.geometry_flags);
 assert(rasterizer_vr_capture_geometry_flags(~0ul,0)==(~0ul&~RASTERIZER_VR_MIRRORED_GEOMETRY_FLAG));
 early.geometry_flags=panel.geometry_flags;early.early=1;panel.child=&early;
 for(int state=0;state<4;state++){
  halo_vr_restore_winding_state(state);
  rasterizer_transparent_geometry_group_draw(&root,0);assert(halo_vr_winding_state()==state);
  rasterizer_transparent_geometry_group_draw(&panel,1);assert(halo_vr_winding_state()==state);
  rasterizer_transparent_geometry_group_draw(&right,0);assert(halo_vr_winding_state()==state);
  rasterizer_transparent_geometry_group_draw(&world,0);assert(halo_vr_winding_state()==state);
 }
 assert(root.calls==4 && right.calls==4 && world.calls==4 && panel.calls==12 && early.calls==12);
 puts("PASS: production queued mirror capture, display-part parity, right/world groups, nested draws and early-return state restoration");
}
'''
(OUT / 'winding.c').write_text(source)
subprocess.run(['clang', '-std=gnu11', '-O1', '-fsanitize=address,undefined',
                str(OUT / 'winding.c'), '-o', str(OUT / 'winding')], check=True)
subprocess.run([str(OUT / 'winding')], check=True)

# Preprocess the entire changed draw body in both editions: flat builds retain
# the original public body, with no scope helper or mirrored-state calls.
start = transparent.index('#ifdef HALO_VR\nstatic void rasterizer_transparent_geometry_group_draw_scoped(')
draw = transparent[start:]
(OUT / 'draw.c').write_text(draw)
for vr in (False, True):
    output = subprocess.check_output(['clang', '-E', '-P', '-x', 'c'] +
                                     (['-DHALO_VR'] if vr else []) + [str(OUT / 'draw.c')], text=True)
    if vr:
        assert 'static void rasterizer_transparent_geometry_group_draw_scoped(' in output
        assert 'halo_vr_restore_winding_state(previous);' in output
    else:
        assert output.startswith('void rasterizer_transparent_geometry_group_draw(')
        assert 'halo_vr_' not in output and 'group_draw_scoped' not in output
print('PASS: VR-only scope; flat preprocessing retains original draw body and transparent group layout')
