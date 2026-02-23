# 07 — Self-Modeling: Adaptive Observation

Neural systems typically have fixed sensor configurations. Self-Modeling explores adaptive systems where parameters controlling observation are themselves subject to optimization.

Formally: a system has sensors parameterized by gains and biases. During training, these sensor parameters adapt to improve performance. This is meta-optimization: the system learns not just what to compute but how to observe its environment.

This approach is stable in controlled settings and has practical applications in robotics and adaptive signal processing. The risks are real: a system optimizing its own sensors can develop pathological feedback loops. Mitigation requires constraints, verification, and conservative defaults.