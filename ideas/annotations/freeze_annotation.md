# `@freeze` Annotation

* `@freeze` marks parameters or subgraphs as immutable at training time. The training environment can optimize and strip gradients for frozen sections.

## As a Lifecycle Action

* When a model is "frozen" as an artifact, it is content-addressed and pushed to `freezer` with full provenance metadata and optional attestations.

## Implications

* Freezing reduces attack surface for accidental retraining and simplifies deployment validation.
* The `freezer` snapshot becomes the canonical artifact for audits and reproductions.

## Opportunities

* Policy-driven freeze workflows (e.g., freeze after passing governance checks).
* Lightweight, reproducible deployment artifacts that are accepted by regulators as immutable records.

## Novel Use Cases

* Device-targeted frozen variants (quantized/fused) stored alongside the canonical frozen artifact for traceable optimization.