#!/usr/bin/env python3
"""
Generate example report with all figures.

This script creates a comprehensive HTML report showcasing
all available charts and analyses.

Configuration is loaded from config/motif-models.yaml
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.charting.report_generator import ReportGenerator
from src.charting.config import get_paths, get_report_config

if __name__ == "__main__":
    paths = get_paths()
    report_cfg = get_report_config()
    
    figures_dir = paths.get("figures", Path("papers/figures"))
    reports_dir = paths.get("reports", Path("papers"))
    
    gen = ReportGenerator(
        figures_dir=figures_dir,
        output_dir=reports_dir
    )

    # Load sections from config
    sections = report_cfg.get("sections", [])

    # Generate HTML
    html = gen.generate_html_report("Motif Ontology Analysis", sections)

    # Write report
    report_filename = report_cfg.get("report_filename", "motif_analysis_report.html")
    report_path = reports_dir / report_filename
    with open(report_path, "w") as f:
        f.write(html)

    print(f"✓ Report written to {report_path}")
