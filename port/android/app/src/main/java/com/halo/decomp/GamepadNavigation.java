package com.halo.decomp;

import android.app.AlertDialog;
import android.content.Context;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.Window;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;

/** Android focus navigation for the launcher and its dialogs. Gameplay stays
 * entirely in SDL; no duplicate Android-to-Xbox button injection. */
final class GamepadNavigation {
    private int direction;
    private int deviceId=-1;
    private final Context context;
    private GamepadNavigation(Context context){this.context=context;}
    private final android.os.Handler handler=new android.os.Handler(android.os.Looper.getMainLooper());
    private Window.Callback repeatTarget;
    private final Runnable repeat=new Runnable(){public void run(){
        if(!controller(InputDevice.getDevice(deviceId))){stop();return;}
        if(direction!=0 && repeatTarget!=null){step(repeatTarget);handler.postDelayed(this,140);}
    }};
    private void stop(){direction=0;repeatTarget=null;handler.removeCallbacks(repeat);}
    private void step(Window.Callback target){
        long now=android.os.SystemClock.uptimeMillis();
        int key=direction==1?KeyEvent.KEYCODE_DPAD_LEFT:direction==2?KeyEvent.KEYCODE_DPAD_RIGHT:
            direction==3?KeyEvent.KEYCODE_DPAD_UP:KeyEvent.KEYCODE_DPAD_DOWN;
        target.dispatchKeyEvent(new KeyEvent(now,now,KeyEvent.ACTION_DOWN,key,0));
        target.dispatchKeyEvent(new KeyEvent(now,now,KeyEvent.ACTION_UP,key,0));
    }
    static boolean controller(InputDevice d) {
        return d != null && !d.isVirtual() &&
            (d.supportsSource(InputDevice.SOURCE_GAMEPAD) || d.supportsSource(InputDevice.SOURCE_JOYSTICK));
    }
    boolean motion(MotionEvent e, Window.Callback target) {
        if (!controller(e.getDevice()) || !e.isFromSource(InputDevice.SOURCE_JOYSTICK)) return false;
        deviceId=e.getDeviceId();
        float x=e.getAxisValue(MotionEvent.AXIS_HAT_X), y=e.getAxisValue(MotionEvent.AXIS_HAT_Y);
        if (x==0 && y==0) { x=e.getAxisValue(MotionEvent.AXIS_X); y=e.getAxisValue(MotionEvent.AXIS_Y); }
        int next=GamepadPolicy.direction(x,y);
        if(next!=direction){
            stop();direction=next;repeatTarget=target;
            if(next!=0){step(target);handler.postDelayed(repeat,300);}
        }
        return true;
    }
    boolean key(KeyEvent e,Window.Callback target) {
        if (!controller(e.getDevice())) return false;
        int mapped;
        int code=e.getKeyCode();
        if(GamepadSupport.prefs(context).getBoolean("pad_swap",false)) {
            if(code==KeyEvent.KEYCODE_BUTTON_A)code=KeyEvent.KEYCODE_BUTTON_B;
            else if(code==KeyEvent.KEYCODE_BUTTON_B)code=KeyEvent.KEYCODE_BUTTON_A;
        }
        switch(code) {
            case KeyEvent.KEYCODE_BUTTON_A: case KeyEvent.KEYCODE_BUTTON_START:
                mapped=KeyEvent.KEYCODE_DPAD_CENTER;break;
            case KeyEvent.KEYCODE_BUTTON_B: mapped=KeyEvent.KEYCODE_BACK;break;
            default:return false;
        }
        target.dispatchKeyEvent(new KeyEvent(e.getDownTime(),e.getEventTime(),e.getAction(),mapped,
            e.getRepeatCount(),e.getMetaState(),e.getDeviceId(),e.getScanCode(),e.getFlags(),e.getSource()));
        return true;
    }
    static void install(Window window) {
        if (BuildConfig.APPLICATION_ID.endsWith(".vr") || window==null) return;
        Window.Callback target=window.getCallback();
        if (target==null || Proxy.isProxyClass(target.getClass())) return;
        GamepadNavigation navigation=new GamepadNavigation(window.getContext());
        // Forward every unrelated Window callback to preserve Android behavior.
        window.setCallback((Window.Callback)Proxy.newProxyInstance(Window.Callback.class.getClassLoader(),
            new Class<?>[]{Window.Callback.class},(proxy,method,args)->{
                if(method.getName().equals("dispatchGenericMotionEvent") && navigation.motion((MotionEvent)args[0],target)) return true;
                if(method.getName().equals("dispatchKeyEvent") && navigation.key((KeyEvent)args[0],target)) return true;
                if(method.getName().equals("onDetachedFromWindow") ||
                    (method.getName().equals("onWindowFocusChanged") && Boolean.FALSE.equals(args[0]))) navigation.stop();
                try { return method.invoke(target,args); }
                catch(InvocationTargetException error) { throw error.getCause(); }
            }));
    }
    static final class Builder extends AlertDialog.Builder {
        Builder(Context context) { super(context); }
        @Override public AlertDialog create() {
            AlertDialog dialog=super.create();install(dialog.getWindow());return dialog;
        }
    }
}
