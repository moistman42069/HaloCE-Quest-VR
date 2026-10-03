package com.halo.decomp;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.hardware.input.InputManager;
import android.os.Handler;
import android.os.Looper;
import android.view.InputDevice;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.widget.*;
import java.util.Locale;

/** Flat Android settings and actual SDL-ready device monitoring. */
final class GamepadSupport implements InputManager.InputDeviceListener {
    private final Activity activity;
    private final TouchControls touch;
    private final Handler handler=new Handler(Looper.getMainLooper());
    private final InputManager manager;
    private boolean running;
    private int lastCount=-1;
    private static native int nativeCount();
    private static native void nativeSettings(float moveDead,float lookDead,float gainX,float gainY,float triggerDead,boolean rumble,boolean swap,boolean focused);
    private final Runnable poll=new Runnable(){public void run(){if(running){refresh();handler.postDelayed(this,500);}}};
    static SharedPreferences prefs(Context c){return c.getSharedPreferences("phone-controls",0);}
    static int mode(Context c){return prefs(c).getInt("controller_touch_mode",GamepadPolicy.AUTO);}
    GamepadSupport(Activity a,TouchControls t){activity=a;touch=t;manager=(InputManager)a.getSystemService(Context.INPUT_SERVICE);}
    void resume(){if(running)return;running=true;manager.registerInputDeviceListener(this,handler);apply(activity.hasWindowFocus());poll.run();}
    void pause(){running=false;handler.removeCallbacks(poll);manager.unregisterInputDeviceListener(this);apply(false);touch.releaseAll();}
    void focus(boolean focused){apply(running&&focused);}
    private void apply(boolean focused){SharedPreferences p=prefs(activity);
        nativeSettings(p.getFloat("pad_move_dead",9000f/32767),p.getFloat("pad_look_dead",9000f/32767),
            p.getFloat("pad_gain_x",1),p.getFloat("pad_gain_y",1),p.getFloat("pad_trigger_dead",.05f),
            p.getBoolean("pad_rumble",true),p.getBoolean("pad_swap",false),focused);}
    private void refresh(){int count=nativeCount();touch.controllerVisibility(mode(activity),count);
        if(count!=lastCount){RunLog.line("Flat controller: SDL-ready="+count+" touch policy="+mode(activity));lastCount=count;}}
    @Override public void onInputDeviceAdded(int id){refresh();}
    @Override public void onInputDeviceRemoved(int id){refresh();}
    @Override public void onInputDeviceChanged(int id){refresh();}

    static void show(Activity a){
        SharedPreferences p=prefs(a); LinearLayout body=new LinearLayout(a);body.setOrientation(1);body.setPadding(24,8,24,8);
        TextView note=new TextView(a);note.setText("Xbox-style USB/Bluetooth gamepads use Android + SDL mappings. D-pad / left stick navigate; A confirms; B returns. In-game Options keeps Halo's layout, look sensitivity and invert settings. Changes below apply on the next game launch.");body.addView(note);
        Spinner visibility=new Spinner(a);visibility.setAdapter(new ArrayAdapter<>(a,android.R.layout.simple_spinner_dropdown_item,new String[]{"Auto: hide touch with a ready controller","Always show touch","Always hide touch"}));visibility.setSelection(Math.max(0,Math.min(2,mode(a))));body.addView(visibility);
        SeekBar move=slider(a,body,"Movement dead zone (%)",0,45,Math.round(p.getFloat("pad_move_dead",9000f/32767)*100));
        SeekBar look=slider(a,body,"Aim dead zone (%)",0,45,Math.round(p.getFloat("pad_look_dead",9000f/32767)*100));
        SeekBar x=slider(a,body,"Horizontal stick response (%)",25,200,Math.round(p.getFloat("pad_gain_x",1)*100));
        SeekBar y=slider(a,body,"Vertical stick response (%)",25,200,Math.round(p.getFloat("pad_gain_y",1)*100));
        SeekBar trigger=slider(a,body,"Trigger dead zone (%)",0,40,Math.round(p.getFloat("pad_trigger_dead",.05f)*100));
        CheckBox rumble=new CheckBox(a);rumble.setText("Controller vibration (when supported)");rumble.setChecked(p.getBoolean("pad_rumble",true));body.addView(rumble);
        CheckBox swap=new CheckBox(a);swap.setText("Swap gameplay A/B and X/Y (Nintendo labels)");swap.setChecked(p.getBoolean("pad_swap",false));body.addView(swap);
        TextView help=new TextView(a);help.setText("Auto restores touch after the last supported pad disconnects. Always hide is an explicit override; change it here if needed. Xbox positions are the default on PlayStation / Nintendo pads. Vibration depends on the controller, connection and Android driver.");body.addView(help);
        Button test=new Button(a);test.setText("Controller input check");test.setOnClickListener(v->diagnostic(a));body.addView(test);
        ScrollView scroll=new ScrollView(a);scroll.addView(body);
        new GamepadNavigation.Builder(a).setTitle("Controller & touch settings").setView(scroll)
            .setPositiveButton("Save",(d,w)->p.edit().putInt("controller_touch_mode",visibility.getSelectedItemPosition())
                .putFloat("pad_move_dead",move.getProgress()/100f).putFloat("pad_look_dead",look.getProgress()/100f)
                .putFloat("pad_gain_x",x.getProgress()/100f).putFloat("pad_gain_y",y.getProgress()/100f)
                .putFloat("pad_trigger_dead",trigger.getProgress()/100f).putBoolean("pad_rumble",rumble.isChecked()).putBoolean("pad_swap",swap.isChecked()).apply())
            .setNegativeButton("Cancel",null).show();
    }
    private static SeekBar slider(Activity a,LinearLayout body,String title,int min,int max,int value){
        TextView text=new TextView(a);body.addView(text);SeekBar bar=new SeekBar(a);bar.setMin(min);bar.setMax(max);bar.setProgress(value);body.addView(bar);
        text.setText(title+": "+bar.getProgress());bar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener(){
            public void onProgressChanged(SeekBar b,int v,boolean user){text.setText(title+": "+v);}
            public void onStartTrackingTouch(SeekBar b){}public void onStopTrackingTouch(SeekBar b){} });return bar;
    }
    static void diagnostic(Activity a){
        TextView text=new TextView(a);text.setPadding(24,24,24,24);text.setText("Press buttons and move both sticks/triggers. B closes this check. This checks Android events; gameplay recognition is logged by SDL.\n"+devices());
        AlertDialog dialog=new AlertDialog(a){
            @Override public boolean dispatchKeyEvent(KeyEvent e){if(GamepadNavigation.controller(e.getDevice())&&e.getKeyCode()!=KeyEvent.KEYCODE_BUTTON_B){
                text.setText(devices()+"\n"+KeyEvent.keyCodeToString(e.getKeyCode())+" "+(e.getAction()==0?"DOWN":"UP"));return true;}
                if(e.getKeyCode()==KeyEvent.KEYCODE_BUTTON_B){if(e.getAction()==KeyEvent.ACTION_UP)dismiss();return true;}return super.dispatchKeyEvent(e);}
            @Override public boolean dispatchGenericMotionEvent(MotionEvent e){if(GamepadNavigation.controller(e.getDevice())){
                text.setText(devices()+String.format(Locale.ROOT,"\nLX %.2f LY %.2f\nZ %.2f RZ %.2f RX %.2f RY %.2f\nLT %.2f RT %.2f\nBrake %.2f Gas %.2f\nHat %.0f %.0f",e.getAxisValue(0),e.getAxisValue(1),e.getAxisValue(11),e.getAxisValue(14),e.getAxisValue(12),e.getAxisValue(13),e.getAxisValue(17),e.getAxisValue(18),e.getAxisValue(23),e.getAxisValue(22),e.getAxisValue(15),e.getAxisValue(16)));return true;}return super.dispatchGenericMotionEvent(e);}
        };dialog.setTitle("Controller input check");dialog.setView(text);dialog.setButton(AlertDialog.BUTTON_NEGATIVE,"Close",(d,w)->d.dismiss());dialog.show();
    }
    private static String devices(){StringBuilder s=new StringBuilder();for(int id:InputDevice.getDeviceIds()){InputDevice d=InputDevice.getDevice(id);if(GamepadNavigation.controller(d))s.append(d.getName()).append(" (USB/Bluetooth input)\n");}return s.length()==0?"No Android gamepad detected. Connect or reconnect a controller.":s.toString();}
}
