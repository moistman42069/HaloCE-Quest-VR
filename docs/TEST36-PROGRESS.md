# Test36 progress — private candidate

**Candidate:** test36 / app version 1.0.17-test36 / Android version code 46  
**Upstream base:** OpenCE Build 157, commit `73dc01d`, network protocol 24  
**Public release:** unchanged at v1.0.16 / code45 / network23  
**Publication:** not authorized; candidate is for owner testing only.

## User reports and scope decision

The new report says a rifle scope veers when support grip engages, but looks
correct with one hand. The supplied clip shows the two-hand path in use but has
no runtime log or controller pose values. Source confirms the exact transition:
`compute_aim_pose()` uses calibrated weapon-hand aim in one-hand mode, then
replaces forward aim with the line from the weapon grip to the support grip
when two-hand grip locks. The scope layer uses that aim pose. This can explain
why the scope's direction/centering changes at two-hand engagement; the clip
does not establish whether the measured grip line is wrong for this headset or
whether the user's two-hand alignment is the cause.

The candidate logs on relevant state changes rather than every frame. Two-hand
engage/release and zoom transitions record hand side, grip separation,
grip-line angle and its forward/right/up components against calibrated
weapon-hand aim, tracking validity, zoom, scope setting and weapon class. Scope
gate logs include the reason, input/tracking state and zoom. When its render
path changes, the scope camera log records zoom, shape, hand mode, two-hand
state, viewport size, eye resolution, screen scale and FOV; the scope-layer log
records its center, applied local offset, shot direction and size. On launch,
the Android log records the active game-data root plus each map's recognized
header/build summary and file size; it does not infer Original/Rev1/Rev2 from a
filename. These additions leave aim, scope placement, zoom, two-hand locking
and smoothing unchanged. Do not alter those behaviors until a device log shows
the measured poses and scope render state at the fault.

Older Rev2 scope and Shade turret reports, and the campaign Continue/save
report, have no matching diagnostic logs for their failing sessions. Shade
turret reports conflict: one report described stick-only aiming, while a later
Quest OS 78 report said Rev2 scopes and Shade turrets worked. This candidate
does not change any of those behaviors. The existing vehicle regression test
checks selected turret aim-source routing (right, left, head, stick) and the
native-facing fallback, but that host test cannot establish which source or
tracking state was active in the reported headset session. Runtime diagnostics
record mounted role, seat and vehicle object, configured/effective aim source,
and controller-tracking/fallback transitions.
If Shade turret aiming fails again, preserve the launch log and note the Quest
OS, game revision, gunner seat, turret aim setting and whether the view was
head- or controller-driven.

## Implementation

- Upgrade native network constants and launcher metadata from network23 to
  network24, as required by OpenCE Build157.
- Preserve the Build148 particle-radius and native error-screen fixes.
- Port Build157 analog trigger pressure for analog-rate-of-fire weapons.
- Port the PC vehicle-set option and Custom Edition item spawn facing.
- Port single-player internet/LAN host start and matching lobby waiting text.
- Port Builds156–157's spatial panning, distance fade, obstruction/occlusion
  filtering and room reverb for stereo sounds positioned in the world; ordinary
  unpositioned stereo remains on its existing path.
- Preserve the accepted Android touch and Quest VR settings/geometry defaults.
- Add transition-only diagnostics for two-hand aim and selected vehicle hand
  aim, scope camera and scope-layer placement; do not alter their runtime math.
- Recommend the original Xbox Halo CE XISO on initial setup, game-file import
  and the main launcher screen. Rev 1/Rev 2 remain importable, but are not the
  recommended files for best compatibility.
- Add a persistent Halo-inspired launcher type option on both initial setup
  and the Play screen; it applies Orbitron to short labels/buttons while keeping
  long instructions in the standard sans font. Both screens also show the
  support DM `@MeWhenINameMyself` on Discord. Orbitron is bundled with its OFL.

## Existing project updater audit (2026-10-08)

`Updater.java` and `UpdatePolicy.java` still target only
`moistman42069/HaloCE-Quest-VR` for installable project releases. They filter
drafts/prereleases, require matching `compatibility.json`, verify release
asset digests and APK package/version/minimum-API/signing certificate, check
that the manifest's network range is valid, and preserve local saves/configuration.
The separate upstream check reads the
network protocol header and reports when integration is needed; it does not
replace the integrated engine. The live GitHub latest endpoint currently
returns stable v1.0.16 with Android and Quest APKs plus `compatibility.json`;
the published asset digests, sizes, package codes 45, minimum API 28 and
network23 fields agree with the manifest. Candidate code46 correctly cannot
be downgraded to that public code45 build. No updater code was changed. This
is a source/metadata audit; it does not substitute for exercising the update
flow on an Android device.

## Validation and remaining owner checks

### Android empty-list report (2026-10-08)

The supplied 11:51 Android session is public 1.0.16/code45/network23 on a
Motorola phone using validated mobile data. It starts signed public discovery
and continues local search broadcasts for about 23 seconds before pausing.
There is no crash or join attempt. The older log has no broker readiness or
listing-rejection information, so it does not establish a carrier block,
version mismatch, empty directory, or Android-specific defect. The stock
System Link log label also appears when OpenCE's public browser initializes
the underlying native client; it does not establish that the wrong screen was
selected.

Compared with pinned OpenCE Build157, the signalling implementation retains
the same transport and broker endpoints. This port reads its existing config
list instead of upstream's external brokers file; the old default migrates to
the same four endpoints. Network23 rejects other network versions by design;
the already planned network24 integration is necessary for network24 hosts,
but cannot be claimed to resolve every empty-list case.

Added observational broker-ready/failure transition logs (limited to one of
each per broker per 30 seconds) and a discovery summary every ten seconds
while browsing. It distinguishes broker readiness, visible games, queued and
received listings, malformed payloads, version rejection, expiry and signature
verification. Foreign version headers are explicitly labeled unverified.
No invite, password or signing-key material is added to these summaries.
The existing signed-listing harness verifies foreign versions remain excluded
and summary frequency stays bounded. Network admission and filters are
unchanged. Retest Play > Multiplayer > Join Game > Server Browser on this
candidate; reset FILTERS and capture at least 30 seconds if the list is empty.

The owner also reproduced the empty list on Wi-Fi. A read-only probe at
2026-10-08 11:59 EDT successfully connected and subscribed to all four default
brokers. Its fresh signed listings included 18 network24 hosts and no
network23 hosts (older incompatible versions were also present). This is a
point-in-time sample from the development machine, not a reconstruction of
the phone's earlier session. It establishes a real current compatibility gap
for the public network23 APK. Official upstream Latest was still Build157.
The follow-up 12:01 EDT sample agreed. A captured fresh listing was also fed
through the production `p2p_lobby.c`/`p2p_crypto.c` with AddressSanitizer:
network24 accepted it and the network23 control rejected it. The independent
read-only probe verified both the Ed25519 signature and the signing key's
X25519/SHA-256 topic-slot identity. No host/join session was performed.

The font review also corrected normal-font restoration after a short label
becomes a long status message. Dynamic import, updater and mod status labels
always retain the standard font.

Automated test/build results and APK hashes are recorded in
[TEST36-DELIVERY.md](TEST36-DELIVERY.md). Host checks do not replace testing on
the Android device and Quest. For the scope report, compare the same weapon and
zoom state one-handed, then engage two-hand grip; keep the generated launch log
and report the app version, Quest OS, game-file set/revision, weapon hand and
whether two-hand grip was manual or automatic. The public network23 release is
not a compatible multiplayer peer for this network24 candidate.
