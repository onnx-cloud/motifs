# Copilot Instructions for Motif Models
## Big Picture 🏗️
1. **Ontology** (`ttl/motifs/*.ttl`) — RDFS+SKOS definitions. Source of truth for motif taxonomy.
2. **Theory** (`FIXED.md`) — Formal proof that 16 primitives ($B^*$) generate 100+ motifs; 3 experimental primitives ($B^+_{19}$).
3. **Visualizations** (`charts/*.yaml` → `sparql/*.sparql` → `papers/figures/`) — YAML configs drive SPARQL queries against TTL to produce Vega-Lite charts.

Data flows: `ttl/*.ttl` ← queried by → `sparql/*.sparql` ← referenced by → `charts/*.yaml` → rendered by `src/charting/chart_generator.py` → `papers/figures/*.json`.
## Quick Commands 🛠️
```bash
make venv && make install-charting  # Setup (once)
make charts      # Generate Vega-Lite figures from TTL+SPARQL
make pdf         # Compile LaTeX paper (requires pdflatex/biber)
make fusion      # Generate .fuse snippets from ontology
pytest tests/    # Run tests
```
## Key Patterns 🧭
### Adding a new motif
1. Define in `ttl/motifs/<category>.ttl` using existing patterns (see `linear.ttl`)
2. Add ONNX mapping in `ttl/motifs/onnx_mappings.ttl` using `skos:exactMatch` + optional `onnx:requiresRuntime`
3. If primitive, update `FIXED.md` Appendix A table and `sparql/basis_primitives.sparql`
### Adding a new chart
1. Create `charts/<name>.yaml` with `query:` pointing to SPARQL file
2. Create `sparql/<name>.sparql` (use VALUES for static data or query TTL)
3. Run `make charts` to generate output in `papers/figures/`
### TTL conventions
- Prefix: `motif:` for motifs, `onnx:` for operators, `skos:` for mappings
- Every motif needs: `a motif:Motif`, `skos:prefLabel`, `motif:hasSignature`, `motif:hasCategory`
- ONNX alignment: `skos:exactMatch onnx:<Op>` for direct mapping, `onnx:requiresRuntime` for custom ops
## File Reference 📁
| Path | Purpose |
|------|---------|
| `FIXED.md` | Formal algebra proof + B* basis definition |
| `ttl/motifs/index.ttl` | Core ontology schema (classes, properties, fingerprints) |
| `ttl/motifs/onnx_mappings.ttl` | Motif→ONNX operator mappings |
| `src/rdf_manager.py` | RDF graph loading + SPARQL execution |
| `src/charting/chart_generator.py` | YAML→SPARQL→Vega-Lite pipeline |
| `sparql/basis_primitives.sparql` | Static table of 16 B* primitives |
| `./tmp/` | Working files - don't use `/tmp/` |
## Naming Conventions
- Motif identifiers: PascalCase in TTL (`motif:ForkJoin`), match `README.md` taxonomy names
- Files: lowercase with underscores (`basis_primitives.yaml`)
- Commit messages: reference motif + section (e.g., `Add Delay primitive (FIXED.md: Appendix C)`)
## What NOT to assume ❌
- The 16-primitive basis in `FIXED.md` is canonical—don't add primitives without updating all tables
- `sparql/*.sparql` files may contain inline VALUES tables (not just queries)—check before assuming live TTL queries
