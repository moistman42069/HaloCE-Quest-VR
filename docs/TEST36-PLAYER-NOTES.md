# Test36 candidate — owner testing notes

This is a private test APK pair, **not a public release**. It is based on
OpenCE Build157 / network24. The current public v1.0.16 release is network23,
so players on those builds cannot join sessions hosted by this candidate.

## Changes in this test

- OpenCE Build157's network24 support and corresponding multiplayer updates.
- Analog fire pressure for weapons that use an analog rate of fire.
- PC vehicle-set choice for variants, Custom Edition item spawn facing and
  starting an Internet/LAN lobby alone.
- Stereo world sounds now pan and fade toward their position and respect
  obstruction/occlusion; unpositioned stereo music keeps its existing mix.
- **Two-hand aim centering diagnostics** record the grip distance and change in
  forward/right/up alignment at support-grip engagement and when zoom changes.
  Scope diagnostics record render gates, camera viewport/FOV and layer pose on
  state changes. Mounted aim logs identify driver/gunner/passenger role, seat,
  selected source and tracking fallback. Scope, aim, turret and vehicle
  behavior remain unchanged by these logs.
- Previous Safe geometry defaults, Android touch controls, VR settings and
  existing scope calibration are retained.
- The launcher recommends the original Xbox Halo CE XISO for best compatibility;
  Rev 1 and Rev 2 are not the recommended images, though the launcher can still
  import supported game data from them.
- A Halo-inspired launcher font is selectable from both the initial game-data
  setup and the Play screen; tap it again for the standard font. Long guidance
  text stays in the standard sans face. Support: DM `@MeWhenINameMyself` on
  Discord.

## Scope report test

For public multiplayer, use **Play > Multiplayer > Join Game > Server
Browser** and check **FILTERS**. This candidate requires network24 hosts;
public v1.0.16/network23 sessions are incompatible. Discovery logs now identify
broker connections and listing rejections. If no servers appear, leave the
browser open for at least 30 seconds and send that launch log; where possible,
compare Wi-Fi and mobile data. The previous empty-list log did not identify
the exact cause, so this is a diagnostic retest rather than a confirmed fix.

In the same level with the same rifle, compare one-hand aim with zoom, then
hold the support grip and repeat. If the scope shifts, exit and send the latest
launch log from Downloads together with the Quest model/OS, selected game-file
set or revision, weapon hand, scope setting, and whether support grip was
manual or automatic. The log should contain a `two-hand aim engaged` line with
grip distance and the angle between the calibrated main-hand aim and grip line.
This build gathers evidence; it does not claim to fix every reported headset
configuration.

If an unrelated multiplayer or save/continue issue occurs, include the full
log from that session and identify host/client roles and the selected
game-data set. If a Shade Turret issue occurs, include the log and note the
Quest OS, selected game-data revision, gunner seat and turret aim setting.
Those behaviors were not changed based on reports without matching logs.
