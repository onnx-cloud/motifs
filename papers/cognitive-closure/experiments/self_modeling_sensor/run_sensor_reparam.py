"""Simple sensor reparameterization experiment.
Saves figure to papers/cognitive-closure/figures/self_modeling_sensor.png
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUT_DIR = Path('papers/cognitive-closure/figures')
OUT_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(0)

T = 1000
sigma_x = 0.1
sigma_s = 0.5

# latent process x_t (random walk)
x = np.zeros(T+1)
for t in range(T):
    x[t+1] = x[t] + np.random.normal(scale=sigma_x)

# initialize parameters
g = 0.5  # sensor gain
w = 0.1  # predictor weight

lr_w = 0.01
lr_g = 0.1

history = {'g': [], 'w': [], 'pred_error': []}

for t in range(T-1):
    s_t = g * x[t] + np.random.normal(scale=sigma_s)
    pred = w * s_t
    target = x[t+1]
    err = (pred - target)
    # update w (gradient descent on squared error)
    gw = 2.0 * err * s_t
    w = w - lr_w * gw
    # estimate gradient wrt g via finite differences
    eps = 1e-3
    s_plus = (g+eps)*x[t]
    pred_plus = w * s_plus
    err_plus = (pred_plus - target)
    s_minus = (g-eps)*x[t]
    pred_minus = w * s_minus
    err_minus = (pred_minus - target)
    d_err_dg = (err_plus**2 - err_minus**2) / (2*eps)
    # gradient descent on g to reduce squared error
    g = g - lr_g * d_err_dg

    history['g'].append(g)
    history['w'].append(w)
    history['pred_error'].append(err**2)

# convert to arrays
for k in history:
    history[k] = np.array(history[k])

# Save final figure
plt.figure(figsize=(8,5))
plt.subplot(2,1,1)
plt.plot(history['g'])
plt.title('Sensor gain g over time')
plt.ylabel('g')
plt.subplot(2,1,2)
plt.plot(history['pred_error'])
plt.title('Prediction squared error over time')
plt.ylabel('error^2')
plt.xlabel('timestep')
plt.tight_layout()
plt.savefig(OUT_DIR / 'self_modeling_sensor.png', dpi=150)

# Save history for tests and analysis
np.savez_compressed(OUT_DIR / 'self_modeling_sensor.npz', g=history['g'], w=history['w'], pred_error=history['pred_error'])

if __name__ == '__main__':
    print('Final g =', history['g'][-1])
    print('Mean prediction error (last 100 steps) =', history['pred_error'][-100:].mean())
    print('Figure saved to:', OUT_DIR / 'self_modeling_sensor.png')
    print('History saved to:', OUT_DIR / 'self_modeling_sensor.npz')
