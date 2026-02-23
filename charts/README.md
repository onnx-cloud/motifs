# Charts

This directory contains Vega-Lite specifications for visualizing the motif algebra and basis structure.
## Charts

| File | Description |
|------|-------------|
| `basis_primitives.yaml` | The 16-element minimal basis B* |
| `derivation_tree.yaml` | How taxonomy motifs derive from primitives |
| `fingerprint_coverage.yaml` | Tag coverage across primitives |
| `motifs_by_category.yaml` | Motifs by category (A-H) |
| `signature_patterns.yaml` | I→O signature distribution |
| `algebraic_structure.yaml` | Monoid/semiring relationships |
| `redundancy_graph.yaml` | Redundant motifs and their derivations |
| `complexity_heatmap.yaml` | Derivation complexity by category |
| `onnx_mapping_summary.yaml` | Distribution of skos:exactMatch to ONNX ops |
| `runtime_usage.yaml` | Distribution of onnx:requiresRuntime capabilities |
| `fingerprint_clusters.yaml` | Heatmap of tag co-occurrence |
| `implementation_readiness.yaml` | Ratio of implemented vs. spec-only motifs |
| `constraint_summary.yaml` | Operational constraints (determinism, etc.) |
| `future_extensions.yaml` | Proposed B+ primitives (Delay, Race, Ref) |
## Viewing

Open any `.vl.json` file in the [Vega Editor](https://vega.github.io/editor/) or render with:

**Interactive index:** open `charts/index.html` in a browser to browse and render specs in `charts/` (requires `.vl.json` files; if missing, run `make charts`).

When you run `make charts`, the generator writes JSON and HTML outputs to `papers/figures/`. If `vl2png` (from `vega-lite-cli`) is available on your PATH, it will also generate PNG exports alongside the JSON/HTML files.

**Generated output index:** an index of generated artifacts is available at `papers/figures/index.html`. Open that file in a browser to view the exported charts (JSON or HTML) that were produced by `make charts`.


```bash
# Install vega-lite-cli
npm install -g vega-lite vega-cli

# Render to SVG
vl2svg charts/basis_primitives.vl.json > papers/figures/basis_primitives.svg

# Render to PNG
vl2png charts/fingerprint_coverage.vl.json > papers/figures/fingerprint_coverage.png
```
## Integration

These charts can be embedded in the paper via:
```latex
\includegraphics[width=\columnwidth]{figures/basis_primitives.pdf}
```
