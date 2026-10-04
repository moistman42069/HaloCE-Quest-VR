# Test20b checkpoint

Private candidate **1.0.2 / code 22**, branch `test20-safe-upload-performance`.
The complete investigation, evidence and status table is in
[TEST20-PROGRESS.md](TEST20-PROGRESS.md); this page lists what test20b adds.

- Keeps the test20 fix for the withdrawn 1.0.1 Quest slowdown (Safe geometry
  uses the fenced stream ring) and the `[render-perf]` log line. Re-inspected;
  unchanged.
- Fixes the Flat2VR armed/unarmed alignment report (2026-10-04): controller
  calibration is now one rigid correction per controller, so the held weapon
  and the empty hand move together. Saved values are kept; the held weapon is
  unchanged for them. Menu pages renamed Calibrate Left/Right, option Aim Source.
- New suite `tools/test_test20_alignment.py` (17 suites in the runner).

Implemented and automatically verified; **not confirmed on a device**. Left-eye
corruption, co-op failures and the populated-host crash guard remain open
(TEST19-COMMUNITY-REVIEW.md). No release without explicit owner approval.
