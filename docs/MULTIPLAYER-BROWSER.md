> **Current release candidate: v1.0.10 (test28, 2026-10-06).** Native System Link and the launcher's separate multiplayer/co-op browsers use OpenCE Build 138/network 20. The prior app's network 9–11 and CE01/CE02 paths are retired. Co-op lobby choices are 2–128; owner testing reports co-op works well, but maximum-size performance is not established. The detailed implementation notes below include earlier browser revisions; see [current OpenCE compatibility](OPENCE-COOP-COMPATIBILITY.md) for the active protocol.

# Current browser behavior (test19 candidate)

**In game: Multiplayer > System Link.** Signed OpenCE public discovery is
integrated from upstream build 84. Up to 256 public games plus nine native LAN
advertisements, deduplicated by host ID and sorted by reported population.
Seven games per page leave rows for Previous/Next/Refresh. Results stay stable
until refresh/navigation. A public selection resolves the host's actual native
advertisement before the normal version/content join gate. Join waits up to
30 seconds and cancels on selection movement or Back. Empty discovery remains
in the list; no automatic public host is created.

The launcher retains community HTTPS catalogs, saved/private invites and its
separate campaign browser. OpenCE signed discovery is not an HTTP directory URL.
PvP public hosting is opt-in. CE01 campaign is not published into the OpenCE PvP
catalog; use the existing co-op directory/private invite/LAN flow. Protocol host
version remains 11; reviewed distributed hosts 9–11 are accepted, with content
and connectivity requirements. No source can enumerate all private servers or
guarantee reachability. Same ISO/revision, missing maps, modified content, NAT,
closed/full sessions and protocol differences have different failure causes.

See [test19 evidence](TEST19-PROGRESS.md) and [player guide](PLAYER-GUIDE.md).
The sections below are historical implementation/research records.

---

> Test15 candidate update: native clients accept v9-v11, PvP hosts advertise v11, and campaign retains CE01 legacy settings serialization. Launcher hosting and controlled updates are described in [TEST15-UPSTREAM.md](TEST15-UPSTREAM.md). Earlier version-specific sections below are historical audit evidence.

# Quest multiplayer browser

Current test12: the full-feed browser and separate campaign host/join are
implemented. See the test12 sections below and CAMPAIGN-PROTOCOL-WIP.md for
runtime limits. Test9-11 paragraphs retain historical behavior and evidence.

## Test11 directory recheck (2026-10-03)

The configured Chupathingy feed returned HTTP 200 with eight listing lines.
No additional compatible native provider was verified. The launcher already
reads this entire feed and supports up to four custom HTTPS feeds; no new
provider preset is justified by the evidence. Primary compatibility reference:
[ChupathingyCE](https://github.com/ChupathingyCE/chupathingyce).
Native campaign co-op remains unfinished; see TEST11-PROGRESS.md and
COOP-FEASIBILITY.md. Web streaming rooms and classic PC/SAPP servers are not
compatible substitutes.

## Test10 update

User confirmed test9 multiplayer worked. The short supplied recording shows
seven listed servers/eighteen reported players followed by gameplay. This
does not establish every platform combination or server as tested.

Test10 merges up to four HTTPS directories (one URL per line in Directory
settings), deduplicates invites and displays up to 512 servers. The entire
merged list is sorted by **descending reported player count**, with readiness
and name only breaking ties; full/incompatible listings stay disabled. The
community list comes before saved invites. One failed source does not erase
the other sources. Chupathingy remains the only verified compatible default;
increasing capacity does not create servers or guarantee more active hosts.

Campaign host/join remains open work; see COOP-FEASIBILITY.md. The following
test9 notes preserve the original implementation/research history.

## Default service and compatibility (checked 2026-10-02)

The Android/Quest launcher's **Multiplayer servers** button reads the live
ChupathingyCE directory at `https://halo.milenko.org/v1/games.txt`. It lists
server names, maps, modes, player counts and network versions. Since test10,
all listings sort by descending player count, with readiness/name breaking ties.
Full/closed or incompatible directory entries cannot be joined from that row.
Refresh is manual; a listing is a host report, not a measured ping or guarantee
of availability. The response checked during development had **6 servers and
27 reported players**, all version 10. This is a dated snapshot, not a claim
about current population or the largest population across all Halo editions.

Research found this live directory attached to the same native engine and
invite protocol, making it the best verified compatible option found. Other
Halo editions' player populations do not establish compatibility. No public
directory service was created or paid for, and no session was published.

Primary references:

- [ChupathingyCE project](https://github.com/ChupathingyCE/chupathingyce):
  Windows, Mac, Linux, Android clients, native OpenCE interoperability, and
  public game listings.
- [Directory parser](https://github.com/ChupathingyCE/chupathingyce/blob/main/port/linux/src/browser.c):
  `parse_game`, `update_list`, `browser_join` specify TSV fields and the same
  64-hex-digit invite code used by this port.
- [Native port multiplayer](https://github.com/cybersecurity/halo-ce-universal/blob/main/port/linux/README.md#internet-play):
  invite lifetime, System Link joining, STUN/UDP hole punching and NAT limits.
- [Version 10 change, pinned commit](https://github.com/cybersecurity/halo-ce-universal/commit/d1c7243cb20eab4488efa1266e259b1f4d5240f6):
  appends `_distributed_message_pings`, an optional scoreboard message; it
  does not change existing game message layouts or join requests.

## Version gate evidence

This build still advertises and sends **network version 9**. Its client accepts
distributed hosts of **9 and 10 only**. Local
`network_distributed_handle_message` explicitly ignores reserved IDs 19-31
(including the v10 ping), rejects IDs outside the enum, and accepts campaign
IDs 32-36 only in campaign sessions. Batches dispatch each bounded submessage separately, so
discarding ping data does not discard a sibling gameplay message. Version-10
scoreboard ping display is not implemented here. No protocol number was
blindly incremented, and no version outside this reviewed pair is accepted.

The Android `BuildConfig` version range is generated from
`halo_port_limits.h`, so its join buttons use the same range as the native
client. Tests cover versions 0–14 with/without the distributed flag, missing
client state, and an invalid advertised-game slot. Actual Quest-to-desktop/Mac
play is still **unverified on hardware**; do not call these tests a multiplayer
session result. Matching maps and compatible game rules are still required.

Retail Halo PC/Custom Edition, MCC and original Xbox are different protocols.
Browser/WebRTC ports cannot be assumed compatible merely because they share
decompiled game code. No gateway for those protocols is included.

## Using it

1. Open the Quest/Android launcher, then **Multiplayer servers**.
2. Pick a compatible open game (the most populated ones appear first).
3. **Join** writes the native invite atomically and starts the game.
4. In the game, use **Multiplayer > System Link** and select the host after
   its tunnel connects. Nearby LAN games are discovered in that same list.

The launcher writes `join_link.txt` beside the active game's maps, including
the VR shared-data fallback `/sdcard/Documents/HaloCE`. Previously it always
wrote the app-private directory, which the game did not poll when shared maps
were selected. Directory failures do not stop Play or erase saved invites.

**Add / paste server invite** saves a host's `halo://join/<64 hex>` link or
bare 64-digit code privately. Invites normally last only as long as the host
process; a saved favorite may need a replacement link after the host restarts.
Old 44-digit invites and malformed inputs are refused. Hosts can use the
existing System Link hosting path; this candidate does not automatically
publish their private invites. ChupathingyCE's site supports manually listing
an OpenCE host invite through its own account flow.

**Directory settings** allows a different HTTPS endpoint or an empty address
for saved-invite-only operation; **Use ChupathingyCE** restores the default.
Alongside `games.txt`, a custom community catalog may use this JSON shape:

```json
{"schema": 1, "servers": [
  {"name": "Example", "invite": "REPLACE_WITH_CURRENT_64_HEX_INVITE",
   "description": "Blood Gulch", "network_version": 9}
]}
```

The placeholder is deliberately invalid; no fake live servers are bundled.
Requests run off the UI thread, require HTTPS including redirects, have
connection/read/body time limits and a 1 MiB response cap per directory. Test12
removes the silent 512-listing cutoff: every valid distinct listing in each
bounded response is retained, with 50 rows shown at a time and a "Show next 50"
button. Sorting happens before paging. Saved private favorites retain a 512 cap.
No game maps, credentials or saved invitations are uploaded. Displayed names
are plain sanitized text. The game retains its authenticated tunnel, host
rules and normal compatibility checks.

## Verification and remaining device checks

`python3 tools/test_quest_browser.py [downloaded-games.txt]` compiles and runs
the production Java invite/TSV parser and extracts the production native join
gate into an ASan/UBSan harness. Checks include malformed, overlong, duplicate,
closed and full listings, old invites, input caps and version rejection.
The downloaded live directory passed the same parser used in the APK.

Device checks: launcher scrolling/controller or pointer use; joining a live
v10 host; v9 host; LAN host; reconnect after a stale invite; offline directory;
Quest-to-Windows/Linux and ChupathingyCE Mac sessions. NAT traversal has no
relay fallback in the existing native transport, so restricted/symmetric NAT
can still prevent a join. Preserve the connection log before diagnosing it.

## Directory recheck, 2026-10-03

A fresh HTTPS GET of the default feed returned seven v10 listings, with reported
player counts 25, 18, 1, 0, 0, 0 and 0. This is a point-in-time directory response,
not a reachability test or a permanent population claim. It is preserved at
`<private-work>\test12\directory-20261003.txt`. No additional compatible
native-port directory was verified. The existing launcher already fetches this
whole feed and merges up to four configured HTTPS catalogs, sorted by population.

The current primary-source [browser.c](https://github.com/ChupathingyCE/chupathingyce/blob/main/port/linux/src/browser.c)
shows `/v1/announce` with form fields invite/name/map/engine/players/maximum_players/
open/score_limit/teams/version, 20-second heartbeats, withdrawal and stale expiry.
It is a candidate opt-in campaign listing transport, not proof the deployed
backend accepts the new campaign version. No announcement request was posted.

### Full-coverage follow-up

The later GET saved as `directory-coverage-recheck.txt` returned five v10 listings
with reported populations 21, 0, 0, 0 and 0. All are in the supported version
range. No second native-port directory was verified; retail CE master servers
use a different protocol and cannot be presented as compatible native games.
The four configurable feeds merge by invite without the former combined 512 cap.
Full and empty listings remain visible, population sorted, with unavailable joins
disabled. An oversized/failed feed is explicitly reported rather than partially
presented as a complete result. LAN discovery and saved/unlisted invites remain
available. "All" covers advertised, discoverable compatible hosts, not private
hosts that never publish an invite or answer LAN discovery.

Campaign 0xCE01 uses the separate co-op browser. Public listing is opt-in from its
host dialog and requires the live native-host heartbeat; see
`CAMPAIGN-PROTOCOL-WIP.md`. Both browsers accept up to four HTTPS catalogs.


## Test17: game files, revisions and server compatibility

Open **Game files & versions** to import one or more ISO/XISO images, select an
extracted maps folder, or scan the displayed `game-versions/inbox` folder. Each
complete set shows detected cache region/build and a SHA-256 fingerprint. Select
**Use** to activate it for the next launch; **Rename** edits your personal label.
The original installation remains **Existing game data**. Saves stay separate
per set, and current settings are copied once into a newly imported set.

Some server incompatibilities may result from different ISO/revision map files
or modified data. Network protocol versions, missing maps, full/closed hosts and
NAT can also prevent joining. Original/Rev1/Rev2 labels are not automatically
verified without trusted hashes. The browser can offer another installed set
containing a missing map, but servers do not advertise authoritative revision or
content fingerprints. Do not change map headers to bypass compatibility checks.

Test17 addresses false rejection of running v11 matches, an action-control
assertion, and reviewed departed-player/rejoin issues. The test16 animation
handoff is preserved. [Full data-library instructions](GAME-DATA-LIBRARY.md).

## Join stages and Quest/Android parity (test20e, 2026-10-04)

The Quest and Android APKs build the same multiplayer code: no networking source
has a VR-only branch, the Java browser/launcher classes, permissions and
`network.*` defaults are shared, and `tools/package-quest.py` refuses a pair whose
networking strings, app classes or entries differ (only the OpenXR loader is
VR-only). `tools/test_test20e_network.py` guards the sources.

A join logs three stages:

1. `joining <host>'s game (stage 1/3: asking the host through signalling)`;
   if nothing answers in 90 s, `no answer from the invite's host (stage 1/3 failed)`.
2. `stage 2/3, the host answered through signalling with N addresses (...)`:
   the direct UDP connection is tried for 30 s and asked for again until the
   join's 90 s run out. A failure says whether packets arrived but did not
   open (a session/build mismatch) or none arrived (a blocked path), and this
   network's NAT class.
3. `stage 3/3, direct connection open after N ms`: the game's own join
   (version check, lobby) follows.

The STUN lines classify this network: "keeps one public port for every
destination" (lenient) or "gives each destination its own port" (strict, usual
on mobile data). Two strict NATs, or a strict joiner and a port-restricted host,
cannot connect without a forwarded port; there is no relay. The run log also
records the device's network type (`Network: Wi-Fi ...` or `mobile data`). The
in-game browser follows these stages instead of a fixed 30 s and shows the
reason (for a strict NAT: "Try Wi-Fi."). With the browser active, the stock
list's "start server if none advertised" fallback no longer prints a red
warning each time A is pressed while a join is in progress.
