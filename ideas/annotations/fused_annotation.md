# `@fused` Annotation

`@fused` denotes that an ONNX artifact is the result of composition or fusion (a compile-time merging of heavy tensors into the model). It also captures provenance about the ingredients and transformation passes used to produce the fused artifact.

## Purpose

* Record the lineage of composed artifacts: which subgraphs were combined, the transformation passes, and any parameter alignment steps applied.

## Implications

* Consumers can verify that a fused artifact is semantically equivalent to its constituent graphs (or intentionally different by documented changes).
* Enables targeted testing and regression checks at composition boundaries.

## Opportunities

* Composition manifests that describe compatibility and test contracts for fused artifacts.
* Tooling to visually compare pre- and post-fusion graphs with deterministic diffs.

## Novel Use Cases

* A deployment manager that prefers pre-validated fused artifacts for high-availability clusters and only resorts to on-the-fly runtime fusion for experimental routing.