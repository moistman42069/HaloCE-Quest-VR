# Test29 — 1.0.11 candidate (private): current OpenCE, HUD tap fix, wrist HUD placement, glasses FOV

Not a release. GitHub's Latest is v1.0.10. Do not publish without explicit
owner approval. Details: [TEST29-PROGRESS.md](TEST29-PROGRESS.md).

## Installation

- Quest/VR: `HaloCE-Quest-test29.apk` (package `com.halo.decomp.vr`)
- Android/flat: `HaloCE-Android-test29.apk` (package `com.halo.decomp`)

Both are **version 1.0.11 / code 37**, ARM64, API 28+, signed with the same
certificate as every release since v1.0.2. They install over v1.0.10 without
uninstalling (`adb install -r <apk>`). Do not uninstall or clear data.

**Network change:** 1.0.11 plays OpenCE's **network 21** (OpenCE build 144),
which is what OpenCE's current co-op and multiplayer games use. It does not
play with 1.0.10 (network 20). Everyone in a game needs 1.0.11, or OpenCE
build 141 or newer.

## Changes

1. **Current OpenCE (build 144).** Today's public co-op games were listed
   on network 21, which 1.0.10 refuses. This build joins them.

   OpenCE's newest fixes come along:
   - bodies no longer hang in the air on other players' screens;
   - killing blows show for everyone;
   - the host crossing into a new area brings the team along;
   - a respawn starts behind a teammate.
2. **HUD head tap fixed.** Hold your gun hand by the side of your head for a
   moment (a short buzz confirms). Do the same again to bring the HUD back.
   Reaching for the shoulder holster no longer hides the HUD by accident.
3. **New rows on VR Settings → HUD:**
   - **HUD: Shown / Hidden** works from the menu at any time.
   - **Head Tap:** Off, or how close the hand must come (on by default).
4. **Wrist HUD:** it now sits on top of the wrist. New rows move it
   (Wrist Along, Across, Height), resize it (Wrist Size) and reset it.
5. **Moving with a hand** (Controls → Move With: Left or Right Hand): with
   both hands on the gun, forward follows the gun. Before, it slowly turned
   into a strafe. Move With: Head, the default, is unchanged.
6. **Graphics (pull request #1, by willemhorak):**
   - **FOV: Glasses 70×66** previews VR glasses and draws fewer pixels.
   - **Resolution** goes up to 200%, and steps above 100% now reach the
     headset; **125% Q3** is about the Quest 3's panels.
   - Auto, and every step up to 100%, look exactly as in 1.0.10.
7. Everything from 1.0.10 is kept.

## Build provenance

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `HaloCE-Quest-test29.apk` | (filled in after the build) | |
| `HaloCE-Android-test29.apk` | (filled in after the build) | |

## Checks performed

- 32 regression suites pass, including the new `test_test29`:
  - network 21 and 21 OpenCE files by hash;
  - the held tap (hide, then show again);
  - wrist placement;
  - two-hand movement;
  - the PR's layout and eye sizes.
- `test_quest_browser` was run against the live directory on 2026-10-07:
  4 of 4 co-op games and 10 multiplayer games joinable at network 21.
- Cache formats pass. Both editions and the host build in release mode.
- **Not done:** no device session with 1.0.11 yet.

## Please test (note app versions, devices, Wi-Fi or mobile data)

1. **Join a current OpenCE co-op game** (Quest, then phone): Multiplayer →
   System Link → Refresh, then join a public co-op game. Play a few minutes:
   fights, a checkpoint, an area change. Send the log.
2. **Host co-op** from the launcher and have someone on 1.0.11 or OpenCE
   join.
3. **HUD tap:**
   - Hold your gun hand by the side of your head until it buzzes (HUD hides).
     Do it again (HUD comes back).
   - Holster and draw at the right shoulder a few times: the HUD should stay.
   - Pause → VR Settings → HUD: try **HUD** Shown/Hidden and **Head Tap**
     Off, then on again.
4. **Wrist HUD:** turn it on (HUD → Wrist HUD: On) and look at your off-hand
   wrist. It should sit on top of the wrist. Try Wrist Along, Across, Height
   and Size, then Reset Wrist.
5. **Two hands:** if you use Move With: Left Hand, hold the gun in both hands
   and walk forward while turning. You should keep going forward.
6. **Graphics:** try FOV Glasses, then Full again. Try Resolution 125% Q3,
   then Auto. Note smoothness and anything odd.
7. **Everything else:** a few minutes of single player in VR and on the
   phone.

If something fails, note the time and send the logs from `Download/HaloCE`.
