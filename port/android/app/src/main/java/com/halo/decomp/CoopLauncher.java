package com.halo.decomp;

import android.app.Activity;
import android.app.AlertDialog;
import android.widget.ArrayAdapter;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.function.BooleanSupplier;

/** Starts the native two-machine lobby; it does not emulate a campaign with PvP settings. */
final class CoopLauncher {
    static final String[] MAPS = {"a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"};
    private final Activity activity;
    private final File root;
    private final BooleanSupplier ready, start;
    private final ServerBrowser.Join join;

    CoopLauncher(Activity activity, File root, BooleanSupplier ready, BooleanSupplier start, ServerBrowser.Join join) {
        this.activity = activity; this.root = root; this.ready = ready; this.start = start; this.join = join;
    }

    void show() {
        new GamepadNavigation.Builder(activity).setTitle("Campaign co-op")
            .setMessage("Both devices need the same app version and the same campaign maps. "
                + "Quest + Quest and Quest + phone both work.\n\n"
                + "TO HOST: press Host campaign, pick the mission and difficulty, leave the server browser box "
                + "ticked and press Host. Wait in the System Link lobby until your partner joins, then start.\n\n"
                + "TO JOIN: press Browse / join, then Refresh directory, pick the host's game and press Join. "
                + "When the game opens, go to Multiplayer > System Link, choose the host's game and join it. "
                + "On the same Wi-Fi it appears there by itself.\n\n"
                + "Two players; no joining a mission in progress. Keep both apps open. "
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
        CheckBox publish = new CheckBox(activity);
        publish.setText("List this game in the co-op server browser (shares your session invite)");
        // On by default so the partner finds the game under Campaign co-op > Browse / join.
        publish.setChecked(true);
        layout.addView(publish);
        TextView status = new TextView(activity);
        status.setText("Ticked: your partner finds this game under Campaign co-op > Browse / join. Untick it to keep "
            + "the game private and share the invite the game copies instead. Listing problems are noted in the launch log.");
        layout.addView(status);
        AlertDialog dialog = new GamepadNavigation.Builder(activity).setTitle("Host campaign")
            .setView(layout).setPositiveButton("Host", null).setNegativeButton("Cancel", null).create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            if (!ready.getAsBoolean()) return;
            int selected = mission.getSelectedItemPosition();
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
                    out.write(("1 " + selected + " " + difficulty.getSelectedItemPosition() + " "
                        + (publish.isChecked() ? 1 : 0) + "\n").getBytes(StandardCharsets.UTF_8));
                    out.getFD().sync();
                }
                if (!partial.renameTo(request)) throw new java.io.IOException("Could not save host request");
                RunLog.line("Campaign host requested: mission=" + MAPS[selected] + " difficulty="
                    + difficulty.getSelectedItemPosition() + " public=" + publish.isChecked());
                if (start.getAsBoolean()) dialog.dismiss();
                else request.delete();
            } catch (java.io.IOException e) {
                partial.delete(); status.setText("Could not start host: " + e.getMessage());
            }
        }));
        dialog.show();
    }
}
