# Test30 checkpoint: profiles deleted in VR, co-op server name

Updated 2026-10-07. Private candidate **test30, version 1.0.12 / code 38**,
branch `test30-profiles-coopname`, on top of the published v1.0.11. Not
released.

## Owner's report and requests

- **Confirmation:** after v1.0.11 the owner wrote "everything here is great".
- **Report:** in VR, pressing X on the main menu to delete a profile did nothing.
- **Request:** a server name option in the launcher's co-op host dialog.
- **Upstream:** OpenCE was checked first. `main` is still build 144
  (network 21), so there is nothing new to merge.

## Deleting a profile in VR

- **Cause:** the profile list deletes on the Xbox's X. The Quest's buttons
  come from the gameplay table (`vr.button_*`), which gave the menus no
  Xbox X:
  - the Quest's X throws a grenade;
  - the game's X (use and reload) is on the Quest's B, which in the menus is
    also the pointer's back, so pressing it leaves the screen.
- **Fix:** in the menus (`menus_active`, which the game updates every frame),
  the Quest's A, X and Y now act as the Xbox's A, X and Y.
  - The prompts' letters match the controller's.
  - The button that is the pointer's back (the right B; for a left-handed
    player, the left Y) does nothing else, so one press goes back once.
  - No grenade is thrown from a menu.
  - Gameplay buttons are unchanged.
- **Flat Android:** unaffected. Its touch overlay has an X button, and pads
  are mapped directly.

## Co-op server name

- **Launcher:** Campaign co-op → Host campaign has an optional **Server name**.
  - It takes printable ASCII, up to 15 characters, the same limit as the
    PvP host and a network game's name.
  - It is remembered for next time.
  - Left empty, the server keeps the device's name, as before.
- **Request file:** `coop_host.txt` format 3 is format 2's line followed by the
  name on a line of its own. Formats 1 and 2 still read.
- **Game:** names the lobby before its settings go out, so the in-game lobby,
  the LAN and public listings, and joining players all show it. The name is
  local to the host; nothing on the wire changes.

## Evidence

`tools/test_test30.py` runs:
- the menus' buttons from the real code: the reported X, A, Y, the single back,
  left-handed play, no grenade from a menu, and gameplay and other controllers
  unchanged;
- the request reader over named, empty, 15-character, 16-character, CRLF,
  control-character, non-ASCII and extra-line cases;
- the launcher's name check.

33 regression suites pass. Both editions build.

## Next

The owner's device tests ([TEST30-DELIVERY.md](TEST30-DELIVERY.md)).
