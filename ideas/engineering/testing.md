# Testing: From Unit Graph Tests to Snapshot Diffs

Testing in this ecosystem ranges from local unit checks on subgraphs to integration testing using tensor snapshots and golden comparisons. Tests are reproducible and linked to the artifact provenance.

## Testing Layers

* **Unit Tests (`fuse`)**: Validate node-level behaviors and shape/contract invariants at source.
* **Integration Tests**: Compose subgraphs and assert end-to-end properties (latency, numeric fidelity, stability).
* **Snapshot Tests**: Use recorded tensor ticks to replay inputs and compare outputs against golden snapshots.
* **Regression & Performance**: Automate regression checks against previous golden artifacts and monitor performance baselines.

## Practices

* Include semantic assertions (e.g., label distributions, invariants) in test manifests.
* Use snapshot diffs that are semantically aware (tolerances, per-channel comparisons, statistical tests).

## Opportunities

* Continuous testing farms that re-run critical snapshots when subgraphs change.
* Test-driven fusion: require composition contracts to have green tests before allowing runtime fusion.
* "Fault injection by simulation": branch from a snapshot, inject failures into a subgraph, and validate system-level resilience.
