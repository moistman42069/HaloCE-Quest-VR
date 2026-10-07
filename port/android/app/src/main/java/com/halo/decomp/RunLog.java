package com.halo.decomp;

import android.content.ContentUris;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.ParcelFileDescriptor;
import android.provider.MediaStore;
import android.util.Log;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/** A public Download/HaloCE log from launcher startup through native exit. */
final class RunLog {
    private static ParcelFileDescriptor publicFile;
    private static FileOutputStream output;
    private static boolean started;
    private static String destination = "Log not started";

    static synchronized void start(Context context) {
        if (started) return;
        started = true;
        String name = "halo_log_" + new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss-SSS", Locale.US)
            .format(new Date()) + "_" + android.os.Process.myPid() + ".txt";
        String failure = null;
        try {
            if (Build.VERSION.SDK_INT >= 29) {
                ContentValues values = new ContentValues();
                values.put(MediaStore.Downloads.DISPLAY_NAME, name);
                values.put(MediaStore.Downloads.MIME_TYPE, "text/plain");
                values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/HaloCE");
                // Visible immediately, including if a crash prevents a shutdown callback.
                values.put(MediaStore.Downloads.IS_PENDING, 0);
                Uri uri = context.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                if (uri == null) throw new java.io.IOException("Downloads provider returned no file");
                try {
                    publicFile = context.getContentResolver().openFileDescriptor(uri, "wa");
                    if (publicFile == null) throw new java.io.IOException("Downloads descriptor unavailable");
                } catch (Exception e) {
                    context.getContentResolver().delete(uri, null, null);
                    throw e;
                }
            } else {
                File folder = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "HaloCE");
                folder.mkdirs();
                publicFile = ParcelFileDescriptor.open(new File(folder, name),
                    ParcelFileDescriptor.MODE_CREATE | ParcelFileDescriptor.MODE_APPEND | ParcelFileDescriptor.MODE_WRITE_ONLY);
            }
            destination = "Download/HaloCE/" + name;
        } catch (Exception e) {
            failure = e.toString();
            try {
                File folder = context.getExternalFilesDir(null);
                if (folder == null) folder = context.getFilesDir();
                File fallback = new File(folder, name);
                publicFile = ParcelFileDescriptor.open(fallback,
                    ParcelFileDescriptor.MODE_CREATE | ParcelFileDescriptor.MODE_APPEND | ParcelFileDescriptor.MODE_WRITE_ONLY);
                destination = fallback.getAbsolutePath();
            } catch (Exception fallback) {
                destination = "Log creation failed: " + fallback.getClass().getSimpleName();
                Log.e("halo", destination, fallback);
            }
        }
        if (publicFile != null) {
            // Own a duplicate so neither stream can close the other's descriptor.
            try { output = new ParcelFileDescriptor.AutoCloseOutputStream(ParcelFileDescriptor.dup(publicFile.getFileDescriptor())); }
            catch (Exception e) { Log.e("halo", "Cannot open Java launch log", e); }
        }
        line("HaloCE launch; package=" + context.getPackageName() + " version=" + BuildConfig.VERSION_NAME
            + " code=" + BuildConfig.VERSION_CODE);
        line("device=" + Build.MANUFACTURER + " " + Build.MODEL + " Android=" + Build.VERSION.RELEASE
            + " SDK=" + Build.VERSION.SDK_INT + " ABI=" + java.util.Arrays.toString(Build.SUPPORTED_ABIS));
        line("Log destination: " + destination);
        android.app.ActivityManager manager = (android.app.ActivityManager)context.getSystemService(Context.ACTIVITY_SERVICE);
        if (manager != null) {
            android.app.ActivityManager.MemoryInfo memory = new android.app.ActivityManager.MemoryInfo();
            manager.getMemoryInfo(memory);
            line("Memory total=" + memory.totalMem + " available=" + memory.availMem + " low=" + memory.lowMemory);
        }
        if (failure != null) line("PUBLIC DOWNLOADS LOG FAILED; private fallback active: " + failure);
        Thread.UncaughtExceptionHandler previous = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((thread, error) -> {
            line("UNCAUGHT JAVA EXCEPTION on " + thread.getName() + ": " + Log.getStackTraceString(error));
            if (previous != null) previous.uncaughtException(thread, error);
        });
        if (Build.VERSION.SDK_INT >= 29) {
            // Only delete this package's own older logs, never another app's files.
            new Thread(() -> prune(context.getApplicationContext()), "halo-log-retention").start();
        }
    }

    static synchronized void line(String text) {
        Log.i("halo", text);
        if (output == null) return;
        try {
            String time = new SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(new Date());
            output.write((time + " [android] " + text + "\n").getBytes(StandardCharsets.UTF_8));
            output.flush();
        } catch (Exception e) { Log.e("halo", "Launch log write failed", e); }
    }

    static synchronized int nativeDescriptor() {
        if (publicFile == null) return -1;
        try { return ParcelFileDescriptor.dup(publicFile.getFileDescriptor()).detachFd(); }
        catch (Exception e) { line("Native log descriptor failed: " + e); return -1; }
    }

    static synchronized String destination() { return destination; }

    private static void prune(Context context) {
        try (Cursor cursor = context.getContentResolver().query(MediaStore.Downloads.EXTERNAL_CONTENT_URI,
            new String[]{MediaStore.Downloads._ID, MediaStore.Downloads.DISPLAY_NAME},
            MediaStore.Downloads.RELATIVE_PATH + "=? AND " + MediaStore.Downloads.OWNER_PACKAGE_NAME + "=?",
            new String[]{Environment.DIRECTORY_DOWNLOADS + "/HaloCE/", context.getPackageName()},
            MediaStore.Downloads.DATE_ADDED + " DESC, " + MediaStore.Downloads._ID + " DESC")) {
            int count = 0;
            while (cursor != null && cursor.moveToNext()) {
                String name = cursor.getString(1);
                if (name == null || !name.startsWith("halo_log_") || !name.endsWith(".txt")) continue;
                if (++count > 10) context.getContentResolver().delete(
                    ContentUris.withAppendedId(MediaStore.Downloads.EXTERNAL_CONTENT_URI, cursor.getLong(0)), null, null);
            }
        } catch (Exception e) { line("Log retention skipped: " + e.getClass().getSimpleName()); }
    }
}
