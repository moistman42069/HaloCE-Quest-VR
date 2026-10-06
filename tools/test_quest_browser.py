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
        // test26: co-op protocol CE02 (52738); a host on another app version's (CE01) is still listed as co-op, marked
        String campaign = row.replace("\t2\t12\t128\t1\t10", "\t0\t1\t2\t1\t52738");
        check(ServerListing.CAMPAIGN_VERSION == 0xCE02);
        check(ServerListing.parse(campaign).get(0).description().contains("Campaign co-op"));
        check(!ServerListing.parse(campaign).get(0).description().contains("another app version"));
        String older = row.replace("\t2\t12\t128\t1\t10", "\t0\t1\t2\t1\t52737");
        check(ServerListing.parse(older).get(0).description().contains("Campaign co-op (another app version)"));
        check(ServerListing.isCampaign(0xCE01) && ServerListing.isCampaign(0xCE02) && !ServerListing.isCampaign(11) && !ServerListing.isCampaign(0));
        for(int cap=1;cap<=128;cap++) {
            check(ServerListing.campaignCapacityCompatible(0xCE02,cap,true)==(cap==2));
            check(ServerListing.campaignCapacityCompatible(11,cap,true));
            check(ServerListing.campaignCapacityCompatible(0xCE02,cap,false));
        }
        // test27: the directory's three kinds (format as served 2026-10-05: 12 columns, the last a roster).
        // Synthetic rows: no real invites or player names.
        String[] synthetic = {
            "%s\tPvP v11\tbloodgulch\t2\t3\t16\t1\t11\t9\t0\t0\t",
            "%s\tPvP v18 roster\tlevels\\test\\hangemhigh\\hangemhigh\t2\t4\t4\t0\t18\t13\t50\t1\t0:A|1:B|0:C|1:D",
            "%s\tLobby v11\tcarousel\t0\t0\t128\t1\t11\t1\t0\t0\t",
            "%s\tLobby v18\tbeavercreek\t0\t6\t16\t1\t18\t81\t0\t0\t",
            "%s\tOpenCE coop v17\ta30\t0\t4\t4\t0\t17\t2\t0\t0\t",
            "%s\tOpenCE coop v18\tb40\t0\t24\t32\t1\t18\t2\t0\t0\t",
            "%s\tOpenCE coop path\tlevels\\A10\\a10\t0\t1\t4\t1\t17\t2\t0\t0\t",
            "%s\tHalo CE co-op - Normal\ta10\t0\t1\t2\t1\t52738\t3\t0\t0\t",
            "%s\tHalo CE co-op - Easy\tc40\t0\t1\t2\t1\t52737\t3\t0\t0\t",
            "%s\tCTF on a campaign map\tb30\t1\t2\t16\t1\t11\t3\t0\t1\t",
            "%s\tFuture columns\tbloodgulch\t2\t1\t16\t1\t11\t3\t0\t0\t\tsomething\tmore",
        };
        StringBuilder body = new StringBuilder();
        for (int i = 0; i < synthetic.length; i++) body.append(String.format(synthetic[i], String.format("%064x", 0x2700 + i))).append('\n');
        var kinds = ServerListing.parse(body.toString());
        check(kinds.size() == synthetic.length);
        ServerListing.Kind M = ServerListing.Kind.MULTIPLAYER, O = ServerListing.Kind.OPENCE_COOP, C = ServerListing.Kind.CAMPAIGN;
        ServerListing.Kind[] expected = {M, M, M, M, O, O, O, C, C, M, M};
        for (int i = 0; i < synthetic.length; i++) check(kinds.get(i).kind == expected[i]);
        check(kinds.get(1).rosterCount == 4 && kinds.get(0).rosterCount == 0 && kinds.get(10).rosterCount == 0);
        check(kinds.get(4).description().contains("OpenCE co-op (network v17)") && kinds.get(5).description().contains("OpenCE co-op (network v18)"));
        check(kinds.get(7).description().contains("Campaign co-op") && !kinds.get(7).description().contains("another"));
        check(kinds.get(8).description().contains("Campaign co-op (another app version)"));
        // listed: the multiplayer browser never shows co-op of either kind; the co-op browser shows both, never multiplayer
        for (ServerListing listing : kinds) {
            boolean coop = listing.kind != M;
            check(ServerListing.listedIn(true, listing.kind) == coop && ServerListing.listedIn(false, listing.kind) == !coop);
        }
        // joinable (network 9-11 here): multiplayer in range from the multiplayer browser only; this app's CE02 co-op
        // from the co-op browser only; OpenCE co-op and CE01 never; pasted invites (version 0) left to the game
        int lo = 9, hi = 11;
        boolean[] joinPvp = {true, false, true, false, false, false, false, false, false, true, true};
        boolean[] joinCoop = {false, false, false, false, false, false, false, true, false, false, false};
        for (int i = 0; i < synthetic.length; i++) {
            ServerListing l = kinds.get(i);
            check(ServerListing.joinable(false, l.kind, l.version, l.maximum, true, lo, hi) == joinPvp[i]);
            check(ServerListing.joinable(true, l.kind, l.version, l.maximum, true, lo, hi) == joinCoop[i]);
        }
        for (int v = 0; v <= 70000; v += 7) for (int engine = -1; engine <= 5; engine++) for (String map : new String[]{"a10", "bloodgulch", ""}) {
            ServerListing.Kind k = ServerListing.kind(v, engine, map);
            boolean pvp = ServerListing.joinable(false, k, v, 16, true, lo, hi), coop = ServerListing.joinable(true, k, v, 2, true, lo, hi);
            if (v != 0) check(!(pvp && coop));                                   // never both
            if (v != 0 && v != 0xCE02) check(!coop);                              // co-op joins only CE02
            if (v > hi && !ServerListing.isCampaign(v)) check(!pvp);              // no newer native protocol, ever
            if (k == O) check(!pvp && (v == 0 || !coop));                         // OpenCE co-op: never joinable
        }
        check(!ServerListing.joinable(true, C, 0xCE02, 4, true, lo, hi));       // CE02 is two players
        check(ServerListing.joinable(true, M, 0, 0, false, lo, hi) && ServerListing.joinable(false, M, 0, 0, false, lo, hi));
        // a saved invite without an engine is never taken for OpenCE co-op
        check(ServerListing.kind(17, -1, "a10") == M && ServerListing.kind(17, 0, "A10") == O);
        System.out.println("PASS: directory kinds (multiplayer, OpenCE co-op on engine 0 + a campaign map, this app's CE co-op),"
            + " 12-column rows with rosters and future columns, browser placement and joinability (OpenCE co-op and newer"
            + " native versions never joinable; CE02 two-player only; pasted invites left to the game)");
        if (args.length > 0) {
            var live = ServerListing.parse(Files.readString(Path.of(args[0])).replace("\ufeff", ""));
            check(!live.isEmpty());
            int players = live.stream().mapToInt(s -> s.players).sum();
            long opence = live.stream().filter(s -> s.kind == O).count(), ours = live.stream().filter(s -> s.kind == C).count();
            long joinable = live.stream().filter(s -> s.kind == M && ServerListing.joinable(false, M, s.version, s.maximum, true, lo, hi)).count();
            System.out.println("PASS: downloaded directory: " + live.size() + " servers, " + players + " reported players; "
                + opence + " OpenCE co-op (not joinable), " + ours + " this app's co-op, " + joinable
                + " multiplayer joinable at network " + lo + "-" + hi);
        }
        System.out.println("PASS: native invites, TSV listings, malformed/duplicate/bounded inputs");
    }
}
''')
subprocess.run(["javac", "-d", str(OUT), str(JAVA / "ServerInvite.java"), str(JAVA / "ServerListing.java"), str(harness)], check=True)
subprocess.run(["java", "-cp", str(OUT), "com.halo.decomp.BrowserCheck", *sys.argv[1:]], check=True)

source = (ROOT / "source/networking/network_client_manager.c").read_text()
start = source.index("boolean network_game_client_advertised_game_compatible(")
end = source.index("\nboolean network_game_client_join_first_available_game(", start)
limits = (ROOT / "port/linux/include/halo_port_limits.h").read_text()
defines = "\n".join(re.findall(r"^#define HALO_PORT_(?:NETWORK_VERSION(?:_MINIMUM|_MAXIMUM)?|ADVERTISED_DISTRIBUTED_FLAG) .*$", limits, re.M))
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
    for (int version = 0; version < 15; version++) for (int flags = 0; flags < 4; flags++) {
        network_game_client_advertised_versions[0].version = version;
        network_game_client_advertised_versions[0].flags = flags;
        assert(network_game_client_advertised_game_compatible(&client, &client.available_games[0], 1)
            == ((flags & HALO_PORT_ADVERTISED_DISTRIBUTED_FLAG) && (version >= HALO_PORT_NETWORK_VERSION_MINIMUM && version <= HALO_PORT_NETWORK_VERSION_MAXIMUM)));
    }
    network_game_client_advertised_versions[0].version = HALO_CAMPAIGN_NETWORK_VERSION;
    for (int flags=0;flags<4;flags++) {
        network_game_client_advertised_versions[0].flags=flags;
        assert(network_game_client_advertised_game_compatible(&client,&client.available_games[0],0)==(flags==3));
    }
    assert(!network_game_client_advertised_game_compatible(NULL, NULL, 0));
    assert(!network_game_client_advertised_game_compatible(&client, &client.available_games[4], 0));
    puts("PASS: 60 native compatibility cases including in-progress PvP, campaign identity, absent client and out-of-range slot");
}
''')
subprocess.run(["clang", "-fsanitize=address,undefined", str(c), "-o", str(OUT / "compatibility")], check=True)
subprocess.run([str(OUT / "compatibility")], check=True)
