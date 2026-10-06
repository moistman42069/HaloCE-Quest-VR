package com.halo.decomp;

import android.content.Context;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.view.Display;
import android.view.WindowManager;
import android.view.ViewGroup;

import org.libsdl.app.SDLActivity;

/**
 * The game: SDL3's activity, running libmain.so (port/android/host), which
 * loads the game image from the APK's assets.
 */
public class HaloActivity extends SDLActivity {
    /** lets system link's broadcasts in over Wi-Fi while the game runs */
    private WifiManager.MulticastLock multicastLock;
    private TouchControls touchControls;
    private GamepadSupport gamepads;
    private PvpPublisher pvpPublisher;

    @Override
    protected String[] getLibraries() {
        return new String[] { "SDL3", "main" };
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        RunLog.start(this);
        RunLog.line("Game activity creating; native logging will use the same launch file");
        RunLog.line("Network: " + NetworkSettings.describe(this));
        java.io.File gameRoot = getExternalFilesDir(null);
        java.io.File shared = new java.io.File("/sdcard/Documents/HaloCE");
        if (BuildConfig.APPLICATION_ID.endsWith(".vr") && new java.io.File(shared, "maps/ui.map").isFile()) gameRoot = shared;
        gameRoot=GameDataLibrary.activeRoot(gameRoot);
        if (gameRoot != null) { new java.io.File(gameRoot, "coop_status.txt").delete(); new java.io.File(gameRoot, "pvp_status.txt").delete(); }
        super.onCreate(savedInstanceState);
        if (gameRoot != null) { pvpPublisher = new PvpPublisher(this, gameRoot); }
        if (!BuildConfig.APPLICATION_ID.endsWith(".vr") && mLayout != null) {
            touchControls = new TouchControls(this);
            mLayout.addView(touchControls, new ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
            touchControls.requestApplyInsets();
            gamepads = new GamepadSupport(this,touchControls);
            RunLog.line("Phone touch controls initialized: player-one merge; multi-touch; hold fire and drag to aim");
        }
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        preferHighestRefreshRate();
        acquireMulticastLock();
        // a new version looked for while the game starts
        Updater.start(this);
    }

    @Override
    protected void onDestroy() {
        if (gamepads != null) gamepads.pause();
        if (touchControls != null) touchControls.releaseAll();
        if (pvpPublisher != null) pvpPublisher.close();
        RunLog.line("Game activity destroying");
        if (multicastLock != null && multicastLock.isHeld())
            multicastLock.release();
        multicastLock = null;
        super.onDestroy();
    }

    /** Called once by SDL's native main; ownership of the duplicate passes to C. */
    public int openGameLog() { return RunLog.nativeDescriptor(); }

    /** Native normal exit runs on the game thread; give withdrawal a bounded chance before _exit. */
    public void prepareGameExit() {
        if (pvpPublisher != null) pvpPublisher.closeBeforeNativeExit();
        RunLog.line("Native exit cleanup finished");
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (gamepads != null) gamepads.resume();
        RunLog.line("Game activity resumed");
    }

    @Override
    protected void onPause() {
        if (gamepads != null) gamepads.pause();
        if (touchControls != null) touchControls.releaseAll();
        RunLog.line("Game activity paused / headset focus changed");
        super.onPause();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        if (gamepads != null) gamepads.focus(hasFocus);
        if (!hasFocus && touchControls != null) touchControls.releaseAll();
        super.onWindowFocusChanged(hasFocus);
    }

    /**
     * Many phones drop the Wi-Fi's broadcast and multicast datagrams to
     * save power unless an app holds this: without it they would not see
     * system link games on the local network, nor be seen hosting one.
     */
    private void acquireMulticastLock() {
        try {
            WifiManager wifi = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
            if (wifi == null)
                return;
            multicastLock = wifi.createMulticastLock("halo-system-link");
            multicastLock.setReferenceCounted(false);
            multicastLock.acquire();
            RunLog.line("System Link Wi-Fi multicast lock acquired");
        } catch (RuntimeException e) {
            // (no Wi-Fi, or not allowed: the local network may miss games)
            multicastLock = null;
            RunLog.line("System Link multicast unavailable: " + e);
        }
    }

    /**
     * The game draws a frame at every display refresh, between its 30 Hz
     * ticks (port/linux/game/render_interpolation.c); Android otherwise
     * often keeps an app at 60 Hz on a faster display.
     */
    private void preferHighestRefreshRate() {
        Display display = getWindowManager().getDefaultDisplay();
        Display.Mode current = display.getMode();
        Display.Mode best = current;

        for (Display.Mode mode : display.getSupportedModes()) {
            if (mode.getPhysicalWidth() == current.getPhysicalWidth() &&
                mode.getPhysicalHeight() == current.getPhysicalHeight() &&
                mode.getRefreshRate() > best.getRefreshRate()) {
                best = mode;
            }
        }
        WindowManager.LayoutParams attributes = getWindow().getAttributes();
        attributes.preferredDisplayModeId = best.getModeId();
        getWindow().setAttributes(attributes);
    }
}
