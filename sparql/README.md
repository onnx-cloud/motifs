# SPARQL Queries for Motif Models Ontology

This directory contains SPARQL queries to analyze and explore the RDF/TTL ontology defined in `../ttl/`.
## Queries
### Basic Exploration
- **list_all_motifs.sparql** — Lists all motifs with their labels, signatures, and categories
- **categories_hierarchy.sparql** — Shows category definitions and hierarchy from SKOS scheme
### Analysis
- **motifs_by_category.sparql** — Groups motifs by category with counts
- **motif_signatures.sparql** — Analyzes signature patterns across all motifs
- **motif_fingerprints.sparql** — Shows all fingerprints and which motifs use them
- **motif_semantics.sparql** — Identifies semantic descriptions and usage frequency
- **signature_patterns.sparql** — Identifies N-to-1, 1-to-N, and other I/O patterns
- **domains_motif_usage.sparql** — Count of domain applications that reference each motif
- **motif_usage_by_domain.sparql** — Counts of motif occurrences per domain (domain × motif)
- **usecases_per_domain.sparql** — Number of technical use cases per application domain
### Quality Checks
- **motif_completeness.sparql** — Checks which motifs have all required properties (signature, category, semantics, etc.)
- **missing_properties.sparql** — Identifies motifs missing key properties
- **fingerprint_cooccurrence.sparql** — Finds motifs with multiple fingerprints (composition indicators)
### Metrics
- **ontology_statistics.sparql** — High-level statistics: total motifs, categories, fingerprints, semantics
### Documentation
- **motifs_with_examples.sparql** — Shows motifs that have example implementations defined
### Misc / Static tables
- **basis_primitives.sparql** — Static table of minimal basis primitives
- **complexity_heatmap.sparql** — Static complexity matrix for primitives by category
- **algebraic_structure.sparql** — Algebraic property table
- **redundancy_graph.sparql** — Derived motif → B* primitive mapping
- **derivation_tree.sparql** — Derivation primitive list (edge sources)
## Usage

To run these queries against the TTL files, use a SPARQL processor such as:

- **Apache Jena** (fuseki server or command-line tools)
- **RDF4J** (Workbench or console)
- **Virtuoso** (open-source RDF database)
### Example with Apache Jena CLI:

```bash
# Load all TTL files and run a query
sparql --data ../ttl/index.ttl \
        --data ../ttl/linear.ttl \
        --data ../ttl/topology.ttl \
        --data ../ttl/control.ttl \
        --query list_all_motifs.sparql
```
### Example with SPARQL endpoint:

```bash
# If running a local SPARQL endpoint at http://localhost:3030/motifs
curl -X POST "http://localhost:3030/motifs/query" \
  --data-urlencode query@list_all_motifs.sparql
```
## Integration with Python/Notebooks

Use **rdflib** to query locally:

```python
from rdflib import Graph

g = Graph()
for ttl_file in ['index.ttl', 'linear.ttl', 'topology.ttl', ...]:
    g.parse(f'../ttl/{ttl_file}', format='turtle')

with open('list_all_motifs.sparql') as f:
    query = f.read()

results = g.query(query)
for row in results:
    print(row)
```
## Notes

- All queries assume prefixes defined in `../ttl/index.ttl`
- Query results are more useful when run against the **complete** set of TTL files in `../ttl/`
- Use `ontology_statistics.sparql` first to verify data has been loaded correctly
