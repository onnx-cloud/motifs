# 04 — Compiled Cognition: From Intent to Execution

Intent can and needs to be compiled into runnable systems. The Fuse language and compiler bridge this gap. Fuse allows engineers to specify neural computation graphs with explicit type annotations, proof obligations, and training semantics.

The compiler performs several transformations:

- **Lowering**: translating high-level specifications into executable ONNX or native code while preserving type constraints
- **Adjoint computation**: automatically generating gradient graphs for backpropagation, with types that ensure gradients have compatible shapes and semantics
- **Projection**: inserting normalization operations when gradient-based updates would violate semantic constraints

These transformations are not heuristic approximations. They must be specified formally and be verified mechanically.