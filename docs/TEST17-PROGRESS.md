# Test17: multiplayer compatibility and game-data library

2026-10-03. Branch `test17-network-data-profiles`, based on test16 continuation
`40d965065654a543fb154a4621d149bc9d71021c`. Private VR/flat testing candidate.
Test14 remains the accepted public release; no new release is authorized.

## Owner result and log findings

The owner reports substantially improved, seamless test16 action animations and
asks to preserve native physical-melee animation online. Preserve that runtime,
Safe VR geometry, Normal flat geometry, Legs + Arms, tracking and grip behavior.
This feedback does not authorize publishing test16 or certify every feature.

All six supplied logs were reviewed. Private originals remain outside Git.

| Run suffix | Evidence | Conclusion |
| --- | --- | --- |
| 15954, 17864 | Rejected network 11 host while identifying this client as 11; subsequent no-frame watchdog messages | Advertisement gate incorrectly treated PvP in-progress flag 0x02 as campaign identity; Android modal warning also blocked frame submission |
| 16658 | Joins v11; host starts loading; unit_control asserts VALID_FLAGS at units.c:1508 | Upstream player-action bit 15 was passed into a unit control record with only 15 native flags |
| 16354 | No responding host during search, then local host and exit; UPnP unavailable | Reachability/no-host evidence, not demonstrated map-revision failure |
| 15234, 18305 | Normal cleanup/exit code 0 | No assertion in these two runs |

These findings explain concrete failures, not every inaccessible server. None of
these logs establishes a disc CRC/revision mismatch as the cause of the two code
defects. NAT, stale invitations, full/closed hosts, missing/unsupported maps and
genuinely unsupported protocols remain independent compatibility boundaries.

## Runtime changes

- Accept reviewed distributed PvP v9-v11 regardless of the native in-progress
  bit. Campaign identity still requires CE01 plus campaign/distributed flags.
  Log the advertised flags and supported range on rejection.
- Restore upstream `UNIT_CONTROL_PORT_ACTION_ONLY_BIT = 15`: keyboard interaction
  without reload fallback remains a player-action flag, and only that bit is
  stripped before native unit controls. Unit bounds/assertions remain intact.
- Android queued platform notices use an asynchronous toast and full native log
  message instead of stopping the game/XR thread in a modal dialog.
- Adopt upstream player-slot queue reuse and departed killer/assist guards from
  [809408c](https://github.com/cybersecurity/halo-ce-universal/commit/809408c6635a1434fe4dbe3b64195211ddcbe8cf).
  Preserve a queue for the same datum; delete a stale occupant before reuse.
  Construct the deleted datum through unsigned shifts to avoid signed-shift UB.
- Integrate v11's reserved-byte `no_map_weapons` meaning and unarmed grenade
  guard from [933aac6](https://github.com/cybersecurity/halo-ce-universal/commit/933aac61754eb5de2c8496dbe9b8278f033e4c1f).
  The options record remains 28 bytes; invalid Boolean values are rejected.
  Restore ping messages in timestamp/stale-packet filtering alongside campaign
  actors. No native melee/VR action-animation policy is changed.
- Add the shared launcher [game-data library](GAME-DATA-LIBRARY.md), atomic
  selection, ISO/XISO and extracted-folder imports, inbox scan, detected build
  labels, per-file/combined SHA-256, editable user labels, and map-based selection
  assistance from the PvP browser. Original data and saves are retained.

The upstream checkout was fetched and reviewed through 933aac6. This is a
selective integration with the project's separate campaign/avatar paths, not a
claim that every upstream file is byte-identical. Network version remains 11.

## Standing request audit

| Requested area | Current implementation / boundary |
| --- | --- |
| VR body, fingers, collision, grip, actions | Test16 behavior retained; Legs + Arms default, deliberate fixed support grip, native action handoff; owner improved-animation report preserved |
| VR geometry | Safe default/migration retained; flat remains Normal |
| Controller orientation | Test15 per-hand alignment, offsets, aim/grip source, flip and reset retained |
| Flat input | Touch layout editor, swipe aim, SDL/Xbox-style gamepads, reconnect cleanup, response settings, rumble and Auto/Show/Hide touch retained |
| PvP discovery | Whole bounded feed, population sort before paging, four configurable catalogs, saved invites/LAN; only one independently verified native directory |
| PvP hosting/capacity | Launcher host options and 2-128 protocol slots retained; 128-player Quest hosting performance not established |
| Co-op | Separate CE01 host/join/browser, actors/lifecycle and remote VR avatar receiver retained; two-player limit for documented multi-peer barriers, not an arbitrary UI cap |
| Remote avatars | Negotiated campaign/supporting PvP avatars retained; older peers stay stock; full per-finger remote skeleton not available |
| Revision management | New managed sets and factual header/fingerprint detection; exact disc revision and per-server required fingerprints remain unavailable |
| Updates | Signed project APK/metadata/version/certificate/hash checks and backups retained; upstream version detection reports integration needs; no blind upstream binary replacement |
| Logs/help/continuation | Per-launch Downloads logging retained; data/network diagnostics, bundled guides, this evidence and delivery records updated |

The earlier pasted requests and current source were reviewed. Co-op beyond two,
unverified directories, optical hand tracking, physical magazine reload and
universal retail-protocol compatibility are not represented as completed features.
See TEST15-PROGRESS, TEST16-PROGRESS, ANDROID-GAMEPAD and COOP-PLAYER-LIMITS for
prior evidence. This pass does not rework accepted animation or body behavior.

The owner additionally requested an explicit ISO/revision compatibility note.
It is included in the PvP/co-op browsers, data manager, data report and bundled
field guide, distinguishing possible content differences from protocol/NAT faults.

## Validation

All eleven targeted suites pass: test17 network/data, test16 actions, campaign
actors/lifecycle/capacity, browser, VR math, render targets, test15 refinements,
test15 I/O and Android gamepad. C harnesses use ASan/UBSan; Java tests execute
production import/selection code with synthetic data, not retail assets.

New coverage: 65,536 control words; 65,535 same/stale queue identifiers including
high-bit salts; invalid indices; asynchronous notice call; 60 PvP version/flag
combinations and separate campaign identity; Java/native profile agreement;
independent saves/config; fingerprints/deduplication; mixed-case map names;
truncated/unsupported headers, absent UI, path/size limits, invalid selections,
cancelled reads and synthetic XDVDFS extraction. A case-distinct filesystem test
runs where supported; duplicate ISO entry rejection always runs.

Device checks still required: join an already-running v11 match; interact/reload
and melee with desktop peers; repeated deaths/quit/rejoin and map rotation;
v9/v10 hosts where available; both launcher flavors' document pickers, imports,
controller navigation and set switching; paired Quest/flat co-op regression.
No game installation/launch, live-match load test or runtime acceptance is claimed.
Additional verification: the production directory parser accepted a fresh feed
of six servers with 48 reported players (a point-in-time report, not a reachability
measurement). The native cache-format suite passed 127 tests; four optional tests
requiring real map fixtures were skipped. Final build and artifact evidence is
recorded in TEST17-DELIVERY and the manifest.
