# RDFS Export Plan — Strict ONNX Node/Graph Model

## Goals 🎯
- Every node in the graph is exported as a well-typed `onnx:Node` with required metadata.
- Every node must declare: `onnx:domain` (IRI), at least one `onnx:hasInput` and one `onnx:hasOutput`.
- Each input/output must be an explicit blank node or reified resource of type `onnx:OperatorInput`/`onnx:OperatorOutput` and include required properties (`onnx:name`, `onnx:required` boolean, optional `onnx:position` integer, optional `onnx:type`).
- Enforce constraints via SHACL shapes and automated tests.

## Example export (Turtle) ✍️

```turtle
@prefix motif: <http://example.org/motif/> .
@prefix onnx: <http://example.org/onnx/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

motif:GPT a onnx:Node ;
  onnx:domain onnx:ai.onnx ;
  onnx:hasInput [ a onnx:OperatorInput ; onnx:name "tokens" ; onnx:required "true"^^xsd:boolean ; onnx:position 0 ] ;
  onnx:hasOutput [ a onnx:OperatorOutput ; onnx:name "tokens" ; onnx:position 0 ] .
```

Note: prefer typed IRIs for `onnx:domain` where possible (e.g., `onnx:ai.onnx`).

## Vocabulary & Predicates 🔧
- `onnx:Node` — class for operators/nodes exposed by models
- `onnx:domain` — IRI of operator domain (required)
- `onnx:hasInput` / `onnx:hasOutput` — links to `onnx:OperatorInput` / `onnx:OperatorOutput`
- `onnx:OperatorInput` / `onnx:OperatorOutput` — must have `onnx:name` (xsd:string) and `onnx:required` (xsd:boolean, default false if omitted only when justified) and optional `onnx:position` (xsd:integer)
- `onnx:requiresRuntime` / `onnx:hasAttribute` — for runtime flags or operator attributes (when applicable)

## Strictness rules & SHACL plan 🛡️
Create SHACL shapes to enforce:
1. `NodeShape` (target class `onnx:Node`) — must have
   - exactly one `onnx:domain` (IRI)
   - min 1 `onnx:hasInput`
   - min 1 `onnx:hasOutput`
2. `OperatorInputShape` / `OperatorOutputShape` — for `onnx:OperatorInput`/`onnx:OperatorOutput`:
   - `onnx:name` required, xsd:string
   - `onnx:required` required, xsd:boolean
   - `onnx:position` optional, xsd:integer (when ordering matters)
3. `DomainIRI` — `onnx:domain` must be an IRI from allowed set or follow IRI pattern (e.g., `^http`)

Implement SHACL tests and fail CI if violations are detected. Provide a `make shacl` target (or extend the existing one) to validate the generated TTL.

## Export rules & algorithm 🔄
1. Source: extract nodes and graphs from model sources (existing TTL mapping files, ONNX operator list, or model parsing scripts).
2. Normalization:
   - Normalize operator names to motif naming conventions (PascalCase)
   - Normalize domain to canonical IRI (map common aliases)
3. For each operator/node:
   - Create a `motif:<Name>` IRI (or use existing motif id if known)
   - Add `a onnx:Node` and `onnx:domain` triple
   - For each input and output, create a blank node with explicit `a onnx:OperatorInput/Output`, `onnx:name` (string), `onnx:required` (boolean), and `onnx:position` (int if ordering present)
   - Add `onnx:hasInput` / `onnx:hasOutput` pointing to those resources
4. Preserve and export operator attributes when they are semantically relevant (e.g., `onnx:requiresRuntime`, attribute default values). If an attribute is optional but has an explicit default in the opset, export it with `onnx:hasAttribute` and document the provenance.

## Files & Implementation tasks 🧭
- Add new documentation: `RDFS.md` (this file) — planning & acceptance criteria ✅
- Add exporter module: `src/onnx/rdfs_exporter.py` (or extend `src/onnx/__init__.py`) to produce TTL in `ttl/onnx_nodes.ttl`
- Add SHACL shapes: `sparql/shapes/onnx_node_shapes.ttl` or `shacl/onnx-node-shapes.ttl`
- Add unit tests: `tests/test_rdfs_export.py` and SHACL tests in `tests/test_shacl_nodes.py`
- Add CI step: extend `.github/workflows` or `Makefile` to run `make shacl` after generation

## Tests & Acceptance Criteria ✅
- Every exported `onnx:Node` passes SHACL validation
- Example model exports (small set: GPT-like layers, Conv, MatMul, Reshape) are generated and asserted against expected TTL fragments
- Round-trip compatibility: mapping lookup (motif → onnx:Op) still works after strict export

## Notes & Edge Cases ⚠️
- Some ops have variable numbers of inputs/outputs — use multiple `onnx:hasInput` triples with `onnx:position` to preserve order.
- If `required` cannot be known, explicitly set `onnx:required "false"^^xsd:boolean` only when semantically correct; otherwise prefer to enrich source to provide the information.
- For graphs (subgraphs), export a `motif:<GraphName> a onnx:Graph` with `onnx:hasNode` linking to constituent `onnx:Node` resources, plus `onnx:hasInput`/`onnx:hasOutput` for graph-level I/O.

## Next steps & timeline ⏱️
1. Implement `src/onnx/rdfs_exporter.py` (1-2 days).
2. Write SHACL shapes and tests (1 day) and wire into CI.
3. Run on whole opset and iterate on vocabulary/shape changes (1 day).


If desired, I can create a skeleton `src/onnx/rdfs_exporter.py` and the SHACL shape starter files and tests. 🔧
