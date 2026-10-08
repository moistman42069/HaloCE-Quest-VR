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
import java.util.HashMap;
import java.util.Map;
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
    private final Button networkSelector;
    private final AlertDialog dialog;
    private volatile boolean closed;
    private volatile HttpsURLConnection connection;
    private int generation;
    private int visibleListings = 50;
    /** 0 shows all observed network versions; a positive value filters one protocol. */
    private int selectedNetworkVersion;
    private boolean directoryLoaded;

    private java.io.File gameRoot() {
        return activity instanceof LauncherActivity ? ((LauncherActivity)activity).gameRoot()
            : GameDataLibrary.activeRoot(activity.getExternalFilesDir(null));
    }

    private static final class Entry {
        final String name, invite, description;
        final int version;
        final int players, maximum;
        final String map;
        final boolean open;
        final boolean customEdition;
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
            customEdition = object.optBoolean("custom_edition", false) || ServerListing.customEditionMap(map);
            open = object.optBoolean("open", true);
            kind = ServerListing.kind(version, object.optInt("engine", -1), map);
        }
        Entry(ServerListing listing) {
            name = listing.name;
            invite = listing.invite;
            description = listing.description();
            version = listing.version;
            players = listing.players; maximum = listing.maximum; map = listing.map;
            customEdition = listing.customEdition;
            open = listing.open;
            capacityKnown = true;
            kind = listing.kind;
        }
        boolean compatible() {
            return version == 0 || NetworkProfile.supported(version);
        }
        JSONObject json() {
            JSONObject object = new JSONObject();
            try {
                object.put("name", name).put("invite", invite).put("description", description)
                    .put("network_version", version).put("custom_edition", customEdition);
                if (capacityKnown) object.put("maximum_players",maximum).put("players",players).put("map",map).put("open",open);
            } catch (org.json.JSONException impossible) { throw new IllegalStateException(impossible); }
            return object;
        }
    }

    private static final class NetworkPopulation {
        final int version;
        int servers;
        int players;
        boolean compatible;
        NetworkPopulation(int version) { this.version = version; }
    }

    ServerBrowser(Activity activity, Join join) {
        this(activity, join, false);
    }

    ServerBrowser(Activity activity, Join join, boolean campaign) {
        this.activity = activity;
        this.join = join;
        this.campaign = campaign;
        preferences = activity.getSharedPreferences(campaign ? "coop_browser" : "server_browser", Activity.MODE_PRIVATE);
        selectedNetworkVersion = NetworkProfile.selected(activity);
        LinearLayout content = column();
        networkSelector = button(content, "Network: All networks", this::selectNetwork);
        refresh = button(content, "Refresh populations & servers", this::refresh);
        status = text(content, "");
        text(content, "Choose a network above, then join a server or return to Play. Network changes apply on the next game launch. Counts are directory reports and may lag.");
        button(content, "Network & joining help", () -> LauncherHelp.page(activity, "Network & joining help",
            "The selector ranks networks by reported player population. Select an available profile to change which host versions the native game discovers and can join on its next launch. "
            + "All compatible networks searches every supported host version. Networks 11–22 are limited to original Xbox-map PvP; co-op and Custom Edition require 23 or 24. Hosting always uses current network 24.\n\n"
            + "A directory Join passes the host's invite to the game. Open Multiplayer > Join Game > LAN and choose that host once the connection appears. "
            + "Direct Link also accepts invites. Public in-game listings are under Multiplayer > Join Game > Server Browser.\n\n"
            + "The community directory is supplied by ChupathingyCE. The in-game browser uses signed OpenCE discovery and LAN. "
            + "These sources can show different results. Retail Halo PC, MCC and Xbox use incompatible protocols.\n\n"
            + LauncherHelp.DATA_COMPATIBILITY_NOTE));
        button(content, "Add / paste server invite", this::addInvite);
        button(content, "Directory settings", this::setDirectory);
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
        text(fields, "Default: ChupathingyCE live directory, which lists games across network versions. Add up to four HTTPS directories, one per line. "
            + "Accepts games.txt format or a schema-1 JSON catalog. Duplicates are merged. "
            + "The Network selector discovers versions from the combined results. Leave empty to use saved invites only. "
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
            directoryLoaded = false;
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
        updateNetworkSelector();
        rows.removeAllViews();
        List<Entry> filtered = filteredDirectory();
        text(rows, selectedNetworkVersion == 0
            ? "Community directory — all networks, most populated servers first"
            : "Community directory — network v" + selectedNetworkVersion + ", most populated first");
        if (directory.isEmpty()) text(rows, "No directory listings loaded.");
        else if (filtered.isEmpty()) text(rows, "No listings for this network in the selected directory. Choose another network above.");
        int shown = Math.min(visibleListings, filtered.size());
        for (int i = 0; i < shown; i++) row(filtered.get(i), false);
        if (shown < filtered.size()) button(rows, "Show next 50 servers (" + shown + "/" + filtered.size() + ")", () -> {
            visibleListings += 50;
            render();
        });
        text(rows, "Saved servers (availability checked when joining)");
        if (saved.isEmpty()) text(rows, "No saved servers. Add an invite from a host.");
        for (Entry entry : saved) row(entry, true);
    }

    private List<Entry> filteredDirectory() {
        if (selectedNetworkVersion == 0) return directory;
        List<Entry> filtered = new ArrayList<>();
        for (Entry entry : directory)
            if (entry.version == selectedNetworkVersion) filtered.add(entry);
        return filtered;
    }

    private static String networkLabel(int version) {
        return ServerListing.isCampaign(version)
            ? "Legacy app co-op CE" + String.format(java.util.Locale.ROOT, "%02X", version & 0xFF)
            : "Network v" + version;
    }

    /** Counts are calculated from the deduplicated listings currently returned by configured directories. */
    private List<NetworkPopulation> networkPopulations() {
        Map<Integer, NetworkPopulation> grouped = new HashMap<>();
        for (int version : NetworkProfile.SUPPORTED) {
            NetworkPopulation population = new NetworkPopulation(version);
            population.compatible = true;
            grouped.put(version, population);
        }
        for (Entry entry : directory) {
            if (entry.version <= 0) continue;
            NetworkPopulation population = grouped.get(entry.version);
            if (population == null) {
                population = new NetworkPopulation(entry.version);
                grouped.put(entry.version, population);
            }
            population.servers++;
            population.players += entry.players;
            population.compatible = NetworkProfile.supported(entry.version);
        }
        List<NetworkPopulation> result = new ArrayList<>(grouped.values());
        result.sort((a, b) -> {
            int players = Integer.compare(b.players, a.players);
            if (players != 0) return players;
            int servers = Integer.compare(b.servers, a.servers);
            return servers != 0 ? servers : Integer.compare(b.version, a.version);
        });
        return result;
    }

    private void updateNetworkSelector() {
        List<NetworkPopulation> populations = networkPopulations();
        String title = NetworkProfile.label(NetworkProfile.selected(activity)) + " · tap to switch";
        if (directoryLoaded && !directory.isEmpty()) title += " · busiest v" + populations.get(0).version
            + ": " + populations.get(0).players + " players";
        networkSelector.setText(title);
    }

    private void selectNetwork() {
        List<NetworkPopulation> populations = networkPopulations();
        String[] choices = new String[populations.size() + 1];
        choices[0] = "All compatible networks (11–24) · " + (directoryLoaded ? compatibleReportedPlayers() + " reported players" : "population unavailable");
        int checked = selectedNetworkVersion == 0 ? 0 : -1;
        for (int i = 0; i < populations.size(); i++) {
            NetworkPopulation population = populations.get(i);
            choices[i + 1] = networkLabel(population.version) + " · "
                + (directoryLoaded ? population.players + " players · " + population.servers + " servers" : "population unavailable")
                + " · " + (population.compatible ? (population.version == NetworkProfile.selected(activity)
                    ? "active" : "switch on next launch") : "unavailable; protocol not included");
            if (population.version >= 11 && population.version < 23) choices[i + 1] += " · Xbox-map PvP only";
            if (population.version == selectedNetworkVersion) checked = i + 1;
        }
        AlertDialog chooser = new GamepadNavigation.Builder(activity).setTitle("Select server network")
            .setSingleChoiceItems(choices, checked, (selected, which) -> {
                int version = which == 0 ? 0 : populations.get(which - 1).version;
                    try { NetworkProfile.select(activity, gameRoot(), version); }
                    catch (java.io.IOException e) {
                        LauncherHelp.page(activity, "Network unavailable", e.getMessage());
                        return;
                    }
                    status.setText(NetworkProfile.label(version) + " selected for the next launch. Return to Play or join a listed server. Hosting remains on network 24.");
                selectedNetworkVersion = version;
                visibleListings = 50;
                render();
                selected.dismiss();
            }).setNegativeButton("Cancel", null).create();
        chooser.show();
    }

    private int compatibleReportedPlayers() {
        int players = 0;
        for (Entry entry : directory)
            if (entry.version > 0 && NetworkProfile.supported(entry.version)
                && (!(campaign || entry.customEdition) || entry.version >= 23)) players += entry.players;
        return players;
    }

    private int totalReportedPlayers() {
        int players = 0;
        for (NetworkPopulation population : networkPopulations()) players += population.players;
        return players;
    }

    private void row(Entry entry, boolean favorite) {
        text(rows, entry.name + " — " + entry.description);
        boolean old = entry.kind == ServerListing.Kind.CAMPAIGN;
        boolean compatible = ServerListing.joinable(campaign, entry.kind, entry.version,
            NetworkProfile.minimum(NetworkProfile.selected(activity)), NetworkProfile.maximum(NetworkProfile.selected(activity)))
            && !((campaign || entry.customEdition) && entry.version > 0 && entry.version < 23);
        String version = entry.version == 0 ? "version checked by game" : networkLabel(entry.version);
        text(rows, version + (compatible ? "" : " — not available with " + NetworkProfile.label(NetworkProfile.selected(activity))));
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
        String blocked = old ? "This co-op game is from this app 1.0.8 or older, whose co-op this version no longer "
            + "plays (it plays co-op as OpenCE does). Ask the host to update to " + BuildConfig.VERSION_NAME + " or later."
            : entry.customEdition && entry.version > 0 && entry.version < 23 ? "Custom Edition maps require a network 23 or 24 host."
            : campaign && entry.version > 0 && entry.version < 23 ? "Legacy co-op on this network is not supported. Use a network 23 or 24 host."
            : !compatible ? "Protocol mismatch: this host uses " + networkLabel(entry.version) + ". "
            + (NetworkProfile.supported(entry.version) ? "Choose it in the Network selector above, then join."
                : "This app has no implementation for that version. Disc revision cannot change the network protocol.")
            : !favorite && entry.players >= entry.maximum ? "Server full. Refresh after a player leaves."
            : !favorite && !entry.open ? "Host is closed to joining (loading, postgame, or locked lobby). Refresh later."
            : "";
        if(!blocked.isEmpty()) text(rows,blocked);
        if(!old && entry.version > BuildConfig.HALO_NETWORK_MAXIMUM)
            button(rows,"Check for compatible update",()->Updater.show(activity,activity instanceof LauncherActivity ? ((LauncherActivity)activity).gameRoot() : activity.getExternalFilesDir(null)));
        else text(rows,"Reachability is checked by the game, not the directory. If the host does not appear: refresh its invite, check Internet settings, and check both networks for NAT/firewall restrictions.");
        open.setEnabled(compatible && (favorite || (entry.open && entry.players < entry.maximum)));
        // (an old co-op host's invite is not one this app can use: not offered for saving)
        if (old && !favorite) return;
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
                    directoryLoaded = false;
                    directory.clear();
                    status.setText("Directory unavailable: " + failure + ". Saved invites remain available.");
                } else {
                    directoryLoaded = true;
                    directory.clear();
                    int old = 0;
                    for (Entry entry : completed)
                        if (ServerListing.listedIn(campaign, entry.kind)) {
                            directory.add(entry);
                            if (entry.kind == ServerListing.Kind.CAMPAIGN) old++;
                        }
                    visibleListings = 50;
                    int players = totalReportedPlayers();
                    List<NetworkPopulation> populations = networkPopulations();
                    int observedVersions = 0;
                    for (NetworkPopulation population : populations) if (population.servers > 0) observedVersions++;
                    String busiest = directory.isEmpty() ? "" : "; busiest network v"
                        + populations.get(0).version + " (" + populations.get(0).players + " reported players)";
                    RunLog.line("Directory classified for the " + (campaign ? "co-op" : "multiplayer") + " browser: "
                        + directory.size() + " listed" + (campaign ? ", " + old + " from this app 1.0.8 or older (not joinable)" : ""));
                    status.setText(directory.size() + " servers · " + players
                        + " reported players across " + observedVersions + " network versions" + busiest
                        + ". Most populated first; full/incompatible games cannot be joined."
                        + (old > 0 ? " " + old + " are co-op games of this app 1.0.8 or older (their hosts need to update)." : "")
                        + (failure == null ? "" : " Some directories failed; showing available results."));
                }
                render();
            });
        });
    }
}
