# Test22 checkpoint: co-op crash, upstream review, vehicle view, ammo display, scopes

Updated 2026-10-04. Private candidate **test22, 1.0.2 / code 28**, branch
`test21-hands-body` (after the published v1.0.3 = test21b, code 27). No
release without explicit owner approval.

## Evidence (owner logs, screenshot and video; kept private)

| Source | What it shows |
| --- | --- |
| Phone logs 16:56 (a10) and 16:58 (a30), screenshot 17:28 | The Android host halts the moment the Quest joins co-op and the mission starts: "EXCEPTION halt in tag_groups.c #3089: #0 is not a valid index in [#0,#0)". The Quest is returned to the menu with a host disconnect. |
| Same crash, symbolised with the exact test21b Android guest | `network_distributed_tick → network_damage_host_tick → unit_unarmed_melee_damage → list_index_to_weapon_definition_index → tag_block_get_element_with_size` |
| Quest video 16:36:07 with log 16:34:36 | First-person Warthog at 105–122 s (`vr.vehicle_view first_person` 16:37:28 to 16:38:09): the interior jumps up and down by tens of pixels between samples 0.1 s apart while the head turns smoothly. |
| Phone log 17:18 | In a 56-player public CTF (bloodgulch) the phone drops to 27 frames per 10 s (normally 46–77), with the game loop running about 34 times in 10 s; it recovers as players leave (40, 38, 100, 116). Co-op campaign on the same phone holds 68–77. |
| Quest logs 19:35, 00:59, 01:44 (another player) | The aim report: **test20e (v1.0.2)**, default calibration (hand pitch −70, gun 0, controller corrections 0), offline campaign c20 and c40. |

## Causes and changes

1. **Co-op campaign host crash.** Every tick the host's damage code notes
   each living player's unarmed blow (`unit_unarmed_melee_damage`). A player's
   biped has none of its own, so it borrows the first multiplayer weapon's, and
   a campaign map's globals list no multiplayer weapons: element 0 of an empty
   block, on the first tick of every co-op mission, on any device pair. Upstream
   fixed the same lookup in PR #73 (`ce77db84`); its guard
   (`unarmed_melee_weapon_definition_index`) is applied to both call sites. It
   also fixes a solo unarmed melee in a10's cryo tutorial.
2. **First-person vehicle view shaking.** The seat's heading was taken in the
   30 Hz control tick from the vehicle's latest orientation, while the vehicle
   is drawn between its last two ticks; turning, the eyes stepped ahead of the
   drawn interior every tick. The view now turns by the drawn vehicle's yaw
   (`vr_seat_frame_heading`; the aim keeps the tick heading). The anchor (the
   driver's head marker) also moved with the driver's steering and bump
   animations; it is now held in the drawn vehicle's own frame and eased over a
   quarter second (`vr_seat_steady_anchor`), so the interior stays put against
   the view while the vehicle's own motion (turns, bounce) is kept whole. New
   seats and jumps snap. Third-person/chase view and vehicle mechanics are
   untouched.
3. **Left-hand ammo display backwards.** The left hand's first-person model is
   the right-handed one mirrored. The display node (`frame display`, the
   assault rifle's counter) and anything under it is now mirrored back about
   its own centre, and while the mirrored model is drawn only parts whose node
   matrix is actually mirrored turn their triangles' winding
   (`halo_vr_skinning_mirrored`, decided from the first node matrix's
   determinant in `rasterizer_set_model_skinning`; VR build only). Right-handed
   play and every other left-hand part are as before.
4. **Aim report (another player).** That player runs test20e. In test20e the
   reticle followed the hand's line, while the game turns every shot toward the
   head line's hit (fixed in test21b, published as v1.0.3, which the owner
   confirms lines up). Offline the shot starts at the hand, below the head, so
   it landed high: aiming at the feet hit the body. No aim change is made; the
   player should update to v1.0.3 or later. New diagnostics log, once per
   weapon and at most every ten seconds: the engine's turn of the shot off the
   aim, the reticle's angle and distance from the shot, and where it left from
   ("vr: shot (...)").
5. **Android frame drop.** Not a leak or a stuck state: the 56-player server's
   simulation costs the phone nearly a whole tick budget per tick, and a network
   client runs up to a second of catch-up ticks per frame to keep pace with its
   host, which settles at a few frames a second. It recovered as players left,
   and campaign is unaffected. Timing is not changed (it is shared with the
   host and other builds); a "[game-ticks]" line now logs when frames have to
   catch up three or more ticks, so another occurrence can be confirmed.

## Upstream review (cybersecurity/halo-ce-universal, build-84 `3304965` → `7e00135`, 16 commits)

No commit changes the native protocol (still 11), so server compatibility is
unaffected. Applied to both editions:

| Upstream | Change | Here |
| --- | --- | --- |
| `ce77db84` (PR #73) | unarmed melee on maps with no multiplayer weapons | Applied (the co-op crash) |
| `1a15a171` | no unarmed grenades from a vehicle's seat | Grenade part applied (our melee code has no unarmed path) |
| `7e00135d` | a frame with no network client | Applied |
| `88a7c07e`/`ffc1512d` | brokers in brokers.txt, upstream's own broker `opence.milenko.org` first | The broker added first to the default list; configs still on the old default take it automatically (no brokers.txt file) |
| `2e3841ff` | shotgun HUD ammo meter left-aligned | Applied (our two files were identical to upstream's before) |

Reviewed and not taken: `d3fc997f` (walked-over weapons readied in
multiplayer: a gameplay change touching the physical-weapons hand state; the
host stays authoritative), `c05864b3` (scoreboard; our scoreboard differs),
`d578f88b` (server browser name cleaning; our browser differs), `39350fb8`
(motion sensor names), split-screen co-op (`193cbf59`, `e3389991`), pause menu
art (`46edf536`), browser row outline (`812ffeea`), release zips (`c3adcfe5`).

## Adjustable scopes (owner request)

A **SCOPES** settings page: pistol and sniper rifle scopes each move forward,
up and right (1 cm steps, ±20 cm; right is the player's right in either hand)
and size (50–200%), with **Reset Scopes**. Defaults (0 cm, 100%) are exactly
the previous placement and size; the rocket launcher's is unchanged. Keys:
`vr.scope_pistol_*`, `vr.scope_sniper_*` (`forward`, `up`, `right`, `scale`).

## Status

| Item | Implemented | Automatically verified | Device |
| --- | --- | --- | --- |
| Co-op host crash | Yes (upstream fix) | Campaign maps never index the empty list; multiplayer unchanged | Needs Android host + Quest join, a10 and a30 |
| Vehicle view | Yes | Anchor rides a moving, turning vehicle exactly (2,000 frames), head bob cut to 11%, heading follows the drawn vehicle | Needs first-person driving |
| Left-hand ammo display | Yes | Wiring | Needs the assault rifle in the left hand |
| Aim diagnostics | Yes | Wiring, rate limit, flat build unchanged | Log on the next report |
| Frame-drop log | Yes | Wiring | Next heavy server |
| Upstream fixes, brokers | Yes | Wiring and migration | Server browser, invites |
| Scopes | Yes | Zero settings identical (pistol, sniper, rocket, both hands); adjustments apply per scope | Needs zooming with each |

Horn: test21b's fix and log stand; no Warthog horn test was in these logs.
