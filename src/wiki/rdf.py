"""RDFManager: simple API stub for loading TTL files and executing SPARQL.

This is a lightweight, testable implementation suitable for the initial API and unit tests.
"""
from __future__ import annotations

from typing import Iterable, List, Optional
import hashlib
import os

try:
    import rdflib
except Exception:  # rdflib may not be installed in minimal test env
    rdflib = None


class RDFManager:
    """Load TTL/RDF sources into a single graph and execute SPARQL queries.

    The implementation here is intentionally small: it provides a stable API and
    simple in-memory behaviors for tests. A fuller implementation will use
    rdflib.Graph for parsing and SPARQL execution.
    """

    def __init__(self, ttl_paths: Optional[Iterable[str]] = None):
        self.ttl_paths = list(ttl_paths) if ttl_paths else []
        self.graph = None
        self._loaded = False

    def load(self) -> None:
        """Load TTL files into an internal graph. Safe to call multiple times."""
        if rdflib is not None:
            g = rdflib.Graph()
            for p in self.ttl_paths:
                if os.path.exists(p):
                    g.parse(p, format="ttl")
            self.graph = g
        else:
            # Minimal placeholder graph
            self.graph = {}
        self._loaded = True

    def query(self, sparql: str) -> List[dict]:
        """Execute a SPARQL query against the loaded graph.

        Returns a list of dicts (rows). This stub returns an empty list unless
        rdflib is available and the graph is loaded.
        """
        if not self._loaded:
            self.load()
        if rdflib is not None and self.graph is not None:
            qres = self.graph.query(sparql)
            results = []
            for row in qres:
                # Convert row to dict if possible
                try:
                    rowd = {str(k): str(v) for k, v in row.asdict().items()}
                except Exception:
                    rowd = {str(i): str(v) for i, v in enumerate(row)}
                results.append(rowd)
            return results
        return []

    def fingerprint(self) -> str:
        """Return a stable fingerprint of the current dataset (paths + mtimes).

        Uses file mtimes and sizes to create a deterministic hash for caching.
        """
        items = []
        for p in sorted(self.ttl_paths):
            try:
                st = os.stat(p)
                items.append(f"{p}:{st.st_mtime_ns}:{st.st_size}")
            except FileNotFoundError:
                items.append(f"{p}:missing")
        joined = "|".join(items)
        return hashlib.sha1(joined.encode("utf-8")).hexdigest()
