# Figures — Full Standalone Summary 🔧

## Overview 🔍
**Core idea:** This folder contains the generated visual evidence supporting the project's claims: motif inventory, mapping coverage to ONNX, motif frequency across model corpora, fingerprint co-occurrence, fusion candidates, redundancy analyses, and implementation/readiness metrics.

---

## Chart Types & Key Insights 📊
- **Inventory & Coverage:** `motif_inventory.*`, `motif-to-onnx_operator_mapping.*`, and `onnx_mapping_coverage.*` show which motifs have canonical ONNX mappings and which remain unmapped.
- **Usage & Frequency:** `motif_frequency_across_models.*` and `model_motif_coverage.*` quantify motif prevalence across datasets and models.
- **Fingerprint & Redundancy:** `fingerprint_co-occurrence.*`, `fingerprint_coverage.*`, and `motif_redundancy.*` reveal overlapping motif definitions and candidate merges.
- **Fusion Candidates:** `fusion_candidates_*.html` highlights promising operator pairs (e.g., attention + linear) for fusion to improve runtime efficiency.
- **Readiness & Runtime:** `implementation_readiness.*`, `runtime_requirements.*`, and `runtime_capability_usage.*` provide a view of practical deployment constraints.

---

## Generation & Provenance 🔁
- **How generated:** Charts are produced by `src/charting/chart_generator.py` using `charts/*.yaml` configurations which contain `query:` entries pointing to `sparql/*.sparql` files.
- **Formats:** Each chart has a Vega-Lite spec (`*.json`), a standalone HTML preview (`*.html`), and a raster (`*.png`) for inclusion in papers.

---

## Conclusions & Usage 🎯
- Visuals provide reproducible, auditable evidence for claims in the other papers (motif prevalence, gaps, and fusion strategies).
- They are the primary interface for reviewers to inspect dataset-driven claims; maintain the `charts/*.yaml` and `sparql/*.sparql` to update figures reproducibly.

---

## Where to look in the repo 📁
- **Chart generator:** `src/charting/chart_generator.py`
- **Config:** repository-level `charts/` YAML files (e.g., `charts/motif_inventory.yaml`)
- **SPARQL:** `sparql/charts/` for queries that source the visualizations.

> **Note:** This README is intended to be a standalone, complete description of what each visualization family represents, how they were produced, and how to interpret them.