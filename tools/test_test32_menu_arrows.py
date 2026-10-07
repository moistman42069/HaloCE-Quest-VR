#!/usr/bin/env python3
"""Replay the production native pointer router against every XML value spinner.

Uses actual menu bounds/arrows and unchanged pointer target/focus/event functions;
only renderer/platform endpoints are fixtures. No game, GPU or APK is launched.
"""
from pathlib import Path
import json
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'port/assets/menus/ce'


def rectangle(widget):
    x, y = int(widget.get('left', '0')), int(widget.get('top', '0'))
    return [y, x, y + int(widget.get('height', '0')), x + int(widget.get('width', '0'))]


def main():
    records = []
    for file in sorted(ASSETS.glob('*.xml')):
        for widget in ET.parse(file).getroot().findall('widget'):
            if widget.get('type') != 'spinner' or len(widget.findall('child')) > 1:
                continue
            arrows = [list(map(int, widget.get(key, '0 0 0 0').split()))
                      for key in ('header_bounds', 'footer_bounds')]
            if not any(any(arrow) for arrow in arrows):
                continue
            assert 'left_right_tabs_items' in widget.get('flags', ''), widget.get('name')
            records.append((widget.get('name'), rectangle(widget), arrows))
    assert len(records) >= 100, len(records)

    category = ET.parse(ASSETS/'main_menu.new_select.port.xml').getroot()
    row, spinner = category.findall('widget')
    child = row.find('child')
    assert rectangle(row) == rectangle(spinner) == [0, 0, 28, 256]
    assert int(child.get('x', '0')) == int(child.get('y', '0')) == 0
    assert spinner.get('text_y') == '3'  # old y2 + text_y1: no visual movement
    assert spinner.get('header_bounds') == '9 3 21 9'
    assert spinner.get('footer_bounds') == '9 247 21 253'
    # Both shared uses retain their footprint and two-pixel separation from map rows.
    for name in ('main_menu.multiplayer_type_select.mp_map_select.xml', 'main_menu.solo_level_select.xml'):
        page = ET.parse(ASSETS/name).getroot()
        owners = [w for w in page.findall('widget') if any(c.get('widget') == row.get('name') for c in w.findall('child'))]
        assert len(owners) == 1
        children = owners[0].findall('child')
        assert children[0].get('x') == '82' and children[0].get('y') == '73'
        assert int(children[1].get('y')) - (73 + 28) == 2

    server_menu = ET.parse(ASSETS/'main_menu.multiplayer_type_select.join_game.xml').getroot()
    server_rows = [w for w in server_menu.findall('widget') if '/server_item_' in w.get('name', '') and
                   w.get('name', '').rsplit('/', 1)[-1][12:].isdigit()]
    assert len(server_rows) == 15
    server_list = next(w for w in server_menu.findall('widget') if w.get('name', '').endswith('/join_game_items_list'))
    positions = {c.get('widget', '').rsplit('/', 1)[-1]: (int(c.get('x', '0')), int(c.get('y', '0')))
                 for c in server_list.findall('child')}
    for index in range(1, 16):
        name = f'server_item_{index}'
        row = next(w for w in server_rows if w.get('name', '').endswith('/' + name))
        assert (int(row.get('width')), int(row.get('height'))) == (620, 18)
        assert positions[name] == (10, 85 + index * 17)
        assert {event.get('event') for event in row.findall('on')} >= {'a', 'left_mouse'}
        for child in row.findall('child'):
            definition = next(w for w in server_menu.findall('widget') if w.get('name') == child.get('widget'))
            assert not definition.findall('on'), (name, child.get('widget'))

    ui = (ROOT/'source/interface/ui_widget.c').read_text()
    router = ui[ui.index('#define UI_MOUSE_MAXIMUM_TARGETS'):ui.index('static void widget_instance_render_recursive(', ui.index('#define UI_MOUSE_MAXIMUM_TARGETS'))]
    renderer = ui[ui.index('static void widget_instance_render_recursive(', ui.index('#define UI_MOUSE_MAXIMUM_TARGETS')):]
    assert renderer.index('if (!widget->visible)') < renderer.index('ui_mouse_note_target(widget, definition, offset);')
    prefix = r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define NUMBEROF(a) ((long)(sizeof(a)/sizeof((a)[0])))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define ABS(a) ((a)<0?-(a):(a))
#define FLAG(bit) (1u<<(bit))
#define TEST_FLAG(flags,bit) (((flags)&FLAG(bit))!=0)
#define csmemmove memmove
#define SPINNER_EXTRA_WIDTH 12
#define MAXIMUM_NUMBER_OF_LOCAL_PLAYERS 4
typedef int boolean;
typedef struct {short y0,x0,y1,x1;} rectangle2d;
typedef struct {short x,y;} point2d;
enum {_ui_widget_type_container,_ui_widget_type_text_box,_ui_widget_type_spinner_list,_ui_widget_type_column_list};
enum {_widget_pass_unhandled_events_to_children_bit=0,_widget_dpad_updown_tabs_thru_children_bit=3,
 _widget_dpad_leftright_tabs_thru_children_bit=4,_widget_dpad_updown_tabs_thru_list_items_bit=5,
 _widget_dpad_leftright_tabs_thru_list_items_bit=6};
enum {_gamepad_analog_button_a=1,_gamepad_analog_button_b,_gamepad_analog_button_x,_gamepad_analog_button_y,
 _gamepad_analog_button_black,_gamepad_analog_button_white,_gamepad_binary_button_start,_gamepad_binary_button_back,
 _widget_event_dpad_left,_widget_event_dpad_right,_widget_event_dpad_up,_widget_event_dpad_down};
#define _widget_event_b_button _gamepad_analog_button_b
#define _ui_audio_feedback_cursor 1
struct ui_widget_definition {
 rectangle2d bounds,list_header_bounds,list_footer_bounds;
 struct {long index;}list_header_bitmap,list_footer_bitmap,text_label_string_list;
 struct {int count;}child_widgets,event_handlers;
 unsigned flags;
};
struct widget_instance {
 struct widget_instance *parent,*child,*next,*focused_child;
 int type,disabled,visible,local_player_index;
 long definition_tag_index;
 short horizontal_offset,vertical_offset;
 char name[80];
 struct {struct {void*list_items;short selected_index,number_of_items;}list;}parameters;
};
static struct {int initialization_thread;struct widget_instance*active_widgets[4];}widget_globals;
struct halo_ui_pointer {short x,y,click_x,click_y;int moved,left_clicks,right_clicks,wheel_steps;};
static struct halo_ui_pointer pointer;
static struct ui_widget_definition definitions[12];
static const char *tags[12];
static int posted,post_count,extra_width,stock,keyboard;
static struct ui_widget_definition *ui_widget_definition_get(long id){assert(id>=0&&id<12);return &definitions[id];}
static const char *tag_get_name(long id){return tags[id];}
static int pc_menu_tag(long id){(void)id;return !stock;}
static int vr_menu_is_setting(long id){(void)id;return 0;}
static int spinner_string_list_extra_count(long id){(void)id;return extra_width;}
static int widget_instance_can_receive_events(struct widget_instance*w){for(;w;w=w->parent)if(w->disabled||!w->visible)return 0;return 1;}
static struct widget_instance *widget_instance_get_topmost_parent(struct widget_instance*w){while(w->parent)w=w->parent;return w;}
static void widget_instance_give_focus_directly(struct widget_instance*root,struct widget_instance*w){(void)root;for(;w->parent;w=w->parent)w->parent->focused_child=w;}
static void ui_play_audio_feedback_sound(int sound){assert(sound==1);}
static int progress_bar_is_active(void){return 0;}
static int virtual_keyboard_active(void){return keyboard;}
static int game_engine_showing_postgame(void){return 0;}
static int halo_ui_pointer_update(int active,struct halo_ui_pointer*out){*out=pointer;return active;}
static void virtual_keyboard_pointer(short x,short y,int a,int b){(void)x;(void)y;(void)a;(void)b;}
static void event_manager_post_button(short controller,short button){assert(controller==0);posted=button;post_count++;}
'''
    rows = ',\n'.join('{' + json.dumps(name) + ',{' + ','.join(map(str, bounds)) + '},{{' +
                           ','.join(map(str, arrows[0])) + '},{' + ','.join(map(str, arrows[1])) + '}}}'
                           for name, bounds, arrows in records)
    tests = r'''
struct record {const char*name;rectangle2d bounds,arrows[2];};
static const struct record records[]={RECORDS};
static struct widget_instance root,row,value,neighbor,button;
static point2d origin={82,73};
static void setup(const struct record*r){
 memset(definitions,0,sizeof(definitions));memset(tags,0,sizeof(tags));
 memset(&root,0,sizeof(root));memset(&row,0,sizeof(row));memset(&value,0,sizeof(value));
 memset(&neighbor,0,sizeof(neighbor));memset(&button,0,sizeof(button));memset(&pointer,0,sizeof(pointer));
 ui_mouse_target_count=ui_mouse_press_count=0;ui_mouse_hover_pending=ui_mouse_click_pending=0;
 root.type=_ui_widget_type_column_list;root.visible=1;root.child=&row;
 root.parameters.list.number_of_items=3;
 row.type=_ui_widget_type_container;row.visible=1;row.parent=&root;row.child=&value;row.next=&neighbor;row.definition_tag_index=1;
 strcpy(row.name,"list_item_0_map_kind");
 value.type=_ui_widget_type_spinner_list;value.visible=1;value.parent=&row;value.definition_tag_index=2;
 neighbor.type=_ui_widget_type_container;neighbor.visible=1;neighbor.parent=&root;neighbor.definition_tag_index=3;neighbor.next=&button;
 strcpy(neighbor.name,"list_item_1");
 button.type=_ui_widget_type_text_box;button.visible=1;button.parent=&root;button.definition_tag_index=4;
 strcpy(button.name,"ok");
 definitions[0].flags=FLAG(_widget_dpad_updown_tabs_thru_children_bit);
 definitions[1].bounds=(rectangle2d){0,-24,28,360};definitions[1].flags=FLAG(_widget_pass_unhandled_events_to_children_bit);
 definitions[2].bounds=r->bounds;definitions[2].list_header_bounds=r->arrows[0];definitions[2].list_footer_bounds=r->arrows[1];
 definitions[2].list_header_bitmap.index=definitions[2].list_footer_bitmap.index=1;
 definitions[2].flags=FLAG(_widget_dpad_leftright_tabs_thru_list_items_bit);
 definitions[3].bounds=(rectangle2d){30,0,58,390};definitions[3].event_handlers.count=1;
 definitions[4].bounds=(rectangle2d){341,298,365,426};definitions[4].event_handlers.count=1;
 widget_globals.active_widgets[0]=&root;posted=-1;post_count=0;stock=extra_width=keyboard=0;
 ui_mouse_noting_targets=1;
}
/* Mirror the production renderer's visible guard and pre-order target capture. */
static void note(void){
 ui_mouse_target_count=0;
 if(row.visible)ui_mouse_note_target(&row,&definitions[1],origin);
 if(row.visible&&value.visible)ui_mouse_note_target(&value,&definitions[2],origin);
 if(neighbor.visible)ui_mouse_note_target(&neighbor,&definitions[3],origin);
 if(button.visible)ui_mouse_note_target(&button,&definitions[4],origin);
}
static int click(int x,int y){
 note();memset(&pointer,0,sizeof(pointer));posted=-1;post_count=0;
 pointer.x=pointer.click_x=x;pointer.y=pointer.click_y=y;pointer.moved=pointer.left_clicks=1;
 ui_widgets_process_mouse();assert(post_count<=1);return posted;
}
static void move_pointer(int x,int y){
 note();memset(&pointer,0,sizeof(pointer));posted=-1;post_count=0;
 pointer.x=x;pointer.y=y;pointer.moved=1;
 ui_widgets_process_mouse();assert(post_count==0);
}
static void test_server_row_hover(void){
 setup(&records[0]);
 memset(&root,0,sizeof(root));memset(&row,0,sizeof(row));memset(&neighbor,0,sizeof(neighbor));
 value.visible=button.visible=0;
 root.type=_ui_widget_type_column_list;root.visible=1;root.child=&row;root.parameters.list.number_of_items=2;
 row.type=neighbor.type=_ui_widget_type_container;row.visible=neighbor.visible=1;
 row.parent=neighbor.parent=&root;row.next=&neighbor;row.definition_tag_index=neighbor.definition_tag_index=1;
 strcpy(row.name,"server_item_1");strcpy(neighbor.name,"server_item_2");
 definitions[0].flags=FLAG(_widget_dpad_updown_tabs_thru_children_bit);
 definitions[1].bounds=(rectangle2d){0,0,18,620};definitions[1].event_handlers.count=1;
 definitions[3].bounds=(rectangle2d){18,0,36,620};definitions[3].event_handlers.count=1;
 origin=(point2d){0,0};root.focused_child=&row;root.parameters.list.selected_index=0;
 ui_mouse_target_count=ui_mouse_press_count=0;ui_mouse_hover_pending=ui_mouse_click_pending=0;
 widget_globals.active_widgets[0]=&root;posted=-1;post_count=0;stock=extra_width=keyboard=0;ui_mouse_noting_targets=1;
 move_pointer(100,25);
 assert(root.focused_child==&neighbor&&root.parameters.list.selected_index==1);
 assert(click(100,25)==_gamepad_analog_button_a);
 assert(root.focused_child==&neighbor&&root.parameters.list.selected_index==1);
 move_pointer(100,5);
 assert(root.focused_child==&row&&root.parameters.list.selected_index==0);
 assert(click(100,5)==_gamepad_analog_button_a);

 /* Pointer travel keeps map/profile rows click-to-select. */
 strcpy(row.name,"list_item_1");strcpy(neighbor.name,"list_item_2");
 root.focused_child=&row;root.parameters.list.selected_index=0;
 move_pointer(100,25);
 assert(root.focused_child==&row&&root.parameters.list.selected_index==0);
 assert(click(100,25)==-1);
 assert(root.focused_child==&neighbor&&root.parameters.list.selected_index==1);
 assert(click(100,25)==_gamepad_analog_button_a);
}
static void test_arrows(const struct record*r){
 setup(r);
 for(int arrow=0;arrow<2;arrow++){
  rectangle2d b=r->arrows[arrow];
  /* Every pixel of the real arrow art must route only left/right, never A. */
  for(int y=b.y0;y<b.y1;y++)for(int x=b.x0;x<b.x1;x++){
   int event=click(origin.x+x,origin.y+y);
   assert(event==(arrow?_widget_event_dpad_right:_widget_event_dpad_left));
   assert(root.focused_child==&row&&row.focused_child==&value);
  }
 }
 /* Text midpoint remains unchanged even when the two arrow margins differ. */
 int middle=(r->bounds.x0+r->bounds.x1)/2,y=origin.y+(r->bounds.y0+r->bounds.y1)/2;
 assert(click(origin.x+middle-1,y)==_widget_event_dpad_left);
 assert(click(origin.x+middle,y)==_widget_event_dpad_right);
 /* Gap and neighboring map row never change this value. First map tap selects;
    its second tap activates, exactly as before. OK retains normal A. */
 assert(click(origin.x+100,origin.y+29)==-1);
 root.focused_child=&row;
 assert(click(origin.x+100,origin.y+31)==-1);
 assert(root.focused_child==&neighbor);
 assert(click(origin.x+100,origin.y+31)==_gamepad_analog_button_a);
 assert(click(origin.x+320,origin.y+350)==_gamepad_analog_button_a);
 /* A physically posted A remains A; pointer has no pending repeat. B still backs out. */
 note();memset(&pointer,0,sizeof(pointer));posted=-1;post_count=0;ui_widgets_process_mouse();assert(!post_count);
 event_manager_post_button(0,_gamepad_analog_button_a);assert(posted==_gamepad_analog_button_a);
 note();pointer.right_clicks=1;post_count=0;ui_widgets_process_mouse();assert(posted==_gamepad_analog_button_b&&post_count==1);
}
int main(int argc,char**argv){
 (void)argv;
 for(long i=0;i<NUMBEROF(records);i++)test_arrows(&records[i]);
 test_server_row_hover();
 struct record category={"category",{0,0,28,256},{{9,3,21,9},{9,247,21,253}}};
 setup(&category);definitions[1].bounds=category.bounds;
 for(int y=0;y<28;y++)for(int x=0;x<256;x++)assert(click(origin.x+x,origin.y+y)==(x<128?_widget_event_dpad_left:_widget_event_dpad_right));
 /* No extra target is introduced; arrow hits are the existing value target. */
 note();assert(ui_mouse_target_count==4);
 /* Invisible/disabled values and parents never acquire arrow targets. */
 for(int which=0;which<4;which++){
  setup(&records[0]);if(which==0)value.visible=0;if(which==1)value.disabled=1;if(which==2)row.visible=0;if(which==3)row.disabled=1;
  note();for(long i=0;i<ui_mouse_target_count;i++)assert(ui_mouse_targets[i].widget!=&value);
 }
 /* Overlapping actionable sibling retains normal final-drawn/topmost priority. */
 setup(&records[0]);definitions[4].bounds=records[0].arrows[0];
 rectangle2d arrow=records[0].arrows[0];
 assert(click(origin.x+arrow.x0,origin.y+arrow.y0)==_gamepad_analog_button_a);
 /* Missing arrow art and stock fallback remain their original text bounds. */
 setup(&records[0]);definitions[2].list_header_bitmap.index=NONE;definitions[2].list_footer_bitmap.index=NONE;note();
 assert(!memcmp(&ui_mouse_targets[1].bounds,&(rectangle2d){records[0].bounds.y0+origin.y,records[0].bounds.x0+origin.x,records[0].bounds.y1+origin.y,records[0].bounds.x1+origin.x},sizeof(rectangle2d)));
 setup(&records[0]);stock=1;note();assert(ui_mouse_targets[1].bounds.x0==records[0].bounds.x0+origin.x);
 /* Read-only text is not promoted to a value by decorative arrow metadata. */
 setup(&records[0]);value.type=_ui_widget_type_text_box;note();for(long i=0;i<ui_mouse_target_count;i++)assert(ui_mouse_targets[i].widget!=&value);
 /* Match the renderer's left arrow shift for extended three-digit spinners. */
 setup(&records[0]);extra_width=1;
 assert(click(origin.x+records[0].arrows[0].x0-SPINNER_EXTRA_WIDTH,origin.y+records[0].arrows[0].y0)==_widget_event_dpad_left);
 /* Mutation run: demonstrate old XML plus old target capture cannot hit arrows. */
 if(argc>1){
  struct record old={"old category",{2,9,24,247},{{9,3,21,9},{9,247,21,253}}};
  setup(&old);stock=1;
  if(click(origin.x+5,origin.y+12)!=_widget_event_dpad_left)return 7;
  return 0;
 }
 printf("PASS: %ld XML value spinners, server-row hover selection, map-row click-to-select, all arrow pixels, focus/events and guards\n",NUMBEROF(records));
 return 0;
}
'''.replace('RECORDS', rows)
    with tempfile.TemporaryDirectory(prefix='test32-menu-arrows-') as folder:
        path = Path(folder)
        source = path/'arrows.c'
        source.write_text(prefix + router + tests)
        for edition in ('flat', 'vr'):
            executable = path/edition
            subprocess.run(['clang', '-std=gnu11', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                            '-g', *(['-DHALO_VR'] if edition == 'vr' else []), str(source), '-o', str(executable)], check=True)
            subprocess.run([str(executable)], check=True)
            old = subprocess.run([str(executable), '--old'], capture_output=True, text=True)
            assert old.returncode == 7, (old.returncode, old.stdout, old.stderr)
    print('PASS: legacy arrow-hit negative control fails in flat and VR; actual shared category layouts retain spacing')


if __name__ == '__main__':
    main()
