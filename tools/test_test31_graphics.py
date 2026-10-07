"""Test imported graphics using production C and software GLES, never a headset.

Run in WSL/Linux with clang, Mesa libEGL/libGL, and Khronos headers (system
or installed Android NDK). No renderer/game launch, packaging or SDK changes.
"""
from pathlib import Path
import glob, os, re, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'port/linux/src'
OUT=ROOT/'build/test31-graphics';OUT.mkdir(parents=True,exist_ok=True)
BASE='d6100629' # pre shadow/lighting/AA integration; only UI added in this commit

def read(name):return (SRC/name).read_text()
def fn(source,name):
    m=re.search(r'^(?:static )?[\w *]+\b'+name+r'\s*\([^;{]*\)\s*\{',source,re.M);assert m,name
    start=source.index('{',m.start());end=start+1;depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[m.start():end]+'\n'

d3d=read('d3d8_gl.c');vsh=read('nv2a_vsh.c');psh=read('nv2a_psh.c');post=read('xgpu_post.c');h=read('xgpu.h')
prepare=fn(d3d,'prepare_draw')
assert 'program->lighting.lights && !program->lighting_failed && per_pixel_lighting()' in prepare
assert 'key.per_pixel_lighting = 0;' in prepare and 'vertex_shader_get(program, immediate, FALSE)' in prepare
assert prepare.index('bind_textures(')<prepare.index('bind_targets(')
assert 'memcmp' in fn(d3d,'fragment_shader_get') and 'sizeof(*key)' in fn(d3d,'fragment_shader_get')
assert 'memset(&object->lighting, 0' in fn(d3d,'halo_vertex_shader_lighting')
assert 'crosshair_capture.active' in fn(d3d,'bind_targets')
assert 'target_samples = 1;' in fn(d3d,'bind_targets')
assert 'glBindVertexArray(device.vertex_array)' in fn(d3d,'halo_screen_anti_alias')
assert 'xgpu_gl_state_invalidate()' in fn(d3d,'halo_screen_anti_alias')
assert 'device.frame - entry->last_rendered > 2' in fn(d3d,'render_target_get')
assert 'entry->target.samples = entry->target.multisample ? -1 : 0' in fn(d3d,'render_target_get')
assert 'render_target_resolve' in fn(d3d,'render_target_multisample')
assert 'GL_NEAREST' in fn(d3d,'render_target_resolve')

# Use headers already installed with the build toolchain; copy only headers to
# this ignored test output so gl32.h cannot pull Android libc into host clang.
headers=Path('/usr/include')
if not (headers/'GLES3/gl32.h').exists():
    candidates=glob.glob('/home/halo/Android/Sdk/ndk/*/toolchains/llvm/prebuilt/linux-x86_64/sysroot/usr/include')
    assert candidates,'GLES headers missing: install/use the project Android NDK'
    headers=OUT/'include';headers.mkdir(exist_ok=True)
    for directory in ('GLES3','GLES2','KHR','EGL'):
        shutil.copytree(Path(sorted(candidates)[-1])/directory,headers/directory,dirs_exist_ok=True)

xdk=(ROOT/'port/include/xdk/xdk_pdb.h').read_text()
constants='\n'.join('#define '+name+' '+value for name,value in dict(re.findall(r'\b(D3D\w+)\s*=\s*(0x[0-9a-fA-F]+|[0-9]+)\b',xdk)).items())
shared=h[h.index('struct xgpu_text\n'):h.index('/* ---------- textures */')]
shim=r"""
#ifndef TEST_GRAPHICS_H
#define TEST_GRAPHICS_H
#include <GLES3/gl32.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <stdarg.h>
typedef int BOOL;typedef uint32_t DWORD;
#define TRUE 1
#define FALSE 0
struct xgpu_capabilities {const char *shading_language;};
extern struct xgpu_capabilities xgpu_capabilities;
const char *config_string(const char *name);
int config_boolean(const char *name);
void platform_log(const char *format,...);
GLuint xgpu_compile_shader(GLenum type,const char *code,const char *what);
GLuint xgpu_link_program(GLuint vertex,GLuint fragment,const char *what);
"""+constants+'\n'+shared+r"""
char *nv2a_vertex_shader_to_glsl_baseline(const DWORD *,unsigned long,unsigned long);
char *nv2a_pixel_shader_to_glsl_baseline(const struct nv2a_pixel_shader_key *);
#endif
"""
(OUT/'shim.h').write_text(shim)
for name in ('xgpu_text.c','nv2a_vsh.c','nv2a_psh.c'):
    (OUT/name).write_text(read(name).replace('#include "xgpu.h"','#include "shim.h"').replace('#include "port_config.h"',''))
for name,func in (('nv2a_vsh.c','nv2a_vertex_shader_to_glsl'),('nv2a_psh.c','nv2a_pixel_shader_to_glsl')):
    base=subprocess.check_output(['git','show',BASE+':port/linux/src/'+name],cwd=ROOT).decode()
    base=base.replace('#include "xgpu.h"','#include "shim.h"').replace('#include "port_config.h"','').replace(func+'(',func+'_baseline(')
    (OUT/('baseline_'+name)).write_text(base)

# Immutable embedded production programs (header plus instruction payload).
table=(ROOT/'source/rasterizer/xbox/rasterizer_xbox_vertex_shaders.c').read_text()
entries=re.findall(r'VERTEX_SHADER_ENTRY\((0x\w+), (0x\w+)\)',table)
blob=(ROOT/'source/rasterizer/xbox/rasterizer_xbox_vertex_shaders_data.inc').read_text()
shader_data='static const DWORD shader_blob[]={\n'+blob+'\n};\nstatic const unsigned entries[][2]={'+','.join('{'+a+','+b+'}' for a,b in entries)+'};\n'

support=r"""
#include "shim.h"
struct xgpu_capabilities xgpu_capabilities={"300 es"};
const char *config_string(const char *name){(void)name;return "";}
int config_boolean(const char *name){(void)name;return 0;}
void platform_log(const char *format,...){va_list args;va_start(args,format);vfprintf(stderr,format,args);fputc('\n',stderr);va_end(args);}
GLuint xgpu_compile_shader(GLenum type,const char *code,const char *what){
 GLuint shader=glCreateShader(type);glShaderSource(shader,1,&code,NULL);glCompileShader(shader);GLint okay=0;glGetShaderiv(shader,GL_COMPILE_STATUS,&okay);
 if(!okay){char log[8192];glGetShaderInfoLog(shader,sizeof(log),NULL,log);fprintf(stderr,"%s: %s\n%s\n",what,log,code);abort();}return shader;
}
GLuint xgpu_link_program(GLuint vertex,GLuint fragment,const char *what){
 GLuint p=glCreateProgram();glAttachShader(p,vertex);glAttachShader(p,fragment);glLinkProgram(p);GLint okay=0;glGetProgramiv(p,GL_LINK_STATUS,&okay);
 if(!okay){char log[8192];glGetProgramInfoLog(p,sizeof(log),NULL,log);fprintf(stderr,"%s: %s\n",what,log);abort();}return p;
}
static void context(void){
 PFNEGLGETPLATFORMDISPLAYEXTPROC get=(void*)eglGetProcAddress("eglGetPlatformDisplayEXT");assert(get);
 EGLDisplay display=get(EGL_PLATFORM_SURFACELESS_MESA,EGL_DEFAULT_DISPLAY,NULL);EGLint major,minor;assert(eglInitialize(display,&major,&minor));assert(eglBindAPI(EGL_OPENGL_ES_API));
 const EGLint attributes[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_ALPHA_SIZE,8,EGL_NONE};
 EGLConfig config;EGLint count;assert(eglChooseConfig(display,attributes,&config,1,&count)&&count);
 const EGLint sizes[]={EGL_WIDTH,128,EGL_HEIGHT,128,EGL_NONE};EGLSurface surface=eglCreatePbufferSurface(display,config,sizes);assert(surface!=EGL_NO_SURFACE);
 const EGLint version[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE};EGLContext ctx=eglCreateContext(display,config,EGL_NO_CONTEXT,version);assert(ctx!=EGL_NO_CONTEXT);
 assert(eglMakeCurrent(display,surface,surface,ctx));printf("GLES test renderer: %s / %s\n",glGetString(GL_RENDERER),glGetString(GL_VERSION));
}
"""
checks=r"""
static void shaders(void){
 unsigned recognized=0;
 for(unsigned i=0;i<sizeof(entries)/sizeof(entries[0]);i++){
  const DWORD *instructions=shader_blob+entries[i][0]/4+1;unsigned count=(entries[i][1]-4)/16;
  char *old=nv2a_vertex_shader_to_glsl_baseline(instructions,count,0),*now=nv2a_vertex_shader_to_glsl(instructions,count,0,NULL);
  assert(!strcmp(old,now));assert(!strstr(now,"xWorldNormal"));free(old);free(now);
  struct nv2a_vertex_lighting lighting={0};int found=nv2a_vertex_shader_lighting(instructions,count,&lighting);
  if(i==9||i==10||i==17||i==27){
   assert(found);assert(lighting.lights==((i==10||i==17)?2:1));recognized++;
   now=nv2a_vertex_shader_to_glsl(instructions,count,0,&lighting);assert(strstr(now,"xWorldNormal"));
   struct nv2a_pixel_shader_key key={0};key.per_pixel_lighting=lighting.lights;
   key.combiner_state[D3DRS_PSFINALCOMBINERINPUTSABCD]=0x00000004; // final diffuse RGB
   key.combiner_state[D3DRS_PSFINALCOMBINERINPUTSEFG]=0x00000400;
   char *pixel=nv2a_pixel_shader_to_glsl(&key);
   GLuint vs=xgpu_compile_shader(GL_VERTEX_SHADER,now,"model vertex"),ps=xgpu_compile_shader(GL_FRAGMENT_SHADER,pixel,"model fragment");
   GLuint program=xgpu_link_program(vs,ps,"model lighting pair");glDeleteProgram(program);glDeleteShader(vs);glDeleteShader(ps);free(now);free(pixel);
   DWORD *changed=malloc(count*16);memcpy(changed,instructions,count*16);
   // A new oD0.xyz write invalidates recognition, never silently lights twice.
   changed[1]=(1u<<21);changed[3]=(14u<<12)|(1u<<11)|(3u<<3);
   assert(!nv2a_vertex_shader_lighting(changed,count,&lighting));free(changed);
  }
 }
 assert(recognized==4);
 for(int fog=0;fog<4;fog++)for(int alpha=0;alpha<9;alpha++)for(int texture=0;texture<4;texture++){
  struct nv2a_pixel_shader_key key={0};key.fog_enable=fog!=0;key.fog_table_mode=fog;
  key.alpha_test_function=alpha?511+alpha:0;key.sampler_type[0]=texture;key.texture_modes=texture?1:0;
  char *old=nv2a_pixel_shader_to_glsl_baseline(&key),*now=nv2a_pixel_shader_to_glsl(&key);
  assert(!strcmp(old,now));assert(!strstr(now,"model_lighting"));free(old);free(now);
 }
 puts("PASS: OFF translation unchanged for 67 vertex programs / 144 pixel keys; four recognized model lighting variants compile and link; altered diffuse writes rejected");
}
static void aa(void){
 unsigned char input[64*64*4],output[sizeof(input)];
 for(int y=0;y<64;y++)for(int x=0;x<64;x++){
  int off=(y*64+x)*4;input[off]=input[off+1]=input[off+2]=(x>y?255:0);input[off+3]=77;
 }
 GLuint target=texture_new(GL_RGBA8,64,64,GL_RGBA,input),fbo=framebuffer_new(target);assert(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE);
 GLint corners[4]={0,0,32,64};assert(xgpu_post_anti_alias(FALSE,fbo,64,64,corners));
 glReadPixels(0,0,64,64,GL_RGBA,GL_UNSIGNED_BYTE,output);assert(glGetError()==GL_NO_ERROR);
 int changed=0;
 for(int y=0;y<64;y++)for(int x=0;x<64;x++){
  int off=(y*64+x)*4;assert(output[off+3]==77);
  if(x>=32)assert(!memcmp(output+off,input+off,4));else if(output[off]!=input[off])changed++;
 }
 assert(changed>0); // real diagonal smoothing, outside viewport/alpha preserved
 GLuint cached[3];unsigned sizes[3]={64,96,128};
 for(int i=0;i<3;i++){textures_fit(FALSE,sizes[i],sizes[i]);cached[i]=post.color;assert(cached[i]);}
 for(int frame=0;frame<100;frame++)for(int i=0;i<3;i++){textures_fit(FALSE,sizes[i],sizes[i]);assert(post.color==cached[i]);}
 textures_fit(FALSE,144,144);assert(post.width==144&&post.height==144); // least recently used; GL names may recycle
 textures_fit(FALSE,96,96);assert(post.color==cached[1]);textures_fit(FALSE,128,128);assert(post.color==cached[2]);
 glDeleteFramebuffers(1,&fbo);glDeleteTextures(1,&target);assert(glGetError()==GL_NO_ERROR);
 puts("PASS: production FXAA GLES compile/link/draw, alpha and split-viewport preservation; three eye/scope scratch sizes reused without churn");
}
int main(int argc,char **argv){if(argc>1)xgpu_capabilities.shading_language=argv[1];context();shaders();aa();return 0;}
"""
# Exercise the actual multisample ownership/resolve functions on Mesa too.
def structure(source,name):
    a=source.index('struct '+name+'\n{');return source[a:source.index('\n};',a)+3]+'\n'
msaa = structure(h,'xgpu_render_target') + structure(d3d,'framebuffer_entry') + r"""
static struct framebuffer_entry *framebuffers;
static int invalidations;
static BOOL multisampling_failed;
static void xgpu_gl_state_invalidate(void){invalidations++;}
#define glClearDepth glClearDepthf
""" + ''.join(fn(d3d,n) for n in ('framebuffer_find','framebuffer_get','framebuffer_forget_renderbuffer','multisampling_disable','render_target_resolve','render_target_multisample')) + r"""
static void multisample_checks(void){
 GLint maximum;glGetIntegerv(GL_MAX_SAMPLES,&maximum);assert(maximum>=4);
 for(int depth=0;depth<2;depth++){
  struct xgpu_render_target target={0};target.depth=depth;target.gl_width=target.gl_height=64;
  glGenTextures(1,&target.texture);glBindTexture(GL_TEXTURE_2D,target.texture);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAX_LEVEL,0);
  glTexImage2D(GL_TEXTURE_2D,0,depth?GL_DEPTH24_STENCIL8:GL_RGBA8,64,64,0,depth?GL_DEPTH_STENCIL:GL_RGBA,depth?GL_UNSIGNED_INT_24_8:GL_UNSIGNED_BYTE,NULL);
  for(int samples=2;samples<=4;samples*=2){
   render_target_multisample(&target,samples);assert(target.samples==samples);assert(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE);
   GLuint name=target.multisample;int before=invalidations;render_target_multisample(&target,samples);assert(name==target.multisample&&invalidations==before);
   if(!depth){glClearColor(.25f,.5f,.75f,77.f/255.f);glClear(GL_COLOR_BUFFER_BIT);}
   target.unresolved=TRUE;render_target_resolve(&target);assert(!target.unresolved);
   assert(glGetError()==GL_NO_ERROR);before=invalidations;render_target_resolve(&target);assert(invalidations==before);
   if(!depth){unsigned char pixel[4];glReadBuffer(GL_COLOR_ATTACHMENT0);glBindFramebuffer(GL_READ_FRAMEBUFFER,framebuffer_get(target.texture,0));glReadPixels(0,0,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);assert(pixel[0]==64&&pixel[1]==128&&pixel[2]==191&&pixel[3]==77);}
  }
  // The renderer marks recycled textures samples=-1 so equal sample count
  // still reallocates the renderbuffer to the new dimensions.
  target.gl_width=96;target.samples=-1;glBindTexture(GL_TEXTURE_2D,target.texture);
  glTexImage2D(GL_TEXTURE_2D,0,depth?GL_DEPTH24_STENCIL8:GL_RGBA8,96,64,0,depth?GL_DEPTH_STENCIL:GL_RGBA,depth?GL_UNSIGNED_INT_24_8:GL_UNSIGNED_BYTE,NULL);
  render_target_multisample(&target,4);glBindRenderbuffer(GL_RENDERBUFFER,target.multisample);GLint width;glGetRenderbufferParameteriv(GL_RENDERBUFFER,GL_RENDERBUFFER_WIDTH,&width);assert(width==96);
  target.unresolved=TRUE;render_target_multisample(&target,0);assert(!target.unresolved&&target.samples==0);assert(glGetError()==GL_NO_ERROR);
 }
 puts("PASS: real GLES MSAA2x/4x color/depth resolve, alpha, idempotence, resize storage and disabling transition");
}
"""
checks=checks.replace('context();shaders();aa();return 0;', 'context();shaders();aa();multisample_checks();return 0;')
fault_support = r"""
static int fail_fbo,fail_pair,fail_storage,fail_texture,texture_uploads;
static GLenum fault_status(GLenum target){
 if(fail_fbo){fail_fbo--;return GL_FRAMEBUFFER_UNSUPPORTED;}
 if(fail_pair){GLint color,depth;glGetFramebufferAttachmentParameteriv(target,GL_COLOR_ATTACHMENT0,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,&color);glGetFramebufferAttachmentParameteriv(target,GL_DEPTH_ATTACHMENT,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE,&depth);
  if(color==GL_RENDERBUFFER&&depth==GL_RENDERBUFFER){fail_pair=0;return GL_FRAMEBUFFER_UNSUPPORTED;}}
 return glCheckFramebufferStatus(target);
}
static void fault_storage(GLenum t,GLsizei s,GLenum f,GLsizei w,GLsizei h){if(fail_storage){fail_storage=0;w=-1;}glRenderbufferStorageMultisample(t,s,f,w,h);}
static void fault_texture(GLenum t,GLint l,GLint i,GLsizei w,GLsizei h,GLint b,GLenum f,GLenum ty,const void *p){texture_uploads++;if(fail_texture){fail_texture=0;w=-1;}glTexImage2D(t,l,i,w,h,b,f,ty,p);}
#define glCheckFramebufferStatus fault_status
#define glRenderbufferStorageMultisample fault_storage
#define glTexImage2D fault_texture
"""
bind_support = r"""
typedef struct {int depth;} D3DSurface;
struct render_target_entry {struct xgpu_render_target target;unsigned long last_rendered;BOOL screen_buffer;};
static struct render_target_entry test_color,test_depth;
static struct {D3DSurface *render_target,*depth_stencil;unsigned long frame;} device;
static struct render_target_entry *render_target_get(const D3DSurface *s){return s?(s->depth?&test_depth:&test_color):NULL;}
static float target_scale[2];static int target_samples=1;
static int anti_aliasing_samples=4;
#define _anti_aliasing_msaa 4
static int anti_aliasing(void){return _anti_aliasing_msaa;}
static void state_framebuffer(GLuint fbo){glBindFramebuffer(GL_FRAMEBUFFER,fbo);}
""" + fn(d3d,'bind_targets')
fault_checks = r"""
static void failure_checks(void){
 unsigned char input[32*32*4],after[sizeof(input)];memset(input,77,sizeof(input));
 GLuint texture=texture_new(GL_RGBA8,32,32,GL_RGBA,input),fbo=framebuffer_new(texture);GLint corners[4]={0,0,32,32};
 for(int which=0;which<2;which++){
  post.failed[0]=FALSE;if(which)fail_texture=1;else fail_fbo=1;
  assert(!xgpu_post_anti_alias(FALSE,fbo,80+which,80+which,corners));assert(post.failed[0]);
  int uploads=texture_uploads;assert(!xgpu_post_anti_alias(FALSE,fbo,80+which,80+which,corners));assert(texture_uploads==uploads);
  glBindFramebuffer(GL_FRAMEBUFFER,fbo);glReadPixels(0,0,32,32,GL_RGBA,GL_UNSIGNED_BYTE,after);assert(!memcmp(input,after,sizeof(input)));assert(glGetError()==GL_NO_ERROR);
 }
 // A failed optional multisample attachment pair must recover in the same
 // bind, using both single-sample attachments and no poisoned FBO cache.
 D3DSurface color={0},depth={1};device.render_target=&color;device.depth_stencil=&depth;
 for(int which=0;which<2;which++){
  multisampling_failed=FALSE;memset(&test_color,0,sizeof(test_color));memset(&test_depth,0,sizeof(test_depth));
  for(int d=0;d<2;d++){
   struct render_target_entry *entry=d?&test_depth:&test_color;entry->screen_buffer=TRUE;
   entry->target.depth=d;entry->target.gl_width=entry->target.gl_height=32;entry->target.scale[0]=entry->target.scale[1]=1;
   glGenTextures(1,&entry->target.texture);glBindTexture(GL_TEXTURE_2D,entry->target.texture);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAX_LEVEL,0);
   glTexImage2D(GL_TEXTURE_2D,0,d?GL_DEPTH24_STENCIL8:GL_RGBA8,32,32,0,d?GL_DEPTH_STENCIL:GL_RGBA,d?GL_UNSIGNED_INT_24_8:GL_UNSIGNED_BYTE,NULL);
  }
  if(which)fail_pair=1;else fail_storage=1;
  BOOL has_depth=FALSE;assert(bind_targets(&has_depth));assert(has_depth&&target_samples==1&&multisampling_failed);
  assert(!test_color.target.unresolved&&!test_depth.target.unresolved);
  assert(!test_color.target.samples&&!test_depth.target.samples);
  assert(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE&&glGetError()==GL_NO_ERROR);
  GLuint buffer=test_color.target.multisample;assert(bind_targets(&has_depth));assert(test_color.target.multisample==buffer);
 }
 puts("PASS: rejected FXAA texture/FBO leaves source untouched and stops retry; rejected MSAA storage/pair falls back to complete single-sample targets");
}
"""
checks=checks.replace('multisample_checks();return 0;', 'multisample_checks();failure_checks();return 0;')
main=OUT/'graphics.c';main.write_text(support+fault_support+post.replace('#include "xgpu.h"','#include "shim.h"')+msaa+bind_support+fault_checks+shader_data+checks)
exe=OUT/'graphics'
subprocess.run(['clang','-std=gnu11','-O1','-DHALO_ANDROID','-D__GBM__','-I',str(headers),'-I',str(OUT),str(main),str(OUT/'xgpu_text.c'),str(OUT/'nv2a_vsh.c'),str(OUT/'nv2a_psh.c'),str(OUT/'baseline_nv2a_vsh.c'),str(OUT/'baseline_nv2a_psh.c'),'-Wl,-l:libEGL.so.1','-Wl,-l:libGL.so.1','-lm','-o',str(exe)],check=True)
for version in ('300 es','310 es'):
    subprocess.run([str(exe),version],env={**os.environ,'LIBGL_ALWAYS_SOFTWARE':'1'},check=True)

# Real shadow config/commit functions with deterministic config/window doubles.
shadow_shim=r"""
#include <assert.h>
#include <stdio.h>
#include <limits.h>
#define HALO_ANDROID 1
#define SCREEN_HEIGHT 480
#define SHADOW_MAP_SIZE 128
#define SHADOW_MAP_MAXIMUM_SCALE 8
static long resolution=128,shadow_scale,screen_width=640;
static unsigned long generation,shadow_scale_read_at;
static float screen_scale[2]={1,1};
static long config_integer(const char *k){(void)k;return resolution;}
static unsigned long config_changes(void){return generation;}
static void platform_log(const char *f,...){(void)f;}
static void anti_aliasing_read(void){}
static long halo_screen_width(void){return 640;}
static void screen_mode_choose(long *w,float s[2]){*w=640;s[0]=s[1]=1;}
"""
shadow_checks=r"""
int main(void){
 assert(halo_shadow_map_scale()==1);
 const long values[]={LONG_MIN,-1,0,127,128,255,256,511,512,1023,1024,LONG_MAX};
 const long expected[]={1,1,1,1,1,1,2,2,4,4,8,8};
 for(int i=0;i<12;i++){long old=halo_shadow_map_scale();resolution=values[i];generation++;
  assert(halo_shadow_map_scale()==old);halo_screen_commit();assert(halo_shadow_map_scale()==expected[i]);}
 puts("PASS: shadow power-of-two 128..1024 selection, invalid/range limits, frame-boundary-only acceptance");
}
"""
shadow_c=OUT/'shadow.c';shadow_exe=OUT/'shadow'
shadow_c.write_text(shadow_shim+''.join(fn(d3d,n) for n in ('shadow_scale_choose','halo_shadow_map_scale','halo_screen_commit'))+shadow_checks)
subprocess.run(['clang','-O1','-fsanitize=address,undefined',str(shadow_c),'-o',str(shadow_exe)],check=True)
subprocess.run([str(shadow_exe)],check=True)
shadow=(ROOT/'source/rasterizer/xbox/rasterizer_xbox_shadows.c').read_text()
assert 'vertex_constants[distance][3] /= (real)scale' in fn(shadow,'rasterizer_shadow_convolve')
assert 'distance *= 2' in fn(shadow,'rasterizer_shadow_convolve')
assert 'rasterizer_shadow_convolve_pass(3, 2,' in shadow and 'rasterizer_shadow_convolve_pass(2, 3,' in shadow
for scale in (1,2,4,8):
    kernel={-1:.25,0:.5,1:.25}
    distance=1
    while distance<scale:
        for _ in range(2):
            grown={}
            for x,value in kernel.items():
                for dx in (-distance,distance):grown[x+dx]=grown.get(x+dx,0)+value*.5
            kernel=grown
        distance*=2
    expected={x:(2*scale-abs(x))/(4*scale*scale) for x in range(-2*scale+1,2*scale)}
    assert kernel==expected and sum(kernel.values())==1
print('PASS: shadow blur passes preserve normalized tent width at 128/256/512/1024')
