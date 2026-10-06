package com.halo.decomp;

import android.app.Activity;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.view.Display;

/** Flat phone gyro aim, an option (off by default). The phone's turn reaches
 * the game as a swipe's look turn does: player one, relative radians, dropped
 * by the game in menus. Listens only while the game is resumed, focused and
 * the option is on; nothing is sent while the touch layout is being edited. */
final class GyroAim implements SensorEventListener {
    private final Activity activity;
    private final TouchControls touch;
    private final SensorManager sensors;
    private final Sensor gyroscope, gravity;
    private final float[] rate=new float[3], up=new float[3], turn=new float[2];
    private boolean resumed, focused, listening, haveUp;
    private long last, rotationAt;
    private int rotation;

    GyroAim(Activity a,TouchControls t) {
        activity=a;touch=t;
        sensors=(SensorManager)a.getSystemService(Context.SENSOR_SERVICE);
        gyroscope=sensors==null?null:sensors.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        gravity=sensors==null?null:sensors.getDefaultSensor(Sensor.TYPE_GRAVITY);
        RunLog.line("Gyro aim: "+(gyroscope==null?"no gyroscope on this device":"gyroscope found"+(gravity==null?", no gravity sensor (screen-axis turning)":", gravity sensor (turns follow the body)"))
            +"; option "+GyroPolicy.MODES[touch.gyroMode()]);
    }

    static boolean available(Context c) {
        SensorManager s=(SensorManager)c.getSystemService(Context.SENSOR_SERVICE);
        return s!=null&&s.getDefaultSensor(Sensor.TYPE_GYROSCOPE)!=null;
    }

    void resume() { resumed=true;update(); }
    void pause() { resumed=false;update(); }
    void focus(boolean hasFocus) { focused=hasFocus;update(); }

    /** called again whenever the option changes */
    void update() {
        boolean want=resumed&&focused&&gyroscope!=null&&touch.gyroMode()!=GyroPolicy.OFF;
        if(want==listening) return;
        listening=want;last=0;haveUp=false;rotationAt=0;
        if(want) {
            sensors.registerListener(this,gyroscope,SensorManager.SENSOR_DELAY_GAME);
            if(gravity!=null) sensors.registerListener(this,gravity,SensorManager.SENSOR_DELAY_GAME);
        } else sensors.unregisterListener(this);
        RunLog.line("Gyro aim "+(want?"listening ("+GyroPolicy.MODES[touch.gyroMode()]+")":"stopped"));
    }

    @Override public void onSensorChanged(SensorEvent e) {
        if(!listening) return;
        if(e.timestamp-rotationAt>250_000_000L||rotationAt==0) { rotation=displayRotation();rotationAt=e.timestamp; }
        if(e.sensor.getType()==Sensor.TYPE_GRAVITY) { GyroPolicy.toScreen(rotation,e.values,up);haveUp=true;return; }
        float seconds=last==0?0:(e.timestamp-last)*1e-9f;last=e.timestamp;
        if(!touch.gyroAiming()) return;
        GyroPolicy.toScreen(rotation,e.values,rate);
        GyroPolicy.step(rate,haveUp?up:null,seconds,touch.gyroX(),touch.gyroY(),touch.gyroInvert(),turn);
        if(turn[0]!=0||turn[1]!=0) TouchControls.look(turn[0],turn[1]);
    }

    @Override public void onAccuracyChanged(Sensor sensor,int accuracy) {}

    @SuppressWarnings("deprecation")
    private int displayRotation() {
        Display d=Build.VERSION.SDK_INT>=30?activity.getDisplay():activity.getWindowManager().getDefaultDisplay();
        return d==null?rotation:d.getRotation();
    }
}
