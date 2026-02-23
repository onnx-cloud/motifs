# Typed Reality 📐

**Overview:**
A statically typed ABI and AST that unifies sensors, symbolic knowledge, and probabilistic models as typed tensors (DType, Shape, Semantics). Enables deterministic interpretation, identical train/test graphs, and compile-time verification with explicit runtime assertions when necessary.

## Sections & Key Points

- **Introduction** — Motivation for grounding computation in measurable reality and the problems with untyped, ad-hoc tensor use.
- **Type System** — Triple-type (DType, Shape, Semantics); subtyping, nominal vs structural semantics, and compile-time checks.
- **Sensors & Modalities** — How modalities (vision, audio, language) map to typed tensors and canonical preprocessing; sensor calibration and metadata.
- **Typed Primitives** — Type-preserving primitive operators and composition rules that maintain semantic invariants across transformations.
- **Graph Construction** — Building test/train graphs with preserved semantics; reproducibility and graph equivalence.
- **Lowering** — Strategies for lowering typed graphs to ONNX, runtime targets, and hardware backends while preserving semantics.
- **EBNF** — Formal grammar for graph specification and verified AST generation.
- **Semantics** — Operational and denotational semantics for typed operations.
- **Formalism** — Proof sketches for type-soundness, elimination of certain runtime checks, and correctness guarantees.
- **Related Work** — Positioning with respect to SOSA/SSN, QUDT, type systems, and prior typed-ML efforts.
- **Type Checking** — Static and dynamic checks, assertion generation, and elision when provably safe.
- **LLM Generatability** — How the grammar and AST enable reliable model-code generation using LLMs.
- **Discussion & Conclusion** — Limitations, future extensions, and summary of contributions.

## Artifacts & Reproducibility
- Source: `papers/typed-reality/` (LaTeX sections and examples)
- Tests and EBNF grammars are included in the repo; use `make` targets to reproduce figures and artifacts.

---
*Concise summary created from `papers/typed-reality/index.tex` and section files.*