package com.halo.decomp;

import android.app.Activity;
import android.app.AlertDialog;
import android.widget.ArrayAdapter;
import android.text.InputFilter;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.function.BooleanSupplier;

/**
 * Campaign co-op as OpenCE plays it (since 1.0.9): a network game on a campaign level. Hosting
 * writes coop_host.txt ("2 mission difficulty public most-players"), which the game reads with
 * its main menu up (network_campaign_session.c) and opens as an OpenCE co-op lobby; joining is
 * any co-op game of the same network version, this app's or OpenCE's.
 */
final class CoopLauncher {
    static final String[] MAPS = {"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"};
    // (OpenCE's Server Setup's co-op sizes, 16 by default there; here a smaller lobby, as it starts when full)
    static final int[] PLAYER_CHOICES = {2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128};
    static final int DEFAULT_PLAYERS = 4;
    // test30: the server's name (a network game's name holds 15, as the PvP host's)
    static final int NAME_LENGTH = 15;

    /** a server name the game takes: printable ASCII, NAME_LENGTH at most (empty: the device's) */
    static boolean validName(String name) {
        return name != null && name.matches("[ -~]{0," + NAME_LENGTH + "}");
    }
    private final Activity activity;
    private final File root;
    private final BooleanSupplier ready, start;
    private final ServerBrowser.Join join;

    CoopLauncher(Activity activity, File root, BooleanSupplier ready, BooleanSupplier start, ServerBrowser.Join join) {
        this.activity = activity; this.root = root; this.ready = ready; this.start = start; this.join = join;
    }

    void show() {
        new GamepadNavigation.Builder(activity).setTitle("Campaign co-op")
            .setMessage("Co-op as OpenCE plays it: up to 128 players on Quest, Android, Windows, Mac and Linux "
                + "(hosting on OpenCE network version " + BuildConfig.HALO_NETWORK_VERSION + "), with the same campaign maps. "
                + "Players can join a mission already under way.\n\n"
                + "TO HOST: press Host campaign, pick the mission, difficulty and most players, name your server if you like, leave the public "
                + "box ticked to be listed, and press Host. Start from the lobby when everyone is in (a full "
                + "lobby starts by itself).\n\n"
                + "TO JOIN: in the game, open Multiplayer > System Link: public co-op games (this app's and "
                + "OpenCE's) and games on your Wi-Fi are listed there. Or press Browse / join here to see the "
                + "community list first and pick one.\n\n"
                + "Full steps: launcher > How to join co-op & find servers.")
            .setPositiveButton("Host campaign", (dialog, which) -> host())
            .setNeutralButton("Browse / join", (dialog, which) -> new ServerBrowser(activity, join, true))
            .setNegativeButton("Back", null).show();
    }

    private Spinner select(LinearLayout layout, String[] choices) {
        Spinner spinner = new Spinner(activity);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(activity, android.R.layout.simple_spinner_item, choices);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter); layout.addView(spinner); return spinner;
    }

    private void host() {
        LinearLayout layout = new LinearLayout(activity);
        layout.setOrientation(LinearLayout.VERTICAL);
        int pad = (int)(16 * activity.getResources().getDisplayMetrics().density);
        layout.setPadding(pad, pad, pad, pad);
        Spinner mission = select(layout, new String[]{"The Pillar of Autumn", "Halo", "The Truth and Reconciliation",
            "The Silent Cartographer", "Assault on the Control Room", "343 Guilty Spark", "The Library",
            "Two Betrayals", "Keyes", "The Maw"});
        Spinner difficulty = select(layout, new String[]{"Easy", "Normal", "Heroic", "Legendary"});
        difficulty.setSelection(1);
        String[] counts = new String[PLAYER_CHOICES.length];
        int chosen = 0;
        for (int i = 0; i < counts.length; i++) {
            counts[i] = "Up to " + PLAYER_CHOICES[i] + " players"
                + (PLAYER_CHOICES[i] > 16 ? " (a big game: the host's device and Wi-Fi carry it)" : "");
            if (PLAYER_CHOICES[i] == DEFAULT_PLAYERS) chosen = i;
        }
        Spinner players = select(layout, counts);
        players.setSelection(chosen);
        // test30: the server's name, as the browsers list it (empty: the device's name, as before)
        TextView nameLabel = new TextView(activity);
        nameLabel.setText("Server name (optional, up to " + NAME_LENGTH + " letters, numbers or symbols)");
        layout.addView(nameLabel);
        EditText serverName = new EditText(activity);
        serverName.setSingleLine(true);
        serverName.setHint("The device's name");
        serverName.setFilters(new InputFilter[]{new InputFilter.LengthFilter(NAME_LENGTH)});
        serverName.setText(activity.getSharedPreferences("coop-host", 0).getString("server_name", ""));
        layout.addView(serverName);
        CheckBox publish = new CheckBox(activity);
        publish.setText("Public: list this game in the server browsers (in-game System Link, OpenCE's and the community list)");
        // On by default so others find the game in the browsers.
        publish.setChecked(true);
        layout.addView(publish);
        TextView status = new TextView(activity);
        status.setText("Public: anyone can find and join this game. Untick it to keep it private and share the invite "
            + "the game copies instead.");
        layout.addView(status);
        AlertDialog dialog = new GamepadNavigation.Builder(activity).setTitle("Host campaign")
            .setView(layout).setPositiveButton("Host", null).setNegativeButton("Cancel", null).create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            if (!ready.getAsBoolean()) return;
            int selected = mission.getSelectedItemPosition();
            String name = serverName.getText().toString().trim();
            if (!validName(name)) {
                status.setText("Use up to " + NAME_LENGTH + " plain letters, numbers, spaces or symbols for the server name.");
                return;
            }
            if (root == null || !new File(root, "maps/" + MAPS[selected] + ".map").isFile()) {
                status.setText("The selected campaign map is missing. Import it before hosting."); return;
            }
            File request = new File(root, "coop_host.txt"), partial = new File(root, "coop_host.txt.tmp");
            try {
                // Do not enter two conflicting network routes on the same launch.
                File pvpHost = new File(root, "pvp_host.txt");
                if (pvpHost.exists() && !pvpHost.delete()) throw new java.io.IOException("Pending PvP host could not be cleared");
                File invite = new File(root, "join_link.txt");
                if (invite.exists() && !invite.delete()) throw new java.io.IOException("Pending invite could not be cleared");
                try (FileOutputStream out = new FileOutputStream(partial)) {
                    out.write(("3 " + selected + " " + difficulty.getSelectedItemPosition() + " "
                        + (publish.isChecked() ? 1 : 0) + " " + PLAYER_CHOICES[players.getSelectedItemPosition()] + "\n"
                        + name + "\n").getBytes(StandardCharsets.UTF_8));
                    out.getFD().sync();
                }
                if (!partial.renameTo(request)) throw new java.io.IOException("Could not save host request");
                activity.getSharedPreferences("coop-host", 0).edit().putString("server_name", name).apply();
                RunLog.line("Campaign host requested: mission=" + MAPS[selected] + " difficulty="
                    + difficulty.getSelectedItemPosition() + " players=" + PLAYER_CHOICES[players.getSelectedItemPosition()]
                    + " public=" + publish.isChecked() + " network=" + BuildConfig.HALO_NETWORK_VERSION
                    + " name=" + (name.isEmpty() ? "(the device's)" : name));
                if (start.getAsBoolean()) dialog.dismiss();
                else request.delete();
            } catch (java.io.IOException e) {
                partial.delete(); status.setText("Could not start host: " + e.getMessage());
            }
        }));
        dialog.show();
    }
}
