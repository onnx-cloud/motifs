# Semantic Graph Naming & Namespacing

## Why

Unambiguous tensor and graph addressing is essential for correct composition, provenance, and policy enforcement. Without consistent naming, tensors can be misbound at runtime, audits become unreliable, and automated tooling breaks.

## What

A set of naming rules and invariants that produce fully-qualified, semantically meaningful tensor addresses that survive compilation, serialization (.onnx), and runtime composition. Primary pattern: `<role>.<domain.graph>@<version_or_hash>.<tensor>`.

## How

- Enforce naming in the `fuse` compiler and preserve names in ONNX `ValueInfo` and node fields.
- Map semantic names to content-addressed artifacts in `freezer`, and record the mapping in RDF TTL snippets in `fabric`.
- Provide linters and CI checks for `no-unqualified-tensors`, `namespace-has-graph`, and `version-or-hash-recommended`.

## Versioning & Provenance

- Prefer content-hash provenance (`domain.graph@sha256:<hash>`) for immutable artifacts used in audits.
- Optionally allow semantic versions (`@v1.2`) for developer ergonomics but require content-hash references for reproducibility.

## Opportunities

* Compiler-enforced name hygiene and automatic name normalization/rewrites during import.
* Registry-backed authoritative namespaces to prevent collisions and enable cross-team delegation.
* Automated mapping tools to reconcile legacy names to fully-qualified names during import.
* Namespacing-aware testing frameworks that assert binding correctness during composition.

## Novel Use Cases

* Runtime re-binding safety: unambiguous names prevent silent runtime misbindings when composing graphs across teams.
* Tensor-level access controls and policy checks enabling precise governance and auditability.
* Predictable artifact resolution for reproducible experiments and regulated audits.