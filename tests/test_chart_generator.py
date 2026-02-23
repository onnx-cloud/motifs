from pathlib import Path
from src.charting.chart_generator import ChartGenerator


def test_chart_process_config():
    gen = ChartGenerator()
    cfg = gen.load_config(Path("charts/motifs_by_category.yaml"))
    res = gen.process_config(cfg)
    assert "vega_spec" in res
    assert isinstance(res["vega_spec"], dict)
    assert "transformed_data" in res
    assert isinstance(res["transformed_data"], list)
