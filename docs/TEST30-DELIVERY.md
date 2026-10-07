# Test30 — 1.0.12 candidate (private): delete profiles in VR, co-op server name

Not a release. GitHub's Latest is v1.0.11. Do not publish without explicit
owner approval. Details: [TEST30-PROGRESS.md](TEST30-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test30.apk` (package `com.halo.decomp.vr`)
- Android/flat: `HaloCE-Android-test30.apk` (package `com.halo.decomp`)

Both are **version 1.0.12 / code 38**, ARM64, API 28+, signed with the same
certificate as every release since v1.0.2. They install over v1.0.11 without
uninstalling. The network is unchanged: OpenCE network 21 (build 144).

## Changes

1. **Deleting a profile in VR works.** In menus, the Quest's buttons now do
   what the on-screen letters say:
   - **X** deletes the selected profile;
   - **A** selects;
   - **Y** is Y;
   - **B** goes back, once.

   In play, the buttons are as before (X still throws a grenade).
2. **Co-op server name.** Launcher → Campaign co-op → Host campaign has a new
   **Server name** box.
   - Up to 15 letters, numbers, spaces or symbols.
   - It's remembered for next time.
   - Leave it empty to keep the device's name.

   The name shows in the server browsers and to players who join.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test30.apk` | 28,347,011 | `dcbce7fed5d02161a22441b7d18cdfc9ded59250b181e83b21ffc1c9e9b27f22` |
| `HaloCE-Android-test30.apk` | 26,270,260 | `63af9c7ac012c3d68d4036af9c432ef7134e274f11a0c69b5f56b9c09151fcf1` |

Runtime source `688a63e3` on branch `test30-profiles-coopname`; later commits
change only documentation. Certificate SHA-256
`53d416f7e123cc62b749940983209bc9a400002e033fd5f50900d4ffad8e2aa4`. Built
serially from a clean tree; payload, signing and 16 KB alignment verified.

## Checks performed

- 33 regression suites pass, including the new `test_test30`, which runs the
  menu buttons and the server-name request.
- Both editions build in release mode.
- **Not done:** no device session with 1.0.12 yet.

## Please test

1. **Delete a profile (Quest).** On the main menu, open the profile list,
   point at a spare profile, press **X** and confirm. Check that:
   - **B** still goes back one screen;
   - **A** and the trigger still select.
2. **In play.** **X** still throws a grenade and **B** still uses and
   reloads.
3. **Server name.** Host campaign with a name such as "Fireteam Q", leave
   Public ticked, and check:
   - the in-game lobby shows the name;
   - the server browser lists it (from another device, or the launcher's
     Browse / join);
   - leaving the name empty gives the device's name, as before.
4. **Everything else.** Play a few minutes as usual on both devices.

If something fails, note the time and send the logs from `Download/HaloCE`.
