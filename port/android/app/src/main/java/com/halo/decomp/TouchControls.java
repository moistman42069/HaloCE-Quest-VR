package com.halo.decomp;

import android.content.Context;
import android.content.SharedPreferences;
import android.app.AlertDialog;
import android.graphics.RectF;
import android.widget.*;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.SparseArray;
import android.view.InputDevice;
import android.view.MotionEvent;
import android.view.View;
import android.view.DisplayCutout;

/** Flat phone overlay. Every contact owns its control until that contact lifts.
 * The JNI snapshot merges into player one, never enumerates an extra gamepad. */
final class TouchControls extends View {
    // Keep in step with port/android/include/halo_touch.h.
    private static final int A=1, B=1<<1, X=1<<2, Y=1<<3, WHITE=1<<4, BLACK=1<<5;
    private static final int CROUCH=1<<6, ZOOM=1<<7, START=1<<8, BACK=1<<9;
    private static final int UP=1<<10, DOWN=1<<11, LEFT=1<<12, RIGHT=1<<13;
    private static final int GRENADE=1<<14, FIRE=1<<15;
    private static final int BUTTON=0, MOVE=1, LOOK=2, FIRE_LOOK=3, TOGGLE=4, EDIT=5;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final SparseArray<Contact> contacts = new SparseArray<>();
    private Control[] controls = new Control[0];
    private boolean controlsShown = true;
    private int insetLeft, insetTop, insetRight, insetBottom;
    private float textSize;
    private TouchLayout layout=new TouchLayout();
    private boolean editing;
    private int selected=-1,dragPointer=-1;
    private float dragOffsetX,dragOffsetY;
    private float unit=1,availableW,availableH;
    private final RectF[] toolbar={new RectF(),new RectF(),new RectF(),new RectF()};
    private static native void nativeLook(float yaw,float pitch);
    private SharedPreferences preferences() { return getContext().getSharedPreferences("phone-controls",0); }
    private void readLayout() {
        SharedPreferences p=preferences();layout=new TouchLayout();
        layout.scale=p.getFloat("scale",1);layout.opacity=p.getFloat("opacity",.65f);
        layout.sensitivityX=p.getFloat("sensitivityX",1);layout.sensitivityY=p.getFloat("sensitivityY",1);
        layout.deadZone=p.getFloat("deadZone",.08f);layout.swipe=p.getBoolean("swipe",true);
        layout.floating=p.getBoolean("floating",false);layout.invert=p.getBoolean("invert",false);layout.color=p.getInt("color",0xff69c9ff);
        for(int i=0;i<TouchLayout.COUNT;i++) { layout.x[i]=p.getFloat("x"+i,layout.x[i]);layout.y[i]=p.getFloat("y"+i,layout.y[i]);
            layout.size[i]=p.getFloat("size"+i,1);layout.alpha[i]=p.getFloat("alpha"+i,1); }
        layout.sanitize();
    }
    private void saveLayout() {
        layout.sanitize();SharedPreferences.Editor e=preferences().edit();
        e.putInt("layout_version",1).putFloat("scale",layout.scale).putFloat("opacity",layout.opacity)
            .putFloat("sensitivityX",layout.sensitivityX).putFloat("sensitivityY",layout.sensitivityY).putFloat("deadZone",layout.deadZone)
            .putBoolean("swipe",layout.swipe).putBoolean("floating",layout.floating).putBoolean("invert",layout.invert).putInt("color",layout.color);
        for(int i=0;i<TouchLayout.COUNT;i++) e.putFloat("x"+i,layout.x[i]).putFloat("y"+i,layout.y[i]).putFloat("size"+i,layout.size[i]).putFloat("alpha"+i,layout.alpha[i]);
        e.apply();RunLog.line("Touch layout saved: swipe="+layout.swipe+" floating="+layout.floating+" sensitivity="+layout.sensitivityX+"/"+layout.sensitivityY);
    }

    private static final class Control {
        final String label;
        float x, y, radius;
        int id;
        final int bit, kind;
        Control(String label, float x, float y, float radius, int bit, int kind) {
            this.label=label; this.x=x; this.y=y; this.radius=radius;
            this.bit=bit; this.kind=kind;
        }
        boolean contains(float px, float py) {
            float dx=px-x, dy=py-y;
            return dx*dx+dy*dy <= radius*radius;
        }
    }
    private final class Contact {
        final Control control;
        final float originX, originY;
        float x, y;
        Contact(Control control, float x, float y) {
            this.control=control; this.x=x; this.y=y;
            originX=control.kind == FIRE_LOOK || (control.kind==MOVE && layout.floating) ? x : control.x;
            originY=control.kind == FIRE_LOOK || (control.kind==MOVE && layout.floating) ? y : control.y;
        }
    }

    private static native void nativeState(int lx, int ly, int rx, int ry,
                                           int buttons, boolean reset);

    TouchControls(Context context) {
        super(context);
        readLayout();
        setFocusable(false); // SDL's surface keeps keyboard/gamepad focus.
        setContentDescription("Halo touch controls: move, look, combat and menus");
        controlsShown=context.getSharedPreferences("phone-controls", 0)
                .getBoolean("shown", true);
        setOnApplyWindowInsetsListener((view, insets) -> {
            insetLeft=insets.getSystemWindowInsetLeft();
            insetTop=insets.getSystemWindowInsetTop();
            insetRight=insets.getSystemWindowInsetRight();
            insetBottom=insets.getSystemWindowInsetBottom();
            DisplayCutout cutout=insets.getDisplayCutout();
            if (cutout != null) {
                insetLeft=Math.max(insetLeft, cutout.getSafeInsetLeft());
                insetTop=Math.max(insetTop, cutout.getSafeInsetTop());
                insetRight=Math.max(insetRight, cutout.getSafeInsetRight());
                insetBottom=Math.max(insetBottom, cutout.getSafeInsetBottom());
            }
            layoutControls();
            return insets;
        });
    }

    @Override protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        layoutControls();
    }

    private void layoutControls() {
        releaseAll();
        float w=getWidth()-insetLeft-insetRight, h=getHeight()-insetTop-insetBottom;
        if (w <= 0 || h <= 0) return;
        unit=Math.min(w/1000f, h/500f); availableW=w;availableH=h;
        float r=34*unit, stick=66*unit;
        textSize=14*unit;
        float left=insetLeft, top=insetTop;
        // Sticks and buttons have separate hit areas even on 16:9 screens.
        controls=new Control[] {
            new Control("MOVE", left+w*.14f, top+h*.74f, stick, 0, MOVE),
            new Control("LOOK", left+w*.67f, top+h*.75f, stick, 0, LOOK),
            new Control("FIRE", left+w*.91f, top+h*.42f, r*1.35f, FIRE, FIRE_LOOK),
            new Control("A / Jump", left+w*.91f, top+h*.76f, r, A, BUTTON),
            new Control("B / Melee", left+w*.96f, top+h*.59f, r, B, BUTTON),
            new Control("X / Use", left+w*.83f, top+h*.61f, r, X, BUTTON),
            new Control("Y / Swap", left+w*.80f, top+h*.42f, r, Y, BUTTON),
            new Control("Crouch", left+w*.28f, top+h*.82f, r, CROUCH, BUTTON),
            new Control("Zoom", left+w*.80f, top+h*.84f, r, ZOOM, BUTTON),
            new Control("Grenade", left+w*.10f, top+h*.38f, r, GRENADE, BUTTON),
            new Control("Type", left+w*.21f, top+h*.38f, r, WHITE, BUTTON),
            new Control("Light", left+w*.32f, top+h*.38f, r, BLACK, BUTTON),
            new Control("Menu", left+w*.56f, top+h*.10f, r, START, BUTTON),
            new Control("Back", left+w*.44f, top+h*.10f, r, BACK, BUTTON),
            new Control("^", left+w*.40f, top+h*.60f, r*.8f, UP, BUTTON),
            new Control("v", left+w*.40f, top+h*.84f, r*.8f, DOWN, BUTTON),
            new Control("<", left+w*.34f, top+h*.72f, r*.8f, LEFT, BUTTON),
            new Control(">", left+w*.46f, top+h*.72f, r*.8f, RIGHT, BUTTON),
            new Control("Touch", left+w*.94f, top+h*.10f, r, 0, TOGGLE),
            new Control("HUD", left+32*unit, top+32*unit, 27*unit, 0, EDIT)
        };
        for(int i=0;i<controls.length;i++) {
            Control c=controls[i];c.id=i;if(i>=TouchLayout.COUNT)continue;
            c.radius=Math.min(Math.min(w,h)*.24f,c.radius*layout.scale*layout.size[i]);
            c.x=left+TouchLayout.position(layout.x[i],w,c.radius);c.y=top+TouchLayout.position(layout.y[i],h,c.radius);
        }
        float barW=Math.min(w,600*unit),barH=44*getResources().getDisplayMetrics().density;
        for(int i=0;i<4;i++)toolbar[i].set(left+i*barW/4,top,left+(i+1)*barW/4,top+barH);
        invalidate();
    }

    void releaseAll() {
        contacts.clear();dragPointer=-1;
        nativeState(0, 0, 0, 0, 0, true);
        invalidate();
    }

    private boolean owned(Control c) {
        for (int i=0; i<contacts.size(); i++)
            if (contacts.valueAt(i).control == c) return true;
        return false;
    }

    @Override public boolean onTouchEvent(MotionEvent event) {
        // External mice continue to SDL. Finger contacts never also fire
        // through SDL's touch-to-mouse emulation underneath the overlay.
        if (!event.isFromSource(InputDevice.SOURCE_TOUCHSCREEN)) return false;
        int action=event.getActionMasked(), index=event.getActionIndex();
        if (action == MotionEvent.ACTION_CANCEL) { releaseAll(); return true; }
        if(editing) return editTouch(event);
        if (action == MotionEvent.ACTION_DOWN) releaseAll();
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            float x=event.getX(index), y=event.getY(index);
            for (int i=controls.length-1; i>=0; i--) {
                Control c=controls[i];
                if ((!controlsShown && c.kind != TOGGLE && c.kind != EDIT) || !c.contains(x, y) || owned(c)) continue;
                if(c.kind==EDIT) {
                    releaseAll();editing=true;selected=-1;invalidate();
                    Toast.makeText(getContext(),"Drag controls. Options edits size, opacity and aiming. Save keeps changes; Cancel restores. Online play continues.",Toast.LENGTH_LONG).show();
                    return true;
                } else if (c.kind == TOGGLE) {
                    controlsShown=!controlsShown;
                    releaseAll();
                    getContext().getSharedPreferences("phone-controls", 0).edit()
                            .putBoolean("shown", controlsShown).apply();
                    RunLog.line("Phone touch controls " + (controlsShown ? "shown" : "hidden"));
                } else {
                    contacts.put(event.getPointerId(index), new Contact(c, x, y));
                }
                break;
            }
        }
        for (int i=0; i<event.getPointerCount(); i++) {
            Contact c=contacts.get(event.getPointerId(i));
            if (c != null) {
                float x=event.getX(i),y=event.getY(i);
                if(layout.swipe && (c.control.kind==LOOK || c.control.kind==FIRE_LOOK)) {
                    // Screen-fraction sensitivity: one safe-area width = 180 degrees.
                    float dx=(x-c.x)/Math.max(1,availableW)*(float)Math.PI*layout.sensitivityX;
                    float dy=(y-c.y)/Math.max(1,availableW)*(float)Math.PI*layout.sensitivityY;
                    nativeLook(-dx,layout.invert?dy:-dy);
                }
                c.x=x;c.y=y;
            }
        }
        if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP)
            contacts.remove(event.getPointerId(index));
        sendState();
        invalidate();
        return true;
    }

    private void sendState() {
        int lx=0, ly=0, rx=0, ry=0, buttons=0;
        for (int i=0; i<contacts.size(); i++) {
            Contact c=contacts.valueAt(i);
            buttons |= c.control.bit;
            if (c.control.kind == BUTTON || (layout.swipe && c.control.kind!=MOVE)) continue;
            float radius=c.control.kind == FIRE_LOOK ? c.control.radius*1.4f : c.control.radius;
            float dx=c.x-c.originX,dy=c.originY-c.y;
            float x=TouchLayout.axis(dx,dy,radius,layout.deadZone),y=TouchLayout.axis(dy,dx,radius,layout.deadZone);
            if(c.control.kind!=MOVE) {x*=layout.sensitivityX;y*=layout.sensitivityY*(layout.invert?-1:1);}
            int ax=Math.round(Math.max(-1,Math.min(1,x))*32767),ay=Math.round(Math.max(-1,Math.min(1,y))*32767);
            if (c.control.kind == MOVE) { lx=ax; ly=ay; }
            else if (ax* (long)ax + ay*(long)ay > rx*(long)rx + ry*(long)ry) { rx=ax; ry=ay; }
        }
        nativeState(lx, ly, rx, ry, buttons, false);
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        for (Control c : controls) {
            if (!editing && !controlsShown && c.kind != TOGGLE && c.kind != EDIT) continue;
            boolean pressed=owned(c);
            float opacity=c.kind==EDIT?1:layout.opacity*(c.id<TouchLayout.COUNT?layout.alpha[c.id]:1);
            if(editing)opacity=Math.max(.65f,opacity);
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(layout.color);paint.setAlpha(Math.round((pressed?150:50)*opacity));
            canvas.drawCircle(c.x, c.y, c.radius, paint);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(2*getResources().getDisplayMetrics().density);
            paint.setColor(editing && c.id==selected?0xffffcc66:pressed?Color.WHITE:layout.color);paint.setAlpha(Math.round(230*opacity));
            canvas.drawCircle(c.x, c.y, c.radius, paint);
            paint.setStyle(Paint.Style.FILL);
            paint.setTextSize(Math.min(textSize, c.radius*1.6f/Math.max(1,c.label.length())*1.7f));
            paint.setTextAlign(Paint.Align.CENTER);
            paint.setColor(Color.WHITE);paint.setAlpha(Math.round(255*Math.max(.4f,opacity)));
            canvas.drawText(c.label, c.x, c.y-(paint.ascent()+paint.descent())/2, paint);
            if (c.kind == MOVE || c.kind == LOOK) {
                float x=0, y=0;
                for (int i=0; i<contacts.size(); i++) {
                    Contact finger=contacts.valueAt(i);
                    if (finger.control == c) { x=finger.x-c.x; y=finger.y-c.y; }
                }
                float length=(float)Math.sqrt(x*x+y*y);
                float limit=c.radius*.70f;
                if (length > limit) { x*=limit/length; y*=limit/length; }
                paint.setColor(layout.color);paint.setAlpha(Math.round(100*opacity));
                canvas.drawCircle(c.x+x, c.y+y, c.radius*.28f, paint);
            }
        }
        if(editing) {
            String[] names={"SAVE","CANCEL","OPTIONS","RESET"};
            for(int i=0;i<4;i++) {paint.setColor(0xf0102434);canvas.drawRect(toolbar[i],paint);
                paint.setColor(0xffbce7ff);paint.setTextSize(16*getResources().getDisplayMetrics().scaledDensity);
                canvas.drawText(names[i],toolbar[i].centerX(),toolbar[i].centerY()-(paint.ascent()+paint.descent())/2,paint);}
        }
    }

    private boolean editTouch(MotionEvent event) {
        int action=event.getActionMasked(),index=event.getActionIndex();
        if(action==MotionEvent.ACTION_DOWN) {
            float x=event.getX(),y=event.getY();
            for(int i=0;i<4;i++) if(toolbar[i].contains(x,y)) {
                releaseAll();
                if(i==0){saveLayout();editing=false;} else if(i==1){readLayout();editing=false;layoutControls();}
                else if(i==2) showOptions();
                else new AlertDialog.Builder(getContext()).setTitle("Reset touch layout?").setMessage("Restore default positions and touch preferences. Save to keep, or Cancel in the editor to restore your old layout.")
                    .setPositiveButton("Reset",(d,w)->{layout=new TouchLayout();selected=-1;layoutControls();}).setNegativeButton("Back",null).show();
                invalidate();return true;
            }
            for(int i=TouchLayout.COUNT-1;i>=0;i--) if(controls[i].contains(x,y)) {
                selected=i;dragPointer=event.getPointerId(0);dragOffsetX=x-controls[i].x;dragOffsetY=y-controls[i].y;break;
            }
        }
        if(action==MotionEvent.ACTION_MOVE && dragPointer>=0 && selected>=0) {
            int p=event.findPointerIndex(dragPointer);if(p>=0) {
                Control c=controls[selected];
                c.x=insetLeft+TouchLayout.position((event.getX(p)-dragOffsetX-insetLeft)/availableW,availableW,c.radius);
                c.y=insetTop+TouchLayout.position((event.getY(p)-dragOffsetY-insetTop)/availableH,availableH,c.radius);
                layout.x[selected]=(c.x-insetLeft)/availableW;layout.y[selected]=(c.y-insetTop)/availableH;
            }
        }
        if((action==MotionEvent.ACTION_UP||action==MotionEvent.ACTION_POINTER_UP)&&event.getPointerId(index)==dragPointer)dragPointer=-1;
        invalidate();return true;
    }
    private interface Value {void set(float value);}
    private void slider(LinearLayout box,String name,float value,float min,float max,Value setter) {
        TextView text=new TextView(getContext());box.addView(text);
        SeekBar bar=new SeekBar(getContext());bar.setMax(100);bar.setProgress(Math.round((value-min)*100/(max-min)));box.addView(bar);
        text.setText(name+": "+String.format(java.util.Locale.ROOT,"%.2f",value));
        bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar b,int progress,boolean user){if(user){float v=min+(max-min)*progress/100;setter.set(v);text.setText(name+": "+String.format(java.util.Locale.ROOT,"%.2f",v));layoutControls();}}
            public void onStartTrackingTouch(SeekBar b){}public void onStopTrackingTouch(SeekBar b){}
        });
    }
    private void check(LinearLayout box,String name,boolean value,java.util.function.Consumer<Boolean> setter) {
        CheckBox check=new CheckBox(getContext());check.setText(name);check.setChecked(value);box.addView(check);check.setOnCheckedChangeListener((b,v)->setter.accept(v));
    }
    private void showOptions() {
        releaseAll();LinearLayout box=new LinearLayout(getContext());box.setOrientation(LinearLayout.VERTICAL);box.setPadding(24,12,24,12);
        Button choose=new Button(getContext());choose.setText("Select a control (including covered controls)");box.addView(choose);
        final AlertDialog[] optionsDialog=new AlertDialog[1];
        choose.setOnClickListener(v->{String[] names=new String[TouchLayout.COUNT];for(int i=0;i<names.length;i++)names[i]=controls[i].label;
            new AlertDialog.Builder(getContext()).setTitle("Edit control").setItems(names,(d,i)->{selected=i;optionsDialog[0].dismiss();showOptions();invalidate();}).show();});
        if(selected>=0) {final int id=selected;TextView label=new TextView(getContext());label.setText("Selected: "+controls[id].label+" (drag to change spacing)");box.addView(label);
            slider(box,"Horizontal position",layout.x[id],0,1,v->layout.x[id]=v);
            slider(box,"Vertical position",layout.y[id],0,1,v->layout.y[id]=v);
            slider(box,"Control size",layout.size[id],.65f,1.6f,v->layout.size[id]=v);
            slider(box,"Control opacity",layout.alpha[id],.15f,1,v->layout.alpha[id]=v);}
        slider(box,"All controls: scale",layout.scale,.65f,1.5f,v->layout.scale=v);
        slider(box,"All controls: opacity",layout.opacity,.15f,1,v->layout.opacity=v);
        slider(box,"Horizontal sensitivity",layout.sensitivityX,.25f,3,v->layout.sensitivityX=v);
        slider(box,"Vertical sensitivity",layout.sensitivityY,.25f,3,v->layout.sensitivityY=v);
        slider(box,"Stick dead zone",layout.deadZone,0,.30f,v->layout.deadZone=v);
        check(box,"Swipe aim (off = hold stick to turn)",layout.swipe,v->layout.swipe=v);
        check(box,"Floating movement origin",layout.floating,v->layout.floating=v);
        check(box,"Invert vertical aim",layout.invert,v->layout.invert=v);
        TextView help=new TextView(getContext());help.setText("Swipe on LOOK or drag FIRE while shooting. Lift to stop turning. Movement starts within MOVE; floating places its center under your finger. Dead zone applies to stick mode and movement. A screen-width swipe turns 180 degrees at sensitivity 1. Layout uses safe screen fractions and adapts around notches. Options stay temporary until SAVE.");box.addView(help);
        String[] colors={"CE blue","Cyan","White","Amber","Green"};int[] values={0xff69c9ff,0xff65eeee,0xffeeeeee,0xffffbd65,0xff8be298};
        Button color=new Button(getContext());color.setText("HUD color");box.addView(color);color.setOnClickListener(v->new AlertDialog.Builder(getContext()).setTitle("HUD color").setItems(colors,(d,i)->{layout.color=values[i];invalidate();}).show());
        ScrollView scroll=new ScrollView(getContext());scroll.addView(box);optionsDialog[0]=new AlertDialog.Builder(getContext()).setTitle("Touch options").setView(scroll).setPositiveButton("Back to editor",null).create();optionsDialog[0].show();
    }

    @Override protected void onDetachedFromWindow() {
        releaseAll();
        super.onDetachedFromWindow();
    }
}
