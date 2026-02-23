import importlib
import os
import pytest


def make_simple_add_model(path):
    try:
        import onnx
        from onnx import helper, TensorProto
    except Exception:
        pytest.skip("onnx not installed in test environment")

    # Create a simple graph: A, B -> Add -> C
    A = helper.make_tensor_value_info("A", TensorProto.FLOAT, [1])
    B = helper.make_tensor_value_info("B", TensorProto.FLOAT, [1])
    C = helper.make_tensor_value_info("C", TensorProto.FLOAT, [1])

    node = helper.make_node("Add", ["A", "B"], ["C"], name="AddNode")

    graph = helper.make_graph([node], "SimpleGraph", [A, B], [C])
    model = helper.make_model(graph)
    onnx.save(model, path)


def test_export_model_ttl(tmp_path):
    try:
        import onnx  # noqa: F401
    except Exception:
        pytest.skip("onnx not installed in test environment")

    from importlib import import_module
    mod = import_module("src.onnx.model_to_ttl")

    model_path = tmp_path / "simple_add.onnx"
    make_simple_add_model(str(model_path))

    out = tmp_path / "out.ttl"
    out_path = mod.export_model_to_ttl(str(model_path), str(out))

    assert os.path.exists(out_path), f"Expected TTL output at {out_path}"

    with open(out_path, "r", encoding="utf-8") as f:
        data = f.read()

    # Check for graph resource and node/inputs/outputs
    assert "a onnx:Graph" in data
    assert "a onnx:Node" in data
    assert "onnx:hasInput [ a onnx:OperatorInput" in data
    assert "onnx:hasOutput [ a onnx:OperatorOutput" in data
    assert "rdfs:label \"Add\"" in data or "rdfs:label \"AddNode\"" in data
