# High-level Specification (WIKI)

High-level classes & contracts
------------------------------
1) RDFManager (src/wiki/rdf.py)
   - Responsibility: load TTL/RDF into a single graphs. support walk, find and SPARQL.

2) Ontology Objects (src/wiki/ontology.py)
   - Responsibility: cached motifs, categories, signatures, ONNX ops etc used by render pipeline. 

2) Page Renderer (src/wiki/page.py)
   - Responsibility: cached partials, render page in context

3) Wiki Generator (src/generator.py)
   - Responsibility: load the confg/wiki.yaml then render the wiki

## Detailed Implementation Plan (Wiki Generator) 🔧
### Goal 🎯
- Produce a fast, reliable, and maintainable wiki generator that renders pages from TTL/RDF + SPARQL into HTML/Markdown using cached/compiled templates and supports incremental builds.
### High-level architecture
- **RDFManager** (`src/wiki/rdf.py`): single graph loader, SPARQL execution, and query caching.
- **Ontology Objects** (`src/wiki/ontology.py`): in-memory objects for motifs, categories, signatures with lightweight caching and invalidation.
- **Page Renderer** (`src/wiki/page.py`): Jinja2 precompiled templates, partials cache, streaming output.
- **Wiki Generator** (`src/generator.py`): orchestration, dependency graph, incremental/parallel rendering.
- **Config**: `config/wiki.yaml` and `config/pages.yaml` to map inputs → pages.
### Non-functional targets ⚡
- Full build (N ≈ 200 pages): ≤ 60s on a CI worker.
- Incremental change: re-render only affected pages, ≤ 1s per page.
- Keep peak memory < 1 GB for typical runs.
- Unit + integration test coverage > 90% for core modules.
- Deterministic output (stable hashes/checksums for caching).
### Milestones & timeline (prioritized)
1. **Design & API (1–2 days)**
   - Define interfaces for `RDFManager`, `Ontology`, `PageRenderer`, `WikiGenerator` and cache semantics (mtime vs content-hash).
2. **Skeleton + tests (1–2 days)**
   - Create module skeletons with typed signatures and tests; add CI job for tests & linting.
3. **Core implementation (3–5 days)**
   - Implement RDF loading (lazy), SPARQL execution and query cache; implement Ontology objects and renderer with precompiled templates.
4. **Incremental + parallel renderer (2–3 days)**
   - Build dependency graph, fingerprint inputs per page, add parallel rendering using a pool.
5. **Caching & persistence (1–2 days)**
   - Persist SPARQL cache on disk and cache template ASTs; implement robust invalidation.
6. **Perf tests, profiling, hardening (1–2 days)**
   - Add benchmarks, profiling scripts, and CI regression checks.
7. **Docs & deployment (1 day)**
   - Add `make wiki`, documentation, and examples.
### Implementation details & optimizations 💡
- Use content-hash or mtime+size to detect TTL/template changes.
- SPARQL cache key = query text + dataset hash; store in sqlite or hashed files.
- Precompile Jinja2 templates and cache partials; stream outputs to avoid high memory use.
- Parallelize rendering for IO-bound work with `ThreadPoolExecutor`; use `ProcessPoolExecutor` where CPU-bound.
- Add profiling (pyinstrument/cProfile) and benchmark tests in CI.
### CI / Automation ✔️
- Add GitHub Actions jobs: lint, unit tests, integration tests, perf baseline (scheduled nightly).
- Makefile targets: `make wiki`, `make wiki-fast`, `make wiki-debug`.

