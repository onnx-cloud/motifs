# Motif Models

This repository is the research artifact for a series of academic papers on **computation‑graph motifs**. It provides a comprehensive taxonomy, formal ontology, 
implementations, and experimental data that support the claims in our publications.

The motif catalog and accompanying tools are intended for **researchers** who are exploring
optimizations, verification, or theoretical properties of graph‑based models.  You will
find:

* a formal RDF/TTL ontology of 100 + motifs, with ONNX/Python reference
  implementations
* tools to visualise motif coverage, generate fusion snippets, and validate graphs
* experiments, proofs, and notebooks that underpin the papers listed below


## Peer‑reviewed artifacts & PDFs

Our work is documented in a set of papers; the PDF versions are built with `make pdf` and
appear in the repository root.  Each PDF includes a self‑contained summary of the
motifs, motivations, and experimental results.

| Paper | Description | PDF |
|-------|-------------|-----|
| Motif Models | Taxonomy of 100+ computation graph motifs, signatures, ontology, and
  case‑studies. | [motif-models.pdf](./motif-models.pdf) |
| Compiled Cognition | How motifs inform compiler transformations and fission/fusion rules. | [compiled-cognition.pdf](./compiled-cognition.pdf) |
| Fused Fabric | Analysis of fusion opportunities, runtime patterns, and hardware
  mapping. | [fused-fabric.pdf](./fused-fabric.pdf) |
| Cognitive Closure | Higher‑order motif composition and theoretical limits of expressivity. | [cognitive-closure.pdf](./cognitive-closure.pdf) |
| Typed Reality | (Early draft) formal type system for graph motifs and LLM generation. | [typed-reality.pdf](./typed-reality.pdf) |

> **Tip:** run `make pdf` to regenerate these files after editing the LaTeX sources in the
> `papers/` directory.



## Algorithmic Graph Motifs

This catalog enumerates common computation graph motifs grouped by functional category. Each motif lists a compact signature (I→O), a small set of fingerprint/analysis tags (T, C, S, R, M, D), and a short note.

## Generated artifacts

- **Micro-site** (default): `$(SITE_OUT)` → `./tmp/site`
- **Fuse snippets** (default): `$(FUSE_OUT)` → `./tmp/fuse`

You can override these when running Make targets, e.g. `make site SITE_OUT=./build/site` or `make fusion FUSE_OUT=./build/fuse`.

## Quick start ✅

1. Create and activate the virtual environment: `make venv && source $(VENV)/bin/activate`
2. Install charting dependencies: `make install-charting`
3. Generate charts: `make charts` (outputs `papers/figures/` — JSON, HTML, PNG)
4. Build the micro-site: `make site` (runs charts, fusion, opset, then site)
5. Generate .fuse snippets only: `make fusion`

> Tip: run `make shacl` to validate TTL files (requires `pyshacl`).

## Common make targets 🔧

- `make charts` — Generate Vega-Lite charts (`papers/figures/`)
- `make site` — Build the documentation micro-site (default `$(SITE_OUT)`)
- `make fusion` — Generate `.fuse` snippets (default `$(FUSE_OUT)`)
- `make shacl` — Validate TTL against SHACL shapes
- `make clean` — Remove generated artifacts

## Tests & CI 🧪

Run the unit tests locally with:

```bash
pytest -q
```

The CI workflow runs `make charts` and `make fusion` as part of its verification. We also include experimental artifacts and formal proofs with the repository:

- Jupyter demo: `notebooks/lof_training.ipynb` demonstrates LOF training with typed projection.
- Scripts: `scripts/run_lof_experiment.py` reproduces the experiment from the command line.
- Formal artifacts: `proofs/typed_projection.v` contains Coq proof skeletons for projection properties used in constrained optimization.

These are exercised by lightweight tests (skipped when dependencies like NumPy are absent) so CI remains robust across environments.

## Troubleshooting 💡

- SHACL validation errors often indicate TTL formatting or missing predicates; run `scripts/run_shacl.py` for more detailed diagnostics.
- Template warnings like "Section end tag mismatch" are rendering issues — check `src/template/` and motif TTL fields used by the templates.
- If charts or PNGs are missing, ensure `vl-convert-python` is installed (`make install-charting`) and rerun `make charts`.

