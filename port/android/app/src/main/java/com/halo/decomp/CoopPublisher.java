package com.halo.decomp;

import android.app.Activity;
import android.os.SystemClock;
import android.widget.Toast;
import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import javax.net.ssl.HttpsURLConnection;

/** Opt-in, live-native-host publication using the community browser's HTTP API. */
final class CoopPublisher implements AutoCloseable {
    private final Activity activity;
    private final File status;
    private final ScheduledExecutorService worker = Executors.newSingleThreadScheduledExecutor();
    private volatile boolean closed;
    private String listed = "", lastState = "";
    private long lastAttempt;
    private boolean warned;

    CoopPublisher(Activity activity, File root) {
        this.activity = activity;
        status = new File(root, "coop_status.txt");
        worker.scheduleWithFixedDelay(this::update, 2, 2, TimeUnit.SECONDS);
    }

    private int post(String operation, String body) throws Exception {
        HttpsURLConnection request = (HttpsURLConnection)new URL("https://halo.milenko.org/v1/" + operation).openConnection();
        try {
            request.setRequestMethod("POST"); request.setDoOutput(true);
            request.setInstanceFollowRedirects(false);
            request.setConnectTimeout(5000); request.setReadTimeout(5000);
            request.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
            byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
            request.setFixedLengthStreamingMode(bytes.length);
            try (OutputStream out = request.getOutputStream()) { out.write(bytes); }
            return request.getResponseCode();
        } finally { request.disconnect(); }
    }

    private void withdraw() {
        if (listed.isEmpty()) return;
        try {
            int code = post("withdraw", "invite=" + listed);
            RunLog.line("Campaign directory withdrawal HTTP " + code);
            if (code == 200) { listed = ""; lastState = ""; }
        } catch (Exception e) { RunLog.line("Campaign withdrawal failed: " + e.getClass().getSimpleName()); }
    }

    private void update() {
        if (closed) return;
        try {
            long age = System.currentTimeMillis() - status.lastModified();
            if (!status.isFile() || age < -5000 || age > 15000 || status.length() > 256) { withdraw(); return; }
            byte[] bytes = new byte[257];
            int used = 0;
            try (FileInputStream in = new FileInputStream(status)) {
                for (int count; used < bytes.length && (count = in.read(bytes, used, bytes.length - used)) > 0;) used += count;
            }
            if (used == bytes.length) { withdraw(); return; }
            String state = new String(bytes, 0, used, StandardCharsets.UTF_8).trim();
            String[] fields = state.split("\\s+");
            if (fields.length != 7 || !fields[0].equals("1") || !fields[1].equals("1")) { withdraw(); return; }
            int mission = Integer.parseInt(fields[2]), difficulty = Integer.parseInt(fields[3]);
            int players = Integer.parseInt(fields[4]), open = Integer.parseInt(fields[5]);
            String invite = ServerInvite.normalize(fields[6]);
            if (mission < 0 || mission >= CoopLauncher.MAPS.length || difficulty < 0 || difficulty > 3
                || players < 1 || players > 2 || open < 0 || open > 1 || invite == null) { withdraw(); return; }
            String code = invite.substring("halo://join/".length());
            if (!listed.isEmpty() && !listed.equals(code)) { withdraw(); if (!listed.isEmpty()) return; }
            long now = SystemClock.elapsedRealtime();
            if (now - lastAttempt < (state.equals(lastState) ? 20000 : 3000)) return;
            lastAttempt = now;
            String[] levels = {"Easy", "Normal", "Heroic", "Legendary"};
            String form = "invite=" + code + "&name=" + URLEncoder.encode("Halo CE co-op - " + levels[difficulty], "UTF-8")
                + "&map=" + CoopLauncher.MAPS[mission] + "&engine=0&players=" + players
                + "&maximum_players=2&open=" + open + "&score_limit=0&teams=0&version="
                + ServerBrowser.CAMPAIGN_VERSION + "&roster=";
            // Keep the invite for withdrawal even if the response is lost/rejected after processing.
            listed = code;
            int http = post("announce", form);
            if (http != 200) throw new java.io.IOException("HTTP " + http);
            if (lastState.isEmpty()) notice("Campaign lobby listed publicly.");
            lastState = state;
            warned = false;
            RunLog.line("Campaign directory heartbeat accepted: mission=" + CoopLauncher.MAPS[mission]
                + " players=" + players + " open=" + open + " version=" + ServerBrowser.CAMPAIGN_VERSION);
        } catch (Exception e) {
            RunLog.line("Campaign directory publication failed: " + e.getClass().getSimpleName() + ": " + e.getMessage());
            if (!warned) notice("Public co-op listing unavailable. Share the game's private invite instead.");
            warned = true;
        }
    }

    private void notice(String message) {
        activity.runOnUiThread(() -> { if (!closed && !activity.isFinishing()) Toast.makeText(activity, message, Toast.LENGTH_LONG).show(); });
    }

    @Override public synchronized void close() {
        if (closed) return;
        closed = true;
        worker.execute(this::withdraw);
        worker.shutdown();
    }

    void closeBeforeNativeExit() {
        close();
        try {
            if (!worker.awaitTermination(3, TimeUnit.SECONDS))
                RunLog.line("Campaign withdrawal still pending at exit; directory expiry will remove a stale listing");
        } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
    }
}
