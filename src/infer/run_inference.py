#!/usr/bin/env python3
"""Run SPARQL CONSTRUCT inference queries and write TTL output.

Usage:
  src/infer/run_inference.py --sparql-dir sparql/infer --out ttl/infer
"""
import argparse
import logging
from pathlib import Path
from datetime import datetime
import rdflib
import sys

from src.rdf_manager import RDFManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def run_inference(sparql_dir: Path, out_dir: Path, ttl_dir: Path):
    rdf = RDFManager(ttl_dir)
    sparql_dir = Path(sparql_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    queries = sorted(sparql_dir.glob("*.sparql"))
    if not queries:
        log.warning("No SPARQL queries found in %s", sparql_dir)
        return 0

    for qf in queries:
        qname = qf.stem
        log.info("Running inference query: %s", qf.name)
        qtext = qf.read_text()
        try:
            res = rdf.execute_query(qtext)
            # For CONSTRUCT queries rdflib returns a Result whose .graph is a Graph
            out_graph = None
            if hasattr(res, "graph") and isinstance(res.graph, rdflib.Graph):
                out_graph = res.graph
            else:
                # Fallback: build a graph from triple iterator
                g = rdflib.Graph()
                for t in res:
                    # t is a tuple (s,p,o)
                    try:
                        g.add(t)
                    except Exception:
                        # some query backends return rdflib.term objects; still add
                        try:
                            g.add((t[0], t[1], t[2]))
                        except Exception:
                            pass
                out_graph = g

            # Bind known namespaces from main graph
            for p, ns in rdf.namespaces.items():
                try:
                    out_graph.bind(p, ns)
                except Exception:
                    pass

            # Add provenance comment as TTL prefix (rdflib doesn't support comments directly)
            out_path = out_dir / f"{qname}.ttl"
            serialized = out_graph.serialize(format="turtle")
            header = f"# Inferred triples from query: {qf.name}\n# generated: {datetime.utcnow().isoformat()}Z\n# source ttl: {ttl_dir}\n\n"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(header)
                f.write(serialized)

            log.info("Wrote %s (%d triples)", out_path, len(out_graph))
        except Exception as e:
            log.error("Failed to execute %s: %s", qf.name, e)
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sparql-dir", type=Path, default=Path("sparql/infer"))
    parser.add_argument("--out", type=Path, default=Path("ttl/infer"))
    parser.add_argument("--ttl-dir", type=Path, default=Path("ttl"), help="Directory of source TTL files to load into graph")
    args = parser.parse_args()

    return run_inference(args.sparql_dir, args.out, args.ttl_dir)


if __name__ == "__main__":
    sys.exit(main())
