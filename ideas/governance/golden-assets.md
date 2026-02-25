# Golden Assets: Certified, Signed, Reproducible

A golden asset is a certified ONNX artifact that has passed all required tests, governance checks, and attestation steps. It is the canonical version that consumers should rely on.

## Properties of Golden Assets

* **Signed & Provenanced**: Accompanied by proofs, provenance metadata, and content-addressed storage references.
* **Tested**: Passed unit, integration, and snapshot-based regressions with recorded metrics.
* **Discoverable**: Registered in catalogs with `@id` and searchable by metadata (capabilities, constraints, proofs).

## Lifecyle

1. Candidate artifact is produced from `factory` with `@train`/`@freeze` metadata.
2. Automated test and governance suites run; artifacts that pass emit `@proof` attestations.
3. Passing artifacts are signed and promoted to golden status and stored in `freezer`.

## Opportunities

* Trust-based distribution models where downstream systems automatically accept golden assets with valid proofs.
* Signed golden bundles for regulated audits that include minimal re-run inputs.

## Novel Use Cases

* Marketplace of certified subgraphs where buyers can filter by provenance and proof status before composing them into products.