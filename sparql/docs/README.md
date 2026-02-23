# SPARQL Queries for Documentation Generator

This directory contains SPARQL queries used by the documentation generator (`src/wiki/generator.py`).
## Query Files

| File | Purpose |
|------|---------|
| `ontology_stats.sparql` | Overall ontology statistics (counts) |
| `category_summary.sparql` | Category counts and descriptions |
| `list_motifs.sparql` | All motifs with basic metadata |
| `motif_detail.sparql` | Single motif full details (parameterized) |
| `motif_onnx_mapping.sparql` | ONNX mappings for a motif |
| `motif_usage.sparql` | Use cases employing a motif |
| `onnx_mappings.sparql` | All motif→ONNX operator mappings |
| `mapping_coverage.sparql` | Mapping coverage statistics |
| `list_domains.sparql` | Industry domains |
| `domain_applications.sparql` | Applications per domain |
| `list_use_cases.sparql` | All use cases |
| `use_case_domains.sparql` | Use cases by application domain |
| `list_categories.sparql` | All categories with definitions |
## Usage

Queries are referenced from `config/wiki.yaml` and executed against the TTL ontology files.
