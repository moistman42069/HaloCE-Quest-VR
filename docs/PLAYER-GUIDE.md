# Installation, multiplayer and troubleshooting

## APK and device

Quest VR test13a is the immersive standalone build. Flat Android test13 is the touch/gamepad build. Their labels differ because test13a only changes VR body default/build identification; both retain the same campaign/avatar implementation. Quest 3 is the reference headset; other devices lack the same owner evidence. Flat requires Android 9/API 28+, ARM64 and compatible OpenGL ES graphics. Neither APK bundles game maps or the signing key.

## Install and import

1. Public APK releases are on hold for co-op testing. Use the candidate supplied directly by the maintainer, or build from source. Candidate `SHA256SUMS.txt` identifies the exact files.
2. Sideload through your authorized Quest installer or Android's package installer. Optional computer command: `adb install -r <apk-file>`.
3. Copy your legally obtained Halo CE Xbox `.iso`/`.xiso` onto the device and select it in the launcher's data-import flow. Allow roughly 1.8 GB for maps plus cache/saves and image space during extraction. This data is distinct from MCC/retail PC installation files.
4. Wait for extraction, then Play. Existing Quest data at `/sdcard/Documents/HaloCE/maps` is recognized when `ui.map` is present; otherwise app external files are used.
5. Recenter standing normally; open campaign pause > VR Settings. [Controls/options](CONTROLS-AND-OPTIONS.md).

| Data | Location |
| --- | --- |
| Quest shared game root, when present | `/sdcard/Documents/HaloCE` |
| Quest app external root | `/sdcard/Android/data/com.halo.decomp.vr/files` |
| Flat app external root | `/sdcard/Android/data/com.halo.decomp/files` |
| Maps/config | `maps/`, `config.toml` under the active root |
| Saves | Preserve app `save/` and any shared-root save data; consult startup log/config for active save root |
| Public launch logs | `Download/HaloCE/halo_log_<date>_<time>_<pid>.txt` |

Only VR selects the shared root, and only when `maps/ui.map` exists. Editing an inactive config has no effect. Android file-manager restrictions may require the system picker or authorized ADB access.

## Updates and backups

Install over the existing project APK to retain data. The original project certificate is retained. Other forks may have the same package ID with a different key; Android rejects that in-place update. Back up maps/config/saves before removing any installation. VR and flat have separate app storage and do not automatically share saves.

These candidates update manually from this project's Releases. They do not automatically follow upstream builds. Existing body choices survive updates: choose Legs + Arms or set `[vr] body = "legs"` while closed if needed. Avoid deleting app data merely to reset one option.

## PvP

1. Launcher > **Multiplayer servers**; Refresh.
2. Select an open compatible host. Population is sorted before paging; **Show next 50** reveals more.
3. Join launches the game with the invite. In-game use **Multiplayer > System Link** after the tunnel connects.
4. Native LAN discovery and saved `halo://join/<64 hex digits>` invites support unlisted hosts. Restarting a host can invalidate its old invite.

Directory settings accepts up to four compatible HTTPS feeds, one per line; **Use ChupathingyCE** restores the verified preset. Saved-only operation is available. Valid distinct listings in bounded responses are retained; oversize/failing feeds are reported. Full/incompatible entries can remain visible with Join disabled. Counts are host reports, not ping measurements. Unadvertised private hosts cannot all be enumerated.

Accepted native PvP host versions: 9/10, with compatible maps/rules. Retail PC/Custom Edition, original Xbox and MCC use other protocols. NAT, firewall and Wi-Fi isolation can prevent joins. Keep the game foregrounded: Android suspends it in the background. [Directory details](MULTIPLAYER-BROWSER.md).

## Campaign co-op (experimental)

Use matching campaign-capable builds and identical mission/resource files: two Quests or Quest plus flat Android. No documented paired-device campaign success is claimed yet.

1. Host: **Campaign co-op > Host campaign**; select mission/difficulty. **List publicly** is optional.
2. Keep the native System Link lobby open. Its private invite is copied and logged.
3. Partner: **Campaign co-op > Browse / join**; select a listing or paste/save the invite. In-game open **Multiplayer > System Link** and choose the host.
4. Intended flow starts the mission with both players present. Host controls scripts/AI/checkpoints/BSP transitions/progression; each process owns its view/input and local saves.

Joining in progress is disabled. Disconnecting closes the session; reconnect through a new lobby. Missing shared checkpoints trigger coordinated restart. Campaign protocol `0xCE01` is separate from ordinary PvP. Backend acceptance for public publication is unverified; use private invite/LAN if it fails. [Implementation scope](CAMPAIGN-PROTOCOL-WIP.md).

Keep both logs when checking opening cinematics, AI/weapons/doors, checkpoint, both players dying, BSP transition, restart and next mission. Those cases need device evidence.

## VR avatars

Supporting hosts/observers negotiate the visual extension automatically. Flat test13 has the receiver; old hosts/clients keep stock animations. Local torso hiding does not remove the remote body. The remote world skeleton has coarse hands, without the local individual finger rig. [Protocol/limits](NETWORK-VR-AVATARS.md).

## Troubleshooting

| Problem | Check |
| --- | --- |
| Install fails | Correct device/ARM64 APK, storage and signing conflict with another fork |
| Quest opens flat | `.vr` package, immersive launch, focus; include startup/OpenXR log lines |
| Missing maps/import failure | Xbox data, completed extraction, active root and `maps/ui.map`; preserve error |
| Old body choice after update | Saved preferences are preserved; change Body explicitly |
| Height/alignment | Recenter standing normally; collision can separate real/virtual positions |
| Automatic support attachment | Set Two Hands to Grip, not Auto; release to detach |
| Gun dropping | Physical mode requires holding after first grip; check holsters/MP Physical or choose Locked |
| Different online movement/melee | Network speed/collision stay stock; clients use native swing; MP Physical defaults off |
| Lower settings | Left decreases; A/right advances; Back traverses page history |
| Poor performance | Compare lower preset/resolution and 72 Hz; report scene/device/settings |
| Missing co-op listing | Backend acceptance is unverified; use matching builds/private invite |
| No Downloads log | Check launcher destination; storage failure falls back to app files where possible |
| Custom content issues | Reproduce stock first; Custom Edition/SPV1 and custom rigs remain experimental |

Logs cover launcher startup through native output/exit and may contain host invites/device details. Review before public posting. Include build, device/OS, map, settings, reproduction steps, host/client roles and peer versions. Video plus the same launch's log helps diagnose body/grip/menu issues.
