from pathlib import Path

from src.wiki.generator import WikiGenerator


def test_generate_types_with_class_only(tmp_path: Path):
    gen = WikiGenerator(Path("config/wiki.yaml"))
    wiki_cfg = {
        "types": [
            {
                "id": "model_architecture",
                "class": "motif:ModelArchitecture",
                "title": "ModelsByClass",
                # omit list_query to exercise class-based listing
                "detail_query": "motif_detail.sparql",
                "index_template": "type_index.mustache",
                "detail_template": "motif_detail.mustache",
                "output_dir": "models_by_class",
                "slug_field": "label",
                "nav": False,
            }
        ]
    }

    gen.output_dir = tmp_path
    gen.generate_types(wiki_cfg)

    idx = tmp_path / "models_by_class" / "index.html"
    assert idx.exists(), f"Expected index at {idx}"
    # ensure at least one detail page
    found = False
    for d in (tmp_path / "models_by_class").iterdir():
        if d.is_dir() and (d / "index.html").exists():
            found = True
            break
    assert found, "Expected at least one detail page"