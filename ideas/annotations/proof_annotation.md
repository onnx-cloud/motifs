# Assertions, Annotation & Attestations

`@proof` tags an artifact or run with cryptographic or policy attestations. Proofs are first-class metadata: signed statements that an artifact satisfies a property (e.g., governance checks passed, metrics thresholds met, training data provenance validated).

## Mechanisms

* Signatures (deterministic content-hash + key) and structured proofs (e.g., signed JSON-LD statements, verifiable credentials).
* `@proof` metadata can reference external attestations stored in `fabric` or `freezer`.

## Implications

* Enables automated trust decisions (deploy only if proofs exist and are valid).
* Simplifies audits by bundling proofs with the artifact instead of separate reports.

## Opportunities

* Attestation services that issue and validate proofs as part of CI/cd and deployment pipelines.
* Fine-grained, revocable attestations that map to specific lifecycle steps (training, testing, governance).

## Novel Use Cases

* A model store that filters search results by valid, non-expired proofs (compliance-aware discovery).