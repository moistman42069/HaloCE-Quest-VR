# Test31 / 1.0.13 private candidate

This is the baseline requested before manual reload, hand contact and world/NPC
interaction work. It is not a public release or a device-accepted build.
Public v1.0.12 remains unchanged. Packaging and exact artifact provenance are
pending the final build checks described below.

## Installation and guide

Install `HaloCE-Quest-test31.apk` on Quest or `HaloCE-Android-test31.apk` on
Android over the existing project app. Both target **1.0.13 / code 39**, ARM64,
Android API 28 or newer, using the original signing certificate. Do not
uninstall or clear app data. Back up your saves and imported game sets first.

Read [TEST31-PLAYER-NOTES.md](TEST31-PLAYER-NOTES.md) for the in-game menu paths,
touch/controller/Quest input, browser filters, hosting steps and settings.
The same notes are included at the top of the launcher's bundled player guide.

## Included changes

1. **Full OpenCE in-game menus:** profiles, campaign, map selection, multiplayer
   browser and filters, Server Setup, gametype editing, settings, controls and
   native text entry. Android direct touch and Quest pointing are connected to
   the widget system. Existing VR pages remain accessible from main, profile
   settings and pause routes.
2. **OpenCE Build 145 / network 22:** reviewed upstream changes, explicit
   Custom Edition map namespaces and missing-map errors. Peers on v1.0.12's
   network 21 cannot join this version. Use compatible network-22 peers with
   matching game files/revisions.
3. **Turrets:** seated fire passes through the physical-weapon empty-hand rule;
   mounted reticles use the native muzzle and aim preview.
4. **Warthog glass:** Vehicles > HOG GLASS controls your first-person glass;
   Hidden preserves the preceding default. Third-person/right-hand vehicle
   defaults remain. This does not claim a new first-person camera solution.
5. **Left-handed AR display:** bounded per-part winding uses actual vertex
   influences, including queued transparent parts.
6. **Menu settings with working consumers:** master/music/effects volume,
   optional room reverb, scoreboard layout and long-list paging, high-resolution
   HUD/text, shadow size, optional model lighting and AA. Reverb, model lighting
   and AA remain OFF initially. Optional AA failures fall back locally.
7. **Connection robustness:** bounded additional standard NAT probes and more
   accurate STUN classification. No relay or universal LTE/VPN guarantee.

## Validation and provenance

- All **46** suites in `tools/run-quest-checks.py` pass.
- Cache-format tests: **127 passed, 4 skipped**.
- Final settings/lifecycle checks were rerun after the persistence failure fix.
- Production C sanitizer tests cover menu lifecycle, settings, input, gametype
  persistence, reverb, scoreboard, turret and networking logic. Software GLES
  tests cover default shader parity, optional graphics and allocation failures.
- Signed-APK and source archive results will be recorded here before delivery.

Host/software-renderer tests do not prove headset appearance, Quest performance
or a real multiplayer session. No device acceptance is claimed.

The source archive, manifest and SHA256SUMS accompany the pair. The original
certificate SHA-256 is
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`.
No game assets, maps, ISOs, private logs or signing keys are included.

## Please test this baseline

1. Open every main/settings/pause route. Create, rename and delete a spare
   profile. Check Save, Cancel and Defaults; exit and restart to check saved
   settings. Type a long invite and password; cancel without changing them.
2. On Quest, check pointer selection, A/B/X/Y actions and VR settings navigation
   in both handedness modes. On Android, check direct touch, controller and
   keyboard/mouse, including a controller-hidden gameplay overlay and reconnect.
3. Browse, filter and join network-22 PvP and co-op. Host on Quest and Android,
   join each from another compatible peer, then test a map transition and a
   missing-map error. Keep both peers' logs. High player limits are options,
   not verified Quest hosting capacity.
4. Fire Warthog and stationary turrets in VR and Xbox layouts; compare reticle
   placement with hits. Check primary/secondary controls and normal on-foot fire.
5. Toggle first-person HOG GLASS, then check third-person and other vehicles.
   Check left/right AR counter visibility and other weapons.
6. Begin with default graphics/audio settings. Then check optional AA, shadows,
   model lighting and reverb: both eyes, scope, reticle, HUD/text, transparency
   and frame timing. Return to OFF/default and confirm the baseline recovers.
7. Check existing body, hands, grip, reload/grenade animation, locomotion,
   flat touch/gamepad and launcher file/update/log workflows.

If something fails, provide device/OS, app version, selected content/revision,
map, host/client and peer versions, settings, steps and logs from Download/HaloCE.
Support: [project server](https://discord.gg/S9uSCKxKx),
[Flat2VR](https://discord.gg/flat2vr), or **@MeWhenINameMyself**.

## Next phase

All **M1–M29** and **W1–W66** remain queued in
[VR-INTERACTION-REQUIREMENTS.md](VR-INTERACTION-REQUIREMENTS.md). Manual reload,
expanded hand contact and world/NPC interactions are not claimed in this pair.
Receive the owner's baseline test results before building further on it.
