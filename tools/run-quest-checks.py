"""Run deterministic Quest/flat regressions serially. Does not launch the game.

Run with Linux/WSL clang and a JDK. Per-suite output is under ignored build/.
Cache-format pytest tests are separate: python3 -m pytest -q tools/test_cache_file_formats.py
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/quest-regressions'
SUITES = [
    'test_test17_network_data', 'test_test16_actions', 'test_campaign_actors',
    'test_campaign_lifecycle', 'test_campaign_capacity', 'test_quest_browser',
    'test_quest_vr_math', 'test_quest_render_targets', 'test_test15_refinements',
    'test_test15_io', 'test_android_gamepad', 'test_vr_vehicle_lifecycle',
    'test_test18_vehicle_tutorial', 'test_test19_network_browser', 'test_test19_media',
    'test_test20_render_perf', 'test_test20_alignment', 'test_test20c_hands', 'test_test20d', 'test_test20e_network', 'test_test20e_reticle', 'test_test21', 'test_test22', 'test_test23', 'test_test24', 'test_test24b', 'test_test25', 'test_test26',
]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    failed = []
    for name in SUITES:
        print('RUN', name, flush=True)
        with (OUT / (name + '.log')).open('w') as log:
            result = subprocess.run([sys.executable, str(ROOT / 'tools' / (name + '.py'))],
                                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        print('FAIL' if result.returncode else 'PASS', name, flush=True)
        if result.returncode:
            failed.append(name)
    print('Failed suites:', failed, flush=True)
    return bool(failed)

if __name__ == '__main__':
    sys.exit(main())
