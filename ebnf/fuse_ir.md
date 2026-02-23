# Fuse IR (EBNF)

**Abstract**
Fuse is a domain-specific language (DSL) designed for expressing cognitive pipelines and high-level graph transformations. The Fuse-IR grammar separates metadata (via pragmas) and computation (graphs and operators) and includes constructs to express proofs and assertions about graphs for verification.

**Use cases**
- Author high-level cognitive graphs with explicit metadata for compilation and lowering to ONNX.
- Capture constants and parameters separately for aggressive constant folding and verification.
- Define proof graphs with assertions used in formal verification and tests.

**Example**
```text
@fuse version 1.0
const SCALE: f32 = 0.75

graph ScaleAdd(x: f32 [N]) -> f32 [N] {
  a: SCALE : f32 [1] = 0.75
  y = Reshape(x, [N, 1])
  y = Div(y, a)
}

@proof graph CheckScale() {
  x: f32 [10]
  y = ReduceSum(x)
  assert y >= 0
}
```

**Notes**
- Source: `papers/compiled-cognition/sections/07_grammar.tex`
- See `papers/compiled-cognition/README.md` for DSL semantics, lowering rules, and tooling notes.
