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
 * co-op (its native network version, game engine 0 and a campaign map: a network game on a
 * campaign level is co-op, as OpenCE plays it from build 128 / network 17, and as this app
 * hosts and joins it since 1.0.9), multiplayer, and this app's own co-op before 1.0.9 (a
 * version in the CE00 family: CE01, CE02), retired, listed so its players know to update.
 */
final class ServerListing {
    // This app's co-op protocol before 1.0.9 (CE01 1.0.0-1.0.7, CE02 1.0.8), retired.
    static final int CAMPAIGN_VERSION = 0xCE02;
    /** The retail campaign's levels (CoopLauncher.MAPS). */
    static final Set<String> CAMPAIGN_MAPS = new HashSet<>(Arrays.asList(
        "a10", "a30", "a50", "b30", "b40", "c10", "c20", "c40", "d20", "d40"));

    enum Kind { CAMPAIGN, OPENCE_COOP, MULTIPLAYER }

    /** This app's co-op protocol before 1.0.9 (0xCE00-0xCEFF: CE01, CE02), retired. */
    static boolean isCampaign(int version) {
        return (version & 0xFF00) == 0xCE00;
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
     * (0: a pasted invite; the game checks the host as it joins); co-op and multiplayer within
     * this build's network range, each from its own browser; this app's co-op before 1.0.9
     * never (its protocol is retired).
     */
    static boolean joinable(boolean campaignBrowser, Kind kind, int version, int nativeMinimum, int nativeMaximum) {
        if (version == 0) return true;
        boolean range = version >= nativeMinimum && version <= nativeMaximum;
        switch (kind) {
            case CAMPAIGN:
                return false;
            case OPENCE_COOP:
                return campaignBrowser && range;
            default:
                return !campaignBrowser && range;
        }
    }

    final String invite, name, map;
    final int engine, players, maximum, version, age;
    final boolean open;
    final boolean customEdition;

    static boolean customEditionMap(String map) {
        return map != null && map.replace('\\', '/').toLowerCase(Locale.ROOT).startsWith("custom_maps/");
    }
    /** The roster's player count when the directory sends one (-1: none). */
    final int rosterCount;
    final Kind kind;

    private ServerListing(String[] fields) {
        invite = ServerInvite.normalize(fields[0]);
        name = ServerInvite.displayName(fields[1]);
        customEdition = customEditionMap(fields[2]);
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
        String mode = isCampaign(version) ? "Co-op of this app 1.0.8 or older"
            : kind == Kind.OPENCE_COOP ? "Co-op (network v" + version + ")"
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
