try:
    import numpy as np
except Exception:  # pragma: no cover - environment may lack numpy
    import pytest
    pytest.skip("numpy not installed, skipping LOF training tests", allow_module_level=True)

from src.compiled_cognition.lof import lof_score, train_reference


def test_lof_forward():
    x = np.array([1.0, 0.0, 0.0])
    center = np.array([0.0, 0.0, 0.0])
    reference = np.array([0.1, -0.1, 0.0])
    out = lof_score(x, center, reference)
    assert abs(out - 0.8333333) < 1e-6


def test_lof_training_reduces_loss():
    center = np.array([0.0, 0.0, 0.0])
    reference = np.array([0.5, -0.5, 0.0])
    samples = [np.array([0.9, 0.0, 0.0]) for _ in range(16)]
    labels = [0.0 for _ in samples]
    ref_after, history = train_reference(reference, center, samples, labels, lr=0.1, steps=50, clip=(-1.0,1.0))
    assert history[0] >= history[-1]
    # ensure projection bounds respected
    assert np.all(ref_after <= 1.0)
    assert np.all(ref_after >= -1.0)
