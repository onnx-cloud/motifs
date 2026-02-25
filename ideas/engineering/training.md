# Training Lifecycle (`fuse` → `factory`)

Training is a first-class, reproducible lifecycle stage in the ecosystem: `fuse` declares intent, `factory` executes, `freezer` and `fabric` capture artifacts and governance. This page sketches the lifecycle from model authoring through productionized training and certification.

## Stages

1. **Design (`fuse`)**: Authors annotate trainable regions with `@train` and `@training` metadata. Models are compiled to ONNX with embedded provenance.
2. **Plan (`factory`)**: `factory` schedules reproducible runs (datasets from `freezer`, compute config, hyperparams from `@training`).
3. **Execute**: Training runs produce checkpoints, metrics, and artifacts. Each output is content-addressed and recorded in `freezer`.
4. **Validate**: Tests and governance checks run automatically; proofs (`@proof`) are emitted for passing artifacts.
5. **Publish**: Golden artifacts and attestations are signed and published to catalogs/registries.

## Best Practices

* Always attach `@training` manifests to training runs for reproducibility.
* Include smoke tests that assert basic functional properties before publishing.
* Create a minimal provenance bundle (model, schema, metrics, proofs) for audits.

## Opportunities

* Auto-generated training manifests from `fuse` that populate CI and scheduler pipelines.
* Reproducibility dashboards that show the full lineage and the minimal inputs needed to re-run.

## Novel Use Cases

* Contract-based training pipelines where SLAs (accuracy, fairness, latency) are encoded and enforced programmatically.