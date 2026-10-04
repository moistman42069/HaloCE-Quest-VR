# Test20 checkpoint: 1.0.1 withdrawal and Quest performance regression

Updated 2026-10-04 (test20b). Branch `test20-safe-upload-performance`, from `main` at
`17d75653`. Working version **1.0.2 / Android code 22**, label `test20b` (test20 = code 21, superseded, untested).
Private candidate only: no GitHub release without explicit owner approval.

## Release status

The owner **deleted the v1.0.1 GitHub release** because of a severe performance
regression. Its source (runtime `bc1f0446`) remains on `main`; it is not an
accepted or working baseline and must not be republished. The current public
release is **v1.0.0** (exact test18 APKs, 1.0-test18 / code 19). Test14 and
v1.0.0 stay unchanged. 1.0.1 installs have code 20, so the next build must use
code >20 to install over them; the updater must not offer v1.0.0 as an update
to code 20/21 (covered by `tools/test_test20_render_perf.py`).

## Evidence identity (owner-supplied logs, kept private)

| Log | Build | Device / runtime | Settings | Session |
| --- | --- | --- | --- | --- |
| 21:12 | 1.0-test18 (`safe streaming`) | Quest 3, Android 14/API 34, Adreno 740, GLES 3.2, Oculus OpenXR 207.297.0 | 72 Hz, auto res 1.00 → 1680x1680/eye, graphics High, Safe on, Legs + Arms, right-hand aim | Menu → PvP Blood Gulch, 22–35 players |
| 23:32 | 1.0.1 package, test19 identity (`safe ordered uploads`) | same | same | Menu → native browser → PvP Rat Race, 34 players |
| 23:33 | 1.0.1, test19 identity | same | same | Menu → campaign (map name not logged) |

Six earlier private test18 logs (20:45–20:48, same headset/settings) supply
more baselines: menu and PvP (putput, chillout, carousel).

## Measured findings

`[vr-perf]` "the game's frame" is the game thread's time between headset frames
(`host_xr.c log_statistics`); "waiting on the headset" is the OpenXR wait.

| Build / scene | frames/s | game frame avg (longest) | headset wait |
| --- | ---: | ---: | ---: |
| test18 menu (5 logs) | 68.3–72.0 | 2.2–3.3 ms | 4–11 ms |
| test18 PvP putput/chillout/carousel | 57.6–72.0 | 0.2–6.3 ms | 3–11 ms |
| test18 Blood Gulch 22+ players | 62.8–66.6 | 5.9–13.4 ms | 1–8 ms |
| 1.0.1 menu | 16.8–21.7 | 44.4–70.7 ms (≤151) | ~0.1 ms |
| 1.0.1 campaign load/start | 6.6 | 143 ms (581) | 0.2 ms |
| 1.0.1 Rat Race 34 players | 3.8–6.6 | 146–248 ms (498) | ~0.1 ms |

- Device, runtime, resolution, refresh, preset and Safe setting are identical.
  The regression is a ~15–20× increase in game-thread time with the headset
  wait near zero: the CPU/driver submission path is stalling, not the GPU
  compositor or display.
- It already appears in the main menu before the public browser starts
  (23:32:17 sample precedes 23:32:21 discovery) and in campaign without the
  browser, so the browser is not required to reproduce it.
- Audio host buffers report no underruns; audio slowdown follows the game loop.

## Source comparison (test18 `f45e32dd` → 1.0.1 `bc1f0446`)

Render hot-path changes: (1) Safe-mode `stream_upload`/`index_upload` switched
from the fence-managed unsynchronized ring write (`host_gl_buffer_write`) to
`glBufferSubData` on every draw's vertex and index data; (2) a cached VAO
rebind in `prepare_draw`; (3) one reticle collision ray per frame (a ray
existed before; it now uses the engine firing ray). Network/browser work runs
on the p2p thread with a bounded signature-verification budget and is touched
by the game thread only while the System Link list is open.

**Cause (strongly supported, device confirmation pending):** change (1).
Safe disables static mirrors, so all geometry is streamed every draw, for both
eyes, into a 16 MB ring buffer. Earlier draws of the same frame are still
queued (Adreno is a deferred tiler) when the next `glBufferSubData` writes
that buffer. The [Khronos ES 3 glBufferSubData reference](https://registry.khronos.org/OpenGL-Refpages/es3.0/html/glBufferSubData.xhtml)
notes that rendering referencing a buffer being updated must drain first; a
driver may instead copy (ghost) the buffer. The repository already records the
same class of cost on Adreno/Mali (`host_gl.c`, `d3d8_gl.c` mirror comments).
The cost scales with draw count, matching menu < campaign < 34-player PvP.
Changes (2) and (3) are a cached bind per frame and one ray per frame; they do
not plausibly explain tens to hundreds of milliseconds.

## Change in test20

- Safe and non-persistent Normal uploads use the test18 fence-managed ring
  write again. Ranges within a frame are disjoint and only grow; a ring slot is
  reused only after `host_gl_wait_frame` passes its fence (`glFinish` on
  timeout); a full non-persistent buffer is orphaned. Safe still disables
  persistent maps/static mirrors and keeps CPU index rebasing. Static mirror
  writes keep ordered `glBufferSubData` (Andiweli a88f257) — unchanged.
- The renderer VAO restoration from test19 is kept (correct and cheap).
- New always-on `[render-perf]` line every 10 s: draws, uploads and KB per
  frame, estimated upload CPU time (1 in 8 uploads timed), stream wraps
  (orphans/finishes) and ring-fence wait. Counting is free; the sampled clock
  reads are rare.
- Startup log reads `safe streaming (fenced ring); CPU index rebasing`; VR
  identity `HaloCE Quest test20 candidate`.

**Tradeoff:** test19's ordered Safe uploads were a hypothesis workaround for
intermittent left-eye corruption seen on test18 (which used this fenced
path). Reverting it may re-expose that corruption if the VAO leak was not
its cause. The new wrap counter tells us whether ring overflow coincides with
the corruption; do not call the left-eye issue fixed.

## Checks

- `tools/test_test20_render_perf.py`: production upload/reserve code writes
  24,000 randomized ranges with no overlap inside any buffer storage
  generation across 1,369 wraps, never calls `glBufferSubData`/`glFinish` in
  Safe; `[render-perf]` emits once per 10 s with correct averages and resets;
  updater never offers v1.0.0 to 1.0.1/1.0.2 installs. ASan/UBSan.
- `tools/test_test15_io.py` updated: Safe and non-persistent Normal use the
  fenced write and exact payload bytes for 768 sizes; persistent retained.
- Full runner, cache tests, both builds and package checks: see
  [TEST20-DELIVERY.md](TEST20-DELIVERY.md).

## What the device test must establish

1. Quest main menu, campaign and a populated PvP server: `[vr-perf]` near
   72 frames/s with game frame back in the test18 range (~2–13 ms).
2. `[render-perf]` uploads estimate well under a few ms per frame. If game
   frame stays high while uploads are low, the stall is elsewhere — send that log.
3. Autumn cryo/control room: watch each eye. Report any left-eye corruption
   with its log; note the `stream wraps` value near that time.
4. Regression pass: reticle, two-hand grip, animation handoff, body/fingers,
   vehicles (third person, right hand), touch/gamepad on flat, co-op, PvP join,
   browser, Versions & updates (must not offer v1.0.0 as an update).

## Status by item (test20b)

| Item | Implemented | Automatically verified | Confirmed on device |
| --- | --- | --- | --- |
| 1.0.1 Safe-upload slowdown | Yes (test20, kept in test20b) | Yes: ring invariant, no `glBufferSubData`, packaging markers | **No** — awaiting Quest log |
| `[render-perf]` diagnostics | Yes | Yes: line format, averages, reset | No |
| Armed/unarmed calibration conflict | Yes (test20b) | Yes: `test_test20_alignment.py` | **No** — awaiting headset check (video welcome) |
| Left-eye corruption | No change beyond test19 VAO restore | VAO restore test | No — open |
| Co-op failures / populated-host crash guard | No new change | Existing suites | No — open (TEST19-COMMUNITY-REVIEW.md) |

The test20 performance fix was re-inspected for test20b against the 1.0.1
logs: Safe and non-persistent Normal stream/index uploads still use only the
fenced ring write; nothing else in the render path changed. Preserved as is.

## Flat2VR follow-up 2026-10-04: armed vs. unarmed hand alignment

Report (Wr3nch, 9:07 a.m. ET): after adjusting an existing setting that seemed
to set "armed" and "unarmed" positions, switching between an empty hand and a
held weapon left only one state correct. The owner confirmed this was not the
Body option. A video may follow.

**Existing settings reviewed (source, not device):**

| Setting | What it actually changes |
| --- | --- |
| VR Settings → Align Left / Align Right (now **Calibrate Left / Right**): Pitch, Yaw, Roll, Right, Up, Back, Flip Roll 180, Reset | One correction per *physical* controller (`vr.align_<side>_*`), applied once per frame before gestures, aiming, IK, contact and avatars |
| Aim Pose (now **Aim Source**) Native/Grip | Whether the weapon/ray uses OpenXR's aim pose or the grip pose |
| Body, Arms, Fingers | What body is shown and how arms are posed; no calibration |
| Weapons Locked/Physical, Two Hands | Weapon handling; no calibration |
| `vr.weapon_offset_*` (config file only) | Weapon model grip offset; affects a held weapon only |

There are **no separate armed/unarmed calibration settings**. Save (each step
writes config), reload (`vr_reload_settings`) and Reset (all seven keys per
side) were checked and are consistent. Calibration is applied exactly once per
frame from fresh runtime poses, so stale state and double application were
ruled out in source.

**Cause (established in source; device confirmation pending):** a held weapon
takes its orientation from the controller's *aim* pose and an empty hand from
its *grip* pose (both use the grip position; `vr_weapon_view`,
`vr_hand_world`). Test15 applied the same local Pitch/Yaw/Roll to each pose
separately. On Touch controllers the two frames are tilted apart, so the same
Yaw or Roll value turns them about different world axes: tuning for the gun
misaligns the empty hand and vice versa. A deterministic model with a 40°
grip/aim tilt shows the old path breaking the hand-to-weapon relationship in
all 2,000 random calibrations.

**Change:** `vr_alignment_apply_controller` applies one rigid correction per
controller. The aim rotation keeps its previous meaning, so a saved calibration
leaves the held weapon's orientation and position bit-identical. The grip turns
by the same world rotation, so the empty hand now matches the weapon. Offsets
move both poses by one vector in the grip frame. With nonzero offsets, the aim
ray origin can shift by up to the offset size, following the visible weapon.
Aim Source Grip and missing-pose fallbacks behave as before. Labels now read
Calibrate Left/Right and Aim Source; config keys and saved values are unchanged
(no migration needed).

**Device check needed:** with a nonzero Yaw/Roll calibration, go from empty hand
→ pistol → another weapon → empty hand. The hand should line up with the
controller in both states, in right- and left-handed modes, with support grip
and reload. If only one state still looks right, a short video plus the log
(it prints both calibrations at startup) is the next evidence needed.

## Unresolved / observations

- 23:33 campaign log reports "the game's sound work 194292 times" in one
  10-second window during load; other windows track the frame count. Not
  explained; watch whether it recurs in test20.
- test18 21:12 log: activity paused mid-match; the watchdog reported no frames
  for ~77 min until resume, then the session ended cleanly as host timed out.
  Expected while paused; not part of this regression.
- Left-eye corruption root cause, populated-host crash guard and co-op remain
  open from test19 (see TEST19-COMMUNITY-REVIEW.md).
