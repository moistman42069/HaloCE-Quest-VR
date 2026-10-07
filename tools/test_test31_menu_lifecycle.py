"""Production tag-table lifecycle and config menu API checks; no game launched."""
from pathlib import Path
import os
import re
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/test31-menu-lifecycle'
OUT.mkdir(parents=True, exist_ok=True)

def fn(s, name):
    m = re.search(r'^(?:static )?[\w *]+\b' + name + r'\s*\([^;{}]*\)\s*\{', s, re.M)
    assert m, name
    end, depth = m.end(), 1
    while depth:
        depth += (s[end] == '{') - (s[end] == '}')
        end += 1
    return s[m.start():end] + '\n'

def compile_run(name, text, extra=(), env=None):
    src = OUT / (name + '.c')
    src.write_text(text)
    exe = OUT / name
    subprocess.run(['clang', '-std=gnu11', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                    '-g', '-I', str(ROOT/'port/linux/src'), '-I', str(ROOT/'port/third_party/tomlc17'),
                    str(src), *extra, '-pthread', '-lm', '-o', str(exe)], check=True)
    subprocess.run([str(exe)], env=env, check=True)

cache = (ROOT/'source/cache/cache_files.c').read_text()
menus = (ROOT/'port/linux/game/menu_tags.c').read_text()
unload = fn(cache, 'scenario_tags_unload')
assert unload.index('texture_cache_close();') < unload.index('vr_menu_tags_unloaded();') < unload.index('menu_tags_unloaded();') < unload.index('cache_file_close();')
assert 'global_tag_count = 0;' in unload
assert 'tag_header->tag_count =' not in fn(cache, 'cache_file_add_tag')
assert 'global_tag_count' in fn(cache, 'cache_get_tag_instance')
assert 'global_tag_count' in fn(cache, 'tag_loaded') and 'global_tag_count' in fn(cache, 'tag_iterator_next')
assert 'existing > 0x7FFF - count' in fn(menus, 'instances_grow')
compile_run('tags', r'''
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#define NONE (-1)
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef int boolean;
#define TRUE 1
#define FALSE 0
struct cache_file_tag_instance {long group_tag,parent_group_tags[2],tag_index;char *name;void *base_address;};
static struct {int tags_loaded;} cache_file_globals;
static struct cache_file_tag_instance *global_tag_instances;
static long global_tag_count;
static int fail_alloc;
static void *test_malloc(size_t n) {return fail_alloc?NULL:malloc(n);}
#define malloc test_malloc
''' + ''.join(fn(cache, n) for n in ['cache_files_tag_instances', 'cache_files_set_tag_instances', 'cache_file_add_tag', 'tag_index_is_group']) + r'''
int main(void) {
 struct cache_file_tag_instance original[3]={{0}}, menu[8]={{0}}, next[2]={{0}};
 long count, tag;
 assert(cache_files_tag_instances(&count)==NULL && count==0);
 assert(cache_file_add_tag(1,2,"test",original)==NONE);
 cache_file_globals.tags_loaded=1; cache_files_set_tag_instances(original,3);
 memcpy(menu, original, sizeof(original));cache_files_set_tag_instances(menu,8);
 fail_alloc=1;assert(cache_file_add_tag(1,2,"test",original)==NONE);
 assert(cache_files_tag_instances(&count)==menu && count==8);
 fail_alloc=0;tag=cache_file_add_tag(1,2,"test",original);
 assert((tag&0xffff)==8 && global_tag_count==9);
 assert(tag_index_is_group(tag,1) && tag_index_is_group(tag,2));
 assert(!tag_index_is_group(tag^0x10000,1) && !tag_index_is_group(tag,3));
 for(int i=0;i<300;i++)assert(cache_file_add_tag(1,2,"grow",original)!=NONE);
 assert(global_tag_count==309 && tag_index_is_group(tag,1));
 /* Menu teardown restores its original raw map table before freeing menu
    definitions. A new map must copy only its own tags, not stale VR pages. */
 cache_files_set_tag_instances(original,3);assert(global_tag_count==3);
 cache_file_globals.tags_loaded=0;assert(cache_files_tag_instances(&count)==NULL&&count==0);
 cache_file_globals.tags_loaded=1;cache_files_set_tag_instances(next,2);
 tag=cache_file_add_tag(7,8,"next",next);assert((tag&0xffff)==2&&global_tag_count==3);
 assert(global_tag_instances[0].tag_index==0);
 global_tag_count=0x7fff;assert(cache_file_add_tag(1,2,"full",next)==NONE);
 global_tag_count=-1;assert(cache_file_add_tag(1,2,"invalid",next)==NONE);
 free(global_tag_instances);global_tag_instances=NULL;
 return 0;
}
''')

config = (ROOT/'port/linux/src/port_config.c').read_text().replace('#include "platform.h"', 'static void platform_log(const char *s, ...) {(void)s;}').replace('#include <SDL3/SDL.h>', '')
test = r'''
#include <assert.h>
int main(void) {
 char text[256],path[1024];size_t size;char *file;
 assert(config_default("renderer.safe_geometry",text,sizeof(text)));
#ifdef HALO_VR
 assert(!strcmp(text,"true"));config_vr_vehicle_defaults();
#else
 assert(!strcmp(text,"false"));
#endif
 assert(config_text("display.menus",text,sizeof(text))&&!strcmp(text,"pc"));
 config_path(path,sizeof(path));file=config_file_read(path,&size);assert(file);
 toml_result_t parsed=toml_parse(file,(int)size);assert(parsed.ok);toml_free(parsed);free(file);
 assert(!config_write("missing.key","1"));
 assert(config_write("browser.engine","5")&&config_integer("browser.engine")==5);
 assert(config_write("audio.music_volume","0.375")&&config_real("audio.music_volume")==0.375);
 assert(config_write("browser.show_empty","false")&&!config_boolean("browser.show_empty"));
 assert(config_write("browser.teams","teams")&&!strcmp(config_string("browser.teams"),"teams"));
 assert(!config_write("browser.engine","9999999999999999999999999"));
 assert(!config_write("browser.engine","2junk")&&!config_write("audio.music_volume","nan"));
 assert(!config_write("audio.music_volume","1bad")&&!config_write("browser.show_empty","maybe"));
 assert(config_default("browser.engine",text,sizeof(text))&&!strcmp(text,"-1"));
 assert(config_text("audio.music_volume",text,sizeof(text))&&!strcmp(text,"0.375"));
 file=config_file_read(path,&size);assert(file);parsed=toml_parse(file,(int)size);assert(parsed.ok);toml_free(parsed);free(file);
 return 0;
}
'''
for vr in (False,True):
    with tempfile.TemporaryDirectory(dir=OUT) as folder:
        env=dict(os.environ,HALO_DATA_ROOT=folder)
        compile_run('config-vr' if vr else 'config-flat', '#define HALO_ANDROID 1\n'+('#define HALO_VR 1\n' if vr else '')+config+test,
                    [str(ROOT/'port/third_party/tomlc17/tomlc17.c')], env)
print('PASS: tag append/grow/OOM/map reload/teardown; immutable raw tag count; VR/flat fresh TOML; menu typed round trips/defaults/invalid input')
