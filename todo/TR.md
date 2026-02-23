# TODO: Typed Reality (TR) — Improvements and Paper Tasks

This TODO collects actionable improvements, experiments, and paper edits to align the Typed Reality draft with the "Statically Typed Reality" conception and to strengthen claims, evaluation, and implementation readiness.

## Short summary ✅
- Core idea already matches: Tensor = (DType, Shape, Semantics). Strong emphasis on semantic preservation and ONNX lowering.
- Gaps: formalization details, evaluation/benchmarks, concrete ONNX metadata mapping, stochastic semantics, and failure-mode treatment.

## Paper/Spec Edits (high priority)
1. **Clarify Distribution semantics**: explicitly distinguish logits (unnormalized) vs normalized probabilities and annotate expected downstream morphs (Sample, Expectation).
2. **Formal rules**: add a compact type judgment syntax and inference rules (typing, subtyping, semantic subsumption). Include brief proof sketches for Preservation + Progress.
3. **Assertion elision algorithm**: describe constraint propagation and when runtime asserts can be elided with examples.
4. **ONNX mapping table**: expand `06_lowering` with precise op-level mapping (which ops, metadata attributes, patterns to encode Assert/Clip checks, and opset compatibility notes).
5. **Safety & failure modes**: add a dedicated subsection about sensor faults, adversarial inputs, and how types help localize but do not eliminate these issues.
6. **Examples & figures**: add a small end-to-end example (camera + tokenizer → transformer → motor) with types annotated on each edge and a lowered ONNX snippet.

## Implementation & Tests (medium priority)
1. **ONNX PoC**: implement a minimal lowering that emits ONNX tensors + Assert/Clip subgraph for Measurements and Enums.
2. **Unit tests**: shape/type/subtyping tests and a set of semantic mismatch tests (e.g., concat of Enum and Measurement should fail at compile time).
3. **Property-based tests**: fuzz small graphs to assert Preservation (type of output after morph matches spec) and that assertion elision is sound.
4. **Benchmarks**: microbenchmarks comparing compile-time checks overhead and runtime penalty of injected asserts vs baseline unannotated model.

## Evaluation & Case Studies (high priority)
1. **Showcase pipelines**: 2-3 multimodal pipelines (vision+text, audio+control) demonstrating bug detection, safer actuator bounds, and auditing tracebacks.
2. **Compare to baseline**: demonstrate a few bugs that would be silent in PyTorch/TensorFlow but caught by TR (unit mismatch, enum misuse, normalization assumptions).
3. **Quantify elision**: percentage of runtime checks elided after symbolic analysis on realistic models.

## LLM/ABI Usability (low-medium priority)
1. **Template ABI**: provide an LLM-friendly JSON/YAML ABI template for sensors/actuators and an example prompt that generates a compliant pipeline.
2. **Examples**: add a small script that generates skeleton graphs from a declarative ABI using an LLM and then type-checks them.

## Documentation & Community (low priority)
1. **Developer guide**: how to add new semantic IRIs (Measurement/Enum), add morph primitives, and extend the ONNX lowering table.
2. **Appendices**: formal semantics, EBNF grammar (expand `07_ebnf.tex`), and an expanded related work paragraph comparing to ROS2 messages and type-safe instrumentation systems.

---

If useful, I can: 1) open a small PR adding the Distribution/Softmax clarification and an ONNX mapping example; 2) start the ONNX PoC lowering and tests. Which task should I begin with?
