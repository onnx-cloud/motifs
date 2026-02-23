#!/usr/bin/env python3
"""Run the LOF training experiment and print summary."""
import json

try:
    import numpy as np
except Exception:
    print('numpy not available; aborting')
    raise

from src.compiled_cognition.lof import lof_score, train_reference


def main():
    center = np.array([0.0,0.0,0.0])
    reference = np.array([0.5,-0.5,0.0])
    samples = [np.array([0.9,0.0,0.0]) for _ in range(16)]
    labels = [0.0 for _ in samples]
    ref_after, history = train_reference(reference, center, samples, labels, lr=0.1, steps=50, clip=(-1.0,1.0))
    out = lof_score(samples[0], center, ref_after)
    print(json.dumps({'final_loss': history[-1], 'final_ref': ref_after.tolist(), 'final_out': float(out)}))

if __name__ == '__main__':
    main()
