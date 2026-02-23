import subprocess
import sys

import pytest


def test_run_lof_experiment_skips_if_no_numpy():
    try:
        import numpy  # noqa
    except Exception:
        pytest.skip("numpy not installed")


def test_run_lof_experiment_executes():
    # run the experiment script and ensure it prints JSON with expected keys
    rc = subprocess.run([sys.executable, 'scripts/run_lof_experiment.py'], capture_output=True, text=True)
    assert rc.returncode == 0
    out = rc.stdout.strip()
    assert out.startswith('{') and 'final_loss' in out and 'final_ref' in out
