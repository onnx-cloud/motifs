# Financial Services

In finance, auditable models and deterministic replay are essential for compliance, back-testing, and risk management. The global ONNX namespace and tensor snapshots enable verifiable audit trails and rapid incident forensics.

## Key Uses

* Fraud detection systems with snapshot-based evidence for contested transactions.
* Risk models that can be exactly re-run for regulatory back-tests and stress tests.

## Implications

* Access controls and proofs (`@proof`) must be fine-grained to satisfy auditors and regulators (e.g., SEC, FCA).
* Snapshot storage must balance fidelity with retention and privacy constraints.

## Opportunities

* Automated regulatory reports that include minimal reproducible artifacts and signed attestations.
* Differential privacy and selective snapshotting for sensitive financial inputs.

## Novel Use Cases

* Market-simulators that branch from real trading snapshots to run counterfactual strategies in isolation.