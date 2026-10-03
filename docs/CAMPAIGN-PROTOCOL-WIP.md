> **Subsequent acceptance, 2026-10-03:** the owner accepted the delivered test14 pair and explicitly authorized publication as the latest release. This supersedes the earlier release hold below. Original investigation/check results remain historical; no complete campaign playthrough or all-device certification is inferred. See [current state](CURRENT-STATE.md) and [release provenance](RELEASE-PROVENANCE.md).

> **Current follow-up: test14 (2026-10-03).** Owner confirmed a Quest/flat session and VR body movement visible on flat Android; NPC animation problems blocked public release. Message 39 adds optional reliable 24-byte NPC animation impulses (round, seed, object, short impulse, word alignment-present, float2 alignment). Existing CE01 layouts and avatar IDs stay fixed; use test14 on both peers. Current evidence and limits: [COOP-COMPATIBILITY-AUDIT.md](COOP-COMPATIBILITY-AUDIT.md), [CURRENT-STATE.md](CURRENT-STATE.md). The test12 statements below are historical.

# Campaign protocol implementation checkpoint

This is the test12 candidate implementation. No successful remote campaign play is claimed.
Last delivered test11 has competitive multiplayer, not native campaign co-op.
The standing implementation audit and both native/Java compiles are complete.
Final artifact checks and paired-device acceptance are separate remaining steps.

## Identity and authority

Protocol 0xCE01, campaign advertisement flag and campaign map marker identify
exactly two players, one campaign mission and difficulty 0..3. Both clients must
support this protocol; competitive v9/v10 layouts and behavior remain separate.
The join nonce has a campaign capability echo, not an authentication claim.
Host scenario scripts and AI decide mission simulation. Client scenario scripts
do not execute; console restrictions remain unchanged. Respawn, all-dead loss,
BSP triggers and remote saved-unit slots use host authority.

## Presentation

Reliable message 32 carries allowlisted native presentation calls, with round,
seed, opcode and typed arguments. Strings are bounded offsets in a 256-byte
buffer; neither pointers nor script source travels. Decoding checks exact size,
count, string termination, type, tag group, object identity and scenario indices.
HUD, fades, camera, titles, input controls, music, scripted impulses and custom
animations are covered. List animations expand to individual unit calls locally.
Actual AI speech playback is captured too; queued speech is not played early.

Scenery/devices/sound scenery join the campaign object mask. Message 33 adds
device power, position, velocities and targets using local device-group mapping.
Object creation precedes presentation and device records. Message 35 adds scale,
visibility, collision/shadow/movie-star flags, non-player health, damaged regions,
permutations and generic attachments. Parent nodes, transforms and ancestor cycles
are checked; inventory/vehicle-seat attachment stays with the existing inventory
path. Device snapshots are forced at barriers even between ordinary send ticks.

Message 36 carries validated non-player unit controls captured from the actual
host `unit_control` calls, including recorded vehicle movements. Clients run the
native animation/fire presentation with those inputs, never independent AI.
Older actor-control datagrams are rejected. Campaign damage accepts scenery and
device targets, retains host hit validation, and sends AI-versus-AI hit effects to
the partner. Competitive filtering and hit masks remain unchanged.

The allowlist also covers navpoints, scripted effects, allegiance changes,
emotion animations, suspension, collision and cinematic BSP-placement control.
No-argument calls are captured by the runtime dispatch; typed argument calls are
captured after evaluation. Script globals stay host-owned with scenario threads;
raw HS state is never copied into the client process.

## Loading, BSP and checkpoints

Message 34 coordinates ready/BSP/save/restore, acknowledgements and release.
The main loop keeps pumping transport and rendering while simulation is held.
Initial loading hashes the mission file, optional map audio and optional shared
bitmaps/sounds/loc resources with SHA-256. Optional-file presence is included.
Files are read locally during loading; only a digest is sent. Mismatches end the
session with a diagnostic before gameplay begins. This deliberately requires the
same resource set even if a particular map does not use every shared resource.

Campaign distributed messages and host clock messages encode an 8-bit generation
and 24-bit tick in their existing time field. Generations prevent pre-restore
traffic being accepted after clocks rewind. Generations now continue across maps,
so delayed generic object packets cannot become valid in the next mission.
A process allows at most 255 barriers and six days of ticks per map; limits end
the session rather than wrap. Restart the application if that limit is reached.
Round/seed checks still guard lifecycle and campaign-specific records. Render
interpolation is reset with simulation clocks at barrier snapshots.

Each peer saves/restores its own native checkpoint; host process memory is never
copied into another process. A fresh host object snapshot follows restoration,
with device/presentation queues and prediction clocks reset. Persistent solo
save export and last-solo resume writes are disabled for online campaign.
Checkpoint requests during a barrier are queued. If no shared checkpoint exists,
both players return through the network loading lobby to restart the mission.

Restart and next mission use ordered native postgame/pregame/loading messages.
Host mission/difficulty settings survive that path; ordinary PvP map/variant
editing cannot erase an active campaign's identity. Final mission completion and
partner disconnect end the session. Late join is refused: replaying full prior
cinematic/checkpoint history is not implemented.

## Bootstrap and remaining work

`network_campaign_session.c` consumes a bounded one-shot `coop_host.txt` in the
game data root: four integers (format 1, mission 0..9, difficulty 0..3, public 0/1).
It uses the normal native network lobby and adds one local controller, then starts
when both machines/players have joined. `CoopLauncher` now writes this request
atomically, checks the selected map exists, and clears conflicting join requests.
The separate campaign browser accepts protocol 0xCE01 and saved private invites;
normal PvP listings retain their independent browser and compatibility checks.

Native `coop_status.txt` is atomically refreshed only for a real hosting session.
`CoopPublisher` reads a bounded fresh status file, announces only when the host
checked the public-listing option, sends 20-second heartbeats, updates population
and join availability, and withdraws on stale status/exit. Failures produce a
launch-log diagnostic and a user-visible private-invite fallback. The backend's
acceptance of protocol 0xCE01 is not proven: no fake public host was posted.
The process's private invite remains usable subject to the existing NAT limits.

Audit fixes: remote-player respawn/teleport no longer requires two *local*
controllers; restored online units use the network attach path; second-player
starting equipment uses the campaign player's slot, not a missing controller.

Before delivery: inspect final artifact identity/signing/contents and package
both APKs with source. Actual
headset/phone campaign acceptance must cover initial cinematics, AI/devices,
checkpoint/both-dead restore, BSP transition, restart and next mission.

Compile results and exact logs are in TEST12-PROGRESS.md. Do not treat this
checkpoint as runtime acceptance or advertise a currently playable release.
