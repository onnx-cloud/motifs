# Stable Identity

`@id` provides a stable, human- and machine-readable identity for graphs, subgraphs, and tensors. Unlike content-addresses, `@id` is a semantic handle that can be resolvable within a namespace and used for governance, discovery, and versioning.

## Uses

* Attach `@id` to nodes or subgraphs in `fuse` to guarantee stable naming across compilation and runtime.
* Map `@id` to content-addressed snapshots in `freezer` and to entries in `fabric` for semantic metadata.

## Implications

* Simplifies references in governance and testing policies by providing consistent lookups.
* `@id` + content-hash pairing enables both stable naming and cryptographic integrity.

## Opportunities

* Name registries and resolution services that bind `@id`s to canonical artifacts and access policies.
* Development workflows that support aliasing and deprecation when `@id`s need to evolve.

## Novel Use Cases

* A global model catalog that allows teams to request `@id`s with attached governance templates for rapid, policy-compliant onboarding.