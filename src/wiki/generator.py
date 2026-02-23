#!/usr/bin/env python3
"""
Semanic Wiki Generator for Motifs.

Generates static HTML documentation from:
  - TTL ontology files (ttl/)
  - SPARQL queries (sparql/docs/)
  - Mustache templates (src/template/docs/)
  - Configuration (config/wiki.yaml)

Usage:
    python src/wiki/generator.py
    python src/wiki/generator.py --config config/wiki.yaml --output docs/
"""

import argparse
import logging
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import signal
try:
    import pystache
except Exception:
    pystache = None
import yaml
import json

from src.rdf_manager import RDFManager

# Simple alias for RDF IRIs used in type annotations
IRI = str

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


class WikiGenerator:

    """Config-driven documentation generator."""

    def generate_all(self):
        """Generate all documentation pages and type indexes as defined in the config."""
        wiki_cfg = self.config
        # Generate type indexes if present
        if wiki_cfg.get("types"):
            self.generate_types(wiki_cfg)
        # Generate all pages
        pages = wiki_cfg.get("pages", [])
        # Support both dict (YAML mapping) and list (YAML sequence) forms
        if isinstance(pages, dict):
            page_items = pages.items()
        elif isinstance(pages, list):
            page_items = ((page.get("name") or page.get("id") or "page", page) for page in pages)
        else:
            page_items = []
        for name, page in page_items:
            try:
                self.generate_page(name, page)
            except Exception as e:
                logging.error(f"Failed to generate page {name}: {e}")
        # Save search index
        self.save_index()

    def __init__(self, config_path: Path):
        """
        Initialize generator from config file.

        Args:
            config_path: Path to wiki.yaml configuration
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.base_dir = config_path.parent.parent  # Assume config/ is under project root

        # Default template dir and output dir (can be overridden by caller)
        self.template_dir = self.base_dir / "src" / "template"
        self.output_dir = self.base_dir / "tmp" / "wiki"

        self.rdf = RDFManager(self.base_dir / "ttl")

        stats = self.rdf.graph_stats()
        logging.info(f"Loaded {stats.get('triples', 0)} triples from TTL sources")

        # Prepare renderer and load partials from `template/partials`
        partials = {}
        # All templates are partials
        partials_dirs = [self.template_dir]
        for partials_dir in partials_dirs:
            if partials_dir.exists() and partials_dir.is_dir():
                for p in partials_dir.glob("*.mustache"):
                    partials[p.stem] = p.read_text()
        # Save partials dict and provide a small wrapper to render templates with them
        self.partials = partials
        self.renderer = pystache.Renderer(partials=partials) if pystache is not None else None
        # Search index entries collected during page generation
        self.search_index = []


    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration. Missing file -> empty config."""
        if not path or not path.exists():
            logging.info(f"Config file not found: {path}, using empty config")
            return {}
        with open(path) as f:
            return yaml.safe_load(f)

    def _load_template(self, template_name: str) -> str:
        """Load mustache template by name."""
        template_path = self.template_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_path.read_text()


    def generate_pages(self): 
        """Resolve site / page configurations from config.

            predicate: motif:hasCategory
            template: cards/categories.mustache   
            body:
            query: ./sparql/wiki/models_by_category.sparql
            template: lists/models_by_category.mustache
        
        """
        return self.config.get("pages", [])

    def generate_page(self, name: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single page by name. Resolve page, hydrate its data, render, and write output."""
        from src.wiki.page import PageRenderer
        import os
        # 1. Hydrate data sections (body/left/right)
        data: Dict[str, List[object]] = {}
        for sec in ("left", "body", "right"):
            sec_spec = spec.get(sec)
            if not sec_spec or not isinstance(sec_spec, dict):
                continue
            # Query by predicate
            if sec_spec.get("predicate"):
                preds = self.find_by_predicate(None, sec_spec.get("predicate"))
                # Map to context key based on template name
                t = sec_spec.get("template", "")
                if "categories" in t:
                    data.setdefault("categories", []).extend(preds)
                elif "fingerprint" in t or "menu" in t:
                    data.setdefault("fingerprints", []).extend(preds)
                else:
                    data.setdefault(f"{sec}_items", []).extend(preds)
            # Query by SPARQL file
            if sec_spec.get("query"):
                rows = self.find_by_sparql(None, sec_spec.get("query"))
                t = sec_spec.get("template", "")
                if "motifs" in t or "models" in t:
                    # Normalize query rows to `items` expected by templates
                    for r in rows:
                        title = r.get("label") or r.get("motif") or r.get("model") or r.get("item")
                        description = r.get("definition") or r.get("categoryLabel") or r.get("label")
                        url = r.get("motif_uri") or r.get("model_uri") or r.get("item_uri") or '#'
                        category = r.get("categoryLabel") or ''
                        notes = r.get("definition") or ''
                        meta = r.get("isPrimitive") or category or ''
                        data.setdefault("items", []).append({"title": title, "description": description, "url": url, "meta": meta, "category": category, "notes": notes})
                elif "fingerprints" in t:
                    # If rows are simple dicts with 'f' or 'label' keys
                    fps = [r.get("label") or r.get("f") or r.get("value") for r in rows]
                    data.setdefault("fingerprints", []).extend([x for x in fps if x])
                elif "runtimes" in t:
                    data.setdefault("runtimes", []).extend(rows)
                elif "categories" in t:
                    # rows may contain ?o ?label ?count
                    cats = []
                    for r in rows:
                        label = r.get("label") or r.get("o")
                        slug = slugify(label) if label else slugify(str(r.get("o_uri") or r.get("o")))
                        cats.append({"label": label, "count": int(r.get("count", 0)) if r.get("count") else 0, "slug": slug})
                    data.setdefault("categories", []).extend(cats)
                else:
                    data.setdefault("items", []).extend(rows)

        # 1b. Generate per-item detail pages for motifs (creates slugified local pages and rewrites item URLs)
        if name == 'motifs':
            detail_q = None
            try:
                detail_q_path = self._resolve_query_path('sparql/docs/motif_detail.sparql')
                detail_q = detail_q_path.read_text()
            except Exception:
                logging.debug('motif detail query not found; skipping detail pages')
            if detail_q:
                from src.wiki.page import PageRenderer
                for it in data.get('items', []):
                    motif_uri = it.get('url')
                    if not motif_uri or not str(motif_uri).startswith('http'):
                        continue
                    slug = slugify(it.get('title') or motif_uri)
                    detail_dir = (self.output_dir / slug)
                    detail_dir.mkdir(parents=True, exist_ok=True)
                    # Bind the target motif and run the detail query
                    # Insert a VALUES binding for ?targetMotif inside the WHERE clause
                    import re
                    if re.search(r'WHERE\s*\{', detail_q, flags=re.I):
                        qtext = re.sub(r'(WHERE\s*\{)', rf"\1 VALUES ?targetMotif {{ <{motif_uri}> }} ", detail_q, flags=re.I, count=1)
                    else:
                        # Fallback to prepend, though SPARQL parsers may reject it
                        qtext = f"VALUES ?targetMotif {{ <{motif_uri}> }}\n" + detail_q
                    try:
                        res = self.rdf.execute_query(qtext)
                        rows = self.rdf.results_to_dicts(res)
                        detail = rows[0] if rows else {}
                    except Exception as e:
                        logging.error(f"Failed to query detail for {motif_uri}: {e}")
                        detail = {}
                    # Render detail page
                    renderer = PageRenderer(str(self.template_dir))
                    ctx = {"page": {"title": detail.get('label') or it.get('title')}, "site": self.config.get('site', {}), "detail": detail}
                    try:
                        detail_html = renderer.render('wiki/detail/motif.mustache', ctx)
                        with open(detail_dir / 'index.html', 'w', encoding='utf-8') as f:
                            f.write(detail_html)
                        # Update item URL to local detail page
                        it['url'] = f"{slug}/index.html"
                        # Add detail page to search index
                        self.search_index.append({"title": detail.get('label') or it.get('title'), "text": detail.get('definition') or it.get('description') or '', "category": 'motif', "url": str((detail_dir / 'index.html').relative_to(self.output_dir))})
                        logging.info(f"✓ Generated detail page for {it.get('title')} -> {detail_dir / 'index.html'}")
                    except Exception as e:
                        logging.error(f"Failed to render/write detail for {motif_uri}: {e}")
        # 2. Render
        logging.info(f"Rendering page {name}: data keys={list(data.keys())}, items_count={len(data.get('items',[]))}")
        if data.get('items'):
            logging.debug(f"First item sample for {name}: {data.get('items')[0]}")
        try:
            html = self.render_page(name, spec, data)
        except Exception as e:
            logging.error(f"Failed to render page {name}: {e}")
            html = f"<html><body><h1>{name}</h1><pre>{e}</pre></body></html>"
        # 3. Write output file
        output_dir = self.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{name}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        # 4. Add to search index (better title + text if available)
        title = spec.get("title") or name
        desc = spec.get("description") or ""
        self.search_index.append({"title": title, "text": desc, "category": name, "url": str(output_file.relative_to(self.output_dir))})
        logging.info(f"✓ Generated {output_file}")
        return {"output": str(output_file)}

    def resolve_page(self, name: str) -> Dict[str, Any]:
        """Resolve page configuration by name from config."""
        pages = self.config.get("pages", {}) or {}
        # Support mapping keys and inline list entries
        if isinstance(pages, dict):
            return pages.get(name, {})
        for p in pages:
            if p.get("name") == name or p.get("id") == name:
                return p
        return {}

    def render_page(self, name: str, spec: Dict[str, Any], data: Dict[str, List[object]]) -> str:
        """Render page configuration by name from config using a template."""
        from src.wiki.page import PageRenderer
        # Provide default site/global context and generation time
        ctx = {"page": spec, "site": self.config.get("site", {}), "generated_at": datetime.utcnow().isoformat(), **data}
        template_name = spec.get("template")
        if not template_name:
            # Attempt to find template from body/left/right
            for sec in ("body", "left", "right"):
                s = spec.get(sec)
                if s and isinstance(s, dict) and s.get("template"):
                    template_name = s.get("template")
                    break
        if not template_name:
            raise RuntimeError(f"No template for page {name}")
        renderer = PageRenderer(str(self.template_dir))
        return renderer.render(template_name, ctx)

    def _resolve_query_path(self, query_ref: str) -> Path:
        """Resolve a query path reference (file path) using config paths."""
        qp = Path(query_ref)
        # Direct file reference
        if qp.exists():
            return qp
        # Try relative to base_dir
        candidate = self.base_dir / query_ref
        if candidate.exists():
            return candidate
        # Try joining with configured sparql path
        sparql_path = Path(self.config.get("paths", {}).get("sparql", "sparql"))
        candidate = self.base_dir / sparql_path / Path(query_ref).name
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"SPARQL query file not found: {query_ref}")

    def find_by_predicate(self, entity: IRI, predicate: IRI) -> List[object]:
        """Return list of objects for triples matching ?s predicate ?o, aggregated by object label/count."""
        # Accept predicate in form 'prefix:local' - support motif: prefix
        # Map known prefixes
        prefix_map = {"motif": "https://ns.onnx.cloud/motif#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#"}
        if ":" in predicate:
            pfx, local = predicate.split(":", 1)
            uri = prefix_map.get(pfx)
            if not uri:
                # fallback to use prefix as-is in SPARQL (hoping it's declared in file)
                pred_ref = predicate
            else:
                pred_ref = f"<{uri}{local}>"
        else:
            pred_ref = predicate
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?o ?label (COUNT(?s) as ?count) WHERE {{ ?s {pred_ref} ?o . OPTIONAL {{ ?o rdfs:label ?label }} }} GROUP BY ?o ?label ORDER BY ?label
        """
        try:
            result = self.rdf.execute_query(query)
            rows = self.rdf.results_to_dicts(result)
            out = []
            for r in rows:
                o = r.get("o") or r.get("o_uri")
                label = r.get("label") or (r.get("o") if r.get("o") else None)
                count = int(r.get("count", 0)) if r.get("count") is not None else 0
                slug = slugify(label) if label else slugify(str(o))
                out.append({"uri": r.get("o_uri"), "label": label, "count": count, "slug": slug})
            return out
        except Exception as e:
            logging.error(f"find_by_predicate error for {predicate}: {e}")
            return []

    def find_by_sparql(self, entity: IRI, query: str) -> List[object]:
        """Execute a SPARQL file or inline query and return list of dicts."""
        try:
            # If it's a file path, resolve and run
            if query.strip().endswith('.sparql') or '/' in query or query.strip().startswith('.'):
                qp = self._resolve_query_path(query)
                res = self.rdf.execute_query_file(qp)
            else:
                res = self.rdf.execute_query(query)
            return self.rdf.results_to_dicts(res)
        except FileNotFoundError as e:
            logging.error(e)
            return []
        except Exception as e:
            logging.error(f"find_by_sparql failed: {e}")
            return []

    def find_by_type(self, entity: IRI, rdfType: str) -> List[object]:
        # Simple helper to list resources of a given rdf:type
        query = f"""
        SELECT ?s ?label WHERE {{ ?s a {rdfType} . OPTIONAL {{ ?s rdfs:label ?label }} }} ORDER BY ?label
        """
        try:
            res = self.rdf.execute_query(query)
            return self.rdf.results_to_dicts(res)
        except Exception as e:
            logging.error(f"find_by_type failed: {e}")
            return []

    def generate_types(self, wiki_cfg: Dict[str, Any]) -> None:
        """Generate simple type index and detail pages from a minimal type config.

        This is a minimal, test-oriented implementation: it lists resources with
        rdfs:label and generates an index and per-resource detail folders.
        """
        types = wiki_cfg.get("types", [])
        for t in types:
            out_dir = self.output_dir / t.get("output_dir", t.get("id", "out"))
            out_dir.mkdir(parents=True, exist_ok=True)

            members = []
            # Collect labeled resources
            for subj in set(self.rdf.graph.subjects()):
                info = self.rdf.get_resource_info(subj)
                if info and info.get("label"):
                    members.append((subj, info.get("label")))

            # Write index and detail pages
            index_path = out_dir / "index.html"
            index_lines = ["<html><body><ul>"]
            for subj, label in members:
                slug = slugify(label)
                detail_dir = out_dir / slug
                detail_dir.mkdir(parents=True, exist_ok=True)
                (detail_dir / "index.html").write_text(f"<html><body><h1>{label}</h1></body></html>")
                index_lines.append(f'<li><a href="{slug}/index.html">{label}</a></li>')
                # Add to search index
                try:
                    rel = detail_dir.relative_to(self.output_dir)
                except Exception:
                    rel = detail_dir
                self.search_index.append({"title": label, "category": t.get("id"), "path": str(rel)})
            index_lines.append("</ul></body></html>")
            index_path.write_text("\n".join(index_lines))


    def save_index(self):
        # Write search index for client-side search UI
        try:
            idx_path = self.output_dir / "search_index.json"
            idx_path.parent.mkdir(parents=True, exist_ok=True)
            with open(idx_path, "w") as f:
                json.dump(self.search_index, f, indent=2)
            try:
                rel = idx_path.relative_to(self.base_dir)
            except Exception:
                rel = idx_path
            logging.info(f"✓ Written {rel}")
        except Exception as e:
            logging.log.error(f"Failed to write search index: {e}")

        logging.info(f"✓ Documentation generated to {self.output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Generate documentation from ontology")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/wiki.yaml"),
        help="Path to docs configuration file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./tmp/wiki/"),
        help="Override output directory",
    )
    args = parser.parse_args()

    if not args.config.exists():
        logging.log.error(f"Config file not found: {args.config}")
        return 1

    gen = WikiGenerator(args.config)
    if args.output:
        gen.output_dir = args.output

    gen.generate_all()
    return 0


if __name__ == "__main__":
    exit(main())
