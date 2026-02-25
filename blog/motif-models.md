# Motif Models 🔍

**Overview:**
A systematic taxonomy of computation-only graph motifs (100+ motifs) that captures recurring, composable patterns in computation graphs and provides canonical ONNX/Python implementations plus an RDF/TTL ontology.

## Sections & Key Points

- **Introduction** — Define motifs, motivation for taxonomy, and scope of coverage.
- **Background** — Prior work on graph patterns, compiler optimizations, and motif detection.
- **Methods** — Taxonomy curation, signature definitions, fingerprinting, and TTL ontology generation.
- **Results** — Catalog of motifs, case studies on transformers/GNNs/RNNs, and measured optimizations (fusion, latency, memory).
- **Discussion** — Implications for optimization, verification, and tooling; limitations and future directions.
- **Conclusion** — Summary of contributions and artifact availability.

## Appendices & Artifacts
- **Appendices**: Extended motif lists, ONNX examples, Python references, RDF/TTL ontology, tests, and benchmarks.
- **Reproducibility**: `examples/`, `src/`, `ttl/motifs.ttl`, and `experiments/` contain runnable artifacts and benchmarks.

---
*Derived from `papers/motif-models/index.tex` and appendices.*