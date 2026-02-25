# Fusion Strategies: Compile-Time and Runtime

## Why

Performance, determinism, and adaptability are all important. We need compile-time optimizations for hot paths and runtime composition for flexibility and rapid iteration.

## What

A hybrid approach: `fuse` provides compile-time fusion and optimization (produce efficient ONNX artifacts), while `fusion` provides runtime composition and dynamic linking of subgraphs for adaptability.

## How

- Use `fuse` to express, validate, and compile performance-critical subgraphs into device-optimized ONNX artifacts.
- Keep experimental or optional components dynamic and bind them at runtime via `fusion`'s composition engine.
- Provide equivalence validators and cross-boundary tracing to ensure compiled+runtime graphs behave as intended.

## Implications

- Build pipelines need to support both compilation and runtime composition tests.
- Tracing must preserve namespace and provenance across compile/runtime boundary.

## Opportunities

* Selective compilation toolchains that compile hot-paths and keep tail paths dynamic for experimentation.
* Equivalence testing frameworks that validate compiled graphs against a runtime composition.
* Latency-aware deployment managers that compile for specific hardware while routing experimental traffic to dynamic components.
* Tools to generate device-specialized variants from the same logical subgraph (e.g., GPU, CPU, edge).

## Novel Use Cases

* Canarying: compile the hot-path for production while canarying new dynamic subgraphs for functionality or fairness testing.
* Live specialization: detect hot subgraphs at runtime and automatically compile them to a target device profile for improved latency.
* Hybrid A/B: keep A path compiled, B path dynamic for quick rollback or iteration without full redeploy.
