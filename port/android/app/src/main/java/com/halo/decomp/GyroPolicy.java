package com.halo.decomp;

/** Gyro aim math, tested without Android. Screen axes: x right, y up, z toward
 * the player. A turn's radians go out as a swipe's do: positive yaw turns
 * left, positive pitch looks up. */
final class GyroPolicy {
    static final int OFF=0, ALWAYS=1, WHILE_TOUCHING=2;
    static final String[] MODES={"Off","Always on","Only while a finger is on LOOK or FIRE"};
    /** below this speed (rad/s) a turn is eased off, so a phone held still does not creep */
    static final float TIGHTEN=.02f;
    /** the most time one sample may stand for (s): a stalled sensor cannot jerk the view */
    static final float LONGEST_STEP=.05f;
    /** player-space yaw: how much a tilted phone's world turn may grow toward its screen turn */
    static final float RELAX=1.41f;

    static int mode(int value) { return value==ALWAYS||value==WHILE_TOUCHING?value:OFF; }

    /** Device axes to screen axes for Surface.ROTATION_0..270 (Android's
     * remapCoordinateSystem mapping, as its accelerometer sample uses). */
    static void toScreen(int rotation,float[] device,float[] screen) {
        float x=device[0],y=device[1];
        switch(rotation&3) {
            case 1: screen[0]=-y;screen[1]=x;break;
            case 2: screen[0]=-x;screen[1]=-y;break;
            case 3: screen[0]=y;screen[1]=-x;break;
            default: screen[0]=x;screen[1]=y;
        }
        screen[2]=device[2];
    }

    /** One gyro sample's look turn in radians, out[0] yaw and out[1] pitch.
     * rate: the screen's turn (rad/s); up: the gravity sensor's reading in
     * screen axes (it points up), or null when the phone has none. With it,
     * turning the body turns the view however far the phone is tilted back. */
    static void step(float[] rate,float[] up,float seconds,float gainX,float gainY,boolean invert,float[] out) {
        out[0]=out[1]=0;
        if(!(seconds>0)||!finite(rate[0])||!finite(rate[1])||!finite(rate[2])) return;
        seconds=Math.min(seconds,LONGEST_STEP);
        float yaw=rate[1],pitch=rate[0];
        if(up!=null&&finite(up[1])&&finite(up[2])) {
            float length=(float)Math.sqrt(up[0]*up[0]+up[1]*up[1]+up[2]*up[2]);
            if(length>1) {
                float world=(up[1]*rate[1]+up[2]*rate[2])/length;
                float screen=(float)Math.sqrt(rate[1]*rate[1]+rate[2]*rate[2]);
                yaw=Math.copySign(Math.min(Math.abs(world)*RELAX,screen),world);
            }
        }
        float speed=(float)Math.sqrt(yaw*yaw+pitch*pitch);
        if(speed<TIGHTEN) { yaw*=speed/TIGHTEN;pitch*=speed/TIGHTEN; }
        out[0]=yaw*seconds*TouchLayout.bound(gainX,.25f,4,1);
        out[1]=pitch*seconds*TouchLayout.bound(gainY,.25f,4,1)*(invert?-1:1);
    }

    private static boolean finite(float v) { return Float.isFinite(v); }
}
