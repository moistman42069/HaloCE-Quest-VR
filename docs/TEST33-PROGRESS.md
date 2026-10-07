# Test33: recover public browsing after a local network session

## Evidence and diagnosis

The supplied Quest 3 log is from Test32, version 1.0.13 / code 42, using
OpenCE Build 145 / network 22. It first creates a local network game at
`127.0.0.1:5150`; the native client joins that host successfully and waits in
the lobby. Later, four public-browser selections each establish the direct
P2P peer connection, but the browser never finds the matching native Halo
game advertisement and times out.

The first `network client disposed` appears only after that timeout. Source
tracing found the lifecycle error: `ui_widget_port_browse()` reused any
existing global network client, including one already joined to the local
host. That client is in pregame/game state and is no longer searching, so it
cannot discover the remote host's native game advertisement. The direct P2P
connections are real; the failure occurs after them, at native game discovery.

I compared the Test31b runtime commit (`3399023a`) with Test32. The P2P
signalling, tunnel, XNet mapping, game protocol, and browser join code did not
change in that interval; Test31b and Test32 both use Build 145 / network 22.
The log's local-host-then-public-browser sequence exposed a missing session
reset in the shared browser entry path. This is a lifecycle fix, not a change
to wire compatibility or protocol version. OpenCE's official
[Build 145 release](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-145)
was the latest release checked for this pass.

## Change

When entering a browser, an existing client is retained only if it is still
in its search state. A client in joining, pregame, gameplay, or postgame state
now goes through the same stock search initializer, which disposes the stale
client/server and creates a fresh game-search client. An existing active
search remains intact. LAN, direct-link, public browser, multiplayer protocol,
co-op simulation, vehicles, VR settings, and Android touch behavior otherwise
remain unchanged.

The added production-helper test covers first entry with no client, preserving
an active search, and resetting joining, pregame, gameplay, and postgame
clients. The attached log remains private and was not copied into the repo or
build archives.

## Candidate status

Target: version **1.0.14 / code 43**, paired Quest VR and flat Android APKs,
OpenCE Build 145 / network 22. The lifecycle repair is shared native code, so
both APKs were rebuilt from runtime commit
`e522f34c04969daaa87bfa952bb0256b222be590`. Each edition passed all 56
registered host regression suites, native compilation, APK assembly, original
project-certificate signature verification, payload-preservation checks, and
16 KB alignment. The paired APK checks confirmed matching application classes
and network paths. Exact hashes, metadata, candidate packaging and the device
test request are in [TEST33-DELIVERY.md](TEST33-DELIVERY.md).

The first build attempt caught obsolete local prototypes conflicting with the
pinned OpenCE header; those redundant declarations were removed before the
successful rebuild. Upstream `source/networking` and `source/bungie_net` remain
unchanged from the accepted Test31b runtime. This establishes a corrected
candidate, not proof the public server join now succeeds on a headset. The
owner's local-host-then-public-browser flow remains the acceptance test.
