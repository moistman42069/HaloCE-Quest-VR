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
    private static final int BUTTON=0, MOVE=1, LOOK=2, FIRE_LOOK=3, TOGGLE=4, EDIT=5, FREE_LOOK=6;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final SparseArray<Contact> contacts = new SparseArray<>();
    private Control[] controls = new Control[0];
    private boolean controlsShown = true;
    private int insetLeft, insetTop, insetRight, insetBottom;
    private float textSize;
    private TouchLayout layout=new TouchLayout();
    private boolean editing;
    private boolean menus, menuStream;
    private int touchMode=GamepadPolicy.AUTO, connectedPads;
    private final MenuTouchGesture menuGesture=new MenuTouchGesture();
    private final RectF menuBack=new RectF();
    private final RectF menuToggle=new RectF();
    private final RectF[] menuButtons={new RectF(),new RectF(),new RectF(),new RectF(),new RectF(),new RectF(),new RectF(),new RectF(),new RectF()};
    private static final int[] MENU_BITS={LEFT,UP,DOWN,RIGHT,X,Y,B,A,START};
    private static final String[] MENU_LABELS={"<","^","v",">","X","Y","B","A","Start"};
    private boolean menuControlsShown=true,menuButtonCancelled;
    private int menuButtonPointer=-1,menuButton=-1;
    private final Control freeLook=new Control("",0,0,0,0,FREE_LOOK);
    /** The production view is exercised with a recording input endpoint in tests. */
    interface Input {
        boolean menus();
        void pointer(int action,float x,float y);
        void state(int lx,int ly,int rx,int ry,int buttons,boolean reset);
        void look(float yaw,float pitch);
    }
    private final Input input;
    private static final Input NATIVE=new Input() {
        public boolean menus(){return nativeMenus();}
        public void pointer(int action,float x,float y){nativePointer(action,x,y);}
        public void state(int lx,int ly,int rx,int ry,int buttons,boolean reset){nativeState(lx,ly,rx,ry,buttons,reset);}
        public void look(float yaw,float pitch){nativeLook(yaw,pitch);}
    };
    private static native boolean nativeMenus();
    private static native void nativePointer(int action,float x,float y);
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
        layout.lookAnywhere=p.getBoolean("look_anywhere",false);
        layout.floating=p.getBoolean("floating",false);layout.invert=p.getBoolean("invert",false);layout.color=p.getInt("color",0xff69c9ff);
        layout.gyroMode=p.getInt("gyroMode",GyroPolicy.OFF);layout.gyroX=p.getFloat("gyroX",1);layout.gyroY=p.getFloat("gyroY",1);layout.gyroInvert=p.getBoolean("gyroInvert",false);
        for(int i=0;i<TouchLayout.COUNT;i++) { layout.x[i]=p.getFloat("x"+i,layout.x[i]);layout.y[i]=p.getFloat("y"+i,layout.y[i]);
            layout.size[i]=p.getFloat("size"+i,1);layout.alpha[i]=p.getFloat("alpha"+i,1); }
        layout.sanitize();
    }
    private void saveLayout() {
        layout.sanitize();SharedPreferences.Editor e=preferences().edit();
        e.putInt("layout_version",1).putFloat("scale",layout.scale).putFloat("opacity",layout.opacity)
            .putFloat("sensitivityX",layout.sensitivityX).putFloat("sensitivityY",layout.sensitivityY).putFloat("deadZone",layout.deadZone)
            .putBoolean("swipe",layout.swipe).putBoolean("floating",layout.floating).putBoolean("invert",layout.invert).putInt("color",layout.color)
            .putBoolean("look_anywhere",layout.lookAnywhere)
            .putInt("gyroMode",layout.gyroMode).putFloat("gyroX",layout.gyroX).putFloat("gyroY",layout.gyroY).putBoolean("gyroInvert",layout.gyroInvert);
        for(int i=0;i<TouchLayout.COUNT;i++) e.putFloat("x"+i,layout.x[i]).putFloat("y"+i,layout.y[i]).putFloat("size"+i,layout.size[i]).putFloat("alpha"+i,layout.alpha[i]);
        e.apply();RunLog.line("Touch layout saved: swipe="+layout.swipe+" anywhere="+layout.lookAnywhere+" floating="+layout.floating+" sensitivity="+layout.sensitivityX+"/"+layout.sensitivityY
            +" gyro="+GyroPolicy.MODES[layout.gyroMode]+" "+layout.gyroX+"/"+layout.gyroY+(layout.gyroInvert?" inverted":""));
    }

    // Gyro aim (GyroAim): its option, and whether it may turn the view now.
    private GyroAim gyro;
    void setGyro(GyroAim g) { gyro=g; }
    private void gyroUpdate() { if(gyro!=null) gyro.update(); }
    int gyroMode() { return layout.gyroMode; }
    float gyroX() { return layout.gyroX; }
    float gyroY() { return layout.gyroY; }
    boolean gyroInvert() { return layout.gyroInvert; }
    boolean gyroAiming() {
        if(editing||menus||layout.gyroMode==GyroPolicy.OFF) return false;
        if(layout.gyroMode==GyroPolicy.ALWAYS) return true;
        if(getVisibility()!=VISIBLE) return false;
        for(int i=0;i<contacts.size();i++) { int kind=contacts.valueAt(i).control.kind; if(kind==LOOK||kind==FIRE_LOOK) return true; }
        return false;
    }
    /** the gyro's turn, sent as a swipe's */
    static void look(float yaw,float pitch) { nativeLook(yaw,pitch); }

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
        this(context,NATIVE);
    }
    TouchControls(Context context,Input input) {
        super(context);
        this.input=input;
        readLayout();
        setFocusable(false); // SDL's surface keeps keyboard/gamepad focus.
        setContentDescription("Halo touch controls: move, look, combat and menus");
        controlsShown=true;
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
            new Control("Type", left+w*.21f, top+h*.38f, r, BLACK, BUTTON),
            new Control("Light", left+w*.32f, top+h*.38f, r, WHITE, BUTTON),
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
        contacts.clear();dragPointer=-1;menuGesture.cancel();
        menuButtonPointer=-1;menuButton=-1;menuButtonCancelled=false;
        input.state(0, 0, 0, 0, 0, true);
        invalidate();
    }

    void controllerVisibility(int mode,int connected) {
        touchMode=mode;connectedPads=connected;
        refreshMenuMode();
        applyVisibility();
    }

    private void applyVisibility() {
        // Menu navigation must remain reachable even with stock-menu fallback,
        // a hidden gameplay HUD or a controller that disconnects in a menu.
        boolean show=menus || editing || GamepadPolicy.showTouch(touchMode,connectedPads);
        int visibility=show?VISIBLE:GONE;
        if(getVisibility()!=visibility) { releaseAll();setVisibility(visibility); }
    }
    private void refreshMenuMode() {
        boolean active=input.menus();
        if(active!=menus) {
            releaseAll();menus=active;menuControlsShown=true;applyVisibility();gyroUpdate();invalidate();
            RunLog.line("Touch mode: "+(menus?"menu (direct taps + navigation buttons)":"gameplay")+" policy="+touchMode+" controllers="+connectedPads);
        }
    }
    private void layoutMenuNavigation() {
        float density=getResources().getDisplayMetrics().density;
        float gap=8*density,height=40*density,width=76*density;
        menuBack.set(getWidth()-insetRight-width-gap,insetTop+gap,
            getWidth()-insetRight-gap,insetTop+gap+height);
        menuToggle.set(insetLeft+gap,insetTop+gap,insetLeft+gap+100*density,insetTop+gap+height);
        // Edge strips leave the menu's central rows available for direct taps.
        // The Controls button can tuck the strips away without losing recovery.
        float size=Math.min(44*density,(getWidth()-insetLeft-insetRight-11*gap)/8);
        size=Math.max(1,size);
        float y=getHeight()-insetBottom-gap-size;
        for(int i=0;i<8;i++) {
            float x=i<4?insetLeft+gap+i*(size+gap):getWidth()-insetRight-gap-4*size-3*gap+(i-4)*(size+gap);
            menuButtons[i].set(x,y,x+size,y+size);
        }
        float center=(insetLeft+getWidth()-insetRight)/2f;
        menuButtons[8].set(center-width/2,insetTop+gap,center+width/2,insetTop+gap+height);
    }
    private int menuButtonAt(float x,float y) {
        if(menuToggle.contains(x,y))return menuButtons.length;
        if(menuControlsShown) for(int i=0;i<menuButtons.length;i++)if(menuButtons[i].contains(x,y))return i;
        return -1;
    }
    private void menuButtonState(boolean down) {
        input.state(0,0,0,0,down && menuButton>=0 && menuButton<MENU_BITS.length?MENU_BITS[menuButton]:0,false);
        invalidate();
    }

    /** Activity-level routing works even when a controller hides the gameplay
     * overlay. Coordinates are translated into the SDL surface's actual bounds.
     * A stream begun in a menu is consumed through its final UP after Resume. */
    boolean dispatchMenuTouch(MotionEvent event,View surface) {
        if(!event.isFromSource(InputDevice.SOURCE_TOUCHSCREEN)) return false;
        refreshMenuMode();
        int action=event.getActionMasked();
        if(!menus && !menuStream) return false;
        if(editing) return false;
        if(!menus) {
            if(action==MotionEvent.ACTION_UP || action==MotionEvent.ACTION_CANCEL) menuStream=false;
            return true;
        }
        if(action==MotionEvent.ACTION_DOWN) {
            releaseAll();menuStream=true;
        } else if(!menuStream) {
            // A gameplay contact already down when pause opened must lift first.
            return true;
        }
        if(action==MotionEvent.ACTION_CANCEL || action==MotionEvent.ACTION_POINTER_DOWN) {
            releaseAll();input.pointer(3,0,0);
            if(action==MotionEvent.ACTION_CANCEL)menuStream=false;
            return true;
        }
        int id=menuButtonPointer>=0?menuButtonPointer:menuGesture.pointer();
        int index=action==MotionEvent.ACTION_DOWN?event.getActionIndex():event.findPointerIndex(id);
        if(index>=0) {
            int[] overlayPos=new int[2];getLocationOnScreen(overlayPos);
            // Activity events are relative to its decor view, including system insets.
            float rawX=event.getRawX()+event.getX(index)-event.getX();
            float rawY=event.getRawY()+event.getY(index)-event.getY();
            float px=rawX-overlayPos[0],py=rawY-overlayPos[1];
            layoutMenuNavigation();
            int button=menuButtonAt(px,py);
            if(action==MotionEvent.ACTION_DOWN && button>=0) {
                menuButtonPointer=event.getPointerId(index);menuButton=button;
                menuButtonState(true);
            }
            if(menuButtonPointer>=0) {
                // A control press never also becomes a menu-pointer click.
                if(button!=menuButton)menuButtonCancelled=true;
                boolean up=action==MotionEvent.ACTION_UP || (action==MotionEvent.ACTION_POINTER_UP && event.getPointerId(event.getActionIndex())==menuButtonPointer);
                if(up && !menuButtonCancelled && menuButton==menuButtons.length)menuControlsShown=!menuControlsShown;
                menuButtonState(!up && !menuButtonCancelled);
                if(up){menuButtonPointer=-1;menuButton=-1;}
            } else if(surface!=null && surface.getWidth()>0 && surface.getHeight()>0) {
                int[] surfacePos=new int[2];surface.getLocationOnScreen(surfacePos);
                float x=(rawX-surfacePos[0])/surface.getWidth(),y=(rawY-surfacePos[1])/surface.getHeight();
                boolean back=menuBack.contains(px,py);
                float slop=android.view.ViewConfiguration.get(getContext()).getScaledTouchSlop()*2f;
                if(action==MotionEvent.ACTION_DOWN) menuGesture.begin(event.getPointerId(index),rawX,rawY,back);
                else menuGesture.move(rawX,rawY,slop);
                if(!menuGesture.back())input.pointer(0,x,y);
                if(action==MotionEvent.ACTION_UP || (action==MotionEvent.ACTION_POINTER_UP && event.getPointerId(event.getActionIndex())==menuGesture.pointer())) {
                    int tap=menuGesture.end(event.getPointerId(index),rawX,rawY,slop,back);
                    if(tap!=0)input.pointer(tap,x,y);
                }
            }
        }
        if(action==MotionEvent.ACTION_UP) {menuStream=false;menuGesture.cancel();}
        return true;
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
        if(dispatchMenuTouch(event,this))return true;
        int action=event.getActionMasked(), index=event.getActionIndex();
        if (action == MotionEvent.ACTION_CANCEL) { releaseAll(); return true; }
        if(editing) return editTouch(event);
        if (action == MotionEvent.ACTION_DOWN) releaseAll();
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            float x=event.getX(index), y=event.getY(index);
            boolean claimed=false;
            for (int i=controls.length-1; i>=0; i--) {
                Control c=controls[i];
                if ((!controlsShown && c.kind != TOGGLE && c.kind != EDIT) || !c.contains(x, y)) continue;
                claimed=true;
                if(owned(c))break; // An occupied button is never free camera space.
                if(c.kind==EDIT) {
                    releaseAll();editing=true;selected=-1;invalidate();
                    Toast.makeText(getContext(),"Drag controls. Options edits size, opacity and aiming. Save keeps changes; Cancel restores. Online play continues.",Toast.LENGTH_LONG).show();
                    return true;
                } else if (c.kind == TOGGLE) {
                    releaseAll();
                    new GamepadNavigation.Builder(getContext()).setTitle("Touch visibility")
                        .setSingleChoiceItems(new String[]{"Auto: hide with controller","Always show","Always hide (restore in launcher)"},GamepadSupport.mode(getContext()),(dialog,which)->{
                            preferences().edit().putInt("controller_touch_mode",which).apply();dialog.dismiss();
                        }).setNegativeButton("Cancel",null).show();
                } else {
                    contacts.put(event.getPointerId(index), new Contact(c, x, y));
                }
                break;
            }
            if(!claimed && layout.lookAnywhere && !owned(freeLook))
                contacts.put(event.getPointerId(index),new Contact(freeLook,x,y));
        }
        for (int i=0; i<event.getPointerCount(); i++) {
            Contact c=contacts.get(event.getPointerId(i));
            if (c != null) {
                float x=event.getX(i),y=event.getY(i);
                if(c.control.kind==FREE_LOOK || (layout.swipe && (c.control.kind==LOOK || c.control.kind==FIRE_LOOK))) {
                    // Screen-fraction sensitivity: one safe-area width = 180 degrees.
                    float dx=(x-c.x)/Math.max(1,availableW)*(float)Math.PI*layout.sensitivityX;
                    float dy=(y-c.y)/Math.max(1,availableW)*(float)Math.PI*layout.sensitivityY;
                    input.look(-dx,layout.invert?dy:-dy);
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
            if (c.control.kind == BUTTON || c.control.kind==FREE_LOOK || (layout.swipe && c.control.kind!=MOVE)) continue;
            float radius=c.control.kind == FIRE_LOOK ? c.control.radius*1.4f : c.control.radius;
            float dx=c.x-c.originX,dy=c.originY-c.y;
            float x=TouchLayout.axis(dx,dy,radius,layout.deadZone),y=TouchLayout.axis(dy,dx,radius,layout.deadZone);
            if(c.control.kind!=MOVE) {x*=layout.sensitivityX;y*=layout.sensitivityY*(layout.invert?-1:1);}
            int ax=Math.round(Math.max(-1,Math.min(1,x))*32767),ay=Math.round(Math.max(-1,Math.min(1,y))*32767);
            if (c.control.kind == MOVE) { lx=ax; ly=ay; }
            else if (ax* (long)ax + ay*(long)ay > rx*(long)rx + ry*(long)ry) { rx=ax; ry=ay; }
        }
        input.state(lx, ly, rx, ry, buttons, false);
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        if(menus && !editing) {
            layoutMenuNavigation();
            drawMenuButton(canvas,menuBack,"Back",false);
            drawMenuButton(canvas,menuToggle,menuControlsShown?"Hide controls":"Show controls",false);
            if(menuControlsShown)for(int i=0;i<menuButtons.length;i++)
                drawMenuButton(canvas,menuButtons[i],MENU_LABELS[i],menuButtonPointer>=0 && menuButton==i && !menuButtonCancelled);
            return;
        }
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

    private void drawMenuButton(Canvas canvas,RectF bounds,String label,boolean pressed) {
        paint.setStyle(Paint.Style.FILL);paint.setColor(pressed?0xd041647a:0xb0102434);
        canvas.drawRoundRect(bounds,8,8,paint);paint.setColor(Color.WHITE);
        paint.setTextAlign(Paint.Align.CENTER);paint.setTextSize(14*getResources().getDisplayMetrics().scaledDensity);
        canvas.drawText(label,bounds.centerX(),bounds.centerY()-(paint.ascent()+paint.descent())/2,paint);
    }

    private boolean editTouch(MotionEvent event) {
        int action=event.getActionMasked(),index=event.getActionIndex();
        if(action==MotionEvent.ACTION_DOWN) {
            float x=event.getX(),y=event.getY();
            for(int i=0;i<4;i++) if(toolbar[i].contains(x,y)) {
                releaseAll();
                if(i==0){saveLayout();editing=false;gyroUpdate();} else if(i==1){readLayout();editing=false;layoutControls();gyroUpdate();}
                else if(i==2) showOptions();
                else new GamepadNavigation.Builder(getContext()).setTitle("Reset touch layout?").setMessage("Restore default positions and touch preferences. Save to keep, or Cancel in the editor to restore your old layout.")
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
            new GamepadNavigation.Builder(getContext()).setTitle("Edit control").setItems(names,(d,i)->{selected=i;optionsDialog[0].dismiss();showOptions();invalidate();}).show();});
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
        check(box,"Drag anywhere to look (unused gameplay space)",layout.lookAnywhere,v->layout.lookAnywhere=v);
        check(box,"Floating movement origin",layout.floating,v->layout.floating=v);
        check(box,"Invert vertical aim",layout.invert,v->layout.invert=v);
        boolean hasGyro=GyroAim.available(getContext());
        Button gyroChoice=new Button(getContext());gyroChoice.setText("Gyro aim: "+(hasGyro?GyroPolicy.MODES[layout.gyroMode]:"no gyroscope on this device"));gyroChoice.setEnabled(hasGyro);box.addView(gyroChoice);
        gyroChoice.setOnClickListener(v->new GamepadNavigation.Builder(getContext()).setTitle("Gyro aim")
            .setSingleChoiceItems(GyroPolicy.MODES,layout.gyroMode,(d,which)->{layout.gyroMode=which;gyroChoice.setText("Gyro aim: "+GyroPolicy.MODES[which]);d.dismiss();}).show());
        slider(box,"Gyro horizontal sensitivity",layout.gyroX,.25f,4,v->layout.gyroX=v);
        slider(box,"Gyro vertical sensitivity",layout.gyroY,.25f,4,v->layout.gyroY=v);
        check(box,"Invert gyro vertical aim",layout.gyroInvert,v->layout.gyroInvert=v);
        TextView help=new TextView(getContext());help.setText("Swipe on LOOK or drag FIRE while shooting. Optional drag-anywhere starts camera movement only on unused gameplay space; buttons and MOVE always keep priority. It uses swipe sensitivity even in held-stick mode. Lift to stop turning. Movement starts within MOVE; floating places its center under your finger. Dead zone applies to stick mode and movement. A screen-width swipe turns 180 degrees at sensitivity 1. Gyro aim turns the view as you turn the phone (sensitivity 1 = the phone's own turn) and works alongside swipes and a controller; 'only while a finger is on LOOK or FIRE' lets you lift to re-center, like lifting a mouse. Layout uses safe screen fractions and adapts around notches. Options stay temporary until SAVE.");box.addView(help);
        String[] colors={"CE blue","Cyan","White","Amber","Green"};int[] values={0xff69c9ff,0xff65eeee,0xffeeeeee,0xffffbd65,0xff8be298};
        Button color=new Button(getContext());color.setText("HUD color");box.addView(color);color.setOnClickListener(v->new GamepadNavigation.Builder(getContext()).setTitle("HUD color").setItems(colors,(d,i)->{layout.color=values[i];invalidate();}).show());
        ScrollView scroll=new ScrollView(getContext());scroll.addView(box);optionsDialog[0]=new GamepadNavigation.Builder(getContext()).setTitle("Touch options").setView(scroll).setPositiveButton("Back to editor",null).create();optionsDialog[0].show();
    }

    @Override protected void onDetachedFromWindow() {
        releaseAll();
        super.onDetachedFromWindow();
    }
}
