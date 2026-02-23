# Typed Reality (EBNF)

**Abstract**
A small, type-oriented grammar defining tensor types, morphisms, and graphs. The grammar is used to represent typed tensors (DType + Shape + Semantics), declare typed morphisms (with constraints and checks), and describe graphs composed of typed nodes and typed edges for verification and lowering to ONNX.

**Use cases**
- Define and verify typed computational graphs for sensor, symbolic, and probabilistic pipelines.
- Emit verifiable ASTs for code generation or LLM-guided transformations.
- Enforce shape/dtype/semantics constraints during compilation and lowering.

**Example**
```text
morph Normalize(x: f32 [1, N] {M{1, "unit", "frame", [0,1]} }) -> f32 [1, N]
{
  const: eps: f32 [1]
  wt: w: f32 [N]
  chk: shape(x, w)
}

graph MyGraph() {
  in: input: f32 [1, 224, 224]
  N1: norm: Normalize
  E1: (input.0) -> (N1.x): f32 [1, 224, 224]
}
```

**Notes**
- Source: `papers/typed-reality/sections/07_ebnf.tex`
- Tests and related artifacts are in `papers/typed-reality/` and may be reproduced via the repository `make` targets.
