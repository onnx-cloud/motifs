#!/usr/bin/env python3
"""
Report generator: Create HTML/Markdown reports with embedded Vega-Lite figures.

Features:
- Embed figures from papers/figures/ into reports
- Generate table of contents
- Support multiple report templates
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict

log = logging.getLogger(__name__)


class ReportGenerator:
    """Generate HTML/Markdown reports with embedded figures."""

    def __init__(self, figures_dir: Path = None, output_dir: Path = None):
        """
        Initialize report generator.

        Args:
            figures_dir: Directory with generated figures (default: papers/figures)
            output_dir: Output directory for reports (default: papers/)
        """
        self.figures_dir = figures_dir or Path("papers/figures")
        self.output_dir = output_dir or Path("papers")

    def discover_figures(self) -> Dict[str, Path]:
        """Find all JSON figure specs."""
        figures = {}
        for json_file in self.figures_dir.glob("*.json"):
            figures[json_file.stem] = json_file
        log.info(f"Discovered {len(figures)} figures")
        return figures

    def generate_html_report(self, title: str, sections: List[Dict]) -> str:
        """
        Generate HTML report with embedded figures.

        Args:
            title: Report title
            sections: List of section dicts with keys:
              - title: Section title
              - description: Section description
              - figures: List of figure names to embed

        Returns:
            HTML content string
        """
        figures = self.discover_figures()
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{title}</title>",
            "<meta charset='utf-8'>",
            "<style>",
            self._get_css_styles(),
            "</style>",
            "<script src='https://cdn.jsdelivr.net/npm/vega@5'></script>",
            "<script src='https://cdn.jsdelivr.net/npm/vega-lite@5'></script>",
            "<script src='https://cdn.jsdelivr.net/npm/vega-embed@6'></script>",
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
            "<div class='toc'>",
            "<h2>Contents</h2>",
            "<ul>",
        ]

        # Table of contents
        for i, section in enumerate(sections, 1):
            section_id = f"section-{i}"
            html_parts.append(f"<li><a href='#{section_id}'>{section['title']}</a></li>")

        html_parts.extend(["</ul>", "</div>"])

        # Content sections
        for i, section in enumerate(sections, 1):
            section_id = f"section-{i}"
            html_parts.extend([
                f"<section id='{section_id}'>",
                f"<h2>{section['title']}</h2>",
                f"<p>{section.get('description', '')}</p>",
            ])

            # Embed figures
            for fig_name in section.get("figures", []):
                if fig_name in figures:
                    fig_path = figures[fig_name]
                    with open(fig_path) as f:
                        spec = json.load(f)
                    spec_json = json.dumps(spec)
                    fig_id = f"vis-{fig_name}"
                    html_parts.extend([
                        f"<div id='{fig_id}' class='figure'></div>",
                        f"<script>vegaEmbed('#{fig_id}', {spec_json});</script>",
                    ])

            html_parts.append("</section>")

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)

    def _get_css_styles(self) -> str:
        """Return CSS styling for report."""
        return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
            }
            h1 { color: #222; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }
            h2 { color: #0066cc; margin-top: 30px; }
            section { margin-bottom: 40px; padding: 20px; background: #f9f9f9; border-radius: 8px; }
            .toc { background: #eef5ff; padding: 15px 20px; border-left: 4px solid #0066cc; }
            .toc ul { list-style: none; padding-left: 0; }
            .toc a { color: #0066cc; text-decoration: none; }
            .toc a:hover { text-decoration: underline; }
            .figure { background: white; padding: 15px; margin: 15px 0; border-radius: 4px; }
            p { color: #555; }
        """
