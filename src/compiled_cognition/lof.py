"""Simple LOF training utilities for experiments.
Provides forward, gradient, projection, and training loop for the LOF example used in papers.
"""
from typing import Sequence, Tuple
import numpy as np

def lof_score(x: np.ndarray, center: np.ndarray, reference: np.ndarray) -> float:
    """Compute LOF-style ratio as scalar.
    x, center, reference are 1-D arrays of same shape.
    """
    dist = np.sum(np.abs(x - center))
    ref_dist = np.sum(np.abs(reference - center))
    ratio = dist / (ref_dist + 1.0)
    return float(ratio)


def grad_wrt_reference(x: np.ndarray, center: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Compute gradient of ratio w.r.t reference.
    Uses subgradient for abs: sign(reference-center).
    d ratio / d reference = - dist / (ref_dist + 1)^2 * sign(reference-center)
    """
    dist = np.sum(np.abs(x - center))
    ref_dist = np.sum(np.abs(reference - center))
    if ref_dist == 0:
        # subgradient ambiguous at 0; use zero gradient to be conservative
        sign = np.zeros_like(reference)
    else:
        sign = np.sign(reference - center)
    grad = - (dist / ((ref_dist + 1.0) ** 2)) * sign
    return grad


def project_box(vec: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Project vector onto axis-aligned box [lo,hi] elementwise."""
    return np.clip(vec, lo, hi)


def train_reference(
    reference: np.ndarray,
    center: np.ndarray,
    samples: Sequence[np.ndarray],
    labels: Sequence[float],
    lr: float = 1e-1,
    steps: int = 100,
    clip: Tuple[float, float] = (-1.0, 1.0),
    verbose: bool = False,
):
    """Simple training loop optimizing reference to reduce MSE of outputs.
    Uses typed projected gradient descent (box projection) as an example of Project_Sigma.
    Returns (reference, history)
    """
    ref = reference.astype(float).copy()
    history = []
    for t in range(steps):
        losses = []
        grads = np.zeros_like(ref)
        for x, y in zip(samples, labels):
            out = lof_score(x, center, ref)
            losses.append((out - y) ** 2)
            # gradient of MSE loss wrt ref: 2*(out-y)*dout/dref
            dout_dref = grad_wrt_reference(x, center, ref)
            grads += 2.0 * (out - y) * dout_dref
        grads = grads / max(1, len(samples))
        ref_temp = ref - lr * grads
        ref = project_box(ref_temp, clip[0], clip[1])
        mean_loss = float(np.mean(losses))
        history.append(mean_loss)
        if verbose and (t % max(1, steps // 10) == 0):
            print(f"step={t}, loss={mean_loss:.6f}, ref={ref}")
    return ref, history
