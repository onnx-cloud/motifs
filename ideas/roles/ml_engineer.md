# Role: ML Engineer

ML Engineers productionize models: build pipelines, deploy composed graphs, and monitor runtime behavior. 

The tensor bus and golden assets become operational primitives for this role.

## Responsibilities

* Build CI/CD that validates artifacts against golden assets and runs snapshot regression suites.
* Implement runtime snapshotting, observability, and rollback mechanics using frozen artifacts.

## Implications

* Emphasis on performance-aware composition and low-latency snapshot capture.
* Need for tooling that maps `@id`/`@proof` metadata into deployment manifests and policy gates.

## Opportunities

* Automated validators that block deployments when snapshot diffs exceed tolerances.
* Runtime orchestration that swaps in certified fused artifacts based on QoS and proofs.