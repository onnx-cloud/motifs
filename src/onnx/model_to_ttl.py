"""Export an ONNX model (graph + nodes) to Turtle (TTL) with strict onnx:Node/OperatorInput/OperatorOutput resources.

Writes to `ttl/models/<modelname>.ttl` by default.

This module follows the conventions from `RDFS.md`.
"""
from datetime import date
import os
import sys

OUT_DIR = os.path.join("ttl", "models")
PREFIXES = """@prefix onnx: <https://ns.onnx.cloud/onnx#> .
@prefix motif: <https://ns.onnx.cloud/motif#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

"""


def safe_literal(s):
    return str(s).replace('"', '\\"')


def export_model_to_ttl(model_path, out_path=None):
    try:
        import onnx
    except Exception:
        raise RuntimeError("ONNX not installed; install with `pip install onnx`")

    model = onnx.load(model_path)
    model_name = os.path.splitext(os.path.basename(model_path))[0]
    if out_path is None:
        os.makedirs(OUT_DIR, exist_ok=True)
        out_path = os.path.join(OUT_DIR, f"{model_name}.ttl")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# Generated from {model_path} on {date.today().isoformat()}\n")
        f.write(PREFIXES)

        # Graph resource
        graph_name = getattr(model.graph, "name", model_name)
        graph_uri = f"motif:{graph_name}"
        f.write(f"{graph_uri} a onnx:Graph ;\n")

        # Graph-level inputs
        for vi in model.graph.input:
            f.write(
                f"  onnx:hasInput [ a onnx:OperatorInput ; onnx:name \"{safe_literal(vi.name)}\" ; ] ;\n"
            )

        # Graph-level outputs
        for vi in model.graph.output:
            f.write(
                f"  onnx:hasOutput [ a onnx:OperatorOutput ; onnx:name \"{safe_literal(vi.name)}\" ; ] ;\n"
            )

        # Nodes (each node becomes a motif resource under the model namespace)
        for idx, node in enumerate(model.graph.node):
            # Create a unique node id
            node_id = f"{graph_name}_node_{idx}_{safe_literal(node.op_type)}"
            node_uri = f"motif:{node_id}"
            domain = node.domain if getattr(node, "domain", None) else "ai.onnx"
            domain_iri = f"https://ns.onnx.cloud/onnx/domain/{domain}"

            f.write(f"  onnx:hasNode {node_uri} ;\n")

            # write node block
            f.write(f"\n{node_uri} a onnx:Node ;\n")
            f.write(f"  onnx:domain <{domain_iri}> ;\n")

            # Inputs
            for pos, name in enumerate(node.input):
                if name:
                    f.write(
                        f"  onnx:hasInput [ a onnx:OperatorInput ; onnx:name \"{safe_literal(name)}\" ; onnx:required \"true\"^^xsd:boolean ; onnx:position {pos} ] ;\n"
                    )

            # Outputs
            for pos, name in enumerate(node.output):
                if name:
                    f.write(
                        f"  onnx:hasOutput [ a onnx:OperatorOutput ; onnx:name \"{safe_literal(name)}\" ; onnx:position {pos} ] ;\n"
                    )

            # label with op_type for readability
            f.write(f"  rdfs:label \"{safe_literal(node.op_type)}\" .\n\n")

    return out_path


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: model_to_ttl.py /path/to/model.onnx [out.ttl]")
        sys.exit(2)
    model_path = argv[0]
    out = argv[1] if len(argv) > 1 else None
    path = export_model_to_ttl(model_path, out)
    print(f"Wrote TTL to {path}")


if __name__ == "__main__":
    main()
