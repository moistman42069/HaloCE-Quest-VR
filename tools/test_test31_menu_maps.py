"""Run the production CE menu adapter against synthetic active-set directories.

No game files are used. Disk enumeration, cache classification and drawing are
test doubles; actual list/index/name/namespace/bounds/refresh code is compiled
with ASan/UBSan. Cache-format parser tests remain a separate suite.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
maps = (ROOT / "port/linux/game/custom_edition_maps.c").read_text()
header = (ROOT / "port/linux/game/custom_edition_maps.h").read_text()
cache = (ROOT / "port/linux/game/custom_edition_cache.c").read_text()
assert '"yelo"' in maps and "cache_files_map_directory()" in maps
assert "CUSTOM_EDITION_INSTALL_MAP_DIRECTORY" not in maps
assert "_scenario_type_solo" in cache[cache.index("boolean custom_edition_cache_campaign("):]
assert "!map_name || !*map_name || !halo_custom_edition_tag_cache()" in cache

shim = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <wchar.h>
typedef int boolean;
typedef unsigned char byte;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define PIN(v,l,h) ((v)<(l)?(l):((v)>(h)?(h):(v)))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define FLAG(n) (1u<<(n))
#define MAXIMUM_FILENAME_LENGTH 255
#define NUMBER_OF_SINGLE_PLAYER_LEVELS 10
#define CUSTOM_EDITION_LEVEL_NAME_PREFIX "custom_maps\\"
#define csstrcasecmp strcasecmp
#define csstrlen strlen
#define csstrcpy strcpy
#define csstrncpy strncpy
#define csmemcpy memcpy
#define csmemset memset
#define csprintf sprintf
#define ustrcpy wcscpy
#define _error_silent 0
#define _name_filename_bit 0
#define _name_extension_bit 1
#define error(...) ((void)0)
struct bitmap_data { void *base_address, *hardware_format; };
struct file_reference { int index; };
struct bmp_file_picture { int unused; };
enum bmp_file_status { _bmp_file_status_ok };
static int enabled=1, scan_count, cursor, freed;
static const char *directory="./menu-test-set-a/";
static const char *cache_files_map_directory(void){return directory;}
static void *halo_custom_edition_tag_cache(void){return enabled?(void*)1:NULL;}
static struct { char name[90]; const char *extension; int kind; } entries[400];
static int entry_count;
static void add(const char *name,const char *ext,int kind){
 assert(entry_count<(int)NUMBEROF(entries));
 snprintf(entries[entry_count].name,sizeof(entries[entry_count].name),"%s",name);
 entries[entry_count].extension=ext; entries[entry_count++].kind=kind;
}
/* This models the real loader's .map-before-.yelo lookup, independent of
directory enumeration order. Kind -1 is unsupported/corrupt, 0 campaign,
1 multiplayer, 2 UI. */
static int kind(const char *name){
 for(int pass=0;pass<2;pass++)for(int i=0;i<entry_count;i++)
  if(!strcasecmp(name,entries[i].name)&&!strcasecmp(entries[i].extension,pass?"yelo":"map"))
   return entries[i].kind;
 return -1;
}
static int custom_edition_cache_campaign(const char *name){return enabled&&kind(name)==0;}
static int custom_edition_cache_multiplayer(const char *name){return enabled&&kind(name)==1;}
static int custom_edition_level_name(const char *name){
 return name&&!strncasecmp(name,CUSTOM_EDITION_LEVEL_NAME_PREFIX,strlen(CUSTOM_EDITION_LEVEL_NAME_PREFIX));
}
static const char *tag_name_strip_path(const char *name){
 const char *last=name;
 for(const char *p=name;*p;p++)if(*p=='\\'||*p=='/')last=p+1;
 return last;
}
static struct file_reference *file_reference_create_from_path(struct file_reference *r,const char *p,int d){
 assert(d && !strcmp(p,directory));r->index=0;return r;
}
static void find_files_start(int flags,struct file_reference *dir){(void)flags;(void)dir;cursor=0;scan_count++;}
static int find_files_next(struct file_reference *r,void *unused){
 (void)unused;if(cursor==entry_count)return 0;r->index=cursor++;return 1;
}
static void file_reference_get_name(struct file_reference *r,int flags,char *out){
 strcpy(out,flags==FLAG(_name_filename_bit)?entries[r->index].name:entries[r->index].extension);
}
static const char *main_get_solo_level_name(short i){
 static const char *names[]={"levels\\a10\\a10","levels\\a30\\a30","levels\\a50\\a50",
 "levels\\b30\\b30","levels\\b40\\b40","levels\\c10\\c10","levels\\c20\\c20",
 "levels\\c40\\c40","levels\\d20\\d20","levels\\d40\\d40"};
 assert(i>=0&&i<10);return names[i];
}
static void bitmap_delete(struct bitmap_data *b){if(b){freed++;free(b);}}
static struct bitmap_data *bitmap_2d_new(int a,int b,int c,int d){(void)a;(void)b;(void)c;(void)d;return NULL;}
static void bitmap_rebuild(struct bitmap_data *b){(void)b;}
static enum bmp_file_status bmp_file_open(void *a,uint32_t b,struct bmp_file_picture *c){(void)a;(void)b;(void)c;return _bmp_file_status_ok;}
static void bmp_file_fit(void *a,struct bmp_file_picture *b,int c,int d,int e,int f,void *g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}
static const char *bmp_file_status_describe(enum bmp_file_status s){(void)s;return "test";}
static char *tag_get_name(long index){(void)index;return "ui\\shell\\bitmaps\\mp_map_grafix";}
static long tag_loaded(long group,const char *name){(void)group;(void)name;return NONE;}
static struct bitmap_data *bitmap_group_get_bitmap_from_sequence(long a,int b,int c){(void)a;(void)b;(void)c;return NULL;}
'''

checks = r'''
int main(void){
 char *stock[]={"levels\\test\\bloodgulch\\bloodgulch","levels\\test\\damnation\\damnation"};
 short total=-1, index, frame;
 add("z_arena","yelo",1); add("a_story","yelo",0); add("icefields","map",1);
 add("a30","map",0); add("bloodgulch","map",1); add("ui","map",2);
 add("broken","map",-1); add("dual","yelo",0); add("dual","map",1);
 char **list=custom_edition_maps_level_list(stock,2,&total);
 assert(total==6&&scan_count==1);
 assert(list[0]==stock[0]&&list[1]==stock[1]);
 assert(!strcmp(list[2],"custom_maps\\bloodgulch"));
 assert(!strcmp(list[3],"custom_maps\\dual"));
 assert(custom_edition_maps_count(0)==4&&custom_edition_maps_count(1)==2);
 assert(custom_edition_maps_display_index(NULL)==NONE&&custom_edition_maps_display_index("")==NONE);
 assert(custom_edition_maps_display_index("levels\\test\\bloodgulch\\bloodgulch")==NONE);
 assert(custom_edition_maps_display_index("bloodgulch")==NONE);
 assert(custom_edition_maps_display_index("custom_maps\\bloodgulch")==0x4000);
 assert(custom_edition_maps_display_index("levels\\a30\\a30")==0x3001);
 assert(custom_edition_maps_display_index("custom_maps\\a30")==0x6000);
 assert(custom_edition_maps_campaign_level(0x3001)==1);
 assert(custom_edition_maps_campaign_level(0x6000)==NONE);
 assert(custom_edition_maps_campaign(0x3001)&&custom_edition_maps_campaign(0x6000));
 assert(!custom_edition_maps_campaign(0x4000)&&!custom_edition_maps_campaign(-1));
 assert(custom_edition_maps_level_campaign("levels\\a30\\a30"));
 assert(custom_edition_maps_level_campaign("custom_maps\\a_story"));
 assert(!custom_edition_maps_level_campaign(NULL));
 assert(!custom_edition_maps_level_campaign("custom_maps\\missing"));
 assert(custom_edition_maps_stock(0x4002));
 assert(!wcscmp(custom_edition_maps_name(0x4002),L"Ice Fields"));
 assert(!wcscmp(custom_edition_maps_name(0x3001),L"Halo"));
 assert(!strcmp(custom_edition_maps_level_name(0x3001),"levels\\a30\\a30"));
 assert(!strcmp(custom_edition_maps_level_name(0x6001),"custom_maps\\a_story"));
 assert(custom_edition_maps_level_name(-1)==NULL&&custom_edition_maps_name(-1)==NULL);
 assert(custom_edition_maps_description(0x6001)!=NULL);
 assert(custom_edition_maps_display_index_of(1,-1)==NONE);
 assert(custom_edition_maps_display_index_of(1,2)==NONE);
 assert(custom_edition_maps_display_index_of(1,1)==0x6001);
 assert(custom_edition_maps_level_display_index(2)==0x4000);
 for(int n=0;n<100;n++)custom_edition_maps_level_list(stock,2,&total);
 assert(scan_count==1); /* no directory or thumbnail churn per menu frame */
 assert(custom_edition_maps_picture(NONE,NULL)==NULL);
 frame=0x6001;assert(custom_edition_maps_picture(1,&frame)==NULL&&frame==13);

 /* A different managed set invalidates both lists and owned thumbnail data. */
 custom_edition_maps_globals.maps[0].picture=calloc(1,sizeof(struct bitmap_data));
 custom_edition_maps_globals.campaigns[0].picture=calloc(1,sizeof(struct bitmap_data));
 entry_count=0;add("new_story","yelo",0);directory="./menu-test-set-b/";
 assert(custom_edition_maps_count(0)==0&&custom_edition_maps_count(1)==1);
 assert(freed==2&&scan_count==2);
 assert(custom_edition_maps_display_index("custom_maps\\a_story")==NONE);
 assert(custom_edition_maps_display_index("custom_maps\\new_story")==0x6000);

 /* Max network level length, unsupported extensions and explicit rescan. */
 entry_count=0;char name[90];memset(name,'a',MAXIMUM_MAP_NAME_LENGTH);name[MAXIMUM_MAP_NAME_LENGTH]=0;
 add(name,"map",1);name[MAXIMUM_MAP_NAME_LENGTH]='a';name[MAXIMUM_MAP_NAME_LENGTH+1]=0;
 add(name,"map",1);add("bad/file","map",1);add("","map",1);add("archive","zip",1);
 custom_edition_maps_look_again();assert(custom_edition_maps_count(0)==1);
 assert(strlen(custom_edition_maps_level_name(0x4000))==63);

 /* Independent bounded lists; no overflow into spinner/stock ranges. */
 entry_count=0;
 for(int n=0;n<130;n++){snprintf(name,sizeof(name),"mp%03d",n);add(name,"map",1);}
 for(int n=0;n<130;n++){snprintf(name,sizeof(name),"sp%03d",n);add(name,"yelo",0);}
 custom_edition_maps_look_again();
 assert(custom_edition_maps_count(0)==128&&custom_edition_maps_count(1)==128);
 assert(custom_edition_maps_display_index_of(0,127)==0x407f);
 assert(custom_edition_maps_display_index_of(1,127)==0x607f);
 assert(custom_edition_maps_display_index_of(0,128)==NONE);
 assert(custom_edition_maps_display_index_of(1,128)==NONE);
 custom_edition_maps_level_list(NULL,-1,NULL);assert(custom_edition_maps_globals.xbox_level_count==0);
 enabled=0;custom_edition_maps_look_again();assert(custom_edition_maps_count(0)==0&&custom_edition_maps_count(1)==0);
 assert(custom_edition_maps_display_index("levels\\a10\\a10")==0x3000);
 assert(custom_edition_maps_display_index("custom_maps\\mp000")==NONE);
 puts("PASS: production CE menu adapter: active sets, stock/CE namespace, campaign classification, .yelo precedence, bounds, display data and cached scanning");
 return 0;
}
'''
out = ROOT / "build/test31-menu-maps"
out.mkdir(parents=True, exist_ok=True)
cfile = out / "menu_maps.c"
cfile.write_text(shim + header + re.sub(r'^#include[^\n]*\n', '', maps, flags=re.M) + checks)
subprocess.run(["clang", "-std=gnu11", "-O1", "-fsanitize=address,undefined",
                "-Wno-multichar", str(cfile), "-o", str(out / "menu_maps")], check=True)
subprocess.run([str(out / "menu_maps")], check=True)
