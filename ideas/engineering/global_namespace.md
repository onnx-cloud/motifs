# Global Asset Namespace

## Why

Ambiguity in addressing artifacts (data, code, snapshots) makes composition and provenance fragile. A global asset namespace ensures artifacts are discoverable, resolvable, and auditable across teams and runtimes.

## What

A global namespace that treats `.onnx` artifacts and related assets as first-class, content-addressed entities with stable URIs, access controls, and versioning semantics.

## How

- Assign resolvable, content-addressed identifiers to artifacts and maintain registry services to resolve and authorize access.
- Expose APIs for searching, tagging, mirroring, and subscribing to namespace subsets for federated or offline operation.
- Attach provenance, tests, and policy metadata to artifacts to enable secure discovery and governance.



## Universal Addressing

The global namespace treats .onnx files as the lingua franca for all tensor-related entities. Whether it's an input tensor from a sensor, a trained subgraph, a fused output, or the current bus configuration, each is accessible via a URI-like scheme (e.g., onnx://global/input/sensor123/tick456). This enables seamless sharing, versioning, and composition across distributed systems.

## Implications

* **Interoperability**: Models from different vendors can be composed by referencing their .onnx addresses in the global namespace.
* **Security and Access Control**: Namespace hierarchies can enforce permissions, allowing fine-grained control over who can read or write specific tensors.
* **Scalability Challenges**: A global namespace requires robust distributed storage and indexing to handle the volume of snapshots.

## Opportunities

* **Cognition Catalog**: AI-native interfaces for exploring and querying the global tensor and computation space.
* **Federated Namespaces**: Organizations can mirror or subscribe to subsets of the global namespace for offline operation.
* **Cross-Platform Composition**: A subgraph trained on one platform can be instantly used on another by resolving and binding its global addresses.
* **Version Control for Tensors**: Git-like operations on .onnx files, enabling branching and merging of tensor states.

## Innovation Acceleration

* **Global AI Library**: A public repository where researchers share pre-trained subgraphs as .onnx snapshots, composable by anyone.
* **Real-Time Collaboration**: Teams worldwide edit and compose graphs by referencing shared namespace addresses, with changes propagating instantly.