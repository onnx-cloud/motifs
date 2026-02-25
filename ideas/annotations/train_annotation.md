# `@train` Annotation (in `fuse`)

`@train` marks regions of a `fuse` graph as trainable and conveys training metadata into the generated ONNX artifact. This makes training intent first-class in source, preserving the contract between model authors and training systems (`factory`).

## How `fuse` Uses It

* Authors annotate subgraphs or parameters with `@train`.
* The `fuse` compiler emits ONNX with embedded metadata and semantic references that link the trainable region to its provenance.

## How `factory` Uses It

* `factory` consumes the ONNX artifact and reads `@train` metadata to create a reproducible training job (dataset, augmentation, optimizer, hyperparameters).
* Training runs emit content-addressed artifacts (checkpoints, metrics, logs) and update the semantic graph with training outcomes.

## Implications

* Training becomes an auditable, reproducible artifact that ties code, data, and runs together.
* Policies and access controls can restrict which `@train` regions are allowed to be retrained in different environments.

## Opportunities

* Declarative training UIs that let non-experts configure training for `@train` regions safely.
* Automatic generation of minimal, signed training manifests that accompany a new trained asset.

## Novel Use Cases

* Multi-tenant personalization where each tenant is given a disjoint `@train` region with strict governance and roll-back controls.

