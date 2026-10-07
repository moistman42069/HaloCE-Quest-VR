"""Run the production invite/list parser and native version gate without Android.

python3 tools/test_quest_browser.py [optional-downloaded-games.txt]
Requires JDK 17 and clang. No connections to game servers are made.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/quest-browser-checks"
OUT.mkdir(parents=True, exist_ok=True)
JAVA = ROOT / "port/android/app/src/main/java/com/halo/decomp"
harness = OUT / "BrowserCheck.java"
harness.write_text(r'''
package com.halo.decomp;
import java.nio.file.*;
public class BrowserCheck {
    static void check(boolean value) { if (!value) throw new AssertionError(); }
    public static void main(String[] args) throws Exception {
        String code = "abcdef0123456789".repeat(4);
        String link = "halo://join/" + code;
        check(link.equals(ServerInvite.normalize(code.toUpperCase())));
        check(link.equals(ServerInvite.normalize("Join me: " + link + " now")));
        check(ServerInvite.normalize("halo://join/" + "a".repeat(44)) == null);
        check(ServerInvite.normalize(link + "a") == null);
        check(ServerInvite.normalize("https://example.org") == null);
        check(ServerInvite.normalize("a".repeat(4097)) == null);
        check(ServerInvite.normalize(null) == null);
        check(ServerInvite.displayName("hi\u202e\nthere").equals("hithere"));
        String row = code + "\tHost\tlevels\\test\\bloodgulch\\bloodgulch\t2\t12\t128\t1\t10\t14\t50\t1\t";
        var servers = ServerListing.parse(row + "\r\n" + row + "\ninvalid");
        check(servers.size() == 1);
        var server = servers.get(0);
        check(server.version == 10 && server.players == 12 && server.maximum == 128 && server.open);
        check(server.map.equals("bloodgulch") && server.invite.equals(link));
        check(server.description().contains("Slayer"));
        for (String bad : new String[] {row.replace("\t12\t128", "\t129\t128"),
            row.replace("\t12\t128", "\t-1\t128"), row.replace("\t12\t128", "\t0\t0"),
            row.replace("\t10\t", "\tNaN\t"), row.replace("\t1\t10", "\t3\t10"),
            row.replace(code, "g".repeat(64))}) check(ServerListing.parse(bad).isEmpty());
        check(ServerListing.parse("").isEmpty());
        check(ServerListing.parse(row.substring(0, row.indexOf("\t14"))).size() == 1);
        check(ServerListing.parse(row.replace("\t1\t10", "\t0\t10")).get(0).open == false);
        StringBuilder many = new StringBuilder();
        for (int i = 0; i < 150; i++) many.append(row.replace(code, String.format("%064x", i))).append('\n');
        check(ServerListing.parse(many.toString()).size() == 150);
        // test27: the directory's three kinds (format as served 2026-10-05/06: 12 columns, the last a roster).
        // This app plays OpenCE's network version (20 here, as build 138): co-op as OpenCE plays it (engine 0 on a
        // campaign map) and multiplayer, each from its browser; this app's own co-op before 1.0.9 (CE01/CE02) is
        // retired: listed, marked, never joinable. Synthetic rows: no real invites or player names.
        check(ServerListing.isCampaign(0xCE01) && ServerListing.isCampaign(0xCE02) && !ServerListing.isCampaign(20) && !ServerListing.isCampaign(0));
        String[] synthetic = {
            "%s\tPvP v11\tbloodgulch\t2\t3\t16\t1\t11\t9\t0\t0\t",
            "%s\tPvP v20 roster\tlevels\\test\\hangemhigh\\hangemhigh\t2\t4\t4\t0\t20\t13\t50\t1\t0:A|1:B|0:C|1:D",
            "%s\tLobby v11\tcarousel\t0\t0\t128\t1\t11\t1\t0\t0\t",
            "%s\tLobby v20\tbeavercreek\t0\t6\t16\t1\t20\t81\t0\t0\t",
            "%s\tCo-op v18\ta30\t0\t4\t4\t0\t18\t2\t0\t0\t",
            "%s\tCo-op v20\tb40\t0\t24\t32\t1\t20\t2\t0\t0\t",
            "%s\tCo-op path v20\tlevels\\A10\\a10\t0\t1\t4\t1\t20\t2\t0\t0\t",
            "%s\tHalo CE co-op - Normal\ta10\t0\t1\t2\t1\t52738\t3\t0\t0\t",
            "%s\tHalo CE co-op - Easy\tc40\t0\t1\t2\t1\t52737\t3\t0\t0\t",
            "%s\tCTF on a campaign map\tb30\t1\t2\t16\t1\t20\t3\t0\t1\t",
            "%s\tFuture columns\tbloodgulch\t2\t1\t16\t1\t20\t3\t0\t0\t\tsomething\tmore",
            "%s\tCo-op v21\tc10\t0\t2\t16\t1\t21\t2\t0\t0\t",
        };
        StringBuilder body = new StringBuilder();
        for (int i = 0; i < synthetic.length; i++) body.append(String.format(synthetic[i], String.format("%064x", 0x2700 + i))).append('\n');
        var kinds = ServerListing.parse(body.toString());
        check(kinds.size() == synthetic.length);
        ServerListing.Kind M = ServerListing.Kind.MULTIPLAYER, O = ServerListing.Kind.OPENCE_COOP, C = ServerListing.Kind.CAMPAIGN;
        ServerListing.Kind[] expected = {M, M, M, M, O, O, O, C, C, M, M, O};
        for (int i = 0; i < synthetic.length; i++) check(kinds.get(i).kind == expected[i]);
        check(kinds.get(1).rosterCount == 4 && kinds.get(0).rosterCount == 0 && kinds.get(10).rosterCount == 0);
        check(kinds.get(4).description().contains("Co-op (network v18)") && kinds.get(5).description().contains("Co-op (network v20)"));
        check(kinds.get(7).description().contains("Co-op of this app 1.0.8 or older") && kinds.get(8).description().contains("1.0.8 or older"));
        // listed: the multiplayer browser never shows co-op of either kind; the co-op browser shows both, never multiplayer
        for (ServerListing listing : kinds) {
            boolean coop = listing.kind != M;
            check(ServerListing.listedIn(true, listing.kind) == coop && ServerListing.listedIn(false, listing.kind) == !coop);
        }
        // joinable at network 20 only: multiplayer from the multiplayer browser, co-op from the co-op browser;
        // CE01/CE02 never; pasted invites (version 0) left to the game
        int lo = 20, hi = 20;
        boolean[] joinPvp = {false, true, false, true, false, false, false, false, false, true, true, false};
        boolean[] joinCoop = {false, false, false, false, false, true, true, false, false, false, false, false};
        for (int i = 0; i < synthetic.length; i++) {
            ServerListing l = kinds.get(i);
            check(ServerListing.joinable(false, l.kind, l.version, lo, hi) == joinPvp[i]);
            check(ServerListing.joinable(true, l.kind, l.version, lo, hi) == joinCoop[i]);
        }
        for (int v = 0; v <= 70000; v += 7) for (int engine = -1; engine <= 5; engine++) for (String map : new String[]{"a10", "bloodgulch", ""}) {
            ServerListing.Kind k = ServerListing.kind(v, engine, map);
            boolean pvp = ServerListing.joinable(false, k, v, lo, hi), coop = ServerListing.joinable(true, k, v, lo, hi);
            if (v != 0) check(!(pvp && coop));                                   // never both
            if (v != 0 && (v < lo || v > hi)) check(!pvp && !coop);               // only this build's network version
            if (ServerListing.isCampaign(v)) check(!pvp && !coop);                // the retired CE01/CE02: never
            if (v == lo && k == O) check(coop && !pvp);                           // OpenCE's co-op: from the co-op browser
        }
        check(ServerListing.joinable(true, M, 0, lo, hi) && ServerListing.joinable(false, M, 0, lo, hi));
        // a saved invite without an engine is never taken for co-op
        check(ServerListing.kind(20, -1, "a10") == M && ServerListing.kind(20, 0, "A10") == O);
        System.out.println("PASS: directory kinds (multiplayer, co-op on engine 0 + a campaign map, this app's retired CE co-op),"
            + " 12-column rows with rosters and future columns, browser placement and joinability at network 20 only"
            + " (co-op from the co-op browser, CE01/CE02 never, pasted invites left to the game)");
        // test29: this build's own network version (the header's, as build.gradle gives the launcher), and the
        // downloaded directory judged at it
        int net = Integer.parseInt(args[0]);
        check(ServerListing.joinable(true, O, net, net, net) && !ServerListing.joinable(false, O, net, net, net));
        check(!ServerListing.joinable(true, O, net - 1, net, net) && !ServerListing.joinable(true, O, net + 1, net, net));
        check(ServerListing.joinable(false, M, net, net, net) && !ServerListing.joinable(false, M, net - 1, net, net));
        System.out.println("PASS: at this build's network version " + net + ": its co-op and multiplayer joinable, "
            + (net - 1) + " and " + (net + 1) + " not");
        if (args.length > 1) {
            var live = ServerListing.parse(Files.readString(Path.of(args[1])).replace("\ufeff", ""));
            check(!live.isEmpty());
            int players = live.stream().mapToInt(s -> s.players).sum();
            long coop = live.stream().filter(s -> s.kind == O).count(), coopJoinable = live.stream()
                .filter(s -> s.kind == O && ServerListing.joinable(true, O, s.version, net, net)).count();
            long joinable = live.stream().filter(s -> s.kind == M && ServerListing.joinable(false, M, s.version, net, net)).count();
            System.out.println("PASS: downloaded directory: " + live.size() + " servers, " + players + " reported players; "
                + coop + " co-op (" + coopJoinable + " joinable at network " + net + "), " + joinable
                + " multiplayer joinable at network " + net);
        }
        System.out.println("PASS: native invites, TSV listings, malformed/duplicate/bounded inputs");
    }
}
''')
subprocess.run(["javac", "-d", str(OUT), str(JAVA / "ServerInvite.java"), str(JAVA / "ServerListing.java"), str(harness)], check=True)
NETWORK = re.search(r"^#define HALO_PORT_NETWORK_VERSION (\d+)$", (ROOT / "port/linux/include/halo_port_limits.h").read_text(), re.M).group(1)
subprocess.run(["java", "-cp", str(OUT), "com.halo.decomp.BrowserCheck", NETWORK, *sys.argv[1:]], check=True)

source = (ROOT / "source/networking/network_client_manager.c").read_text()
start = source.index("boolean network_game_client_advertised_game_compatible(")
end = source.index("\nboolean network_game_client_join_first_available_game(", start)
limits = (ROOT / "port/linux/include/halo_port_limits.h").read_text()
defines = "\n".join(re.findall(r"^#define HALO_PORT_(?:NETWORK_VERSION(?:_MINIMUM|_MAXIMUM)?|ADVERTISED_DISTRIBUTED_FLAG|ADVERTISED_IN_PROGRESS_FLAG) .*$", limits, re.M))
c = OUT / "compatibility.c"
c.write_text(r'''
#include <assert.h>
#include <stdio.h>
typedef int boolean;
typedef unsigned short word;
#define NONE (-1)
#define TRUE 1
#define FALSE 0
#define MAXIMUM_NETWORK_ADVERTISED_GAMES 4
#define csprintf sprintf
#define network_event(...) ((void)0)
#define HALO_CAMPAIGN_NETWORK_VERSION 0xCE01
#define HALO_CAMPAIGN_ADVERTISED_FLAG 2
static boolean network_campaign_advertised(unsigned short v, unsigned char f) { return v==HALO_CAMPAIGN_NETWORK_VERSION && (f&3)==3; }
struct network_advertised_game { int unused; };
struct network_game_client { struct network_advertised_game available_games[4]; };
static struct { unsigned int version, flags; } network_game_client_advertised_versions[4];
static void platform_show_message(const char *title, const char *message) { (void)title; (void)message; }
''' + defines + "\n" + source[start:end] + r'''
int main(void) {
    struct network_game_client client = {0};
    for (int version = 0; version < 26; version++) for (int flags = 0; flags < 4; flags++) {
        network_game_client_advertised_versions[0].version = version;
        network_game_client_advertised_versions[0].flags = flags;
        assert(network_game_client_advertised_game_compatible(&client, &client.available_games[0], 1)
            == ((flags & HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG) && (version >= HALO_PORT_NETWORK_VERSION_MINIMUM && version <= HALO_PORT_NETWORK_VERSION_MAXIMUM)));
    }
    /* test27: this app's own co-op before 1.0.9 (CE01, CE02) is retired: never joined, whatever its flags */
    for (int version = 0xCE01; version <= 0xCE02; version++) for (int flags=0;flags<4;flags++) {
        network_game_client_advertised_versions[0].version = version;
        network_game_client_advertised_versions[0].flags=flags;
        assert(!network_game_client_advertised_game_compatible(&client,&client.available_games[0],1));
    }
    assert(!network_game_client_advertised_game_compatible(NULL, NULL, 0));
    assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[4], 0));
    printf("PASS: 112 native compatibility cases: network %d only (OpenCE's, in progress or not), the retired CE01/CE02 refused, absent client and out-of-range slot\n", HALO_PORT_NETWORK_VERSION);
}
''')
subprocess.run(["clang", "-fsanitize=address,undefined", str(c), "-o", str(OUT / "compatibility")], check=True)
subprocess.run([str(OUT / "compatibility")], check=True)
