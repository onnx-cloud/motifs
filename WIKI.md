# Semantic Wiki Architecture for Motif Models ✅
## Purpose 🎯
Provide a concise, reusable, modular, and high-performance architecture for a Semantic Wiki that:
- Walks the RDF graph (TTL sources) and renders most classes and predicates
- Is driven by `config/wiki.yaml` and data in `ttl/` and `sparql/`
- Produces static HTML with good search and navigation

## High-level overview 🔧

- Data sources: `ttl/` (primary), optional remote SPARQL endpoints, JSON-LD imports
- RDF layer: a single `RDFManager` abstraction that loads TTL, caches graphs, and exposes SPARQL and traversal primitives
- Query layer: parameterized SPARQL templates (e.g., `sparql/wiki/*.sparql`) with timeouts and limits (configured in `wiki.yaml`)
- Rendering layer: mustache/partials in `src/template/wiki` (or `src/template/docs`), plus a generic entity renderer
- Generator: CLI `src/wiki/generator.py` that reads `config/wiki.yaml`, generates pages, a search index (`search_index.json`) and static assets
- Search: client-side index (Fuse.js or Lunr) built from generator's collected metadata

## Design principles ✨
- Config-driven: everything pluggable from `wiki.yaml` (pages, templates, sparql paths, limits)
- Convention over configuration: auto-generate entity pages for every RDF class and for every IRI encountered
- Safe defaults: query timeouts, `max_foreach_rows`, depth limits on graph walking
- Performance-first: TTL parsing/caching, SPARQL caching, incremental builds, and streaming where possible
- Testable: unit tests for RDF queries + snapshot tests for rendered output

## Rendering model (how entities and predicates are presented) 🖼️

1. Entity page model - strict:
   - Header: skos:prefLabel + type badges (`rdf:type`)
   - Summary: `skos:definition`, 
   - Predicates: `motif:hasCategory`, `motif:hasFingerprint`, `skos:exactMatch`, `onnx:requiresRuntime` rendered as badges/links/cards
   - Relations: group triples by predicate category (identifiers/labels, classification, mappings, signatures, examples)
   - Backlinks: incoming links (who references this entity)
   - Raw: option to view raw TTL / JSON-LD

2. Predicate rendering rules:
   - Special-cased predicates: render with richer UI (cards/links). Examples:
     - `skos:prefLabel` → large title
     - `skos:exactMatch` → link to ONNX operator page with icon
     - `motif:hasSignature` → render as parameter table
   - Generic predicates: display as key/value lists with values linked because they're IRIs
   - Multivalued predicates: show as lists; allow collapse/expand when long

3. Lists and index pages:
   - Config-driven lists (as in `wiki.yaml`): use paged results, search, sort by label or frequency

## Graph traversal & heuristics (walking the graph) 🧭

- Depth-limited BFS/DFS with a default depth (e.g., 1 outgoing + 1 incoming) to avoid explosion and cycles
- Respect `rdf:type` to generate class-level pages and index members of each class
- Use SPARQL for heavy joins (tabulated pages) and traversal for local context rendering
- Avoid traversing large literal-heavy subgraphs; use `max_foreach_rows` config to cap expansions
- Record provenance and query performance to detect slow queries (jsonl)

## Performance & caching ⚡

- TTL parse cache: store parsed graphs (serialized) with a file modification hash to avoid reparsing
- SPARQL result cache: store query output (with TTL or cache-invalidated by source changes)

- Incremental generator: detect changed TTL/SPARQL/templates and only rebuild affected pages
- Use SPARQL `VALUES` and restricted patterns to reduce execution time
- Limit rows and apply pagination to heavy queries

## Extensibility & modularity 🧩

- Plugin points:
- Renderer plugins for predicate-specific rendering (e.g., fingerprint visualization, signature tables)
- Templates & partials: provide a theme layer; allow project-specific overrides in config
- Schema/manifest: curriculum for adding new page types via config; page specs are declarative

## Observability & reliability 📈

- Metrics: track query durations, page generation time, cache hit ratio
- Logging: structured logs for generator and RDF operations
- Circuit-breakers: abort queries hitting configured timeouts
- SHACL validation: run `scripts/run_shacl.py` during CI to catch data-model violations

## Testing & QA ✅
- Unit tests for `RDFManager` and SPARQL templates (use existing `tests/test_rdf_and_fuse.py` as pattern)
- Snapshot tests for rendered HTML (use `tests/test_wiki_generation.py` scaffold)
- Performance tests for long-running queries (timeout assertions)
- Data coverage tests: ensure top predicates and classes have pages

## Implementation roadmap (practical steps) 🛠️
1. Create `WIKI.md` (this document) and add to repo ✅
2. Implement the generator scaffolding in `src/wiki/generator.py` (create `generate_all()`, `generate_page()` and generic entity renderer)
3. Add templates/partials: `entity.mustache`, `predicate-row.mustache`, `lists/*.mustache`
4. Build graph traversal utilities in `RDFManager` (walk_outgoing/incoming, label picking, type extraction)
5. Implement caching & incremental build logic
6. Write tests and add CI job to run generation and snapshot tests
7. Add search index creation and client-side search UI
8. Iterate on rendering rules and edge-case handling (large lists, cycles)

## Example config snippets and patterns 🧾
- Use `wiki.yaml`'s `pages:` shape to declare simple index pages and composition (left/body/right)
- Provide fallback rendering for unknown predicates using a default partial

## File map (where things live in this repo) 📂
- Config: `config/wiki.yaml` (existing)
- Templates: `src/template/wiki/` (or `src/template/docs`)
- Generator: `src/wiki/generator.py` (existing, needs implementation)
- SPARQL queries: `sparql/wiki/*.sparql` (existing)
- TTL sources: `ttl/`
- Tests: `tests/test_wiki_generation.py` (create/update)

## Quick checklist (prioritized) 🔎
1. Implement `generate_all()` and entity page generation (high impact)
2. Add generic entity renderer and a handful of templates
3. Add caching + incremental builds
4. Add search index generation and client-side search
5. Add tests and CI coverage


> Notes: keep pages small and focused. Prefer precomputation and caching for heavy joins. If the dataset grows or remote endpoints become authoritative, adopt a hybrid dynamic/static approach where core pages are static and large lists are served on-demand.

If you'd like, I can open a PR implementing the generator improvements and a minimal template set that covers entity pages, lists, and the search index. 💡