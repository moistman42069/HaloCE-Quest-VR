> Historical development record. Current release/defaults/continuation instructions are in `docs/CURRENT-STATE.md` (or `CURRENT-STATE.md` from this directory). Dated branch/private-work references below describe earlier work.

# Test13 candidate: matching Quest VR and flat Android

Install the APK for the device. Both retain their package IDs and original
signing certificate. Preserve game data; no maps or signing key are included.
Exact source and hashes are in the package manifest.

## VR settings and body

- Full body is the default for new/unset configurations. An explicitly saved
  visibility choice is preserved. Change **VR SETTINGS > BODY > BODY** anytime.
- Four views: **FULL**, **ARMS + HANDS**, **LEGS + ARMS** (torso hidden), and
  **HANDS ONLY**. These affect your view; peers can still see the whole avatar.
- Settings use bounded pages with four rows per column. **NEXT PAGE** opens
  the next page; **B** returns to the preceding page/category. A/right raises
  or advances a setting; left lowers it. Numeric limits clamp. Custom numeric
  values advance to the next value in the requested direction.
- Elbow swivel uses temporal continuity and a small bend at extension;
  shoulder reach and arm extension are limited. Wrist twist stays continuous
  across its angular wrap. Shoulders anchor to the solved collar line.
- Deep crouches allow more downward torso adjustment; neck clearance and the
  local duplicate shoulder geometry were revised. Existing foot planting and
  room-scale following remain. Hands-only keeps IK, grip and finger interaction.

## Other players seeing VR motion

Both host and observer need test13 (or a build implementing this extension).
This works through an explicit capability exchange in co-op and compatible PvP.
The flat APK now includes the avatar receiver and renderer. Older public servers
and clients retain stock animation. See NETWORK-VR-AVATARS.md for exact bounds.

The remote avatar includes head, arms, torso and legs. The stock biped's coarse
hand skeleton does not contain separate finger bones. Local visibility filters
are not sent. Multiplayer hitboxes and movement remain stock.

Co-op host/join instructions remain in TEST12-README.md. Public directory
acceptance of the campaign protocol remains unverified; use private invites
if publication is rejected. PvP directory coverage/population sorting, flat
touch, logging, deliberate support grip, first-grip spawn protection, contact,
crosshairs and SPV1 recovery are retained. Physical reload remains deferred.

## What still needs your devices

Build/signature checks cannot prove there is no clipping in every pose. Please
retain both Download/HaloCE logs and recordings for menu paging/decrement,
all four body modes, straight/downward/cross-body/overhead arms, deep crouch,
room-scale stepping, weapon/support grip and observer pose behavior. Also retain
the pending paired co-op lifecycle checks from test12. No APK is installed or
game launched automatically; the stable branch has not been advanced.

Claude Cloud / VS Code: use the private quest-vr-test9-wip branch and read
TEST13-PROGRESS.md, the latest delivery record, and
CLAUDE-CLOUD-VSCODE-WORKFLOW.md. Work on D: locally and preserve exact artifacts.
