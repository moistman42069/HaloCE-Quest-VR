#!/usr/bin/env python3
"""Run the complete production TouchControls view through Android event lifecycles.

Android framework classes are deterministic in-memory test doubles; the view,
settings, gesture policy and its event handlers are compiled unchanged. This
checks routing and state transitions, not physical Android rendering or JNI ABI.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'port/android/app/src/main/java/com/halo/decomp'
STUBS = {
'android/util/DisplayMetrics.java': '''package android.util;
public class DisplayMetrics { public float density=1,scaledDensity=1; }''',
'android/content/res/Resources.java': '''package android.content.res;
public class Resources { private final android.util.DisplayMetrics metrics=new android.util.DisplayMetrics();
public android.util.DisplayMetrics getDisplayMetrics(){return metrics;} }''',
'android/content/SharedPreferences.java': '''package android.content;
public interface SharedPreferences { float getFloat(String k,float d);int getInt(String k,int d);boolean getBoolean(String k,boolean d);Editor edit();
interface Editor {Editor putFloat(String k,float v);Editor putInt(String k,int v);Editor putBoolean(String k,boolean v);void apply();} }''',
'android/content/Context.java': '''package android.content;
import java.util.*;
public class Context {
 private final android.content.res.Resources resources=new android.content.res.Resources();
 private final Map<String,SharedPreferences> prefs=new HashMap<>();
 public android.content.res.Resources getResources(){return resources;}
 public SharedPreferences getSharedPreferences(String n,int mode){return prefs.computeIfAbsent(n,k->new MemoryPreferences());}
 private static class MemoryPreferences implements SharedPreferences {
  private final Map<String,Object> values=new HashMap<>();
  public float getFloat(String k,float d){return values.containsKey(k)?(Float)values.get(k):d;}
  public int getInt(String k,int d){return values.containsKey(k)?(Integer)values.get(k):d;}
  public boolean getBoolean(String k,boolean d){return values.containsKey(k)?(Boolean)values.get(k):d;}
  public Editor edit(){return new Editor(){private final Map<String,Object> staged=new HashMap<>();
   public Editor putFloat(String k,float v){staged.put(k,v);return this;}
   public Editor putInt(String k,int v){staged.put(k,v);return this;}
   public Editor putBoolean(String k,boolean v){staged.put(k,v);return this;}
   public void apply(){values.putAll(staged);}};}
 }
}''',
'android/content/DialogInterface.java': '''package android.content;
public interface DialogInterface {void dismiss();interface OnClickListener {void onClick(DialogInterface d,int which);}}''',
'android/graphics/RectF.java': '''package android.graphics;
public class RectF {public float left,top,right,bottom;
public void set(float l,float t,float r,float b){left=l;top=t;right=r;bottom=b;}
public boolean contains(float x,float y){return x>=left&&x<right&&y>=top&&y<bottom;}
public float centerX(){return (left+right)/2;}public float centerY(){return (top+bottom)/2;}}''',
'android/graphics/Color.java': '''package android.graphics;public class Color {public static final int WHITE=-1;}''',
'android/graphics/Paint.java': '''package android.graphics;
public class Paint {public static final int ANTI_ALIAS_FLAG=1;public enum Style{FILL,STROKE}public enum Align{CENTER}
public Paint(int flags){}public void setStyle(Style s){}public void setColor(int c){}public void setAlpha(int a){}
public void setTextSize(float s){}public void setTextAlign(Align a){}public void setStrokeWidth(float s){}
public float ascent(){return -10;}public float descent(){return 2;}}''',
'android/graphics/Canvas.java': '''package android.graphics;
public class Canvas {public final java.util.List<String> labels=new java.util.ArrayList<>();
public void drawRoundRect(RectF r,float x,float y,Paint p){}public void drawCircle(float x,float y,float r,Paint p){}
public void drawRect(RectF r,Paint p){}public void drawText(String s,float x,float y,Paint p){labels.add(s);}}''',
'android/util/SparseArray.java': '''package android.util;
public class SparseArray<T> {private final java.util.TreeMap<Integer,T> values=new java.util.TreeMap<>();
public void clear(){values.clear();}public int size(){return values.size();}public T valueAt(int i){return new java.util.ArrayList<T>(values.values()).get(i);}
public void put(int k,T v){values.put(k,v);}public T get(int k){return values.get(k);}public void remove(int k){values.remove(k);}}''',
'android/view/InputDevice.java': '''package android.view;public class InputDevice {public static final int SOURCE_TOUCHSCREEN=0x1002,SOURCE_MOUSE=0x2002;}''',
'android/view/DisplayCutout.java': '''package android.view;public class DisplayCutout {
public int getSafeInsetLeft(){return 0;}public int getSafeInsetTop(){return 0;}public int getSafeInsetRight(){return 0;}public int getSafeInsetBottom(){return 0;}}''',
'android/view/WindowInsets.java': '''package android.view;public class WindowInsets {public final int l,t,r,b;
public WindowInsets(int l,int t,int r,int b){this.l=l;this.t=t;this.r=r;this.b=b;}
public int getSystemWindowInsetLeft(){return l;}public int getSystemWindowInsetTop(){return t;}public int getSystemWindowInsetRight(){return r;}public int getSystemWindowInsetBottom(){return b;}
public DisplayCutout getDisplayCutout(){return null;}}''',
'android/view/ViewConfiguration.java': '''package android.view;public class ViewConfiguration {
public static ViewConfiguration get(android.content.Context c){return new ViewConfiguration();}public int getScaledTouchSlop(){return 8;}}''',
'android/view/MotionEvent.java': '''package android.view;
public class MotionEvent {
 public static final int ACTION_DOWN=0,ACTION_UP=1,ACTION_MOVE=2,ACTION_CANCEL=3,ACTION_POINTER_DOWN=5,ACTION_POINTER_UP=6;
 private final int action,index,source;private final int[] ids;private final float[] xs,ys;
 private float rawOffsetX,rawOffsetY;
 public MotionEvent(int a,int i,int source,int[] ids,float[] xs,float[] ys){action=a;index=i;this.source=source;this.ids=ids;this.xs=xs;this.ys=ys;}
 public MotionEvent offset(float x,float y){rawOffsetX=x;rawOffsetY=y;return this;}
 public boolean isFromSource(int s){return (source&s)==s;}public int getActionMasked(){return action;}public int getActionIndex(){return index;}
 public int getPointerCount(){return ids.length;}public int getPointerId(int i){return ids[i];}
 public int findPointerIndex(int id){for(int i=0;i<ids.length;i++)if(ids[i]==id)return i;return -1;}
 public float getX(){return getX(0);}public float getY(){return getY(0);}public float getX(int i){return xs[i];}public float getY(int i){return ys[i];}
 public float getRawX(){return getX()+rawOffsetX;}public float getRawY(){return getY()+rawOffsetY;}
}''',
'android/view/View.java': '''package android.view;
public class View {
 public static final int VISIBLE=0,GONE=8;private int visibility=VISIBLE,width,height,left,top;private final android.content.Context context;
 private OnApplyWindowInsetsListener insets;private OnClickListener click;
 public View(android.content.Context c){context=c;}
 public android.content.Context getContext(){return context;}public android.content.res.Resources getResources(){return context.getResources();}
 public int getWidth(){return width;}public int getHeight(){return height;}public void getLocationOnScreen(int[] p){p[0]=left;p[1]=top;}
 public void layout(int l,int t,int r,int b){int oldw=width,oldh=height;left=l;top=t;width=r-l;height=b-t;onSizeChanged(width,height,oldw,oldh);}
 public void setFocusable(boolean b){}public void setContentDescription(String s){}public void setEnabled(boolean b){}
 public void setVisibility(int v){visibility=v;}public int getVisibility(){return visibility;}public void invalidate(){}
 public interface OnApplyWindowInsetsListener {WindowInsets onApplyWindowInsets(View v,WindowInsets i);}
 public void setOnApplyWindowInsetsListener(OnApplyWindowInsetsListener l){insets=l;}
 public void dispatchApplyWindowInsets(WindowInsets i){if(insets!=null)insets.onApplyWindowInsets(this,i);}
 public interface OnClickListener {void onClick(View v);}public void setOnClickListener(OnClickListener l){click=l;}
 public void performClick(){if(click!=null)click.onClick(this);}public void setPadding(int a,int b,int c,int d){}
 protected void onSizeChanged(int w,int h,int ow,int oh){}protected void onDraw(android.graphics.Canvas c){}
 protected void onDetachedFromWindow(){}public boolean onTouchEvent(MotionEvent e){return false;}
}''',
'android/widget/TextView.java': '''package android.widget;
public class TextView extends android.view.View {public String text="";public TextView(android.content.Context c){super(c);}public void setText(String s){text=s;}}''',
'android/widget/Button.java': '''package android.widget;public class Button extends TextView {public Button(android.content.Context c){super(c);}}''',
'android/widget/CheckBox.java': '''package android.widget;public class CheckBox extends Button {
private boolean checked;private OnCheckedChangeListener listener;public CheckBox(android.content.Context c){super(c);}
public interface OnCheckedChangeListener{void onCheckedChanged(CheckBox b,boolean value);}
public void setOnCheckedChangeListener(OnCheckedChangeListener l){listener=l;}
public void setChecked(boolean c){checked=c;if(listener!=null)listener.onCheckedChanged(this,c);}public boolean isChecked(){return checked;}}''',
'android/widget/LinearLayout.java': '''package android.widget;
public class LinearLayout extends android.view.View {public static final int VERTICAL=1;public final java.util.List<android.view.View> children=new java.util.ArrayList<>();
public LinearLayout(android.content.Context c){super(c);}public void setOrientation(int i){}public void addView(android.view.View v){children.add(v);}}''',
'android/widget/ScrollView.java': '''package android.widget;public class ScrollView extends LinearLayout {public ScrollView(android.content.Context c){super(c);}}''',
'android/widget/SeekBar.java': '''package android.widget;public class SeekBar extends android.view.View {
public SeekBar(android.content.Context c){super(c);}public void setMax(int n){}public void setProgress(int n){}
public interface OnSeekBarChangeListener{void onProgressChanged(SeekBar b,int p,boolean u);void onStartTrackingTouch(SeekBar b);void onStopTrackingTouch(SeekBar b);}
public void setOnSeekBarChangeListener(OnSeekBarChangeListener l){}}''',
'android/widget/Toast.java': '''package android.widget;public class Toast {public static final int LENGTH_LONG=1;
public static Toast makeText(android.content.Context c,String s,int n){return new Toast();}public void show(){}}''',
'android/app/AlertDialog.java': '''package android.app;
public class AlertDialog implements android.content.DialogInterface {
 public static AlertDialog last;public android.view.View view;public android.content.DialogInterface.OnClickListener positive,negative;
 public String title;public void show(){last=this;}public void dismiss(){}
 public static class Builder {protected final AlertDialog dialog=new AlertDialog();public Builder(android.content.Context c){}
 public Builder setTitle(String s){dialog.title=s;return this;}public Builder setMessage(String s){return this;}public Builder setView(android.view.View v){dialog.view=v;return this;}
 public Builder setSingleChoiceItems(String[] a,int selected,android.content.DialogInterface.OnClickListener l){return this;}
 public Builder setItems(String[] a,android.content.DialogInterface.OnClickListener l){return this;}
 public Builder setPositiveButton(String s,android.content.DialogInterface.OnClickListener l){dialog.positive=l;return this;}
 public Builder setNegativeButton(String s,android.content.DialogInterface.OnClickListener l){dialog.negative=l;return this;}
 public AlertDialog create(){return dialog;}public AlertDialog show(){dialog.show();return dialog;}}
}''',
'com/halo/decomp/GamepadNavigation.java': '''package com.halo.decomp;final class GamepadNavigation {
static class Builder extends android.app.AlertDialog.Builder {Builder(android.content.Context c){super(c);}}}''',
'com/halo/decomp/GamepadSupport.java': '''package com.halo.decomp;final class GamepadSupport {
static int mode(android.content.Context c){return c.getSharedPreferences("phone-controls",0).getInt("controller_touch_mode",0);}}''',
'com/halo/decomp/GyroAim.java': '''package com.halo.decomp;final class GyroAim {void update(){}static boolean available(android.content.Context c){return true;}}''',
'com/halo/decomp/RunLog.java': '''package com.halo.decomp;final class RunLog {static void line(String s){}}''',
}

CHECK = r'''package com.halo.decomp;
import android.content.*;import android.view.*;import android.graphics.*;import android.widget.*;import android.app.*;import java.lang.reflect.*;
public class TouchLifecycleCheck {
 static int checks;
 static void check(boolean ok,String message){checks++;if(!ok)throw new AssertionError(message);}
 static void near(float a,float b,String message){check(Math.abs(a-b)<.0001f,message+": "+a+" != "+b);}
 static Object field(Object o,String name)throws Exception {Field f=o.getClass().getDeclaredField(name);f.setAccessible(true);return f.get(o);}
 static final class Input implements TouchControls.Input {
  boolean menus;int lx,ly,rx,ry,buttons,pressed,resets,clicks,backs,motions;float yaw,pitch,px,py;
  public boolean menus(){return menus;}
  public void state(int lx,int ly,int rx,int ry,int buttons,boolean reset){this.lx=lx;this.ly=ly;this.rx=rx;this.ry=ry;this.buttons=buttons;
   if(reset){resets++;pressed=0;yaw=pitch=0;}else pressed|=buttons;}
  public void pointer(int a,float x,float y){if(a==1)clicks++;if(a==2)backs++;if(a==0)motions++;px=x;py=y;}
  public void look(float y,float p){yaw+=y;pitch+=p;}
  void clean(){pressed=clicks=backs=motions=0;yaw=pitch=0;}
 }
 static final class Rig {
  final Context context=new Context();final Input input=new Input();final TouchControls view=new TouchControls(context,input);final View surface=new View(context);
  Rig(){view.layout(0,0,1000,500);surface.layout(0,0,1000,500);view.controllerVisibility(GamepadPolicy.AUTO,0);}
  void menu(boolean value){input.menus=value;view.controllerVisibility(GamepadPolicy.AUTO,0);}
  void event(int action,int index,int[] ids,float[] xs,float[] ys){MotionEvent e=new MotionEvent(action,index,InputDevice.SOURCE_TOUCHSCREEN,ids,xs,ys);
   if(!view.dispatchMenuTouch(e,surface)&&view.getVisibility()==View.VISIBLE)view.onTouchEvent(e);}
  void one(int action,float x,float y){event(action,0,new int[]{41},new float[]{x},new float[]{y});}
  void tap(float x,float y){one(MotionEvent.ACTION_DOWN,x,y);one(MotionEvent.ACTION_UP,x,y);}
  void two(int action,int index,float x0,float y0,float x1,float y1){event(action,index,new int[]{41,93},new float[]{x0,x1},new float[]{y0,y1});}
  void button(int n)throws Exception{RectF b=((RectF[])field(view,"menuButtons"))[n];tap(b.centerX(),b.centerY());}
  Canvas draw(){Canvas c=new Canvas();view.onDraw(c);return c;}
  CheckBox option(String prefix){return findCheck(AlertDialog.last.view,prefix);}
 }
 static CheckBox findCheck(View v,String prefix){if(v instanceof CheckBox&&((CheckBox)v).text.startsWith(prefix))return (CheckBox)v;
  if(v instanceof LinearLayout)for(View c:((LinearLayout)v).children){CheckBox found=findCheck(c,prefix);if(found!=null)return found;}return null;}
 static void editor(Rig r){r.tap(32,32);check((Boolean)get(r.view,"editing"),"HUD opens real editor");}
 static Object get(Object o,String n){try{return field(o,n);}catch(Exception e){throw new RuntimeException(e);}}
 static void setAnywhere(Rig r,boolean enabled,boolean save){editor(r);r.tap(375,22);check("Touch options".equals(AlertDialog.last.title),"real Options dialog");
  CheckBox toggle=r.option("Drag anywhere");check(toggle!=null,"visible anywhere toggle");toggle.setChecked(enabled);AlertDialog.last.dismiss();
  r.tap(save?75:225,22);check(!(Boolean)get(r.view,"editing"),"editor closes");}
 static void empty(Rig r,String label){check(r.input.buttons==0&&r.input.lx==0&&r.input.ly==0&&r.input.rx==0&&r.input.ry==0,label);}
 public static void main(String[] args)throws Exception {
  // The menu flag is intentionally backend-independent: both OpenCE and the
  // stock fallback retain navigation even when pointer targets are unavailable.
  for(String backend:new String[]{"OpenCE", "stock fallback"}) {
   Rig r=new Rig();r.menu(true);Canvas c=r.draw();
   check(c.labels.contains("A")&&c.labels.contains("B")&&c.labels.contains("^")&&c.labels.contains("Hide controls"),backend+" visible navigation");
   for(int i=0;i<9;i++){r.input.clean();r.button(i);int[] bits={4096,1024,2048,8192,4,8,2,1,256};check((r.input.pressed&bits[i])!=0,backend+" button "+i);empty(r,"button released");check(r.input.clicks==0,"no duplicate pointer activation");}
   r.input.clean();r.tap(500,200);check(r.input.clicks==1,"direct menu click exactly once");near(r.input.px,.5f,"menu x");near(r.input.py,.4f,"menu y");
   r.tap(950,28);check(r.input.backs==1,"persistent Back");
   r.tap(50,28);check(!r.draw().labels.contains("A")&&r.draw().labels.contains("Show controls"),"tuck away overlapping controls");
   r.tap(50,28);check(r.draw().labels.contains("A"),"recover controls");
   r.one(MotionEvent.ACTION_DOWN,966,470);check(r.input.buttons==1,"hold A");r.one(MotionEvent.ACTION_MOVE,500,200);empty(r,"sliding off cancels button");
   r.one(MotionEvent.ACTION_MOVE,966,470);empty(r,"cancelled button cannot reenter");r.one(MotionEvent.ACTION_UP,966,470);
   r.input.clean();r.one(MotionEvent.ACTION_DOWN,500,200);r.one(MotionEvent.ACTION_MOVE,700,200);r.one(MotionEvent.ACTION_UP,500,200);check(r.input.clicks==0,"drag no accidental row click");
   r.one(MotionEvent.ACTION_DOWN,966,470);r.two(MotionEvent.ACTION_POINTER_DOWN,1,966,470,500,200);empty(r,"second menu finger releases held button");r.two(MotionEvent.ACTION_POINTER_UP,1,966,470,500,200);r.one(MotionEvent.ACTION_UP,966,470);check(r.input.clicks==0,"multitouch cancelled pointer");
   r.input.clean();r.one(MotionEvent.ACTION_DOWN,966,470);r.menu(false);empty(r,"menu to campaign releases confirm");
   r.one(MotionEvent.ACTION_MOVE,910,380);r.one(MotionEvent.ACTION_UP,910,380);empty(r,"resume contact cannot become jump");
   check(r.draw().labels.contains("MOVE")&&r.draw().labels.contains("FIRE")&&r.draw().labels.contains("HUD"),"gameplay HUD restored");
   r.input.clean();r.tap(910,380);check((r.input.pressed&1)!=0,"new gameplay jump works");
  }
  Rig r=new Rig();r.one(MotionEvent.ACTION_DOWN,910,380);check(r.input.buttons==1,"gameplay A held");
  r.menu(true);empty(r,"opening pause releases gameplay");r.one(MotionEvent.ACTION_UP,910,380);check(r.input.clicks==0,"existing gameplay lift does not activate menu");
  r.view.controllerVisibility(GamepadPolicy.HIDE,1);check(r.view.getVisibility()==View.VISIBLE,"menu usable with always-hide/controller");
  r.input.menus=false;r.view.controllerVisibility(GamepadPolicy.AUTO,1);check(r.view.getVisibility()==View.GONE,"Auto hides with gamepad");
  r.view.controllerVisibility(GamepadPolicy.AUTO,0);check(r.view.getVisibility()==View.VISIBLE,"disconnect restores touch");
  r.view.controllerVisibility(GamepadPolicy.SHOW,2);check(r.view.getVisibility()==View.VISIBLE,"always show with two gamepads");
  r.view.controllerVisibility(GamepadPolicy.HIDE,0);check(r.view.getVisibility()==View.GONE,"manual hide remains explicit gameplay preference");
  r.input.menus=true;r.one(MotionEvent.ACTION_DOWN,500,200);check(r.view.getVisibility()==View.VISIBLE,"Activity-level menu event restores hidden overlay");r.one(MotionEvent.ACTION_UP,500,200);
  check(!r.view.dispatchMenuTouch(new MotionEvent(MotionEvent.ACTION_DOWN,0,InputDevice.SOURCE_MOUSE,new int[]{0},new float[]{500},new float[]{200}),r.surface),"external mouse passes to SDL");
  r=new Rig();r.one(MotionEvent.ACTION_DOWN,600,200);r.one(MotionEvent.ACTION_MOVE,650,220);r.one(MotionEvent.ACTION_UP,650,220);near(r.input.yaw,0,"anywhere off by default");
  setAnywhere(r,true,false);check(!r.context.getSharedPreferences("phone-controls",0).getBoolean("look_anywhere",false),"Cancel does not persist");
  r.one(MotionEvent.ACTION_DOWN,600,200);r.one(MotionEvent.ACTION_MOVE,650,220);r.one(MotionEvent.ACTION_UP,650,220);near(r.input.yaw,0,"Cancel restores live setting");
  setAnywhere(r,true,true);check(r.context.getSharedPreferences("phone-controls",0).getBoolean("look_anywhere",false),"Save persists new option");
  TouchControls reopened=new TouchControls(r.context,new Input());check(((TouchLayout)field(reopened,"layout")).lookAnywhere,"reopen loads saved setting");
  r.input.clean();r.one(MotionEvent.ACTION_DOWN,600,200);r.one(MotionEvent.ACTION_MOVE,650,220);near(r.input.yaw,-.05f*(float)Math.PI,"anywhere swipe sensitivity");near(r.input.pitch,-.02f*(float)Math.PI,"anywhere pitch");empty(r,"free look no axes/buttons");
  r.one(MotionEvent.ACTION_MOVE,910,380);check(r.input.buttons==0,"crossing a button never presses it");r.one(MotionEvent.ACTION_UP,910,380);
  // Touches on movement and buttons always claim their own stream first.
  r.input.clean();r.one(MotionEvent.ACTION_DOWN,140,370);r.one(MotionEvent.ACTION_MOVE,195,370);check(r.input.lx>0,"movement still analog");near(r.input.yaw,0,"MOVE doesn't camera look");
  r.two(MotionEvent.ACTION_POINTER_DOWN,1,195,370,600,200);r.two(MotionEvent.ACTION_MOVE,0,195,370,650,220);near(r.input.yaw,-.05f*(float)Math.PI,"independent second finger look");check(r.input.lx>0,"movement survives second finger");
  r.two(MotionEvent.ACTION_POINTER_UP,1,195,370,650,220);check(r.input.lx>0,"releasing look preserves MOVE");r.one(MotionEvent.ACTION_UP,195,370);empty(r,"MOVE release");
  r.input.clean();r.one(MotionEvent.ACTION_DOWN,910,380);r.two(MotionEvent.ACTION_POINTER_DOWN,1,910,380,910,380);r.two(MotionEvent.ACTION_MOVE,1,910,380,600,200);near(r.input.yaw,0,"occupied button is not unclaimed look space");r.one(MotionEvent.ACTION_CANCEL,0,0);empty(r,"cancel clears all fingers");
  r.input.clean();r.one(MotionEvent.ACTION_DOWN,910,210);r.one(MotionEvent.ACTION_MOVE,960,210);check((r.input.buttons&32768)!=0,"FIRE stays held");near(r.input.yaw,-.05f*(float)Math.PI,"FIRE swipe not doubled by anywhere");r.one(MotionEvent.ACTION_UP,960,210);
  // Relative free look remains relative even if the dedicated LOOK pad is a stick.
  ((TouchLayout)field(r.view,"layout")).swipe=false;r.input.clean();r.one(MotionEvent.ACTION_DOWN,600,200);r.one(MotionEvent.ACTION_MOVE,650,200);near(r.input.yaw,-.05f*(float)Math.PI,"free swipe independent of stick mode");empty(r,"no held-look axis from free swipe");
  r.menu(true);near(r.input.yaw,0,"menu entry clears pending aim");r.one(MotionEvent.ACTION_UP,650,200);r.input.clean();r.tap(500,200);near(r.input.yaw,0,"menu gestures cannot turn camera");r.menu(false);
  r.one(MotionEvent.ACTION_DOWN,600,200);r.one(MotionEvent.ACTION_MOVE,650,200);r.view.releaseAll();empty(r,"activity pause/focus loss hook releases");near(r.input.yaw,0,"activity hook clears pending aim");r.one(MotionEvent.ACTION_MOVE,700,200);near(r.input.yaw,0,"cancelled contact cannot revive");r.one(MotionEvent.ACTION_UP,700,200);
  r.one(MotionEvent.ACTION_DOWN,600,200);r.view.layout(0,0,1200,500);r.one(MotionEvent.ACTION_MOVE,700,200);near(r.input.yaw,0,"resize clears contacts");r.one(MotionEvent.ACTION_UP,700,200);
  r.view.layout(0,0,1000,500);r.view.dispatchApplyWindowInsets(new WindowInsets(24,8,16,10));r.menu(true);r.draw();RectF[] nav=(RectF[])field(r.view,"menuButtons");check(nav[0].left>=24&&nav[7].right<=984&&nav[0].bottom<=490,"menu navigation stays inside safe area");
  r.view.onDetachedFromWindow();empty(r,"detach releases input");
  // Follow the real Reset dialog action and Save to restore default preferences.
  r=new Rig();setAnywhere(r,true,true);editor(r);r.tap(525,22);check("Reset touch layout?".equals(AlertDialog.last.title),"Reset confirmation");AlertDialog.last.positive.onClick(AlertDialog.last,0);r.tap(75,22);
  check(!r.context.getSharedPreferences("phone-controls",0).getBoolean("look_anywhere",true),"Reset + Save disables optional look");
  System.out.println("touch view lifecycle: "+checks+" checks passed (full production view, dialogs, pointer streams, menus/fallback, gameplay, controller and persistence)");
 }
}
'''


def main():
    with tempfile.TemporaryDirectory(prefix='test31-touch-view-') as tmp:
        out = Path(tmp)
        sources = []
        for name, text in STUBS.items():
            p = out / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
            sources.append(p)
        check = out / 'com/halo/decomp/TouchLifecycleCheck.java'
        check.write_text(CHECK)
        sources.append(check)
        sources += [JAVA / (name + '.java') for name in
                    ['TouchControls', 'TouchLayout', 'MenuTouchGesture', 'GamepadPolicy', 'GyroPolicy']]
        subprocess.run(['javac', '-d', str(out), *map(str, sources)], check=True)
        subprocess.run(['java', '-cp', str(out), 'com.halo.decomp.TouchLifecycleCheck'], check=True)
    # Ensure the production activity uses the tested cancellation/routing hooks
    # and flat-only construction; this suite never substitutes the view logic.
    activity = (JAVA / 'HaloActivity.java').read_text()
    assert 'if (!BuildConfig.APPLICATION_ID.endsWith(".vr") && mLayout != null)' in activity
    assert activity.count('touchControls.releaseAll()') >= 3
    assert activity.index('touchControls.dispatchMenuTouch(event,mSurface)') < activity.index('return super.dispatchTouchEvent(event)')


if __name__ == '__main__':
    main()
