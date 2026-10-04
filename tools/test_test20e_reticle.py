"""Test20e: the crosshair moves at the headset's frame rate.

Owner report (2026-10-04): the crosshair looked like it ran at a lower frame
rate than everything else. On foot its world point came from the unit's aiming
vector, camera position and hand origin, which advance only on the game's
30 Hz ticks. It now follows this frame's hand ray, with the engine's own rules
for where a shot starts. Static checks; the world-to-XR conversion is covered
by test_test19_media.
"""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
render = (ROOT / 'port/linux/game/vr_render.c').read_text(encoding='utf-8')
start = render.index("/* Reticle on the engine's pre-spread firing ray, as it is this frame.")
block = render[start:render.index('vr_set_reticle_world(vr_render.game_camera_position.n, hit.n);', start)]
assert 'vr_hand_ray(vr_render.game_camera_position.n, origin.n, direction.n)' in block
for stale in ['unit_get_camera_position(', 'vr_render_hand_origin(']:
    assert stale not in block, 'tick-rate input in the per-frame reticle: ' + stale
assert 'real_point3d camera = vr_render.game_camera_position;' in block, 'the interpolated camera, not the tick one'
assert 'if (dot_product3d(&aiming, &direction) < 0.866f)' in block and 'direction = aiming;' in block
assert "game_connection() != _game_connection_local ||" in block and 'origin = camera;' in block
assert 'collision_test_vector(_collision_test_for_projectiles_flags, &origin, &vector, unit_index,' in render[start:start + 4000]
# the engine's shot origin rule the reticle mirrors (vr_render_hand_origin's source)
hand = render[render.index('where the hand\'s shots start: the hand, seen from the unit\'s eye'):]
assert 'game_connection() == _game_connection_local' in hand[:600] and 'FLAG(_collision_test_structure_bit)' in hand[:1200]
print('PASS: the on-foot crosshair follows this frame\'s hand ray (no 30 Hz tick inputs), keeps the engine\'s '
      'shot-origin rules and falls back to the game\'s aim when it clamps')
