# Test35 private candidate — Android and Quest VR

**Version:** 1.0.16 / Android version code 45

**Upstream:** OpenCE Build 148 / network 23

**Status:** private test candidate; device acceptance and public release are pending.

## What changed

- OpenCE Build 148 corrects negative or NaN particle collision radii and widths
  as map tags load. This covers particles, particle systems, contrails,
  weather particles, effects and breakable-surface particles.
- A runtime fallback also clamps an invalid computed radius to zero before
  point physics can assert. It records the first fallback in the game log.
- Native error screens identify the platform/build flavor and show recent
  errors first. The full `debug.txt` log remains the detailed diagnostic.
- The multiplayer protocol remains network 23. Build 147/Test34 network-23
  peers remain protocol-compatible; this update does not bring back protocol
  21/22 compatibility.
- Test34 cursor selection, scope diagnostics/alignment, CE validation and
  co-op safeguards remain. The owner-accepted Android touch behavior and VR
  settings design are carried forward.
- **SPV1 size note:** its ten listed maps are about 157-253 MiB each, above the
  128 MiB figure sometimes quoted. The current Custom Edition reader accepts
  ordinary map files up to 384 MiB (576 MiB with OpenSauce memory upgrades),
  so those files fit the parser's size bound. Protected-map conversion,
  resource-map handling and a full SPV1 campaign remain unverified; the
  launcher labels it experimental and explains this distinction.

## Install and test

Install the matching Android or Quest APK over the previous app to preserve
game files, saves and settings. Do not uninstall or clear app data. No game
content is included. For known controls, game-file import, server browsing,
co-op hosting/joining and revision notes, see the in-app guide and current
[player guide](PLAYER-GUIDE.md).

Please test both editions, representative maps/effects, Android touch controls,
Quest startup and menus, and network-23 multiplayer. If an error occurs, save
the full `debug.txt` log and include the on-screen build label, device/model,
game revision/content source and steps to reproduce. See the detailed
[Test35 progress checklist](TEST35-PROGRESS.md).
