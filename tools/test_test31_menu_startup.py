"""Real XML -> game menu-tag startup on ILP32 with production debug allocation.

Requires clang, libc6-dev-i386 and gcc-multilib on Ubuntu. WSL1 also needs
qemu-user; its missing MAP_FIXED_NOREPLACE is handled only in the child QEMU
process by the tested non-replacing hint shim below. No app toolchain changes.
Uses the production parser, tag builder, layout headers, debug-memory/CRC
functions, and cseries allocation macros. Only map/renderer/OS boundaries are
fixtures; no game assets, GPU, device, package or app build are used.
"""
from pathlib import Path
import importlib.util
import errno
import json
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/test31-menu-startup'
OUT.mkdir(parents=True, exist_ok=True)


def read(path):
    return (ROOT/path).read_text()


def function(text, name):
    m = re.search(r'^(?:static )?[\w *]+\b' + name + r'\s*\([^;{}]*\)\s*\{', text, re.M)
    assert m, name
    end, depth = m.end(), 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[m.start():end] + '\n'


def structure(text, name):
    start = text.index('struct ' + name + '\n{')
    return text[start:text.index('\n};', start)+3]+'\n'


spec = importlib.util.spec_from_file_location('embed_assets', ROOT/'tools/embed_assets.py')
embed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(embed)
xml_names = [n for n in embed.menu_files() if n.endswith('.xml')]
assert len(xml_names) >= 50
parser = read('port/linux/src/menu_files.c').split('/* ---------- art */', 1)[0]
for header in ('hud_hires.h', 'platform.h', 'port_config.h', 'xgpu.h'):
    parser = parser.replace('#include "' + header + '"', '')
parser = parser.replace('#include <SDL3/SDL.h>', '')
parser_prefix = r'''
#include <stddef.h>
void platform_log(const char *format,...);
void config_folder(char *out,unsigned long size);
'''
arrays, rows = [], []
for i, name in enumerate(xml_names):
    contents = (ROOT/'port/assets/menus'/name).read_bytes()
    arrays.append(f'static const unsigned int xml{i}[] = {{\n'+ '\n'.join(embed.words(contents))+'\n};')
    rows.append('{'+json.dumps(name)+f',xml{i},{len(contents)}'+'},')
parser += '\n'+'\n'.join(arrays)+'\nconst struct menu_file_embedded menu_files_embedded[]={\n'+'\n'.join(rows)+'\n};\n'
parser += f'const unsigned int menu_files_embedded_count={len(rows)};\n'
(OUT/'parser.c').write_text(parser_prefix+parser)

# The stock lookup fixture contains only public XML reference names and frame
# counts. It does not contain maps, original bitmap pixels or extracted tags.
stock = {}
groups = {'font':'font', 'sound':'snd!', 'map':'bitm', 'bitmap':'bitm',
          'header_bitmap':'bitm', 'footer_bitmap':'bitm', 'string_list':'ustr',
          'widget':'DeLa', 'open':'DeLa', 'replace':'DeLa', 'focus':'DeLa',
          'otherwise':'DeLa', 'description':'DeLa'}
for name in xml_names:
    for element in ET.parse(ROOT/'port/assets/menus'/name).getroot().iter():
        for key, value in element.attrib.items():
            if key in groups and '\\' in value:
                group = groups[key]
                stock[(group,value)] = max(stock.get((group,value),1),int(element.get('index','0'))+1 if key=='map' else 1)
for font in ('ui\\large_ui','ui\\small_ui','ui\\interstate'):
    stock[('font',font)] = 1
stock[('DeLa','ui\\shell\\main_menu\\main_menu')] = 1
stock_rows = '\n'.join('{'+repr(group)+','+json.dumps(name)+f',{frames}'+'},' for (group,name),frames in sorted(stock.items()))
events = read('source/interface/ui_widget_event_handler_functions.c').split('event_handler_function_list =',1)[1].split('\n};',1)[0]
event_names = re.findall(r'"([^"\n]+)"',events)
assert len(event_names)==102
event_rows = ',\n'.join(json.dumps(n) for n in event_names)

memory = read('source/cseries/debug_memory.c')
crc = read('source/memory/crc.c')
constants = memory[memory.index('enum\n{'):memory.index('\n};',memory.index('enum\n{'))+3]
allocator = '#include "cseries.h"\n#include "memory/crc.h"\n'
allocator += 'void *system_malloc(long);void *system_realloc(void*,long);void system_free(void*);static word local_random(void){return 42;}\n'
allocator += constants+'\n'+structure(memory,'debug_memory_globals')+structure(memory,'debug_memory_header')
allocator += 'typedef char allocator_header_size[sizeof(struct debug_memory_header)==0x20?1:-1];\n'
allocator += 'typedef char allocator_crc_offset[offsetof(struct debug_memory_header,checksum)==0x1c?1:-1];\n'
allocator += 'static struct debug_memory_globals debug_memory_globals;\n'+structure(crc,'crc_globals')+'static struct crc_globals crc_globals;\n'
for name in ('crc_new','build_crc_table','crc_checksum_buffer'):
    allocator += function(crc,name)
for name in ('debug_memory_manager_initialize','debug_check_memory_globals','debug_memory_header_checksum',
             'debug_check_pointer_header','debug_check_pointer_overrun','debug_memory_add_pointer',
             'debug_memory_remove_pointer','debug_memory_fill_with_random','debug_malloc',
             'debug_free','debug_realloc','debug_check_memory'):
    allocator += function(memory,name)
allocator += 'long test_heap_bytes(void){return debug_memory_globals.current_heap_size;}\n'
allocator += 'long test_heap_blocks(void){long n=0;struct debug_memory_header *p=debug_memory_globals.first_pointer;for(;p;p=p->next)n++;return n;}\n'
(OUT/'allocator.c').write_text(allocator)

harness = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stddef.h>
static long fail_after=-1, allocations;
static int tracing=1,site_count;
static struct {void *a,*b;long first,last;} sites[128];
static void record_allocation(void *a,void *b){int i;if(!tracing)return;for(i=0;i<site_count;i++)if(sites[i].a==a&&sites[i].b==b)break;if(i==site_count){if(site_count==128)exit(91);sites[i].a=a;sites[i].b=b;sites[i].first=allocations;site_count++;}sites[i].last=allocations;}
void *system_malloc(long n){allocations++;record_allocation(__builtin_return_address(1),__builtin_return_address(2));if(fail_after==0)return NULL;if(fail_after>0)fail_after--;return malloc(n);}
void *system_realloc(void *p,long n){allocations++;record_allocation(__builtin_return_address(1),__builtin_return_address(2));if(fail_after==0)return NULL;if(fail_after>0)fail_after--;return realloc(p,n);}
void system_free(void *p){free(p);}
void *csmemcpy(void *a,const void *b,unsigned long n){return memcpy(a,b,n);}
void *csmemset(void *a,long c,unsigned long n){return memset(a,(int)c,n);}
char *csstrcpy(char *a,const char *b){return strcpy(a,b);}
char *csstrcat(char *a,const char *b){return strcat(a,b);}
long csstrcmp(const char *a,const char *b){return strcmp(a,b);}
long csstrncmp(const char *a,const char *b,unsigned long n){return strncmp(a,b,n);}
char *csstrncpy(char *a,const char *b,unsigned long n){return strncpy(a,b,n);}
unsigned long csstrlen(const char *a){return strlen(a);}
char *_strdup(const char *s){size_t n=strlen(s)+1;char *p=malloc(n);if(p)memcpy(p,s,n);return p;}
char *csprintf(char *out,char *format,...){va_list a;va_start(a,format);vsprintf(out,format,a);va_end(a);return out;}
char temporary[256];
void system_exit(long code){exit((int)code);}
void display_assert(char *text,char *file,long line,unsigned char fatal){fprintf(stderr,"ASSERT %s:%ld: %s\n",file,line,text?text:"");exit(90);}
void release_assert_failed(const char *text,const char *file,long line,unsigned char fatal){fprintf(stderr,"ASSERT %s:%ld: %s\n",file,line,text?text:"");exit(90);}
#include "MENU_TAGS_SOURCE"
typedef char test_long32[sizeof(long)==4?1:-1];
typedef char test_pointer32[sizeof(void*)==4?1:-1];
typedef char test_wchar16[sizeof(wchar_t)==2?1:-1];
long test_heap_bytes(void);long test_heap_blocks(void);
void debug_memory_manager_initialize(void);
static char const *const stock_event_names[]={EVENT_ROWS};
static struct {long group;char const *name;int frames;} const stock_description[]={STOCK_ROWS};
static struct cache_file_tag_instance stock_instances[512];
static struct bitmap_group stock_bitmaps[512];
static struct bitmap_data stock_frames[512][32];
static struct ui_widget_definition stock_widgets[512];
static struct cache_file_tag_instance *current;
static long current_count,original_count,bitmap_count,logs,errors;
static int missing_font,mp_mode;
static struct tag_block pause_collection;
static struct tag_reference pause_screens[1];
static struct ui_widget_child_reference pause_screen_children[1],pause_children[1];
static struct ui_widget_event_handler_reference pause_quit_events[1];
static struct ui_widget_definition *pause_list;
static char const *override_folder;
void platform_log(char const *format,...){va_list a;logs++;va_start(a,format);vprintf(format,a);putchar('\n');va_end(a);}
void config_folder(char *out,unsigned long size){snprintf(out,size,"%s/",override_folder);}
char const *config_string(char const *key){return !strcmp(key,"display.menus")?"pc":"";}
int platform_display_resolutions(long *widths,long *heights,int n){return 0;}
int platform_window_sizes(long *widths,long *heights,int n){return 0;}
void *global_network_game_server_get(void){return mp_mode==2?(void*)1:NULL;}
boolean pc_menu_profile_edit_begin(void){return TRUE;}
void *cache_files_tag_instances(long *count){*count=current_count;return current;}
void cache_files_set_tag_instances(void *p,long n){current=p;current_count=n;}
char *tag_get_name(long index){long i=DATUM_INDEX_TO_ABSOLUTE_INDEX(index);assert(i>=0&&i<current_count);return current[i].name;}
long tag_loaded(long group,const char *name){long i;if(missing_font&&group=='font')return NONE;for(i=0;i<current_count;i++)if(current[i].group_tag==group&&!strcmp(current[i].name,name))return current[i].tag_index;return NONE;}
void *tag_get(long group,long index){long i=DATUM_INDEX_TO_ABSOLUTE_INDEX(index);assert(i>=0&&i<current_count&&current[i].group_tag==group);return current[i].base_address;}
char const *ui_widget_event_handler_function_name(long index){return index>=0&&index<102?stock_event_names[index]:NULL;}
boolean rasterizer_bitmap_new(struct bitmap_data *bitmap){bitmap_count++;bitmap->hardware_format=(void*)1;return TRUE;}
void rasterizer_bitmap_delete(struct bitmap_data *bitmap){assert(bitmap->hardware_format);bitmap->hardware_format=NULL;bitmap_count--;}
void halo_menus_art_register(void const *texture,char const *png){assert(texture&&png);}
void halo_menus_art_forget(void){}
static void fixture(void){long i,j;assert(NUMBEROF(stock_description)<512);for(i=0;i<NUMBEROF(stock_description);i++){
 stock_instances[i].group_tag=stock_description[i].group;stock_instances[i].tag_index=(1L<<16)|i;
 stock_instances[i].parent_group_tags[0]=stock_instances[i].parent_group_tags[1]=NONE;
 stock_instances[i].name=(char*)stock_description[i].name;
 if(stock_description[i].group=='bitm'){
  assert(stock_description[i].frames<=32);stock_bitmaps[i].bitmaps.count=stock_description[i].frames;
  stock_bitmaps[i].bitmaps.address=stock_frames[i];stock_instances[i].base_address=&stock_bitmaps[i];
  for(j=0;j<stock_description[i].frames;j++){stock_frames[i][j].width=stock_frames[i][j].height=64;stock_frames[i][j].depth=1;}
 }else if(stock_description[i].group=='DeLa')stock_instances[i].base_address=&stock_widgets[i];
 }
 current=stock_instances;current_count=original_count=NUMBEROF(stock_description);
 if(mp_mode){
  long base=original_count,k;static char *names[]={"ui\\shell\\multiplayer","ui\\shell\\multiplayer\\pause","ui\\shell\\multiplayer\\pause_list","ui\\shell\\multiplayer\\quit"};
  for(k=0;k<4;k++){stock_instances[base+k].group_tag=k?'DeLa':'Soul';stock_instances[base+k].tag_index=(1L<<16)|(base+k);stock_instances[base+k].name=names[k];stock_instances[base+k].base_address=k?(void*)&stock_widgets[base+k]:(void*)&pause_collection;memset(&stock_widgets[base+k],0,sizeof(stock_widgets[base+k]));}
  pause_collection.count=1;pause_collection.address=pause_screens;pause_screens[0].index=(1L<<16)|(base+1);
  stock_widgets[base+1].child_widgets.count=1;stock_widgets[base+1].child_widgets.address=pause_screen_children;
  pause_screen_children[0].widget_tag.index=(1L<<16)|(base+2);pause_screen_children[0].vertical_offset=73;
  pause_list=&stock_widgets[base+2];pause_list->type=3;pause_list->bounds.y1=200;
  pause_list->child_widgets.count=1;pause_list->child_widgets.address=pause_children;
  pause_children[0].widget_tag.index=(1L<<16)|(base+3);pause_children[0].vertical_offset=35;
  stock_widgets[base+3].event_handlers.count=1;stock_widgets[base+3].event_handlers.address=pause_quit_events;
  pause_quit_events[0].function=ui_function_named("mp game player quit");pause_quit_events[0].flags=FLAG(_event_handler_run_function_bit);
  current_count=original_count+=4;
 }
}
int main(int argc,char **argv){
 int cycle,expect_fail=argc>2?atoi(argv[2]):0;
 assert(argc>=2);override_folder=argv[1];missing_font=argc>3&&!strcmp(argv[3],"missing-font");
 if(argc>3&&!missing_font)fail_after=atol(argv[3]);
 mp_mode=argc>4?atoi(argv[4]):0;debug_memory_manager_initialize();
 for(cycle=0;cycle<3;cycle++){
  fixture();menu_tags_unloaded();menu_tags_loaded(mp_mode?"bloodgulch":"ui");
  if(expect_fail){assert(!menu_tags.loaded);assert(!strcmp(pc_menus_root_name(),"ui\\shell\\main_menu\\main_menu"));}
  else{assert(menu_tags.loaded);assert(current!=stock_instances&&current_count>original_count);
   if(!mp_mode)assert(!strcmp(pc_menus_root_name(),"pc\\main_menu\\main_menu"));
   if(mp_mode)assert(pause_list->child_widgets.count==(mp_mode==2?3:2));
   assert(menu_tags.setting_count>=35);
  }
  if(expect_fail&&mp_mode){assert(pause_list->child_widgets.address==pause_children&&pause_list->child_widgets.count==1&&pause_list->bounds.y1==200);assert(pause_screen_children[0].vertical_offset==73);}
  menu_tags_unloaded();menu_tags_unloaded();
  assert(current==stock_instances&&current_count==original_count);assert(bitmap_count==0);
  debug_check_memory(__FILE__,__LINE__);assert(test_heap_bytes()==0&&test_heap_blocks()==0);
  if(cycle==0){long s;for(s=0;s<site_count;s++)printf("SITE %ld %ld\n",sites[s].first,sites[s].last);tracing=0;}
  if(argc>3){fail_after=-1;missing_font=0;expect_fail=0;}
 }
 printf("PASS ILP32 real parser/tag builder/allocator: failure=%d, allocations=%ld, repeated map unload/reload clean\n",expect_fail,allocations);
 return 0;
}
'''.replace('MENU_TAGS_SOURCE',str(ROOT/'port/linux/game/menu_tags.c')).replace('EVENT_ROWS',event_rows).replace('STOCK_ROWS',stock_rows)
(OUT/'startup.c').write_text(harness)

compiler = shutil.which('clang')
assert compiler, 'clang required'
include = ['-I'+str(ROOT/p) for p in ('port/linux/include','port/include/xdk','source','source/cseries','source/math','port/third_party/expat','port/linux/src')]
common = [compiler,'-m32','-fshort-wchar','-fms-extensions','-fno-strict-aliasing','-fwrapv','-O1','-g','-fno-inline','-fno-omit-frame-pointer','-fno-optimize-sibling-calls','-DHALO_LINUX_PLATFORM_LAYER','-Wno-nonportable-include-path','-Wno-visibility',*include]
game = ['-std=gnu11','-D__STRICT_ANSI__','-DHALO_ANDROID=1','-DHALO_RELEASE=1',
        '-include',str(ROOT/'port/linux/include/halo_linux_prefix.h'),'-Wno-multichar',
        '-Wno-duplicate-decl-specifier','-Wno-incompatible-pointer-types']
objects=[]
for name, flags in [('startup',game),('allocator',game),('parser',['-std=gnu11','-D_GNU_SOURCE','-DHALO_ANDROID=1','-DHAVE_EXPAT_CONFIG_H'])]:
    obj=OUT/(name+'.o');objects.append(obj)
    subprocess.run([*common,*flags,'-c',str(OUT/(name+'.c')),'-o',str(obj)],check=True)
for name in ('xmlparse','xmlrole','xmltok'):
    obj=OUT/(name+'.o');objects.append(obj)
    subprocess.run([*common,'-std=gnu11','-DHAVE_EXPAT_CONFIG_H','-c',str(ROOT/'port/third_party/expat'/(name+'.c')),'-o',str(obj)],check=True)
exe=OUT/'startup'
subprocess.run([compiler,'-m32','-static',*(str(p) for p in objects),'-lm','-o',str(exe)],check=True)

# Guard the WSL1 compatibility helper independently: it must never introduce
# MAP_FIXED or accept a reservation at a different address. Fake mmap results
# exercise every branch without mapping or modifying any real address.
shim = ROOT/'tools/test_support/qemu_wsl_mmap.c'
shim_test = r'''
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/mman.h>
#include <errno.h>
#include <assert.h>
#include <stdio.h>
typedef void *(*mmap_function)(void *, size_t, int, int, int, off64_t);
static int calls, unmaps, first_error, second_error, wanted_flags;
static void *first_result,*second_result;
static void *fake_mmap(void *a,size_t n,int p,int f,int d,off64_t o){
 assert(a==(void*)0x12340000||!a);assert(n==4096&&p==PROT_NONE&&d==-1&&o==0);
 assert(f==(calls?wanted_flags&~MAP_FIXED_NOREPLACE:wanted_flags));
 errno=calls?second_error:first_error;return calls++?second_result:first_result;
}
static int fake_unmap(void *a,size_t n){assert(a==second_result&&n==4096);unmaps++;return 0;}
#define munmap fake_unmap
HELPER
static void check(void *address,int flags,int e1,void *r1,int e2,void *r2,int want_calls,int want_unmaps,void *want,int want_errno){
 void *r;calls=unmaps=0;wanted_flags=flags;first_error=e1;second_error=e2;first_result=r1;second_result=r2;
 r=mmap_noreplace_compat(fake_mmap,address,4096,PROT_NONE,flags,-1,0);
 assert(r==want&&calls==want_calls&&unmaps==want_unmaps);if(want_errno)assert(errno==want_errno);
}
int main(void){void *a=(void*)0x12340000;int f=MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE;
 check(a,f,0,a,0,0,1,0,a,0);
 check(a,f,EINVAL,MAP_FAILED,0,a,2,0,a,0);
 check(a,f,EOPNOTSUPP,MAP_FAILED,0,a,2,0,a,0);
 check(a,f,EINVAL,MAP_FAILED,0,(void*)0x43210000,2,1,MAP_FAILED,EEXIST);
 check(a,f,ENOMEM,MAP_FAILED,0,a,1,0,MAP_FAILED,ENOMEM);
 check(a,f&~MAP_FIXED_NOREPLACE,EINVAL,MAP_FAILED,0,a,1,0,MAP_FAILED,EINVAL);
 check(a,f|MAP_FIXED,EINVAL,MAP_FAILED,0,a,1,0,MAP_FAILED,EINVAL);
 check(NULL,f,EINVAL,MAP_FAILED,0,a,1,0,MAP_FAILED,EINVAL);
 check(a,f,EINVAL,MAP_FAILED,ENOMEM,MAP_FAILED,2,0,MAP_FAILED,ENOMEM);
 puts("PASS QEMU shim: exact-address-only, no replacement, failure guards");return 0;
}
'''.replace('HELPER',function(shim.read_text(),'mmap_noreplace_compat'))
(OUT/'shim_test.c').write_text(shim_test)
subprocess.run([compiler,'-std=gnu11','-Wall','-Wextra','-Werror','-fsanitize=undefined',
                str(OUT/'shim_test.c'),'-o',str(OUT/'shim_test')],check=True)
subprocess.run([str(OUT/'shim_test')],check=True)

prefix=[]
child_env=None
def run_fixture(folder, fail=False, fault=None, mode=0):
    args=[str(exe),str(folder),str(int(fail))]
    if fault is not None or mode:
        args.extend([str(fault if fault is not None else -1),str(mode)])
    result=subprocess.run([*prefix,*args],env=child_env,capture_output=True,text=True,timeout=90)
    assert result.returncode==0,(args,result.returncode,result.stdout,result.stderr)
    assert 'PASS ILP32 real parser/tag builder/allocator' in result.stdout
    return result.stdout

with tempfile.TemporaryDirectory(prefix='test31-startup-',dir=OUT) as folder:
    try:
        first=run_fixture(folder)
    except OSError as error:
        if error.errno!=errno.ENOEXEC:
            raise
        qemu=shutil.which('qemu-i386')
        assert qemu,'Native ILP32 execution unavailable: install qemu-user for this mandatory ABI test'
        prefix=[qemu,'-B','0x10000000000','-R','256M']
        release=Path('/proc/sys/kernel/osrelease').read_text().lower()
        if 'microsoft' in release and 'wsl2' not in release:
            shim_so=OUT/'qemu_wsl_mmap.so'
            subprocess.run([compiler,'-shared','-fPIC','-Wall','-Wextra','-Werror',str(shim),'-ldl','-o',str(shim_so)],check=True)
            child_env=os.environ.copy()
            child_env['LD_PRELOAD']=str(shim_so)
        print('ILP32 execution: QEMU'+(' with scoped WSL1 reservation shim' if child_env else ''),flush=True)
        first=run_fixture(folder)
    failures=0
    for mode in range(3):
        result=first if mode==0 else run_fixture(folder,mode=mode)
        sites=[int(n)-1 for pair in re.findall(r'^SITE (\d+) (\d+)$',result,re.M) for n in pair]
        assert len(sites)>=30
        # First and last allocation at every actual builder callsite/context;
        # this reaches late registry growth and final pause tag-name publication.
        for fault in sorted(set(sites)):
            run_fixture(folder,True,fault,mode)
            failures+=1
        # UI requires its stock fonts; multiplayer maps deliberately permit
        # absent UI references (map_tag), so exercise that accepted branch too.
        run_fixture(folder,mode==0,'missing-font',mode)
        print(f'PASS menu startup mode {mode}: build/unload/reload, {len(set(sites))} allocation faults + missing-font handling',flush=True)

    # The exact release defect parsed successfully but failed widget_build.
    relative='ce/main_menu.settings_select.player_setup.player_profile_edit.network_setup.xml'
    original=(ROOT/'port/assets/menus'/relative).read_text()
    assert 'text="USE LAUNCHER"' in original
    override=Path(folder)/'menus'/relative
    override.parent.mkdir(parents=True)
    override.write_text(original.replace('text="USE LAUNCHER"','strings="USE LAUNCHER"'))
    rejected=run_fixture(folder,True)
    assert 'strings' in rejected and 'spinner' in rejected and "using the game's own menus" in rejected
    override.write_text('<menus><broken')
    rejected=run_fixture(folder,True)
    assert "using the game's own menus" in rejected
    override.unlink()
    run_fixture(folder)
    print(f'PASS {len(xml_names)} actual XML assets: semantic/XML negative controls, {failures} allocation faults, stock rollback and recovery; no device/GPU claim',flush=True)
