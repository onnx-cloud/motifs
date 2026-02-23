import subprocess
from pathlib import Path
import numpy as np

FIG = Path('papers/cognitive-closure/figures/self_modeling_sensor.png')
NPZ = Path('papers/cognitive-closure/figures/self_modeling_sensor.npz')


def test_run_self_modeling_script(tmp_path):
    # run the script
    subprocess.check_call(['python3', 'papers/cognitive-closure/experiments/self_modeling_sensor/run_sensor_reparam.py'])
    assert FIG.exists(), 'Figure was not created'
    assert NPZ.exists(), 'History npz was not created'
    data = np.load(NPZ)
    pred_error = data['pred_error']
    # check that prediction error decreased (mean of first 100 > mean of last 100)
    assert pred_error[:100].mean() > pred_error[-100:].mean(), 'Prediction error did not decrease'
