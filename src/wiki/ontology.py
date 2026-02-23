"""Ontology objects and light-weight caching for the wiki renderer."""
from __future__ import annotations

from typing import List
from .rdf import RDFManager


class Ontology:
    """Wraps an RDFManager and exposes convenient accessors used by templates.

    This class caches results and provides a `refresh` method to invalidate
    caches when the underlying RDF dataset changes.
    """

    def __init__(self, rdf: RDFManager):
        self.rdf = rdf
        self._cache = {}

    def get_motifs(self) -> List[str]:
        """Return a list of motif identifiers (strings)."""
        if "motifs" not in self._cache:
            # A minimal implementation: use a SPARQL query in a full impl.
            self._cache["motifs"] = []
        return self._cache["motifs"]

    def get_categories(self) -> List[str]:
        """Return a list of categories."""
        if "categories" not in self._cache:
            self._cache["categories"] = []
        return self._cache["categories"]

    def refresh(self) -> None:
        """Invalidate caches and refresh data from RDFManager."""
        self._cache.clear()
        self.rdf.load()
