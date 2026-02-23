import os
from pathlib import Path
import pytest

from src.wiki.generator import WikiGenerator


def test_generate_types_minimal(tmp_path: Path):
    """Smoke test: generate a small wiki slice (categories) and ensure index + a detail page are created."""
    gen = WikiGenerator(Path("config/wiki.yaml"))
    # Use a tiny in-memory wiki config so test doesn't depend on repo config
    wiki_cfg = {
        "types": [
            {
                "id": "motif",
                "class": "motif:Motif",
                "title": "Motifs",
                "list_query": "list_motifs.sparql",
                "detail_query": "motif_detail.sparql",
                "index_template": "type_index.mustache",
                "detail_template": "motif_detail.mustache",
                "output_dir": "motifs",
                "slug_field": "label",
                "nav": False,
            }
        ]
    }

    # Point output at tmp
    gen.output_dir = tmp_path
    gen.generate_types(wiki_cfg)

    idx = tmp_path / "motifs" / "index.html"
    assert idx.exists(), f"Expected index at {idx}"

    # Ensure at least one detail folder exists
    found = False
    for d in (tmp_path / "motifs").iterdir():
        if d.is_dir() and (d / "index.html").exists():
            found = True
            break
    assert found, "Expected at least one motif detail page to be generated"

    # search index should include generated pages
    si = [s for s in gen.search_index if s.get("category") == "motif"]
    assert len(si) > 0, "Expected search index entries for generated motif pages"
