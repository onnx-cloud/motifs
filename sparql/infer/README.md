This folder contains SPARQL CONSTRUCT queries to infer higher-level composition patterns from motif data.

Usage:
- Run each CONSTRUCT query against the combined TTL graph (ttl/). The output graph contains inferred triples in the `https://ns.onnx.cloud/infer#` namespace.

Files:
- `iterative.sparql` — infer `infer:Iterative` instances when `motif:Loop`, `motif:Scan`, etc. appear
- `conditional.sparql` — infer `infer:Conditional` instances when `motif:If`, `motif:Switch`, etc. appear
- `sequential.sparql` — infer `infer:Sequential` when one composed motif uses another (heuristic)
- `parallel.sparql` — infer `infer:Parallel` when two composed motifs co-occur and do not use each other

Notes & heuristics:
- These queries are conservative heuristics (based on `motif:composedOf` and `motif:usesMotif`). They aim to provide useful diagnostic inferences rather than formal proof of dataflow ordering.
- After generating inferred triples, load them back into your graph and re-run charts or SPARQL analyses.

Example run (with a SPARQL command-line tool or your RDF manager):

  sparql --data ttl/*.ttl --query sparql/infer/iterative.sparql --results ttl > tmp/inferred_iterative.ttl
  # then merge inferred triples into your graph

