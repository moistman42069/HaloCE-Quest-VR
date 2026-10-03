# Current development state

Updated 2026-10-03. Canonical public repository: [moistman42069/HaloCE-Quest-VR](https://github.com/moistman42069/HaloCE-Quest-VR), branch **main**. The initial public snapshot is the latest complete test13a source, with refreshed player/project documentation and private identifying metadata removed. Older private Git history remains a backup, not the continuation branch.

## Delivered versions

- **Quest VR test13a**, version `1.0-test13a`, code 14: latest VR runtime. Body defaults to `legs` (Legs + Arms); saved values preserved.
- **Flat Android test13**, version `1.0-test13`, code 13: current companion. Includes touch overlay and campaign/avatar receiver; the VR-only default does not require a flat update.
- Test13a changed the body default and identity from test13; the IK/menu/network implementation is the test13 work. Runtime files in public main match the latest private source snapshot. Public documentation and manual workflow metadata are refreshed.

See [RELEASE-PROVENANCE.md](RELEASE-PROVENANCE.md) and the release manifest for hashes/source identity. Do not confuse GitHub's automatically generated current-source ZIP with the separate shipped-flat source snapshot.

## Observed device evidence

The owner reported improved gameplay, working multiplayer/settings/Downloads logs, good room-scale legs and then that Legs + Arms works great. Earlier Quest 3 baseline observations included immersive launch and approximately 72 Hz play. These are specific reports, not an all-device/all-feature certification. The supplied test12 log ended through normal cleanup/exit; footage showed menu overlap and chest/shoulder crowding that motivated test13.

## Current implementation

| Area | Included | Remaining evidence/limits |
| --- | --- | --- |
| Quest render/input | Native OpenXR, tracked headset/Touch, hand aiming, room-scale, scope, menu pointer, vehicle/cinematic options | Other headsets and all performance settings not accepted |
| Body | Four views, inferred full-body rig, room-scale feet, bounded shoulder reach, smooth elbows/twist, local torso hiding | Extreme/cross-body/overhead poses and custom rigs can still clip; no hip/foot trackers |
| Hands | Controller-driven finger poses, smoothing, palm/finger/world and approximate held-gun contact | Not optical hand tracking/full hand rigid-body simulation |
| Grip | Deliberate support grip default, fixed support anchor, first-grip protection, physical/locked weapons and holsters | Paired network physical weapon behavior unverified; off by default online |
| Movement/melee | Offline arm-run sprint and close contact, stock network speed/collision, impact or swing melee | Physical reload deferred; button reload works |
| Settings | Generated pages/dynamic storage, directional stepping, body and graphics options | Custom pause tags may not provide same menu |
| PvP browser | Full bounded feed, population sort then paging, four catalogs, invites/LAN, v9/v10 compatibility | Only ChupathingyCE preset verified; not retail PC/MCC/Xbox protocol |
| Campaign co-op | Separate host/join/browser/protocol, campaign authority/replication/transitions | No paired-device campaign acceptance; public announcement acceptance unverified |
| Remote avatars | Negotiated render-only snapshots, owner/bounds checks, interpolation/expiry, flat receiver | Paired visual acceptance pending; world skeleton has no separate fingers; old peers stock |
| Flat input | Multi-touch overlay, fire-drag aim, gamepad coexistence, lifecycle release | Phone layout/input validation and Type/Light profile labels pending |
| Logging/content | Per-launch Download/HaloCE logs with fallback; SPV1 original-map recovery | Custom content/dependencies remain experimental |

## Next work after user results

1. Reproduce reports with exact APK, settings, device, map and log; preserve the delivered binary/source.
2. Paired Quest/Quest and Quest/flat co-op: cinematic, AI/weapon/door behavior, checkpoints, both-dead recovery, BSP, restart/next mission, disconnect/reconnect.
3. Observe replicated VR head/arms/torso/legs and held weapons; check death/respawn and loss fallback. Test supporting PvP host with old/new peers.
4. Exercise flat touch movement+fire+aim, pointer cancellation/focus changes, gamepad coexistence, labels and screen sizes.
5. Diagnose any remaining menu/body/grip regressions from footage; maintain the approved Legs + Arms default and room-scale leg behavior.

The current publishing task adds documentation and public distribution, not gameplay changes or new runtime acceptance. Historical TEST9–TEST13 documents are dated development evidence; this file, release provenance and current player guides take precedence. Source/privacy review must exclude original author emails, personal workstation paths, signing keys and private evidence from public artifacts.
