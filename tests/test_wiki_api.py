"""Tests for wiki API stubs: RDFManager, Ontology, PageRenderer, WikiGenerator."""
from __future__ import annotations

import os
from src.wiki.rdf import RDFManager
from src.wiki.ontology import Ontology
from src.wiki.page import PageRenderer
from src.generator import WikiGenerator


def test_rdf_manager_fingerprint_is_stable():
    mgr = RDFManager(ttl_paths=["nonexistent.ttl"])  # missing files ok
    fp = mgr.fingerprint()
    assert isinstance(fp, str) and len(fp) == 40  # sha1 hex length


def test_ontology_uses_rdf_manager_and_refresh():
    mgr = RDFManager()
    ont = Ontology(mgr)
    assert isinstance(ont.get_motifs(), list)
    ont._cache["motifs"] = ["X"]
    ont.refresh()
    assert ont.get_motifs() == []


def test_page_renderer_renders_string_template():
    renderer = PageRenderer()
    out = renderer.render_string("Hello {name}", {"name": "world"})
    assert out == "Hello world"


def test_wiki_generator_build_returns_list():
    gen = WikiGenerator()
    out = gen.build()
    assert isinstance(out, list)
