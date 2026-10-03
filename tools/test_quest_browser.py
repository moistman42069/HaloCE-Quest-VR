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
        String campaign = row.replace("\t2\t12\t128\t1\t10", "\t0\t1\t2\t1\t52737");
        check(ServerListing.parse(campaign).get(0).description().contains("Campaign co-op"));
        for(int cap=1;cap<=128;cap++) {
            check(ServerListing.campaignCapacityCompatible(0xCE01,cap,true)==(cap==2));
            check(ServerListing.campaignCapacityCompatible(11,cap,true));
            check(ServerListing.campaignCapacityCompatible(0xCE01,cap,false));
        }
        if (args.length > 0) {
            var live = ServerListing.parse(Files.readString(Path.of(args[0])).replace("\ufeff", ""));
            check(!live.isEmpty());
            int players = live.stream().mapToInt(s -> s.players).sum();
            System.out.println("PASS: downloaded directory: " + live.size() + " servers, " + players + " reported players");
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
