package com.halo.decomp;

/** Device-independent touch settings and bounded geometry; tested without Android. */
final class TouchLayout {
    static final int COUNT=19;
    final float[] x=new float[COUNT],y=new float[COUNT],size=new float[COUNT],alpha=new float[COUNT];
    float scale=1f,opacity=.65f,sensitivityX=1f,sensitivityY=1f,deadZone=.08f;
    boolean swipe=true,floating=false,invert=false,lookAnywhere=false;
    int color=0xff69c9ff;
    /** gyro aim (GyroPolicy modes; off by default), its sensitivities (1 = the phone's own turn) and invert */
    int gyroMode=GyroPolicy.OFF;
    float gyroX=1f,gyroY=1f;
    boolean gyroInvert=false;
    static final float[] DEFAULT_X={.14f,.67f,.91f,.91f,.96f,.83f,.80f,.28f,.80f,.10f,.21f,.32f,.56f,.44f,.40f,.40f,.34f,.46f,.94f};
    static final float[] DEFAULT_Y={.74f,.75f,.42f,.76f,.59f,.61f,.42f,.82f,.84f,.38f,.38f,.38f,.10f,.10f,.60f,.84f,.72f,.72f,.10f};
    TouchLayout() { for(int i=0;i<COUNT;i++) { x[i]=DEFAULT_X[i];y[i]=DEFAULT_Y[i];size[i]=alpha[i]=1; } }
    static float bound(float value,float min,float max,float fallback) {
        return Float.isFinite(value)?Math.max(min,Math.min(max,value)):fallback;
    }
    void sanitize() {
        scale=bound(scale,.65f,1.5f,1); opacity=bound(opacity,.15f,1,.65f);
        sensitivityX=bound(sensitivityX,.25f,3,1);sensitivityY=bound(sensitivityY,.25f,3,1);
        deadZone=bound(deadZone,0,.30f,.08f);
        gyroMode=GyroPolicy.mode(gyroMode);gyroX=bound(gyroX,.25f,4,1);gyroY=bound(gyroY,.25f,4,1);
        for(int i=0;i<COUNT;i++) { x[i]=bound(x[i],0,1,DEFAULT_X[i]);y[i]=bound(y[i],0,1,DEFAULT_Y[i]);
            size[i]=bound(size[i],.65f,1.6f,1);alpha[i]=bound(alpha[i],.15f,1,1); }
    }
    static float axis(float delta,float other,float radius,float deadZone) {
        if(!Float.isFinite(delta)||!Float.isFinite(other)||!Float.isFinite(radius)||radius<=0) return 0;
        float x=delta/radius,y=other/radius,length=(float)Math.sqrt(x*x+y*y);
        return length<=deadZone?0:x*Math.min(1,(length-deadZone)/(1-deadZone))/length;
    }
    static float position(float normalized,float length,float radius) {
        return Math.max(radius,Math.min(length-radius,normalized*length));
    }
}
