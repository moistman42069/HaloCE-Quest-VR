> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test12 candidate: Quest VR and flat Android

Install the APK matching your device. Both are signed with the existing candidate
key and use separate package IDs. Keep your existing game data. No maps or signing
keys are included. The manifest identifies the exact source commit and hashes.

## Changes

- Native animated/target-colored crosshairs, with hide, size and opacity controls.
- Arm wrist-roll distribution, bounded free-hand shoulder reach, idle foot
  planting and turn steps. Full body remains optional; arms are the default.
- Flat Android multi-touch movement, aiming and combat/menu controls. VR retains
  controller tracking and its existing input path.
- Campaign co-op host/join and opt-in live-host publication, on the separate
  campaign protocol described below.
- PvP directories retain every valid distinct listing in each bounded response,
  sorted by population before paging. Use **Show next 50** for larger feeds.
- SPV1 uninstall restores original maps before deleting mod files, with recovery
  for interrupted changes. Settings decrement/increment and per-launch public
  Download/HaloCE logs remain present.

Prior grip/finger/contact behavior is retained: deliberate grip is the default
support-hand mode, the support pose stays locked to the gun, and spawning/picking
up a gun does not drop it before the first grip action. AUTO remains optional.
Finger smoothing, palm/finger contacts, held-gun contact approximation, physical
melee sweeps, backwards movement, offline sprint and closer offline contact remain.
Network movement and collision retain stock rules. Physical reload was explicitly
deferred in earlier scope and is still deferred; normal button reload works.

## Campaign co-op

Both players need this matching campaign build and identical mission/resource
files. The intended pairings are two Quest headsets or Quest plus flat Android.
Ordinary desktop/native PvP builds do not implement this campaign protocol.

1. Host: launcher **Campaign co-op > Host campaign**. Pick mission/difficulty.
   Check **List publicly** if you want to share the session through the directory.
2. The native System Link lobby opens. The game copies its private invite; it is
   also in the host log. Keep that lobby open while the partner joins.
3. Partner: **Campaign co-op > Browse / join**. Choose the host, or save/paste its
   invite. In-game, use **Multiplayer > System Link** to select the host.
4. The mission starts once both players are present. The host controls mission
   scripts, AI, checkpoints, BSP changes and progression. Each player keeps their
   own tracked view/input; saves are local to each process, not shared memory.

Joining a mission already in progress is disabled. A partner leaving closes the
session; start a new lobby to reconnect. Content mismatches and transition failures
are logged. A missing shared checkpoint causes a coordinated mission restart.

Public publication uses the community directory's documented announce/withdraw
API, only while a real native host reports fresh status. This new campaign
version has **not** been confirmed accepted by the deployed directory. A failed
announcement is logged and shown as a toast; use the private invite/LAN route.
Normal exit attempts bounded withdrawal; crashes/timeouts rely on stale expiry.
Existing native NAT traversal limits still apply.

## What is and is not verified

Source compilation is recorded in TEST12-PROGRESS.md. Packaging checks certificate,
package IDs, ABI, native payloads, touch/OpenXR separation and archive integrity.
There is no new paired-device campaign result or test12 headset acceptance yet.
Do not describe these artifacts as a proven end-to-end campaign release.

For the first paired run, retain both Download/HaloCE logs and check the opening
cinematic, weapons/AI/doors, a checkpoint, both players dying, a BSP transition,
restart and next mission. Also compare PvP and the revised body/grip pose against
test11. Flat touch, body appearance and public co-op listing need device results.
The unchanged stable branch remains test8; this candidate stays on the WIP branch.

## Resume in Claude Cloud or VS Code

Use historical repo `moistman42069/HaloCE-Quest-VR`, branch `quest-vr-test9-wip`.
Read CLAUDE.md, TEST12-PROGRESS.md, CAMPAIGN-PROTOCOL-WIP.md and
CLAUDE-CLOUD-VSCODE-WORKFLOW.md. Work on D: locally. Preserve the delivered source
commit and user logs when diagnosing; do not infer headset acceptance from builds.
