package com.halo.decomp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/**
 * ChupathingyCE /v1/games.txt, documented by its browser.c parse_game(): tab-separated
 * invite, name, map, engine, players, maximum, open, network version, then (optional, as
 * the directory adds them) age in seconds, score limit, teams and a roster. Columns past
 * those known are ignored, so a directory that adds more keeps working.
 *
 * Three kinds of game share the directory (checked against the live directory 2026-10-05):
 * this app's campaign co-op (a version in the CE00 family: CE02 since 1.0.8), OpenCE's own
 * co-op (its native network version, game engine 0 and a campaign map: a network game on a
 * campaign level is co-op upstream, OpenCE build 128 / network 17 on), and multiplayer.
 */
final class ServerListing {
    // CE02 since 1.0.8 (CE01 1.0.0-1.0.7): both co-op players need the same app version.
    static final int CAMPAIGN_VERSION = 0xCE02;
    // Campaign identity/lifecycle is two-player; independent of native PvP's 128 slots.
    static final int CAMPAIGN_MAXIMUM = 2;
    /** The retail campaign's levels (CoopLauncher.MAPS). */
    static final Set<String> CAMPAIGN_MAPS = new HashSet<>(Arrays.asList(
        "a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"));

    enum Kind { CAMPAIGN, OPENCE_COOP, MULTIPLAYER }

    /** Any campaign co-op protocol (0xCE00-0xCEFF), this app's or another version's. */
    static boolean isCampaign(int version) {
        return (version & 0xFF00) == 0xCE00;
    }
    static boolean campaignCapacityCompatible(int version,int maximum,boolean known) {
        return version != CAMPAIGN_VERSION || !known || maximum == CAMPAIGN_MAXIMUM;
    }
    /** A map name (any path, any case) that is a campaign level. */
    static boolean campaignMap(String map) {
        if (map == null) return false;
        String path = map.replace('\\', '/');
        return CAMPAIGN_MAPS.contains(path.substring(path.lastIndexOf('/') + 1).toLowerCase(Locale.ROOT));
    }
    /** engine: the listing's game engine, or -1 when the source does not say (a saved invite). */
    static Kind kind(int version, int engine, String map) {
        if (isCampaign(version)) return Kind.CAMPAIGN;
        if (version > 0 && engine == 0 && campaignMap(map)) return Kind.OPENCE_COOP;
        return Kind.MULTIPLAYER;
    }
    /** Whether the campaign co-op browser (true) or the multiplayer one (false) lists it. */
    static boolean listedIn(boolean campaignBrowser, Kind kind) {
        return campaignBrowser ? kind != Kind.MULTIPLAYER : kind == Kind.MULTIPLAYER;
    }
    /**
     * Whether this build can join it (before fullness and the open flag): a version not known
     * (0: a pasted invite; the game checks the host as it joins); this app's co-op at exactly
     * its version and two players; multiplayer within the native network range; OpenCE co-op
     * never (its co-op is its own netcode version).
     */
    static boolean joinable(boolean campaignBrowser, Kind kind, int version, int maximum, boolean capacityKnown,
                            int nativeMinimum, int nativeMaximum) {
        if (version == 0) return true;
        switch (kind) {
            case CAMPAIGN:
                return campaignBrowser && version == CAMPAIGN_VERSION && campaignCapacityCompatible(version, maximum, capacityKnown);
            case OPENCE_COOP:
                return false;
            default:
                return !campaignBrowser && (version == 0 || (version >= nativeMinimum && version <= nativeMaximum));
        }
    }

    final String invite, name, map;
    final int engine, players, maximum, version, age;
    final boolean open;
    /** The roster's player count when the directory sends one (-1: none). */
    final int rosterCount;
    final Kind kind;

    private ServerListing(String[] fields) {
        invite = ServerInvite.normalize(fields[0]);
        name = ServerInvite.displayName(fields[1]);
        String path = fields[2].replace('\\', '/');
        map = ServerInvite.displayName(path.substring(path.lastIndexOf('/') + 1));
        engine = Integer.parseInt(fields[3]);
        players = Integer.parseInt(fields[4]);
        maximum = Integer.parseInt(fields[5]);
        open = "1".equals(fields[6]);
        version = Integer.parseInt(fields[7]);
        age = fields.length > 8 && !fields[8].isEmpty() ? Integer.parseInt(fields[8]) : -1;
        // (the roster, "team:name|team:name": only how many, names are not shown)
        rosterCount = fields.length > 11 ? (fields[11].isEmpty() ? 0 : fields[11].split("\\|", -1).length) : -1;
        kind = kind(version, engine, map);
    }

    String description() {
        String[] modes = {"Unknown", "CTF", "Slayer", "Oddball", "King", "Race"};
        String mode = version == CAMPAIGN_VERSION ? "Campaign co-op"
            : isCampaign(version) ? "Campaign co-op (another app version)"
            : kind == Kind.OPENCE_COOP ? "OpenCE co-op (network v" + version + ")"
            : engine >= 1 && engine < modes.length ? modes[engine] : "Custom";
        return map + " · " + mode + " · " + players + "/" + maximum + " players"
            + (open ? "" : " · closed") + (age >= 0 ? " · updated " + age + "s ago" : "");
    }

    static List<ServerListing> parse(String body) {
        List<ServerListing> result = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        if (body.length() > 1024 * 1024) throw new IllegalArgumentException("Directory exceeds 1 MiB");
        for (String line : body.split("\\r?\\n")) {
            String[] fields = line.split("\\t", -1);
            if (fields.length < 8 || fields[0].length() != 64) continue;
            try {
                ServerListing entry = new ServerListing(fields);
                if (entry.invite == null || entry.players < 0 || entry.maximum < 1 || entry.maximum > 128
                    || entry.players > entry.maximum || entry.version < 1 || entry.version > 65535
                    || !("0".equals(fields[6]) || "1".equals(fields[6]))) continue;
                if (seen.add(entry.invite)) result.add(entry);
            } catch (NumberFormatException ignored) { /* malformed listing does not hide valid ones */ }
        }
        return result;
    }
}
