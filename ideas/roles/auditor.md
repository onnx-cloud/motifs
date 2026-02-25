# Role: Auditor

Auditors examine artifacts, provenance, and proofs to verify compliance and investigate incidents. Snapshot-driven replay enables efficient and precise audits with minimal reliance on live systems.

## Responsibilities

* Verify training and test artifacts against declared policies and proofs.
* Re-run selected snapshots and compare outcomes to published golden assets.

## Implications

* Auditable packages should include minimal, self-contained inputs to enable deterministic re-runs.
* Access controls and privacy redaction must balance audit needs with data protection.

## Opportunities

* Automated audit reports that summarize checkpoint provenance, tests run, and proof validity.
* Tools for differential audits that focus attention on components with the greatest risk or drift.