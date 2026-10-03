package com.halo.decomp;

/** Pure policy shared by UI and focused tests. */
final class GamepadPolicy {
    static final int AUTO=0, SHOW=1, HIDE=2;
    static boolean showTouch(int mode, int connected) {
        return mode == SHOW || (mode != HIDE && connected == 0);
    }
    static float bounded(float value,float min,float max,float fallback) {
        return Float.isFinite(value) ? Math.max(min,Math.min(max,value)) : fallback;
    }
    static int direction(float x,float y) {
        if (!Float.isFinite(x) || !Float.isFinite(y) || Math.max(Math.abs(x),Math.abs(y)) < .55f) return 0;
        return Math.abs(x)>Math.abs(y) ? (x<0?1:2) : (y<0?3:4);
    }
}
