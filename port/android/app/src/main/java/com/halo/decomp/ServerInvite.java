package com.halo.decomp;

import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** The existing native p2p.c invite format: 16-byte host hash + 16-byte token. */
final class ServerInvite {
    private static final Pattern LINK = Pattern.compile(
        "(?i)halo://join/([0-9a-f]{64})(?![0-9a-f])");
    private static final Pattern CODE = Pattern.compile("(?i)[0-9a-f]{64}");

    static String normalize(String text) {
        if (text == null || text.length() > 4096) return null;
        String trimmed = text.trim();
        if (CODE.matcher(trimmed).matches())
            return "halo://join/" + trimmed.toLowerCase(Locale.ROOT);
        Matcher match = LINK.matcher(trimmed);
        return match.find() ? "halo://join/" + match.group(1).toLowerCase(Locale.ROOT) : null;
    }

    static String displayName(String text) {
        if (text == null) return "Unnamed server";
        String clean = text.replaceAll("[\\p{Cntrl}\\p{Cf}]", "").trim();
        return clean.isEmpty() ? "Unnamed server" : clean.substring(0, Math.min(80, clean.length()));
    }
}
