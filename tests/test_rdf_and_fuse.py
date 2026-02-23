import os
from pathlib import Path
import pytest

from src.rdf_manager import RDFManager
from src.fuse_generator import FuseGenerator


def test_get_operator_spec_add():
    rdf = RDFManager(Path("ttl"))
    spec = rdf.get_operator_spec("Add")
    assert spec is not None, "Add operator spec should be found"
    assert spec.get("label") in ("Add", "add")
    assert isinstance(spec.get("inputs"), list)
    assert len(spec.get("inputs")) >= 1
    # structured inputs should be dicts with a 'name' field
    first = spec.get("inputs")[0]
    assert isinstance(first, dict) and "name" in first


def test_operator_domain_iri_and_attr_defaults():
    rdf = RDFManager(Path("ttl"))
    spec = rdf.get_operator_spec("Selu")
    assert spec is not None, "Selu operator spec should be found"
    # Domain IRI should be present and a proper URL
    assert spec.get("domain_iri") and spec.get("domain_iri", "").startswith("https://"), spec
    # Find 'gamma' or 'alpha' in attributes and ensure default is numeric
    attrs = spec.get("attributes", [])
    nums = [a.get("default") for a in attrs if a.get("name") in ("gamma", "alpha")]
    assert nums and any(isinstance(x, (float, int)) for x in nums), f"Expected numeric default for Selu attributes, got {nums}"


def test_fuse_generator_smoke(tmp_path: Path):
    outdir = tmp_path / "fuse_out"
    gen = FuseGenerator(ttl_dir=Path("ttl"), sparql_dir=Path("sparql"), output_dir=outdir)
    count = gen.generate_all_motifs()
    assert count > 0
    # categories summary should exist
    assert (outdir / "categories_summary.fuse").exists()
    # At least one .fuse file
    files = list(outdir.glob("*.fuse"))
    assert files, "No .fuse files generated"

    # If an operator spec exists for Add, it should appear in the Add snippet
    add_file = outdir / "add.fuse"
    if add_file.exists():
        text = add_file.read_text()
        # Either Operator spec block or Definition should be present
        assert "// Operator spec" in text or "// Definition:" in text


def test_fuse_with_template(tmp_path: Path):
    # Use the repository template and ensure rendering places operator label
    outdir = tmp_path / "fuse_out_tmpl"
    tmpl = Path("src/template/fuse-motifs.mustache")
    gen = FuseGenerator(ttl_dir=Path("ttl"), sparql_dir=Path("sparql"), output_dir=outdir, template_path=tmpl)
    count = gen.generate_all_motifs()
    assert count > 0
    # check one generated file contains template fields
    files = list(outdir.glob("*.fuse"))
    assert files, "No .fuse files generated"
    # Ensure at least one generated file contains motif header
    assert any("Motif:" in f.read_text() for f in files)
    # Ensure at least one file includes either an operator spec or a definition block
    assert any("// Operator spec" in f.read_text() or "// Definition:" in f.read_text() for f in files)
