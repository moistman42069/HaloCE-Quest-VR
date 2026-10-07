"""Production native VR menu generation/layout/lifetime tests (ASan/UBSan).

The tag registry/font/config are test doubles. The complete production tag
builder, callbacks and allocation lifecycle run on fixtures with and without
OpenCE/solo/MP templates. Guest ABI offsets remain compile-time assertions in C.
"""
from pathlib import Path
import re
import subprocess
ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'port/linux/game/vr_menu.c').read_text()
header = (ROOT / 'port/linux/include/halo_vr.h').read_text()
ui = (ROOT / 'source/interface/ui_widget_game_data_input_functions.c').read_text()
assert 'void vr_menu_tags_unloaded(void);' in header
assert 'focused_child->type == _ui_widget_type_column_list' in ui
assert 'VR_MENU_GAME_DATA_FUNCTION' in ui and 'vr_menu_setting_text(' in ui
assert 'child_widgets.count != 5' not in source
assert 'child_widgets.count != 4' not in source
assert 'static short const hints_x = 328, right_column_x = 328 - 72;' in source
assert 'VR_MENU_BUTTON_WIDTH 250' in source

def struct(name):
    start = source.index('struct ' + name + '\n{')
    return source[start:source.index('\n};',start)+3]+'\n'

shim = r"""
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stddef.h>
#include <math.h>
#include <wchar.h>
typedef int boolean;
typedef unsigned char byte;
typedef unsigned short word;
typedef struct {short y0,x0,y1,x1;} rectangle2d;
typedef struct {float alpha,red,green,blue;} real_argb_color;
struct tag_reference {unsigned long group_tag;char *name;long name_length,index;};
struct tag_block {long count;void *address,*definition;};
#define TRUE 1
#define FALSE 0
#define NONE (-1L)
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define NUMBEROF(a) ((long)(sizeof(a)/sizeof(*(a))))
#define VR_MENU_WIDGET_TAG 0x44654C61
#define VR_MENU_GAME_DATA_FUNCTION 41
#define VR_MENU_NEXT_FUNCTION 102
#define VR_MENU_PREVIOUS_FUNCTION 103
#define VR_MENU_BUTTON_WIDTH 250
#define VR_MENU_SETTINGS_PER_SCREEN 8
#define VR_MENU_PAGES(n) (((n)+7)/8)
#define VR_MENU_PAGE_COUNT NUMBEROF(vr_menu_pages)
static int fail_after=-1;
static void *test_malloc(size_t n){if(fail_after==0)return NULL;if(fail_after>0)--fail_after;return malloc(n);}
#define malloc test_malloc
static struct {unsigned long group;char *name;void *data;} tags[4096];
static long tag_count;
static void *fixture[512];static int fixture_count;
static void *owned(size_t size){void *p=calloc(1,size);assert(p);fixture[fixture_count++]=p;return p;}
static long cache_file_add_tag(unsigned long group,unsigned long parent,char *name,void *data){
 (void)parent;assert(tag_count<4096);tags[tag_count].group=group;tags[tag_count].name=name;tags[tag_count].data=data;return tag_count++;
}
static long tag_loaded(unsigned long group,const char *name){for(long i=0;i<tag_count;i++)if(tags[i].group==group&&!strcmp(tags[i].name,name))return i;return NONE;}
static void *tag_get(unsigned long group,long index){assert(index>=0&&index<tag_count);assert(tags[index].group==group);return tags[index].data;}
static char *tag_get_name(long index){assert(index>=0&&index<tag_count);return tags[index].name;}
static int logs;
static void platform_log(const char *format,...){(void)format;logs++;}
static const char *ui_widget_event_handler_function_name(long i){return i==7?"mp game player quit":"other";}
"""
# Layout/types come from production; pointer/long sizes follow the test host.
structs = ''.join(struct(n) for n in ('vr_menu_event_handler','vr_menu_child','vr_menu_game_data_input','vr_menu_widget'))
constants = source[source.index('#define VR_MENU_CLOSE_CURRENT'):source.index('/* ---------- the settings */')]
settings_enum = source[source.index('enum\n{'):source.index('#define VR_MENU_MAXIMUM_VALUES')]
settings_struct = '#define VR_MENU_MAXIMUM_VALUES 12\n'+struct('vr_menu_setting')
stubs = r"""
static struct vr_menu_setting test_settings[17];
struct vr_menu_page {char const *label;struct vr_menu_setting const *settings;long count;};
static struct vr_menu_page vr_menu_pages[] = {
 {"ONE",test_settings,17},{"TWO",test_settings,9},{"THREE",test_settings,8},
 {"FOUR",test_settings,1},{"FIVE",test_settings,4},{"SIX",test_settings,5},
 {"SEVEN",test_settings,7},{"EIGHT",test_settings,8},{"NINE",test_settings,3}
};
static long vr_menu_value_index(struct vr_menu_setting const *s){(void)s;return 0;}
static int vr_gun_class(void){return 0;}
static char const *vr_gun_class_label(int k){(void)k;return "RIFLE";}
static char const *vr_gun_class_key(int k){(void)k;return "rifle";}
static double config_real(const char *key){(void)key;return 0.0;}
static double vr_menu_hand_angle(const char *key){(void)key;return 0.0;}
"""
start=source.index('struct vr_menu_navigation {')
end=source.index('boolean vr_menu_setting_change(')
builder=source[start:end]
checks=r"""
static struct vr_menu_widget *widget(const char *name,short type,short x,short y,short w,short h,long *tag){
 struct vr_menu_widget *p=owned(sizeof(*p));p->type=type;p->controller_index=4;
 p->bounds=(rectangle2d){y,x,y+h,x+w};p->text_font.index=NONE;p->background_bitmap.index=NONE;
 *tag=cache_file_add_tag(VR_MENU_WIDGET_TAG,NONE,(char*)name,p);return p;
}
static void attach(struct vr_menu_widget *p,long count){p->child_widgets.count=count;p->child_widgets.address=owned(count*sizeof(struct vr_menu_child));}
static void child(struct vr_menu_widget *p,long index,long tag,short x,short y){vr_menu_child_set((struct vr_menu_child*)p->child_widgets.address+index,tag,x,y);}
static long main_tag,settings_tag,solo_tag,solo_list,mp_tag,mp_list;
static void setup(int kind,int font){
 long tag;struct vr_menu_widget *p,*q,*r;
 main_tag=settings_tag=solo_tag=solo_list=mp_tag=mp_list=NONE;
 if(font) cache_file_add_tag('font',NONE,"ui\\small_ui",owned(1));
 if(kind==0||kind==2||kind==3){
  p=widget("pc\\main_menu/main_menu_select_list",3,0,0,640,480,&main_tag);attach(p,5);
  for(long i=0;i<5;i++){widget("main row",1,0,0,256,33,&tag);child(p,i,tag,192,247+36*i);}
  p=widget("pc\\main_menu/settings_select/player_setup/player_profile_edit/profile_edit_select_list",3,0,0,640,480,&settings_tag);attach(p,10);
  for(long i=0;i<9;i++){widget("settings row",1,51,78+33*i,232,32,&tag);child(p,i,tag,0,0);}
  widget("button bar",3,0,0,640,28,&tag);child(p,9,tag,0,414);
 }
 if(kind==1||kind==2){
  p=widget("ui\\shell\\solo_game\\pause_game\\pause_game",0,0,0,640,480,&solo_tag);attach(p,2);
  q=widget("ui\\shell\\solo_game\\pause_game\\pause_list",3,0,0,200,140,&solo_list);attach(q,3);child(p,0,solo_list,72,180);
  for(long i=0;i<3;i++){widget("solo row",1,0,0,200,28,&tag);child(q,i,tag,0,i*28);}
  widget("solo hints",1,0,0,200,28,&tag);child(p,1,tag,72,264);
 }
 if(kind==3||kind==4){
  p=widget("mp pause",0,0,0,640,480,&mp_tag);attach(p,1);
  q=widget("mp pause list",3,0,0,240,84,&mp_list);attach(q,3);child(p,0,mp_list,192,190);
  for(long i=0;i<3;i++){r=widget("mp row",1,0,0,240,28,&tag);child(q,i,tag,0,i*28);if(i==2){
   struct vr_menu_event_handler *e=owned(sizeof(*e));e->flags=VR_MENU_RUN_FUNCTION;e->function=7;
   r->event_handlers.count=1;r->event_handlers.address=e;
  }}
  struct tag_block *b=owned(sizeof(*b));struct tag_reference *refs=owned(2*sizeof(*refs));
  refs[0].index=mp_tag;refs[1].index=mp_tag;b->address=refs;b->count=2;
  cache_file_add_tag('Soul',NONE,"ui\\shell\\multiplayer",b);
 }
}
static void teardown(void){
 vr_menu_tags_unloaded();vr_menu_tags_unloaded();assert(!vr_menu.loaded&&!vr_menu.allocations&&!vr_menu.allocation_count);
 for(int i=0;i<fixture_count;i++)free(fixture[i]);fixture_count=0;tag_count=0;
}
static void bounds(long tag,long x,long y){
 struct vr_menu_widget *p=vr_menu_widget_get(tag);assert(p);assert(!(p->flags&2));
 assert(x+p->bounds.x0>=0&&y+p->bounds.y0>=0&&x+p->bounds.x1<=640&&y+p->bounds.y1<=480);
 for(long i=0;i<p->child_widgets.count;i++){
  struct vr_menu_child *c=(struct vr_menu_child*)p->child_widgets.address+i;
  bounds(c->widget_tag.index,x+c->horizontal_offset,y+c->vertical_offset);
 }
}
static void verify(void){
 wchar_t text[128];long before=tag_count;
 assert(vr_menu.categories_tag_index!=NONE&&vr_menu.button_tag_index!=NONE);
 vr_menu_tags_loaded();assert(tag_count==before);
 assert(vr_menu_setting_text(vr_menu.button_tag_index,text,128)&&!wcscmp(text,L"VR SETTINGS"));
 assert(vr_menu_setting_text(vr_menu.hints_tag_index,text,128)&&wcsstr(text,L"B: BACK"));
 assert(!vr_menu_is_setting(vr_menu.title_tag_index)&&!vr_menu_is_setting(vr_menu.hints_tag_index));
 bounds(vr_menu.categories_tag_index,0,0);
 for(long page=0;page<VR_MENU_PAGE_COUNT;page++){
  bounds(vr_menu.page_tag_indices[page],0,0);
  for(long i=0;i<vr_menu_pages[page].count;i++){
   long tag=vr_menu.setting_tag_indices[page][i];struct vr_menu_widget *w=vr_menu_widget_get(tag);
   assert(vr_menu_is_setting(tag));assert(w->bounds.x1-w->bounds.x0==250);
   assert(w->text_font.index!=NONE&&w->game_data_inputs.count==1);
   assert(((struct vr_menu_game_data_input*)w->game_data_inputs.address)->function==41);
   struct vr_menu_event_handler *e=w->event_handlers.address;
   assert(w->event_handlers.count==3&&e[0].event_type==0&&e[0].function==102&&e[1].event_type==11&&e[1].function==102&&e[2].event_type==10&&e[2].function==103);
   assert(vr_menu_setting_text(tag,text,128)&&wcsstr(text,L"SETTING"));
  }
 }
 for(long i=0;i<vr_menu.navigation_count;i++){
  struct vr_menu_widget *w=vr_menu_widget_get(vr_menu.navigation[i].tag);
  struct vr_menu_event_handler *e=w->event_handlers.address;
  assert(e->flags==VR_MENU_OPEN_WIDGET&&e->widget_tag.index!=NONE);bounds(e->widget_tag.index,0,0);
  assert(vr_menu_setting_text(vr_menu.navigation[i].tag,text,128)&&wcsstr(text,L"NEXT PAGE"));
 }
 if(main_tag!=NONE){
  struct vr_menu_widget *w=vr_menu_widget_get(main_tag);assert(w->child_widgets.count==6);
  struct vr_menu_child *c=w->child_widgets.address;assert(c[5].vertical_offset+28<=446);
  for(int i=0;i<5;i++)assert(c[i].vertical_offset+33<c[i+1].vertical_offset);
  assert(vr_menu_main(main_tag));assert(w->child_widgets.count==6);
 }
 if(settings_tag!=NONE){
  struct vr_menu_widget *w=vr_menu_widget_get(settings_tag);assert(w->child_widgets.count==11);
  struct vr_menu_child *c=w->child_widgets.address;assert(c[9].vertical_offset==377&&c[10].vertical_offset==414);
  struct vr_menu_widget *row=vr_menu_widget_get(c[9].widget_tag.index);assert(row->type==3&&row->child_widgets.count==1);
  assert(((struct vr_menu_child*)row->child_widgets.address)->widget_tag.index==vr_menu.button_tag_index);
 }
 if(solo_tag!=NONE){
  struct vr_menu_widget *w=vr_menu_widget_get(solo_list);assert(w->child_widgets.count==4);
  assert(vr_menu_pause_list(solo_tag,solo_list));assert(w->child_widgets.count==4);
  struct vr_menu_child *c=vr_menu_widget_get(solo_tag)->child_widgets.address;assert(c[1].horizontal_offset==328);
 }
 if(mp_tag!=NONE){
  struct vr_menu_widget *w=vr_menu_widget_get(mp_list);assert(w->child_widgets.count==(settings_tag==NONE?4:3));
  if(settings_tag==NONE){vr_menu_multiplayer_fallback();assert(w->child_widgets.count==4);}
 }
}
int main(void){
 for(long i=0;i<17;i++){test_settings[i].label="SETTING";test_settings[i].key="vr.fake";test_settings[i].values[0].label="ON";}
 for(int cycle=0;cycle<3;cycle++)for(int kind=0;kind<5;kind++){setup(kind,1);vr_menu_tags_loaded();verify();teardown();}
 setup(0,0);long before=tag_count;vr_menu_tags_loaded();assert(tag_count==before&&vr_menu.categories_tag_index==NONE);teardown();
 /* Failed construction never installs a dead entry into the map's UI. */
 for(int fail=0;fail<120;fail++){
  setup(0,1);fail_after=fail;vr_menu_tags_loaded();fail_after=-1;
  if(vr_menu.button_tag_index==NONE){assert(vr_menu_widget_get(main_tag)->child_widgets.count==5);assert(vr_menu_widget_get(settings_tag)->child_widgets.count==10);}
  teardown();
 }
 assert(logs);puts("PASS: native VR main/settings/solo/MP routes, safe columns/paging, callbacks, reload/idempotence and allocation failures");
}
"""
out=ROOT/'build/test31-vr-menu';out.mkdir(parents=True,exist_ok=True)
cfile=out/'vr_menu.c';exe=out/'vr_menu'
cfile.write_text(shim+structs+constants+settings_enum+settings_struct+stubs+builder+checks)
subprocess.run(['clang','-std=gnu11','-Wno-multichar','-O1','-fsanitize=address,undefined',str(cfile),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
