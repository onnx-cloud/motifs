# Asset Lifecycle: From Source to Golden

An ONNX artifact in this universe is more than a file — it is an asset that travels a deterministic lifecycle: design, training, freeze, governance, testing, publication, and ongoing monitoring.

## Lifecycle Phases

* **Authoring (`fuse`)**: Graphs and annotations (`@id`, `@train`, `@freeze`) are authored with semantic bindings.
* **Training (`factory`)**: Annotated graphs are materialized into trained artifacts with captured metrics and checkpoints.
* **Freezing (`freezer`)**: Stable, audited artifacts are content-addressed and stored with provenance and optional proofs.
* **Governance (`fabric`)**: Policies are applied and attestations (`@proof`) recorded; access control is enforced.
* **Testing & Goldenization**: Artifacts pass integration tests and are promoted to golden status with signatures.
* **Deployment (`fusion`)**: Deployed artifacts are composed at runtime with observability and snapshotting.
* **Monitoring & Iteration**: Runtime telemetry, snapshot-driven incidents, and cyclic retraining where allowed.

## Key Guarantees

* **Reproducibility**: Minimal bundles exist to recreate any artifact deterministically.
* **Traceability**: Every asset maps back to code, data, and training runs.
* **Governance**: Automated gates and proofs ensure only compliant artifacts are published.

## Opportunities

* Lifecycle orchestration tools that map `fuse` annotations directly into CI/CD workflows for continuous AI.
* Compliance-as-Code that ties policy tests to lifecycle transitions (e.g., only freeze after passing privacy checks).
* "One-click certification": from training to signed golden artifact, with reproducible attestation packages ready for regulators.