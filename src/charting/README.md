# Chart Generation & Reporting Toolkit

This directory contains tools to generate data-driven Vega-Lite charts from SPARQL queries on the TTL ontology.
## Architecture

```
charts/                        # YAML chart specifications (root level)
├── motifs_by_category.yaml
├── signature_patterns.yaml
├── fingerprint_coverage.yaml
├── completeness.yaml
├── ontology_stats.yaml
└── motif_inventory.yaml

src/charting/
├── chart_generator.py          # Core: SPARQL → Vega-Lite conversion
├── report_generator.py         # HTML/Markdown report composition
├── config.py                   # Configuration and path utilities
└── ...other modules...
```
## Quick Start
### 1. Install Dependencies (via Makefile)

```bash
make install-charting
```
### 2. Generate Charts

```bash
# Generate all charts (uses venv)
make charts

# Or manually with venv
venv/bin/python src/charting/chart_generator.py --config charts/
```
### 3. Output Locations

Charts are written to `papers/figures/`:
- `*.json` — Vega-Lite JSON specifications (for embedding)
- `*.html` — Standalone HTML viewers
## Creating New Charts
### Step 1: Write or Select a SPARQL Query

Queries are in `sparql/*.sparql`. For example:

```sparql
# sparql/my_query.sparql
SELECT ?motif ?category (COUNT(?fp) AS ?fingerprints)
WHERE {
  ?motif a motif:Motif ;
    motif:hasCategory ?category ;
    motif:hasFingerprint ?fp .
}
GROUP BY ?motif ?category
```
### Step 2: Create a YAML Config

```yaml
# src/charting/configs/my_chart.yaml
title: My Motif Analysis
description: |
  This chart shows fingerprint distribution
  across motif categories.

query: ./sparql/charts/my_query.sparql

# Optional data transformation
transform:
  rename:
    fingerprints: count
  keep:
    - motif
    - category
    - count

# Vega-Lite specification
vega:
  width: 800
  height: 400
  mark: bar
  encoding:
    x:
      field: category
      type: nominal
    y:
      field: count
      type: quantitative
    color:
      field: category
      type: nominal
```
### Step 3: Generate

```bash
python src/charting/chart_generator.py \
    --config src/charting/configs/my_chart.yaml \
    --output-dir papers/figures/
```
## YAML Config Reference
### Top-level Keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `title` | string | Yes | Chart title |
| `description` | string | No | Longer description |
| `query` | string or dict | Yes | SPARQL query file or inline query |
| `transform` | dict | No | Data transformations |
| `vega` | dict | Yes | Vega-Lite specification (will be merged with data) |
### Query Specification

The `query` field supports multiple formats:

```yaml
# Relative path to sparql/ directory (filename only)
query: motifs_by_category.sparql

# Explicit relative path from project root
query: ./sparql/charts/motifs_by_category.sparql

# Inline SPARQL (string starting with PREFIX)
query: |
  PREFIX motif: <https://ns.onnx.cloud/motif#>
  SELECT ?label WHERE { ... }
```
### Transform Specification

Transforms are applied in order:

```yaml
transform:
  # Rename fields
  rename:
    oldName: newName
    categoryLabel: category
  
  # Keep only these fields
  keep:
    - category
    - count
  
  # Compute new fields
  compute:
    label: "Motion: ${motif}"
```
### Vega-Lite Specification

Use standard Vega-Lite JSON, but specified as YAML:

```yaml
vega:
  width: 600
  height: 400
  mark: bar
  encoding:
    x:
      field: category
      type: nominal
      axis:
        labelAngle: -45
    y:
      field: count
      type: quantitative
    color:
      field: category
      type: nominal
      scale:
        scheme: category10
    tooltip:
      - field: category
      - field: count
```
## Integration with Paper Generation
### Embedding Figures in LaTeX

Generated JSON specs can be embedded using `vega-lite-tex` or similar:

```tex
\begin{figure}
  \includegraphics[width=0.8\textwidth]{papers/figures/motifs_by_category.png}
  \caption{Distribution of motifs across functional categories}
\end{figure}
```
### Embedding in HTML Reports

Use `ReportGenerator` to create HTML reports with embedded charts:

```python
from src.charting.report_generator import ReportGenerator

gen = ReportGenerator()
html = gen.generate_html_report(
    "Motif Analysis Report",
    sections=[
        {
            "title": "Distribution",
            "description": "High-level motif statistics",
            "figures": ["motifs_by_category", "signature_patterns"]
        },
        {
            "title": "Coverage",
            "description": "Completeness metrics",
            "figures": ["completeness", "fingerprint_coverage"]
        }
    ]
)

with open("papers/motif_report.html", "w") as f:
    f.write(html)
```
## Advanced Usage
### Custom Data Transformations

Add computed fields in transforms:

```yaml
transform:
  compute:
    percentage: "${count} / 100 * 100"
    label: "Category: ${category}"
```
### Filtering Results

Use SPARQL `FILTER` in the query itself for complex filtering.
### Exporting to Different Formats

The `chart_generator.py` CLI supports:
- `json` — Vega-Lite JSON specs
- `html` — Standalone viewers
- `data` — CSV/JSON query results

Extend `ChartGenerator.write_output()` to add SVG, PNG export.
## Troubleshooting
### "Query returned 0 rows"

1. Verify TTL files are loaded: run `ontology_statistics.sparql`
2. Check SPARQL syntax: test query directly with `sparql` command-line tool
3. Verify field names match your ontology
### "field not found in Vega spec"

Ensure your `transform.keep` or computed fields match your `vega.encoding` field names.
### Chart displays but data looks wrong

1. Check transformed data: run with `--output-formats json html data`
2. Review `*.data.json` to see what the chart is receiving
3. Verify SPARQL query is correct
## References

- [SPARQL Query Language](https://www.w3.org/TR/sparql11-query/)
- [Vega-Lite Grammar](https://vega.github.io/vega-lite/)
- [RDFlib Documentation](https://rdflib.readthedocs.io/)
- [YAML Spec](https://yaml.org/)
