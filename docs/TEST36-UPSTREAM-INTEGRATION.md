# Test36 OpenCE Build 157 integration

## Upstream reference

Build157 is the upstream release used for this candidate. Its network-version
change is required: OpenCE's network24 vehicle-set value is transmitted in
game variant data, and network23 peers cannot interpret it. The candidate
therefore advertises and accepts network24 only. Test36 cannot join v1.0.16 or
other network23 sessions.

Primary sources:

- [OpenCE Build 157 release](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-157)
- [OpenCE Build 156 release](https://github.com/OpenCommunityEdition/OpenCE/releases/tag/build-156)
- [OpenCE PR #173](https://github.com/OpenCommunityEdition/OpenCE/pull/173)
- [network24 commit](https://github.com/OpenCommunityEdition/OpenCE/commit/11117d7c287d519bf263db83273bc26295a87cb9)
- [stereo world-audio reverb/occlusion commit](https://github.com/OpenCommunityEdition/OpenCE/commit/2d2348c)
- [stereo distance-attenuation commit](https://github.com/OpenCommunityEdition/OpenCE/commit/0e220b8)

## Ported runtime changes

- **Analog trigger pressure:** fire input now reads the mapped gamepad trigger
  pressure (0–255 normalized to 0–1) rather than a held-tick count. Binary
  mapped buttons remain full-pressure. This preserves analog-rate-of-fire
  weapons and touch-generated digital presses.
- **PC vehicle set:** the variant enum, option validation, lobby spinner,
  vehicle-placement admission and vehicle remapping recognize PC's “every
  vehicle placed by the map” set.
- **Custom Edition item facing:** CE equipment placements spawn with their
  authored facing when CE tag data is active.
- **Host-alone start:** an Internet/LAN host can start with one player; the
  game remains open for join-in-progress. Lobby waiting text reflects that
  one machine/player is enough to begin.
- **Spatial stereo world audio (Builds 156–157):** stereo sounds with a world
  position are panned toward their source, attenuated by distance, and receive
  obstruction/occlusion filtering and room reverb. Unpositioned stereo music
  and other 2D sounds keep their previous mix. The Quest SDL mixer retains its
  existing resampler, limiter and reverb path; this adds a separate opt-in
  branch for positioned stereo voices.
- **Network24:** native and launcher compatibility ranges are pinned to the
  upstream network protocol.

The upstream diff was reviewed against this Android/Quest port. Desktop-only
build tooling and platform-specific behavior were not copied into the mobile
runtime. Build157's relevant network, controller, vehicle and CE spawn behavior
is represented above; this is not a claim that unrelated desktop modules are
byte-for-byte identical.

## Preserved behavior and risk boundary

Build148's particle-radius validation and halt-screen diagnostics remain.
Existing server browser, campaign replication, revision checks, safe geometry,
Android touch UI, VR settings, scope alignment and turret behavior are not
rewritten. The scope and turret logs are observational only. Save recovery is
not changed without the failing session's log and save-state evidence.

Automated regression and package checks are listed in
[TEST36-DELIVERY.md](TEST36-DELIVERY.md). Audio spatialization checks include
sanitized mixer tests and byte-identical output for ordinary, unpositioned
stereo and the existing mono/3D paths. Network24 intentionally partitions
this candidate from the public network23 release until a matching release is
published.
