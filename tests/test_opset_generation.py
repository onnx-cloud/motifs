import importlib
import os
import pytest

OPSET_PATH = os.path.join("ttl", "onnx", "opset.ttl")


def test_generate_opset_ttl():
    try:
        import onnx  # noqa: F401
    except Exception:
        pytest.skip("onnx not installed in test environment")

    # Import and call the generator
    mod = importlib.import_module("src.onnx.opset_to_ttl")
    mod.main()

    assert os.path.exists(OPSET_PATH), f"Expected {OPSET_PATH} to exist"

    # Ensure at least one common operator is present in the monolithic file
    with open(OPSET_PATH, "r", encoding="utf-8") as f:
        data = f.read()
    assert "rdfs:label \"Add\"" in data or "rdfs:label \"MatMul\"" in data

    # And ensure a per-operator file was created for Add under ttl/onnx/operators
    domain_safe = "ai.onnx".replace('.', '_')
    add_path = os.path.join("ttl", "onnx", "operators", domain_safe, "Add.ttl")
    assert os.path.exists(add_path), f"Expected per-operator file {add_path} to exist"
    with open(add_path, "r", encoding="utf-8") as f:
        opdata = f.read()
    assert "rdfs:label \"Add\"" in opdata


def test_opset_structured_triples():
    try:
        import onnx  # noqa: F401
    except Exception:
        pytest.skip("onnx not installed in test environment")

    # Ensure the per-operator file for Add contains structured blank nodes AND domain IRI
    domain_safe = "ai.onnx".replace('.', '_')
    add_path = os.path.join("ttl", "onnx", "operators", domain_safe, "Add.ttl")
    assert os.path.exists(add_path), f"Expected per-operator file {add_path} to exist"
    with open(add_path, "r", encoding="utf-8") as f:
        opdata = f.read()
    # Look for structured hasInput/hasOutput/hasAttribute patterns
    assert "onnx:hasInput [" in opdata or "onnx:hasOutput [" in opdata or "onnx:hasAttribute [" in opdata, (
        "Expected structured blank-node triples like 'onnx:hasInput [', found none in Add.ttl"
    )
    # Domain should be an IRI
    assert "onnx:domain <https://ns.onnx.cloud/onnx/domain/" in opdata


def test_attr_default_typed():
    try:
        import onnx  # noqa: F401
    except Exception:
        pytest.skip("onnx not installed in test environment")

    # Pick an operator known to have numeric defaults (Selu alpha/beta)
    domain_safe = "ai.onnx".replace('.', '_')
    selu_path = os.path.join("ttl", "onnx", "operators", domain_safe, "Selu.ttl")
    assert os.path.exists(selu_path), f"Expected per-operator file {selu_path} to exist"
    with open(selu_path, "r", encoding="utf-8") as f:
        selu = f.read()
    # Should contain an onnx:default with a typed numeric literal (^^xsd:double or ^^xsd:integer)
    assert "onnx:default" in selu
    assert "^^xsd:double" in selu or "^^xsd:integer" in selu, (
        "Expected numeric typed default in Selu.ttl"
    )
