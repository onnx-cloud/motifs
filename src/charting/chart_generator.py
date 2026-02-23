#!/usr/bin/env python3
"""
Chart Generator: Convert SPARQL queries + YAML configs to Vega-Lite specifications.

This tool:
1. Reads YAML figure configs from charts/
2. Executes SPARQL queries against TTL files in ttl/
3. Transforms query results into Vega-Lite JSON specifications
4. Generates chart outputs to papers/figures/

Configuration is loaded from config/motif-models.yaml

Usage:
    python chart_generator.py --config charts/motifs_by_category.yaml
    python chart_generator.py --config charts/
"""

import json
import yaml
import logging
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.rdf_manager import RDFManager

# rdflib is a dependency of RDFManager; ensure it's available at runtime

from src.charting.config import get_paths, get_chart_config
try:
    import pystache
except Exception:
    pystache = None


# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


class ChartGenerator:
    """Generate Vega-Lite charts from SPARQL queries and YAML configs."""

    def __init__(self, ttl_dir: Path = None, sparql_dir: Path = None):
        """
        Initialize chart generator.

        Args:
            ttl_dir: Directory containing TTL files (default from config)
            sparql_dir: Directory containing SPARQL queries (default from config)
        """
        paths = get_paths()
        self.ttl_dir = ttl_dir or paths.get("ttl", Path("ttl"))
        self.sparql_dir = sparql_dir or paths.get("sparql", Path("sparql"))

        # Use modular RDFManager to load and manage TTL ontology
        self.rdf = RDFManager(self.ttl_dir)
        stats = self.rdf.graph_stats()
        log.info(f"Ontology loaded: {stats.get('triples', 0)} triples; subjects={stats.get('subjects')}")


    def _execute_sparql(self, query_path: str) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL query file and return results as list of dicts.

        Args:
            query_path: Path to .sparql file or inline query string

        Returns:
            List of result rows as dictionaries
        """
        # Try to read as a file first
        query_file = Path(query_path)
        
        try:
            if query_file.exists():
                with open(query_file) as f:
                    query = f.read()
                log.debug(f"Loaded query from file: {query_file}")
            else:
                # Try resolving from current directory
                query_file = Path.cwd() / query_path
                if query_file.exists():
                    with open(query_file) as f:
                        query = f.read()
                    log.debug(f"Loaded query from resolved path: {query_file}")
                else:
                    # Assume it's inline SPARQL
                    query = query_path
                    log.debug("Using inline SPARQL query")
        except Exception as e:
            # If all else fails, assume inline SPARQL
            query = query_path
            log.debug(f"Error reading file, using as inline query: {e}")

        log.info(f"Executing SPARQL query")
        # Heuristics to detect inline SPARQL vs file path. Inline queries typically contain newlines
        # or start with SPARQL keywords like SELECT/PREFIX/ASK/CONSTRUCT/etc.
        # NOTE: use the loaded `query` content (not the original path) when available so we
        # don't accidentally pass a file path string to the SPARQL parser.
        q_text = str(query)
        is_inline = ("\n" in q_text) or q_text.strip().upper().startswith(("SELECT", "PREFIX", "ASK", "CONSTRUCT", "DESCRIBE", "WITH", "INSERT", "DELETE", "MERGE"))

        # If the query string looks explicitly like a path (starts with '/' or './'),
        # treat it as a direct file path and fail fast if it does not exist. Do not probe
        # multiple candidate locations — the caller should pass the correct path.
        if not is_inline and q_text.strip().startswith(('.', '/')):
            p = Path(q_text)
            if p.exists():
                try:
                    with open(p) as f:
                        q_text = f.read()
                    is_inline = True
                except Exception as e:
                    raise RuntimeError(f"Failed to read SPARQL file {p}: {e}")
            else:
                raise FileNotFoundError(f"SPARQL file not found: {p}")

        if is_inline:
            result = self.rdf.execute_query(q_text)
        else:
            # If this is not inline and not an explicit path, resolve strictly relative to
            # the configured SPARQL directory and fail if not present.
            qpath = Path(self.sparql_dir) / q_text
            if qpath.exists():
                result = self.rdf.execute_query_file(qpath)
            else:
                raise FileNotFoundError(f"SPARQL file not found: {qpath}")

        rows = self.rdf.results_to_dicts(result)
        log.info(f"Query returned {len(rows)} rows")
        return rows

    def _transform_data(self, data: List[Dict[str, Any]], transform: Optional[Dict]) -> List[Dict]:
        """
        Apply optional transformations to query results.

        Args:
            data: Query result rows
            transform: Transformation config (rename, filter, compute)

        Returns:
            Transformed data
        """
        if not transform:
            return data

        result = data.copy()

        # Field renaming
        if "rename" in transform:
            renames = transform["rename"]
            result = [
                {renames.get(k, k): v for k, v in row.items()}
                for row in result
            ]

        # Field filtering
        if "keep" in transform:
            keep_fields = set(transform["keep"])
            result = [
                {k: v for k, v in row.items() if k in keep_fields}
                for row in result
            ]

        # Computed fields
        if "compute" in transform:
            for row in result:
                for field_name, expr in transform["compute"].items():
                    row[field_name] = self._eval_expr(expr, row)

        return result

    def _eval_expr(self, expr: str, row: Dict) -> Any:
        """
        Evaluate a simple expression with row context.

        Supports: ${fieldname}, basic arithmetic, string concat
        """
        result = expr
        for key, val in row.items():
            result = result.replace(f"${{{key}}}", str(val))
        return result

    def generate_vega_spec(self, config: Dict[str, Any], data: List[Dict]) -> Dict:
        """
        Generate Vega-Lite JSON specification from config and data.

        Args:
            config: Figure config with vega section
            data: Transformed query data

        Returns:
            Vega-Lite JSON specification
        """
        vega = config.get("vega", {})
        title = config.get("title", "Untitled")
        description = config.get("description", "")

        # Build base spec
        spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "title": title,
            "description": description,
            "data": {"values": data},
        }

        # Merge in vega config
        spec.update(vega)

        return spec

    def load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load and validate YAML config."""
        with open(config_path) as f:
            config = yaml.safe_load(f)
        log.info(f"Loaded config: {config_path.name}")
        return config

    def process_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a figure config: execute SPARQL, transform, generate Vega spec.

        Args:
            config: Figure configuration

        Returns:
            Result dict with vega_spec and output_path
        """
        # Execute SPARQL query
        query_spec = config.get("query", {})
        if isinstance(query_spec, str):
            # Detect inline SPARQL (multi-line or starts with SPARQL keywords)
            qtext = query_spec
            is_inline = ("\n" in qtext) or qtext.strip().upper().startswith(("SELECT", "PREFIX", "ASK", "CONSTRUCT", "DESCRIBE", "WITH", "INSERT", "DELETE", "MERGE"))
            if is_inline:
                # Pass inline query text directly
                query_path = qtext
            else:
                # Treat as a filename: prefer files inside the configured sparql_dir, else resolve relative to cwd
                query_file = Path(qtext)
                candidate = Path.cwd() / self.sparql_dir / query_file.name
                if candidate.exists():
                    query_path = str(candidate)
                else:
                    if not query_file.is_absolute():
                        query_file = Path.cwd() / query_file
                    query_path = str(query_file)
        else:
            query_path = str(Path.cwd() / self.sparql_dir / query_spec.get("file", ""))

        query_data = self._execute_sparql(query_path)

        # Transform data
        transform = config.get("transform")
        data = self._transform_data(query_data, transform)

        # Generate Vega spec
        vega_spec = self.generate_vega_spec(config, data)

        return {
            "title": config.get("title"),
            "config": config,
            "query_data": query_data,
            "transformed_data": data,
            "vega_spec": vega_spec,
        }

    def write_output(self, result: Dict[str, Any], output_dir: Path, formats: List[str] = None):
        """
        Write chart outputs in requested formats.

        Args:
            result: Result from process_config
            output_dir: Output directory for figures
            formats: List of formats (json, html, svg, png)
        """
        if not formats:
            formats = ["json", "html"]

        output_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize title for filename
        title = result["title"].lower().replace(" ", "_")
        base_path = output_dir / title

        # JSON (Vega-Lite spec)
        if "json" in formats:
            json_path = base_path.with_suffix(".json")
            with open(json_path, "w") as f:
                json.dump(result["vega_spec"], f, indent=2)
            log.info(f"✓ Written {json_path.relative_to(output_dir.parent.parent)}")

        # HTML (embedded Vega-Lite viewer)
        if "html" in formats:
            html_path = base_path.with_suffix(".html")
            html_content = self._generate_html(result["vega_spec"], result["title"])
            with open(html_path, "w") as f:
                f.write(html_content)
            log.info(f"✓ Written {html_path.relative_to(output_dir.parent.parent)}")

        # Data JSON (query results)
        if "data" in formats:
            data_path = base_path.with_suffix(".data.json")
            with open(data_path, "w") as f:
                json.dump(result["transformed_data"], f, indent=2)
            log.info(f"✓ Written {data_path.relative_to(output_dir.parent.parent)}")

        # PNG generation using vl-convert-python if requested
        if "png" in formats:
            png_path = base_path.with_suffix(".png")
            try:
                import vl_convert as vlc
                png_data = vlc.vegalite_to_png(result["vega_spec"], scale=2)
                with open(png_path, "wb") as f:
                    f.write(png_data)
                log.info(f"✓ Written {png_path.relative_to(output_dir.parent.parent)}")
            except ImportError:
                log.warning("vl-convert-python not installed; run: pip install vl-convert-python")
            except Exception as e:
                log.warning(f"PNG generation failed: {e}")

    def _generate_html(self, vega_spec: Dict, title: str) -> str:
        """Generate HTML by rendering the `chart_page.mustache` template and wrapping it with `charts_layout.mustache` so site chrome is included."""
        spec_json = json.dumps(vega_spec)
        # Render chart content fragment
        try:
            content_html = self._render_template("chart_page.mustache", {"title": title, "spec_json": spec_json})
        except FileNotFoundError:
            content_html = f"<div><h1>{title}</h1><pre>{spec_json}</pre></div>"

        # Include Vega lib scripts in the layout head_extra slot
        head_extra = '\n'.join([
            '<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>',
            '<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>',
            '<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>',
        ])

        # Render full page using charts layout so header/nav/footer are present
        html = self._render_template("charts_layout.mustache", {"title": title, "content": content_html, "head_extra": head_extra, "nav": "", "nav_footer": ""})
        return html

    def _render_template(self, template_name: str, context: Dict) -> str:
        """Render a mustache template from `src/template` with the layout partial available.

        Arguments:
            template_name: template filename (e.g., 'charts_index.mustache')
            context: context dictionary for rendering
        Returns:
            Rendered HTML string
        """
        template_dir = Path(__file__).parents[1] / "template"
        template_file = template_dir / template_name
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")

        template_text = template_file.read_text()
        # Load partials from the partials/ directory (header, nav, footer etc.)
        partials = {}
        partials_dir = template_dir / "partials"
        if partials_dir.exists() and partials_dir.is_dir():
            for p in partials_dir.glob("*.mustache"):
                key = p.stem
                partials[key] = p.read_text()

        # Also load layout partial if present
        layout_file = template_dir / "charts_layout.mustache"
        if layout_file.exists():
            partials["charts_layout"] = layout_file.read_text()

        renderer = pystache.Renderer(partials=partials)
        return renderer.render(template_text, context)

    def _write_index(self, index_path: Path, title: str, charts: List[Dict], subtitle: str = None, nav: str = None, nav_footer: str = None):
        """Write an index.html file using the charts_index.mustache template.

        The `charts` list should contain dictionaries with keys: title, desc, json, html, png, yaml
        """
        ctx = {
            "title": title,
            "subtitle": subtitle or "",
            "charts": charts,
            "nav": nav or "",
            "nav_footer": nav_footer or "",
        }
        html = self._render_template("charts_index.mustache", ctx)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(html)
        log.info(f"✓ Written {index_path}")


def main():
    chart_cfg = get_chart_config()
    paths = get_paths()
    
    parser = argparse.ArgumentParser(
        description="Generate Vega-Lite charts from SPARQL + YAML configs"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=paths.get("charts_config", Path("charts")),
        help="Config file or directory containing *.yaml configs (default from config/motif-models.yaml)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=paths.get("figures", Path("papers/figures")),
        help="Output directory for charts (default from config)",
    )
    parser.add_argument(
        "--output-formats",
        nargs="+",
        default=chart_cfg.get("output_formats", ["json", "html"]),
        help="Output formats (default from config)",
    )
    parser.add_argument(
        "--ttl-dir",
        type=Path,
        default=paths.get("ttl", Path("ttl")),
        help="Directory with TTL files (default from config)",
    )
    parser.add_argument(
        "--sparql-dir",
        type=Path,
        default=paths.get("sparql", Path("sparql")),
        help="Directory with SPARQL queries (default from config)",
    )

    args = parser.parse_args()

    # Initialize generator
    gen = ChartGenerator(ttl_dir=args.ttl_dir, sparql_dir=args.sparql_dir)

    # Collect config files
    if args.config.is_dir():
        config_files = sorted(args.config.glob("*.yaml"))
    else:
        config_files = [args.config]

    log.info(f"Processing {len(config_files)} config(s)")

    # Process each config
    spec_entries = []
    output_entries = []

    for config_path in config_files:
        log.info(f"\n--- {config_path.name} ---")
        config = gen.load_config(config_path)
        result = gen.process_config(config)
        gen.write_output(result, args.output_dir, args.output_formats)

        # Build metadata entries for the index files
        title = result.get("title") or config_path.stem
        base_name = title.lower().replace(" ", "_")

        spec_entry = {
            "title": title,
            "desc": config.get("description", ""),
            "yaml": config_path.name,
            "vljson": f"{config_path.stem}.vl.json",
            "json": f"../{args.output_dir.name}/{base_name}.json",
            "html": f"../{args.output_dir.name}/{base_name}.html",
        }
        spec_entries.append(spec_entry)

        output_entry = {
            "title": title,
            "desc": config.get("description", ""),
            "json": f"{base_name}.json",
            "html": f"{base_name}.html",
            "png": (f"{base_name}.png" if "png" in args.output_formats else None),
            "yaml": config_path.name,
        }
        output_entries.append(output_entry)

    # Write index.html into charts/ (spec-level) and into the output directory (generated artifacts)
    charts_dir = args.config if args.config.is_dir() else Path(args.config).parent
    try:
        gen._write_index(charts_dir / "index.html", title="Charts (specs)", charts=spec_entries, subtitle="Spec-level index of charts")
    except Exception as e:
        log.warning(f"Failed to write charts/index.html: {e}")

    try:
        gen._write_index(args.output_dir / "index.html", title="Generated Figures", charts=output_entries, subtitle="Generated output artifacts")
    except Exception as e:
        log.warning(f"Failed to write {args.output_dir}/index.html: {e}")

    log.info(f"\n✓ All figures written to {args.output_dir}/")


if __name__ == "__main__":
    main()
