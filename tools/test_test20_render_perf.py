"""Test20: Safe transient uploads and [render-perf] diagnostics; no GPU/device.

1.0.1 sent every Safe-mode stream/index upload through glBufferSubData into a
16 MB ring buffer still read by queued draws. Quest logs showed 44-248 ms game
frames against 2-13 ms in test18. These checks execute the production upload,
reserve and diagnostic functions with recording GL stubs.
Run under Linux/WSL with clang.
"""
from pathlib import Path
import re, subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/test20-render-perf'; OUT.mkdir(parents=True,exist_ok=True)

def fn(text,name):
    start=text.index(name); start=text.rfind('\n',0,start)+1
    body=text.index('{',start); depth=1; end=body+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}'); end+=1
    return text[start:end]+'\n'

def run(name,text):
    p=OUT/(name+'.c'); p.write_text(text)
    subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined',
                    str(p),'-lm','-o',str(OUT/name)],check=True)
    subprocess.run([str(OUT/name)],check=True)

gl=(ROOT/'port/linux/src/d3d8_gl.c').read_text(encoding='utf-8')

# Static guard: no Android branch of a transient upload may call glBufferSubData.
for name in ('static unsigned long stream_upload(','static unsigned long index_upload('):
    body=re.sub(r'/\*.*?\*/','',fn(gl,name),flags=re.S); android=body[body.index('#ifdef HALO_ANDROID'):body.index('#else')]
    assert 'glBufferSubData' not in android, name
    assert 'host_gl_buffer_write(' in android, name
assert 'safe streaming (fenced ring); CPU index rebasing' in gl

common=r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#define HALO_ANDROID 1
#define BOOL int
#define TRUE 1
#define FALSE 0
#define GL_ARRAY_BUFFER 1
#define GL_ELEMENT_ARRAY_BUFFER 2
#define GL_STREAM_DRAW 3
#define STREAM_BUFFER_SIZE (64 * 1024)
#define INDEX_BUFFER_SIZE (8 * 1024)
typedef long GLintptr; typedef long GLsizeiptr;
static struct {unsigned long stream_offset,index_offset;int stream_buffer,index_buffer,stream_persistent,index_persistent;} device;
static int safe_geometry=1;
static void platform_log(const char *f,...);
'''

perf=fn(gl,'static unsigned long long perf_now_ns(')
perf_block=gl[gl.index('#define UPLOAD_TIMING_SAMPLE'):gl.index('static unsigned long long perf_now_ns(')]

run('ring',common+r'''
/* generation of each buffer's storage: glBufferData orphans start a new one */
static int generation[3];
typedef struct {int target,generation;unsigned long start,end;} range;
static range written[100000];static int written_count;
static unsigned long long fake_ns;
static int logs;
static void platform_log(const char *f,...){(void)f;logs++;}
static void state_array_buffer(int b){(void)b;}
static void state_element_array_buffer(int b){(void)b;}
static void glFinish(void){assert(!"glFinish in non-persistent Safe mode");}
static void glBufferData(int target,int size,void*d,int u){(void)size;(void)d;(void)u;generation[target]++;}
static void glBufferSubData(int t,GLintptr o,GLsizeiptr n,const void*d){(void)t;(void)o;(void)n;(void)d;assert(!"glBufferSubData on Android ring");}
static int host_gl_buffer_write_persistent(int b,unsigned o,unsigned n,const void*d){(void)b;(void)o;(void)n;(void)d;assert(!"persistent in Safe");return 0;}
static void host_gl_buffer_write(int target,unsigned offset,unsigned size,const void*d){
 unsigned long limit=target==GL_ARRAY_BUFFER?STREAM_BUFFER_SIZE:INDEX_BUFFER_SIZE;(void)d;
 assert(offset+size<=limit);
 for(int i=0;i<written_count;i++){range *r=&written[i];
  if(r->target==target&&r->generation==generation[target])assert(offset>=r->end||offset+size<=r->start);}
 written[written_count++]=(range){target,generation[target],offset,offset+size};
}
#include <time.h>
'''+perf_block.replace('#include','//')+r'''
static unsigned long long perf_now_ns(void){return fake_ns+=10;}
'''+fn(gl,'static void upload_perf_add_timed(')+fn(gl,'static void stream_reserve(')+fn(gl,'static unsigned long stream_upload(')+fn(gl,'static unsigned long index_upload(')+r'''
int main(void){
 static unsigned char data[9000];unsigned seed=7;unsigned long uploads=0;
 for(int frame=0;frame<40;frame++){
  /* a frame: monotonic offsets; a fenced ring slot starts empty (present) */
  device.stream_offset=device.index_offset=0;written_count=0;generation[1]++;generation[2]++;
  for(int draw=0;draw<300;draw++){
   seed=seed*1103515245+12345;unsigned long v=1+seed%9000,ix=1+(seed>>8)%700;
   stream_upload(data,v);index_upload(data,ix);uploads+=2;
  }
 }
 assert(upload_perf.uploads==uploads);assert(upload_perf.orphans>0);
 assert(upload_perf.timed_uploads==uploads/UPLOAD_TIMING_SAMPLE);
 printf("PASS: Safe ring writes 24000 disjoint ranges per storage generation across %lu wraps; no glBufferSubData/glFinish (ASAN)\n",upload_perf.orphans);
}
''')

run('report',common+r'''
#include <time.h>
static unsigned long long fake_ns;static char line[1024];static int logs;
static void platform_log(const char *f,...){va_list a;va_start(a,f);vsnprintf(line,sizeof line,f,a);va_end(a);logs++;}
'''+perf_block.replace('#include','//')+r'''
static unsigned long long perf_now_ns(void){return fake_ns;}
'''+fn(gl,'static void upload_perf_add_timed(')+fn(gl,'static void upload_perf_frame(')+r'''
int main(void){
 fake_ns=1000;
 for(int f=0;f<=720;f++){
  if(f)fake_ns+=13888889ULL;
  for(int u=0;u<400;u++){upload_perf.uploads++;upload_perf.upload_bytes+=1024;}
  upload_perf.draws+=200;
  for(int s=0;s<50;s++){unsigned long long t=fake_ns;fake_ns+=2000;upload_perf_add_timed(t);fake_ns-=2000;}
  upload_perf.ring_wait_ns+=100000;if(upload_perf.ring_wait_max_ns<100000)upload_perf.ring_wait_max_ns=100000;
  upload_perf_frame(TRUE);
  if(f<720)assert(logs==0);
 }
 assert(logs==1);
 assert(strstr(line,"[render-perf] 10.0 s, 721 frames, safe geometry"));
 assert(strstr(line,"200 draws, 400 uploads (400 KB)"));
 assert(strstr(line,"uploads about 0.80 ms (sampled 1 in 8"));
 assert(strstr(line,"ring fence wait 0.10 ms average (0.10 longest)"));
 assert(upload_perf.uploads==0&&upload_perf.frames==0&&upload_perf.start_ns==fake_ns);
 puts(line);
 puts("PASS: one [render-perf] line per 10 s window, per-frame averages, sampled upload estimate and reset");
}
''')

# v1.0.1 was withdrawn: v1.0.0 (code 19) is the newest public release. A 1.0.1
# (code 20) or this 1.0.2 (code 21) install must never be offered it.
java=OUT/'PolicyCheck.java'
java.write_text(r'''
package com.halo.decomp;
public class PolicyCheck {
 static void check(boolean b){if(!b)throw new AssertionError();}
 public static void main(String[] a){
  check(!UpdatePolicy.newer("v1.0.0","1.0.2"));check(!UpdatePolicy.newer("v1.0.0","1.0.1"));
  check(!UpdatePolicy.newerCode(19,21));check(!UpdatePolicy.newerCode(19,20));check(!UpdatePolicy.newerCode(21,21));
  check(UpdatePolicy.newer("v1.0.2","1.0.1"));check(UpdatePolicy.newerCode(21,20));
  check("HaloCE-Quest-1.0.2.apk".equals(UpdatePolicy.asset("v1.0.2",true)));
  System.out.println("PASS: withdrawn 1.0.1 and candidate 1.0.2 never offered public 1.0.0 as an update");
 }
}
''')
subprocess.run(['javac','-d',str(OUT),str(ROOT/'port/android/app/src/main/java/com/halo/decomp/UpdatePolicy.java'),str(java)],check=True)
subprocess.run(['java','-cp',str(OUT),'com.halo.decomp.PolicyCheck'],check=True)
