Run the minimal self-modeling sensor experiment:

```
./scripts/run_self_modeling_sensor.sh
```

Outputs:
- `papers/cognitive-closure/figures/self_modeling_sensor.png` — time series plot of sensor gain and prediction error
- `papers/cognitive-closure/figures/self_modeling_sensor.npz` — compressed numpy archive containing `g`, `w`, and `pred_error` arrays

The notebook `notebooks/self_modeling_sensor.ipynb` contains an interactive version of the experiment and a scope clarification cell to request preferred frameworks or datasets.