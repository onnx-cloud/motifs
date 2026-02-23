# 05 — Fused Fabric: Composing Types and Graphs

Typed Reality and Compiled Cognition are independent ideas. Fused Fabric is their integration: a framework where graphs and type systems compose deterministically.

At the core is a compatibility predicate: given a computation graph and a semantic grounding, is the graph a valid implementation of that semantics? The compiler checks this automatically. If a graph violates type constraints or semantic invariants, compilation fails with a clear explanation.

Implementation uses RDF and SPARQL: graphs and types are represented as logical triples, composition rules are SPARQL queries, and provenance is recorded explicitly. This choice prioritizes auditability and clarity over performance.