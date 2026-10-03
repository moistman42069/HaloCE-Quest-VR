package com.halo.decomp;

import android.content.Context;
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
    private static final int BUTTON=0, MOVE=1, LOOK=2, FIRE_LOOK=3, TOGGLE=4;
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final SparseArray<Contact> contacts = new SparseArray<>();
    private Control[] controls = new Control[0];
    private boolean controlsShown = true;
    private int insetLeft, insetTop, insetRight, insetBottom;
    private float textSize;

    private static final class Control {
        final String label;
        final float x, y, radius;
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
    private static final class Contact {
        final Control control;
        final float originX, originY;
        float x, y;
        Contact(Control control, float x, float y) {
            this.control=control; this.x=x; this.y=y;
            originX=control.kind == FIRE_LOOK ? x : control.x;
            originY=control.kind == FIRE_LOOK ? y : control.y;
        }
    }

    private static native void nativeState(int lx, int ly, int rx, int ry,
                                           int buttons, boolean reset);

    TouchControls(Context context) {
        super(context);
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
        float unit=Math.min(w/1000f, h/500f);
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
            new Control("Touch", left+w*.94f, top+h*.10f, r, 0, TOGGLE)
        };
        invalidate();
    }

    void releaseAll() {
        contacts.clear();
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
        if (action == MotionEvent.ACTION_DOWN) contacts.clear();
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            float x=event.getX(index), y=event.getY(index);
            for (int i=controls.length-1; i>=0; i--) {
                Control c=controls[i];
                if ((!controlsShown && c.kind != TOGGLE) || !c.contains(x, y) || owned(c)) continue;
                if (c.kind == TOGGLE) {
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
            if (c != null) { c.x=event.getX(i); c.y=event.getY(i); }
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
            if (c.control.kind == BUTTON) continue;
            float radius=c.control.kind == FIRE_LOOK ? c.control.radius*1.4f : c.control.radius;
            float x=(c.x-c.originX)/radius, y=(c.originY-c.y)/radius;
            float length=(float)Math.sqrt(x*x+y*y);
            // Radial dead zone, then full analog range. No per-axis square gate.
            float scale=length <= .08f ? 0 : Math.min(1, (length-.08f)/.92f)/length;
            int ax=Math.round(x*scale*32767), ay=Math.round(y*scale*32767);
            if (c.control.kind == MOVE) { lx=ax; ly=ay; }
            else if (ax* (long)ax + ay*(long)ay > rx*(long)rx + ry*(long)ry) { rx=ax; ry=ay; }
        }
        nativeState(lx, ly, rx, ry, buttons, false);
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        for (Control c : controls) {
            if (!controlsShown && c.kind != TOGGLE) continue;
            boolean pressed=owned(c);
            paint.setStyle(Paint.Style.FILL);
            paint.setColor(pressed ? 0x9958a9c4 : 0x44304048);
            canvas.drawCircle(c.x, c.y, c.radius, paint);
            paint.setStyle(Paint.Style.STROKE);
            paint.setStrokeWidth(2*getResources().getDisplayMetrics().density);
            paint.setColor(pressed ? 0xddffffff : 0x8899b8c8);
            canvas.drawCircle(c.x, c.y, c.radius, paint);
            paint.setStyle(Paint.Style.FILL);
            paint.setTextSize(textSize);
            paint.setTextAlign(Paint.Align.CENTER);
            paint.setColor(Color.WHITE);
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
                paint.setColor(0x6699ccee);
                canvas.drawCircle(c.x+x, c.y+y, c.radius*.28f, paint);
            }
        }
    }

    @Override protected void onDetachedFromWindow() {
        releaseAll();
        super.onDetachedFromWindow();
    }
}
