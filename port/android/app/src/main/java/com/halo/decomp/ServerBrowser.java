package com.halo.decomp;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.text.InputType;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import javax.net.ssl.HttpsURLConnection;

/** Live native-port community directory + private saved invites. No auto-publication. */
final class ServerBrowser {
    interface Join { boolean open(String invite); }
    private static final int MAX_SERVERS = 512, MAX_BYTES = 1024 * 1024;
    private static final String DEFAULT_DIRECTORY = "https://halo.milenko.org/v1/games.txt";
    private final Activity activity;
    private final Join join;
    private final boolean campaign;
    static final int CAMPAIGN_VERSION = ServerListing.CAMPAIGN_VERSION;
    private final SharedPreferences preferences;
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private final List<Entry> saved = new ArrayList<>(), directory = new ArrayList<>();
    private final LinearLayout rows;
    private final TextView status;
    private final Button refresh;
    private final AlertDialog dialog;
    private volatile boolean closed;
    private volatile HttpsURLConnection connection;
    private int generation;
    private int visibleListings = 50;

    private static final class Entry {
        final String name, invite, description;
        final int version;
        final int players, maximum;
        final String map;
        final boolean open;
        final boolean capacityKnown;
        final ServerListing.Kind kind;
        Entry(JSONObject object) {
            name = ServerInvite.displayName(object.optString("name", "Unnamed server"));
            invite = ServerInvite.normalize(object.optString("invite", ""));
            description = ServerInvite.displayName(object.optString("description", "Invite session"));
            version = object.optInt("network_version", 0);
            players = Math.max(0, Math.min(128, object.optInt("players", 0)));
            maximum = Math.max(1, Math.min(128, object.optInt("maximum_players", 128)));
            capacityKnown = object.has("maximum_players");
            map = ServerInvite.displayName(object.optString("map", ""));
            open = object.optBoolean("open", true);
            kind = ServerListing.kind(version, object.optInt("engine", -1), map);
        }
        Entry(ServerListing listing) {
            name = listing.name;
            invite = listing.invite;
            description = listing.description();
            version = listing.version;
            players = listing.players; maximum = listing.maximum; map = listing.map;
            open = listing.open;
            capacityKnown = true;
            kind = listing.kind;
        }
        boolean compatible() {
            return version == 0 || (version >= BuildConfig.HALO_NETWORK_MINIMUM
                && version <= BuildConfig.HALO_NETWORK_MAXIMUM);
        }
        JSONObject json() {
            JSONObject object = new JSONObject();
            try {
                object.put("name", name).put("invite", invite).put("description", description)
                    .put("network_version", version);
                if (capacityKnown) object.put("maximum_players",maximum).put("players",players).put("map",map).put("open",open);
            } catch (org.json.JSONException impossible) { throw new IllegalStateException(impossible); }
            return object;
        }
    }

    ServerBrowser(Activity activity, Join join) {
        this(activity, join, false);
    }

    ServerBrowser(Activity activity, Join join, boolean campaign) {
        this.activity = activity;
        this.join = join;
        this.campaign = campaign;
        preferences = activity.getSharedPreferences(campaign ? "coop_browser" : "server_browser", Activity.MODE_PRIVATE);
        LinearLayout content = column();
        text(content, campaign ? "Campaign co-op: two players using this campaign build, VR or flat Android, "
            + "with identical campaign maps and resources. Join before the mission starts. "
            + "OpenCE's own co-op games are listed too, marked OpenCE co-op: they use OpenCE's network version and "
            + "cannot be joined from this app."
            : "Cross-play: native Windows, Mac, Linux and Android ports with compatible network versions "
            + "and maps. Retail Halo PC, MCC and Xbox are incompatible.");
        text(content, "How to join: pick a game and press Join. When the game opens, go to Multiplayer > System Link "
            + "and choose the same host. Upstream ports may call this Direct Link. Nearby LAN games also appear there. "
            + "Public listings are supplied by ChupathingyCE; availability may change.");
        if (!campaign) text(content, "In-game server browser: press Play, then in the game's main menu open "
            + "Multiplayer > System Link and press Refresh. It lists public games and games on your Wi-Fi, busiest first.");
        text(content, LauncherHelp.DATA_COMPATIBILITY_NOTE);
        button(content, "Add / paste server invite", this::addInvite);
        button(content, "Directory settings", this::setDirectory);
        refresh = button(content, "Refresh directory", this::refresh);
        status = text(content, "");
        rows = column();
        content.addView(rows);
        ScrollView scroll = new ScrollView(activity);
        scroll.addView(content);
        dialog = new GamepadNavigation.Builder(activity).setTitle(campaign ? "Campaign co-op servers" : "Multiplayer servers")
            .setView(scroll).setNegativeButton("Back", null).create();
        dialog.setOnDismissListener(ignored -> {
            closed = true;
            generation++;
            HttpsURLConnection current = connection;
            if (current != null) current.disconnect();
            worker.shutdownNow();
        });
        try { readEntries(new JSONArray(preferences.getString("saved", "[]")), saved, false); }
        catch (Exception e) { status.setText("Saved list could not be read. Add an invite to start a new list."); }
        render();
        dialog.show();
        refresh();
    }

    private LinearLayout column() {
        LinearLayout layout = new LinearLayout(activity);
        layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int)(12 * activity.getResources().getDisplayMetrics().density);
        layout.setPadding(padding, padding, padding, padding);
        return layout;
    }

    private TextView text(LinearLayout parent, String value) {
        TextView view = new TextView(activity);
        view.setText(value);
        view.setTextColor(Color.WHITE);
        view.setTextSize(16);
        parent.addView(view);
        return view;
    }

    private Button button(LinearLayout parent, String title, Runnable action) {
        Button button = new Button(activity);
        button.setText(title);
        button.setAllCaps(false);
        button.setOnClickListener(ignored -> action.run());
        parent.addView(button);
        return button;
    }

    private EditText input(LinearLayout parent, String hint, String initial) {
        EditText view = new EditText(activity);
        view.setSingleLine(true);
        view.setHint(hint);
        view.setText(initial);
        parent.addView(view);
        return view;
    }

    private void addInvite() {
        LinearLayout fields = column();
        EditText name = input(fields, "Server name", "");
        EditText link = input(fields, "halo://join/... or invite code", "");
        link.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS);
        AlertDialog edit = new GamepadNavigation.Builder(activity).setTitle("Save server")
            .setView(fields).setPositiveButton("Save", null).setNegativeButton("Cancel", null).create();
        edit.setOnShowListener(ignored -> edit.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String normalized = ServerInvite.normalize(link.getText().toString());
            if (normalized == null) { link.setError("Use a current 64-digit native-port invite."); return; }
            if (saved.size() >= MAX_SERVERS) { link.setError("Remove a saved server first (limit 512)."); return; }
            try {
                Entry entry = new Entry(new JSONObject().put("name", name.getText().toString())
                    .put("invite", normalized));
                saved.removeIf(previous -> previous.invite.equals(normalized));
                saved.add(entry);
                persist();
                render();
                edit.dismiss();
            } catch (org.json.JSONException e) { link.setError("Could not save this invite."); }
        }));
        edit.show();
    }

    private void setDirectory() {
        LinearLayout fields = column();
        text(fields, "Default: ChupathingyCE live directory. Add up to four HTTPS directories, one per line. "
            + "Accepts games.txt format or a schema-1 JSON catalog. Duplicates are merged. "
            + "Leave empty to use saved invites only. "
            + "Your saved invites are never uploaded.");
        EditText url = input(fields, "https://.../servers.json", preferences.getString("directory", DEFAULT_DIRECTORY));
        button(fields, "Use ChupathingyCE", () -> url.setText(DEFAULT_DIRECTORY));
        url.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        url.setSingleLine(false);
        url.setMinLines(3);
        AlertDialog edit = new GamepadNavigation.Builder(activity).setTitle("Community directory")
            .setView(fields).setPositiveButton("Save", null).setNegativeButton("Cancel", null).create();
        edit.setOnShowListener(ignored -> edit.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String value = url.getText().toString().trim();
            try { if (!value.isEmpty()) checkedDirectories(value); }
            catch (Exception e) { url.setError("Use an HTTPS URL without a password or username."); return; }
            preferences.edit().putString("directory", value).apply();
            directory.clear();
            render();
            edit.dismiss();
            refresh();
        }));
        edit.show();
    }

    private void persist() {
        JSONArray array = new JSONArray();
        for (Entry entry : saved) array.put(entry.json());
        preferences.edit().putString("saved", array.toString()).apply();
    }

    private void render() {
        rows.removeAllViews();
        text(rows, "Community directory — most populated first");
        if (directory.isEmpty()) text(rows, "No directory listings loaded.");
        int shown = Math.min(visibleListings, directory.size());
        for (int i = 0; i < shown; i++) row(directory.get(i), false);
        if (shown < directory.size()) button(rows, "Show next 50 servers (" + shown + "/" + directory.size() + ")", () -> {
            visibleListings += 50;
            render();
        });
        text(rows, "Saved servers (availability checked when joining)");
        if (saved.isEmpty()) text(rows, "No saved servers. Add an invite from a host.");
        for (Entry entry : saved) row(entry, true);
    }

    private void row(Entry entry, boolean favorite) {
        text(rows, entry.name + " — " + entry.description);
        boolean unsupportedCapacity = campaign && !ServerListing.campaignCapacityCompatible(entry.version,entry.maximum,entry.capacityKnown);
        boolean opence = entry.kind == ServerListing.Kind.OPENCE_COOP;
        boolean compatible = !unsupportedCapacity && ServerListing.joinable(campaign, entry.kind, entry.version, entry.maximum,
            entry.capacityKnown, BuildConfig.HALO_NETWORK_MINIMUM, BuildConfig.HALO_NETWORK_MAXIMUM);
        String version = entry.version == 0 ? "version checked by game" : "network v" + entry.version;
        text(rows, version + (compatible ? "" : " — incompatible; supported: "
            + (opence ? "this app's co-op (CE02, both players on this app version)"
            : campaign ? "matching campaign build" : BuildConfig.HALO_NETWORK_MINIMUM + "–" + BuildConfig.HALO_NETWORK_MAXIMUM)));
        Button open = button(rows, "Join " + entry.name, () -> {
            Runnable connect=()->{
                RunLog.line("Multiplayer join requested: " + entry.name + " network=" + entry.version + " map=" + entry.map
                    + " over " + NetworkSettings.describe(activity));
                if (join.open(entry.invite)) dialog.dismiss();
                else status.setText("Could not write the invite. Check game-data storage access, then try again.");
            };
            if(!campaign&&activity instanceof LauncherActivity)((LauncherActivity)activity).withServerMap(entry.map,connect);
            else connect.run();
        });
        String blocked = opence ? "OpenCE co-op: this host runs OpenCE's own co-op (network v" + entry.version
            + "), which this app cannot join yet. This app's co-op needs this app on both devices; host one with "
            + "Campaign co-op > Host campaign, or join a game marked Campaign co-op."
            : unsupportedCapacity ? "Unsupported campaign capacity: this build supports two-player co-op. Larger PvP limits do not apply to campaign."
            : !compatible && campaign ? "Version mismatch: this co-op game is from a different HaloCE Quest/Android version. "
            + "Both players need the same app version (this one is " + BuildConfig.VERSION_NAME + ")."
            : !compatible ? "Protocol mismatch: this host uses network v" + entry.version +
            ". Disc revision cannot change the network protocol. Ask the host to update or choose a compatible server."
            : !favorite && entry.players >= entry.maximum ? "Server full. Refresh after a player leaves."
            : !favorite && !entry.open ? "Host is closed to joining (loading, postgame, or locked lobby). Refresh later."
            : "";
        if(!blocked.isEmpty()) text(rows,blocked);
        if(!campaign && !opence && entry.version > BuildConfig.HALO_NETWORK_MAXIMUM)
            button(rows,"Check for compatible update",()->Updater.show(activity,activity instanceof LauncherActivity ? ((LauncherActivity)activity).gameRoot() : activity.getExternalFilesDir(null)));
        else text(rows,"Reachability is checked by the game, not the directory. If the host does not appear: refresh its invite, check Internet settings, and check both networks for NAT/firewall restrictions.");
        open.setEnabled(compatible && (favorite || (entry.open && entry.players < entry.maximum)));
        // (an OpenCE co-op host's invite is not one this app can use: not offered for saving)
        if (opence && !favorite) return;
        button(rows, favorite ? "Remove saved server" : "Save server", () -> {
            if (favorite) saved.remove(entry);
            else {
                if (saved.size() >= MAX_SERVERS) { status.setText("Saved-server limit reached (512)."); return; }
                saved.removeIf(previous -> previous.invite.equals(entry.invite));
                saved.add(entry);
            }
            persist();
            render();
        });
    }

    private static URL checkedUrl(String value) throws Exception {
        URL url = new URL(value);
        if (!"https".equalsIgnoreCase(url.getProtocol()) || url.getHost().isEmpty()
            || url.getUserInfo() != null || value.length() > 2048) throw new Exception("Invalid directory URL");
        return url;
    }

    private static String[] checkedDirectories(String value) throws Exception {
        String[] addresses = value.trim().split("\\s+");
        if (addresses.length > 4) throw new Exception("Use at most four directories");
        for (String address : addresses) checkedUrl(address);
        return addresses;
    }

    private static void readEntries(JSONArray array, List<Entry> destination, boolean requireVersion) throws Exception {
        if (!requireVersion && array.length() > MAX_SERVERS) throw new Exception("Saved list exceeds 512 servers");
        Set<String> seen = new HashSet<>();
        for (Entry entry : destination) seen.add(entry.invite);
        for (int i = 0; i < array.length(); i++) {
            JSONObject object = array.optJSONObject(i);
            if (object == null) continue;
            Entry entry = new Entry(object);
            if (entry.invite == null || (requireVersion && entry.version <= 0)) continue;
            if (seen.add(entry.invite)) destination.add(entry);
        }
    }

    private List<Entry> fetch(String address) throws Exception {
        URL url = checkedUrl(address);
        for (int redirects = 0; redirects <= 3 && !closed; redirects++) {
            HttpsURLConnection request = (HttpsURLConnection)url.openConnection();
            connection = request;
            try {
                request.setConnectTimeout(10000);
                request.setReadTimeout(10000);
                request.setInstanceFollowRedirects(false);
                request.setRequestProperty("Accept", "text/plain, application/json");
                int code = request.getResponseCode();
                if (code == 301 || code == 302 || code == 303 || code == 307 || code == 308) {
                    String location = request.getHeaderField("Location");
                    if (location == null) throw new Exception("Directory redirect has no location");
                    url = checkedUrl(new URL(url, location).toString());
                    continue;
                }
                if (code != 200) throw new Exception("Directory returned HTTP " + code);
                if (request.getContentLengthLong() > MAX_BYTES) throw new Exception("Directory exceeds 1 MiB");
                ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                long deadline = System.nanoTime() + 15_000_000_000L;
                try (InputStream input = request.getInputStream()) {
                    byte[] buffer = new byte[4096];
                    for (int count; (count = input.read(buffer)) != -1;) {
                        if (closed || System.nanoTime() > deadline) throw new Exception("Directory request cancelled or timed out");
                        if (bytes.size() + count > MAX_BYTES) throw new Exception("Directory exceeds 1 MiB");
                        bytes.write(buffer, 0, count);
                    }
                }
                String body = bytes.toString(StandardCharsets.UTF_8.name()).trim();
                List<Entry> result = new ArrayList<>();
                if (body.startsWith("{")) {
                    JSONObject root = new JSONObject(body);
                    if (root.optInt("schema", 0) != 1) throw new Exception("Unsupported directory schema");
                    readEntries(root.getJSONArray("servers"), result, true);
                } else {
                    for (ServerListing listing : ServerListing.parse(body)) result.add(new Entry(listing));
                    if (!body.isEmpty() && result.isEmpty()) throw new Exception("No valid native-port listings in response");
                }
                result.sort((a, b) -> {
                    int population = Integer.compare(b.players, a.players);
                    if (population != 0) return population;
                    int ready = Boolean.compare(b.compatible() && b.open, a.compatible() && a.open);
                    return ready != 0 ? ready : a.name.compareToIgnoreCase(b.name);
                });
                return result;
            } finally { request.disconnect(); connection = null; }
        }
        throw new Exception("Directory has too many redirects or was closed");
    }

    private void refresh() {
        if (closed) return;
        int requestId = ++generation;
        String address = preferences.getString("directory", DEFAULT_DIRECTORY);
        if (address.isEmpty()) {
            status.setText("No public directory configured. Add a saved invite or set your community's directory URL.");
            refresh.setEnabled(true);
            return;
        }
        refresh.setEnabled(false);
        status.setText("Loading directory…");
        worker.execute(() -> {
            List<Entry> result = null;
            String error = null;
            try {
                result = new ArrayList<>();
                Set<String> seen = new HashSet<>();
                int successful = 0;
                for (String source : checkedDirectories(address)) {
                    try {
                        List<Entry> incoming = fetch(source);
                        successful++;
                        RunLog.line("Directory " + checkedUrl(source).getHost() + ": " + incoming.size() + " listings");
                        for (Entry entry : incoming) {
                            if (seen.add(entry.invite)) result.add(entry);
                        }
                    } catch (Exception e) {
                        error = "One or more directories unavailable";
                        RunLog.line("Directory request failed: " + e.getClass().getSimpleName());
                    }
                }
                if (successful == 0) result = null;
                else result.sort((a, b) -> {
                    int population = Integer.compare(b.players, a.players);
                    if (population != 0) return population;
                    int ready = Boolean.compare(b.compatible() && b.open, a.compatible() && a.open);
                    return ready != 0 ? ready : a.name.compareToIgnoreCase(b.name);
                });
            }
            catch (Exception e) { error = e.getMessage() == null ? "Connection failed" : e.getMessage(); }
            List<Entry> completed = result;
            String failure = error;
            activity.runOnUiThread(() -> {
                if (closed || requestId != generation || activity.isFinishing()) return;
                refresh.setEnabled(true);
                if (completed == null) {
                    directory.clear();
                    status.setText("Directory unavailable: " + failure + ". Saved invites remain available.");
                } else {
                    directory.clear();
                    int opence = 0;
                    for (Entry entry : completed)
                        if (ServerListing.listedIn(campaign, entry.kind)) {
                            directory.add(entry);
                            if (entry.kind == ServerListing.Kind.OPENCE_COOP) opence++;
                        }
                    visibleListings = 50;
                    int players = 0;
                    for (Entry entry : directory) players += entry.players;
                    RunLog.line("Directory classified for the " + (campaign ? "co-op" : "multiplayer") + " browser: "
                        + directory.size() + " listed" + (campaign ? ", " + opence + " OpenCE co-op (not joinable)" : ""));
                    status.setText(directory.size() + " servers · " + players
                        + " reported players. Most populated first; full/incompatible games cannot be joined."
                        + (opence > 0 ? " " + opence + " are OpenCE co-op games this app cannot join." : "")
                        + (failure == null ? "" : " Some directories failed; showing available results."));
                }
                render();
            });
        });
    }
}
