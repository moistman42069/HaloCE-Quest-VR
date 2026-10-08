# Halo CE Quest VR + Android 1.0.16

**Version:** 1.0.16 / Android version code 45
**Upstream:** OpenCE Build 148 / network 23
**Release:** public release v1.0.16. No Android or Quest device session on this exact APK pair is recorded.

## What changed

- OpenCE Build 148 repairs negative or NaN particle collision radii and widths when map tags load. A runtime physics guard also clamps invalid computed radii before assertion; native halt screens identify the platform/build and show recent errors first.
- The in-game server browser, OpenCE-native campaign co-op, network-23 compatibility, co-op lobby options, CE map validation, and player avatars are retained.
- Android and Quest share the same game/network path. Android keeps touch controls, optional gyro aim and Xbox-style controller support; Quest retains tracked hands, body/arm/leg modes, fingers, Safe geometry and VR settings.
- **SPV1 remains experimental and unverified.** Its listed maps are 157–253 MiB, above the sometimes-quoted 128 MiB size. The current Custom Edition reader accepts up to 384 MiB (576 MiB with OpenSauce upgrades), so size alone does not rule it out; protected-map conversion, resources and campaign play still need testing.

## Install and report

Install the APK for your device over the existing app to preserve game data, saves and settings. Do not uninstall or clear app data. Supply your own game files. For controls, setup and multiplayer instructions, use this guide and the release notes.

For a crash, failed join, desync or other problem, include the full launch log from `Download/HaloCE`, device/model and OS, game revision/content set, network type, steps to reproduce and logs from all peers. DM **@MeWhenINameMyself** or report in the [Halo CE Decomp Discord](https://discord.gg/S9uSCKxKx). Remove private invite/device details before sharing.
