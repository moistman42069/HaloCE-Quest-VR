"""Exercise the production render-target cache with a counted fake GL backend."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/quest-target-checks"
OUT.mkdir(parents=True, exist_ok=True)
source = (ROOT / "port/linux/src/d3d8_gl.c").read_text()
start = source.index("static struct render_target_entry *render_target_get(")
end = source.index("\nstruct xgpu_render_target *xgpu_render_target_find", start)
test = r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned GLuint;
typedef int BOOL;
typedef int GLsizei;
#define GL_TEXTURE_2D 0
#define GL_TEXTURE_MAX_LEVEL 0
#define GL_DEPTH24_STENCIL8 0
#define GL_DEPTH_STENCIL 0
#define GL_UNSIGNED_INT_24_8 0
#define GL_RGBA8 0
#define GL_BGRA 0
#define GL_UNSIGNED_BYTE 0
#define SCREEN_HEIGHT 480
#define FALSE 0
typedef struct { unsigned long Data; int depth; } D3DSurface;
struct render_target_entry {
    struct render_target_entry *next, *next_in_bucket;
    struct { unsigned long data, width, height, gl_width, gl_height; BOOL depth; float scale[2]; GLuint texture, multisample; int samples; BOOL unresolved; } target;
    unsigned long last_rendered;
    BOOL screen_buffer;
};
static struct render_target_entry *render_targets, *bucket;
static struct { unsigned long frame; D3DSurface back_buffer,depth_buffer; } device;
static float screen_scale[2] = {1, 1};
static unsigned textures, allocations;
static struct render_target_entry **render_target_bucket(unsigned long data) { (void)data; return &bucket; }
static int halo_screen_width(void) { return 640; }
static BOOL surface_is_shadow_map(const D3DSurface *s) { (void)s; return 0; }
static long halo_shadow_map_scale(void) { return 1; }
static void surface_dimensions(const D3DSurface *s, unsigned long *w, unsigned long *h, BOOL *depth) {
    *w=640; *h=480; *depth=s->depth;
}
static void glGenTextures(int n, GLuint *t) { assert(n==1); *t=++textures; }
static void glBindTexture(int a, GLuint b) { (void)a; (void)b; }
static void glTexParameteri(int a, int b, int c) { (void)a; (void)b; (void)c; }
static void glTexImage2D(int a,int b,int c,GLsizei w,GLsizei h,int d,int e,int f,void *p) {
    (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)p; assert(w>0 && h>0); allocations++;
}
static void xgpu_gl_state_invalidate(void) {}
'''
test += source[start:end]
test += r'''
static GLuint render(D3DSurface *surface, float scale) {
    screen_scale[0]=screen_scale[1]=scale;
    struct render_target_entry *entry=render_target_get(surface);
    entry->last_rendered=device.frame+1;
    return entry->target.texture;
}
int main(void) {
    D3DSurface surface={1,0}, depth={2,1}, empty={0,0};
    assert(render_target_get(NULL)==NULL && render_target_get(&empty)==NULL);
    GLuint first[3];
    float scales[3]={1.5f,2.f,1.f};
    for (int pass=0;pass<3;pass++) first[pass]=render(&surface,scales[pass]);
    assert(first[0]!=first[1] && first[1]!=first[2]);
    unsigned baseline=allocations;
    for (device.frame=1;device.frame<100;device.frame++) for (int pass=0;pass<3;pass++) {
        assert(render(&surface,scales[pass])==first[pass]);
    }
    assert(allocations==baseline); /* no per-frame texture storage churn */
    for (int setting=0;setting<100;setting++) {
        for (int frame=0;frame<6;frame++,device.frame++) {
            render(&surface,1.1f+setting*.003f);
            render(&surface,2.f);
            render(&surface,1.f);
            render(&depth,1.1f+setting*.003f);
        }
    }
    assert(textures<=8); /* bounded despite 100 unique eye resolutions */
    /* A stale MSAA allocation is invalidated when its texture storage is
       recycled: the next bind must reallocate even for equal sample count. */
    struct render_target_entry *stale=render_target_get(&surface);
    stale->target.multisample=99;stale->target.samples=4;stale->target.unresolved=1;
    for(struct render_target_entry *p=render_targets;p;p=p->next)p->last_rendered=device.frame;
    stale->last_rendered=0;device.frame+=10;
    screen_scale[0]=screen_scale[1]=3.0f;
    assert(render_target_get(&surface)==stale);
    assert(!stale->target.unresolved && stale->target.samples==-1);
    assert(stale->target.multisample==99); /* same GL name/FBO attachment */
    while (render_targets) { struct render_target_entry *next=render_targets->next; free(render_targets); render_targets=next; }
    printf("PASS: stable per-pass storage; 100 resolution changes used %u textures\n",textures);
}
'''
c = OUT / "targets.c"
c.write_text(test)
subprocess.run(["clang", "-fsanitize=address,undefined", str(c), "-o", str(OUT / "targets")], check=True)
subprocess.run([str(OUT / "targets")], check=True)
