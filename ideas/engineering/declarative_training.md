# Declarative Training

## Why

Training scope ambiguity leads to accidental drift, policy violations, and hard-to-audit personalization. Declaring trainable regions at the source improves safety, reproducibility, and policy enforcement.

## What

A declarative mechanism (`@train` annotations in `fuse`) that marks which parameters or subgraphs are trainable. This metadata is persisted into ONNX and the provenance chain so training runs and their scope are auditable and machine-verifiable.

## How

- Allow authors to mark trainable regions in `fuse` source.
- Emit training metadata into ONNX and registry records (content-hash + trainability manifest).
- Make training pipelines consume manifests and produce signed run artifacts with training scope, hyperparameters and environment metadata.

## Implications

- Facilitates policy enforcement (e.g., blocking training on sensitive parameters) and fine-grained access control.
- Simplifies auditing and certification of training runs.

## Opportunities

* Declarative pipelines that validate trainability manifests and produce verified artifacts (signed models, training logs, metrics).
* Fine-grained access controls: role-based training authorizations and per-subgraph permissioning.
* Safe personalization frameworks that expose constrained trainable interfaces for user-level customization.
* Certification products that attest training runs for compliance-heavy domains.
* Testing harnesses that assert trainability contracts in CI before training occurs.

## Novel Use Cases

* Multi-tenant personalization where each tenant can only update a small, auditable parameter set.
* Certified training runs for pharmaceuticals or finance where regulators require attestable training scopes.
* Marketplace-subgraph leasing: permit temporary trainability granted under escrowed conditions and audit trails.
