"""Fuse snippet generator for motifs.

Queries RDF/TTL ontology via SPARQL to extract motif metadata,
generates .fuse snippet templates for each motif.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import sys
import argparse

# Mustache renderer (pystache)
try:
    import pystache
except Exception:
    pystache = None

from src.rdf_manager import RDFManager

logger = logging.getLogger(__name__)


class FuseGenerator:
    """Generates .fuse snippets from motif ontology."""

    def __init__(self, ttl_dir: Path, sparql_dir: Path, output_dir: Path, template_path: Optional[Path] = None):
        """Initialize Fuse generator.

        Args:
            ttl_dir: Directory containing TTL ontology files
            sparql_dir: Directory containing SPARQL query files
            output_dir: Output directory for .fuse files
            template_path: Optional mustache template for rendering snippets
        """
        self.ttl_dir = Path(ttl_dir)
        self.sparql_dir = Path(sparql_dir)
        self.output_dir = Path(output_dir)
        self.rdf = RDFManager(self.ttl_dir)

        # Load template if provided
        self.template_path = Path(template_path) if template_path else None
        self.template = None
        if self.template_path and self.template_path.exists():
            try:
                self.template = self.template_path.read_text(encoding="utf-8")
                logger.info(f"Loaded template: {self.template_path}")
            except Exception as e:
                logger.warning(f"Failed to read template {self.template_path}: {e}")

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Fuse generator initialized. Output: {self.output_dir}")

    def generate_all_motifs(self) -> int:
        """Generate .fuse snippets for all motifs.

        Returns:
            Number of snippets generated
        """
        # Query all motifs - search recursively for the query file so subdirectories (e.g., sparql/fusion/) are supported
        query_name = "list_all_motifs.sparql"
        query_file = next(self.sparql_dir.rglob(query_name), None)
        if query_file is None or not query_file.exists():
            logger.error(f"Query file not found under {self.sparql_dir}: {query_name}")
            return 0
        else:
            logger.debug(f"Using motifs query: {query_file}")

        try:
            result = self.rdf.execute_query_file(query_file)
            motif_dicts = self.rdf.results_to_dicts(result)
            logger.info(f"Found {len(motif_dicts)} motifs")

            count = 0
            for motif_data in motif_dicts:
                if self._generate_snippet(motif_data):
                    count += 1

            # Always generate categories summary after creating snippets
            try:
                self.generate_categories_summary()
            except Exception as e:
                logger.warning(f"Failed to generate categories summary: {e}")

            logger.info(f"Generated {count} .fuse snippets")
            return count

        except Exception as e:
            logger.error(f"Failed to generate motifs: {e}")
            return 0

    def _generate_snippet(self, motif_data: dict) -> bool:
        """Generate .fuse snippet for a single motif.

        Args:
            motif_data: Dictionary with motif properties from SPARQL result

        Returns:
            True if snippet was created successfully
        """
        try:
            label_raw = motif_data.get("label") or "Unknown"
            label = str(label_raw).lower()
            signature = motif_data.get("signature") or "?→?"
            category = motif_data.get("categoryLabel") or "Uncategorized"

            # Create filename - sanitize label (replace spaces/slashes with underscores)
            safe_label = label.replace(" ", "_").replace("/", "_")
            filename = f"{safe_label}.fuse"
            filepath = self.output_dir / filename

            # Generate snippet content
            definition = (motif_data.get("definition") or "").strip()

            # Try to find an ONNX operator spec matching the motif label (best-effort)
            op_spec = None
            try:
                op_spec = self.rdf.get_operator_spec(motif_data.get("label") or "")
            except Exception:
                op_spec = None

            # Render using template if present and pystache available
            if self.template and pystache is not None:
                context = {
                    "label": label,
                    "label_title": motif_data.get("label") or label_raw,
                    "signature": signature,
                    "category": category,
                    "motif_uri": motif_data.get("motif") or "",
                    "definition": definition,
                    "definition_lines": [l for l in definition.splitlines() if l.strip()],
                    "operator_spec": op_spec,
                }
                try:
                    snippet = pystache.render(self.template, context)
                except Exception as e:
                    logger.warning(f"Template render failed for {label}: {e}")
                    snippet = self._create_snippet_content(
                        label=label,
                        label_title=motif_data.get("label") or label_raw,
                        signature=signature,
                        category=category,
                        motif_uri=motif_data.get("motif") or "",
                        definition=definition,
                        operator_spec=op_spec,
                    )
            else:
                snippet = self._create_snippet_content(
                    label=label,
                    label_title=motif_data.get("label") or label_raw,
                    signature=signature,
                    category=category,
                    motif_uri=motif_data.get("motif") or "",
                    definition=definition,
                    operator_spec=op_spec,
                )

            with open(filepath, "w") as f:
                f.write(snippet)
            logger.debug(f"Created {filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate snippet for motif {motif_data.get('label')}: {e}")
            return False

    @staticmethod
    def _create_snippet_content(
        label: str,
        label_title: str,
        signature: str,
        category: str,
        motif_uri: str = "",
        definition: str = "",
        operator_spec: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create content for a .fuse snippet.

        Args:
            label: Motif name (lowercase)
            label_title: Motif display name
            signature: Input/output signature (e.g., "1→1")
            category: Motif category (e.g., "Linear")
            motif_uri: Full URI of motif in ontology
            definition: Human-readable definition/description from ontology
            operator_spec: Optional structured operator spec (from opset)

        Returns:
            .fuse snippet content
        """
        uri_comment = f"  // URI: {motif_uri}\n" if motif_uri else ""

        # Format definition as comment block, preserving line breaks
        def_block = ""
        if definition:
            def_lines = [line.strip() for line in definition.splitlines() if line.strip()]
            if def_lines:
                def_block = "// Definition:\n"
                for line in def_lines:
                    def_block += f"// {line}\n"
                def_block += "\n"

        # Render operator spec if available
        op_block = ""
        if operator_spec:
            op_block = "// Operator spec (onnx):\n"
            if operator_spec.get("label"):
                op_block += f"//   label: {operator_spec.get('label')}\n"
            if operator_spec.get("domain"):
                op_block += f"//   domain: {operator_spec.get('domain')}\n"
            if operator_spec.get("sinceVersion"):
                op_block += f"//   since: {operator_spec.get('sinceVersion')}\n"
            if operator_spec.get("inputs"):
                op_block += "//   inputs:\n"
                for itm in operator_spec.get("inputs", []):
                    desc = f" {itm.get('desc')}" if itm.get('desc') else ""
                    op_block += f"//     - {itm.get('name')}{desc}\n"
            if operator_spec.get("outputs"):
                op_block += "//   outputs:\n"
                for itm in operator_spec.get("outputs", []):
                    desc = f" {itm.get('desc')}" if itm.get('desc') else ""
                    op_block += f"//     - {itm.get('name')}{desc}\n"
            if operator_spec.get("attributes_raw"):
                attrs = operator_spec.get("attributes_raw")
                op_block += f"//   attributes: {attrs}\n"
            op_block += "\n"

        snippet = f"""// Motif: {label_title}
// Category: {category}
// Signature: {signature}
{uri_comment}{def_block}{op_block}// Description:
// This .fuse snippet demonstrates the '{label_title}' motif pattern.
// It illustrates the computation graph structure and data flow.

fuse {label} {{
    // Input tensors
    input x: Tensor

    // Core computation
    // TODO: Define the computation pattern based on motif semantics

    // Output tensors
    output y: Tensor
}}

// Example usage:
// fuse_graph = {label}(x)
"""
        return snippet

    def generate_categories_summary(self) -> bool:
        """Generate a summary .fuse file listing all categories.

        Returns:
            True if generated successfully
        """
        # Query all motifs to build categories from actual data
        query_name = "list_all_motifs.sparql"
        query_file = next(self.sparql_dir.rglob(query_name), None)
        if query_file is None or not query_file.exists():
            logger.warning(f"Motifs query not found under {self.sparql_dir}: {query_name}")
            return False
        else:
            logger.debug(f"Using motifs query for categories: {query_file}")

        try:
            result = self.rdf.execute_query_file(query_file)
            categories = {}

            for row in result:
                cat_label = row.get("categoryLabel", "Uncategorized")
                motif_label = row.get("label", "Unknown")
                
                if cat_label not in categories:
                    categories[cat_label] = []
                categories[cat_label].append(motif_label)

            # Generate summary file
            summary = "// Motif Categories Summary\n"
            summary += f"// Total motifs: {sum(len(m) for m in categories.values())}\n\n"
            
            for cat in sorted(categories.keys()):
                motifs = sorted(categories[cat])
                summary += f"// {cat}\n"
                summary += f"//   Count: {len(motifs)}\n"
                summary += f"//   Motifs: {', '.join(motifs)}\n\n"

            filepath = self.output_dir / "categories_summary.fuse"
            with open(filepath, "w") as f:
                f.write(summary)

            logger.info(f"Generated categories summary with {len(categories)} categories")
            return True

        except Exception as e:
            logger.error(f"Failed to generate categories summary: {e}")
            return False


def main():
    """CLI entry point for fuse generator."""
    parser = argparse.ArgumentParser(
        description="Generate .fuse snippets from motif ontology"
    )
    parser.add_argument(
        "--ttl-dir",
        type=Path,
        default=Path("ttl"),
        help="Directory containing TTL ontology files",
    )
    parser.add_argument(
        "--sparql-dir",
        type=Path,
        default=Path("sparql"),
        help="Directory containing SPARQL query files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tmp/fuse"),
        help="Output directory for .fuse snippets",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("src/template/fuse-motifs.mustache"),
        help="Path to mustache template for snippet rendering",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Also generate categories summary file",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Generate snippets
    generator = FuseGenerator(
        ttl_dir=args.ttl_dir,
        sparql_dir=args.sparql_dir,
        output_dir=args.output_dir,
        template_path=args.template,
    )

    count = generator.generate_all_motifs()

    if args.summary:
        generator.generate_categories_summary()

    if count > 0:
        print(f"✓ Generated {count} .fuse snippets in {args.output_dir}")
        return 0
    else:
        print(f"✗ No snippets generated", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
