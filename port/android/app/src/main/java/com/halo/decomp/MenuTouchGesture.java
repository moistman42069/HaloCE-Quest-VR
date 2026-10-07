package com.halo.decomp;

/** One tap owns a menu action. Extra contacts, cancellation and long drags do
 * not select anything; a menu's closing finger cannot become a gameplay press. */
final class MenuTouchGesture {
    private int pointer = -1;
    private float startX, startY;
    private boolean back, dragged;
    void begin(int id, float x, float y, boolean isBack) {
        pointer=id; startX=x; startY=y; back=isBack; dragged=false;
    }
    int pointer() { return pointer; }
    boolean back() { return back; }
    void move(float x, float y, float slop) {
        if (!Float.isFinite(x) || !Float.isFinite(y) || Math.abs(x-startX)>slop || Math.abs(y-startY)>slop) dragged=true;
    }
    int end(int id, float x, float y, float slop, boolean isBack) {
        if(id!=pointer || pointer<0) return 0;
        move(x,y,slop);
        int action=dragged || back!=isBack ? 0 : back ? 2 : 1;
        cancel(); return action;
    }
    void cancel() { pointer=-1; dragged=false; }
}
