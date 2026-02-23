# Composable Architectures

Operators are fusible subgraphs and composition patterns for ML models, agents and fleets. You can think of operators as weight-less models.

## Overview ✅

Operators are reusable, composable building blocks that express patterns of computation and interaction. They are intended to:

- Capture recurring subgraph patterns (motifs) and higher-level orchestration patterns.
- Be fused into models or runtime graphs without necessarily carrying weights (i.e., they describe structure and behavior).
- Enable modular composition of models, agents, and systems at development and deployment time.
## Definition 🔧
An **Operator** is a named descriptor containing:

- `id` — Unique identifier (e.g., `op:ForkJoin`).
- `signature` — Inputs/outputs and cardinality constraints.
- `pattern` — The subgraph or composition pattern (SPARQL snippet, motif reference, or proto description).
- `runtime` (optional) — Requirements or hints for execution (e.g., GPU, runtime library).
- `meta` — Human-readable label, description, tags, and provenance.

Operators may be expressed as TTL/JSON/YAML artifacts in `ttl/` or `operators/` and should reference motifs where applicable.
## Composition & Fusion 🔁
- Operators are designed to be fusible: multiple operators can be composed to form a single fused graph.
- Fusion rules should be deterministic and expressed in the `fuse_generator` pipeline.
- Operators should include compatibility metadata to guide safe composition (e.g., input/output axis semantics).
## Examples ✏️
- A routing operator that dispatches tensors to separate subgraphs (e.g., `Router`).
- A monitoring operator that attaches metrics collection (weight-less instrumentation).
- An ensemble operator expressing the composition of submodels with a selection policy.
## Integration with this repo 🔗
- Add operator descriptors under `ttl/` or a dedicated `operators/` folder.
- Provide SPARQL queries in `sparql/` to locate operator occurrences and to drive `fuse_generator` outputs.
- Update `WIKI_TODO.md` and docs to include documentation pages for operators.
## Contributing & Governance 🧭
- Follow the motif conventions (use `skos:prefLabel`, `motif:hasSignature`, etc.).
- Include `onnx:requiresRuntime` where applicable.
- Add tests to `tests/` demonstrating operator discovery and fusion behavior.

