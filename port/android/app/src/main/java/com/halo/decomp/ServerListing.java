package com.halo.decomp;

import java.util.ArrayList;
import java.util.List;
import java.util.HashSet;
import java.util.Set;

/** ChupathingyCE /v1/games.txt, documented by its browser.c parse_game(). */
final class ServerListing {
    static final int CAMPAIGN_VERSION = 0xCE01;
    final String invite, name, map;
    final int engine, players, maximum, version, age;
    final boolean open;

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
        age = fields.length > 8 ? Integer.parseInt(fields[8]) : -1;
    }

    String description() {
        String[] modes = {"Unknown", "CTF", "Slayer", "Oddball", "King", "Race"};
        String mode = version == CAMPAIGN_VERSION ? "Campaign co-op"
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
