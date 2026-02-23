"""Modular RDF/TTL manager for motif ontology queries.

Loads and manages RDF graph from TTL files, provides interface for
executing named SPARQL queries and retrieving results in structured format.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
try:
    import rdflib
    from rdflib import Namespace, Literal
    from rdflib.query import Result
except Exception:  # rdflib not available in minimal test env, provide lightweight stubs
    from types import SimpleNamespace

    class _DummyGraph:
        def __init__(self):
            self._triples = []

        def parse(self, *args, **kwargs):
            return None

        def query(self, *args, **kwargs):
            return []

        def predicate_objects(self, subj):
            return iter(())

        def objects(self, subj=None, pred=None):
            return iter(())

        def triples(self, pattern):
            return iter(())

        def subjects(self):
            return iter(())

        def predicates(self):
            return iter(())

        def __len__(self):
            return 0

    rdflib = SimpleNamespace(Graph=_DummyGraph, URIRef=str, RDFS=SimpleNamespace(label=None, comment=None), Literal=str)
    Namespace = lambda uri: uri
    Literal = str
    Result = list

logger = logging.getLogger(__name__)


def _sanitize_opset_content(text: str) -> str:
    """Sanitize ONNX opset TTL content to collapse multiline attribute blocks.

    This is a best-effort sanitizer that replaces multiline attribute blocks
    with a single-line quoted summary to avoid Turtle parse errors from
    generated operator schemas.
    """
    # Replace multiline onnxop:attributes "..." ; and onnx:default "..." ; blocks with single-line summary
    def repl(m):
        inner = m.group(1)
        # Collapse whitespace and escape internal quotes
        safe = re.sub(r"\s+", " ", inner).replace('"', '\\"')
        return f'onnx:attributes "{safe}" ;'

    def repl_default(m):
        inner = m.group(1)
        safe = re.sub(r"\s+", " ", inner).replace('"', '\\"')
        return f'onnx:default "{safe}" ;'

    # Match patterns like: onnx:attributes "..." ; or onnx:default "..." ; spanning multiple lines
    sanitized = re.sub(r'onnx:attributes\s*"([\s\S]*?)"\s*;', repl, text, flags=re.IGNORECASE)
    sanitized = re.sub(r'onnx:default\s*"([\s\S]*?)"\s*;', repl_default, sanitized, flags=re.IGNORECASE)
    return sanitized


class RDFManager:
    """Manages RDF graph loading, querying, and result retrieval."""

    def __init__(self, ttl_dir: Path):
        """Initialize RDF manager with TTL directory.

        Args:
            ttl_dir: Directory containing TTL files to load
        """
        self.ttl_dir = Path(ttl_dir)
        self.graph = rdflib.Graph()
        self.namespaces = {}
        self._load_ttl_files()

    def _load_ttl_files(self) -> None:
        """Load all TTL files from ttl_dir recursively."""
        ttl_files = list(self.ttl_dir.rglob("*.ttl"))
        if not ttl_files:
            logger.warning(f"No TTL files found in {self.ttl_dir}")
            return

        for ttl_file in ttl_files:
            try:
                # Read file text and sanitize any problematic multiline attribute or default blocks
                text = open(ttl_file, "r", encoding="utf-8").read()
                sanitized = _sanitize_opset_content(text)
                if sanitized != text:
                    try:
                        self.graph.parse(data=sanitized, format="turtle")
                        logger.debug(f"Loaded (sanitized) {ttl_file.name}")
                        continue
                    except Exception as e:
                        # If sanitized parsing fails, fall back to parsing the original text
                        logger.debug(f"Sanitized parse failed for {ttl_file.name}: {e}; falling back to original text parse")
                # Try parsing original text
                try:
                    self.graph.parse(data=text, format="turtle")
                    logger.debug(f"Loaded {ttl_file.name}")
                except Exception as e:
                    # As a last resort, have rdflib read from filename (it will open the file itself)
                    self.graph.parse(str(ttl_file), format="turtle")
                    logger.debug(f"Loaded via file path {ttl_file.name}")
            except Exception as e:
                logger.error(f"Failed to load {ttl_file.name}: {e}")

        logger.info(f"Loaded {len(ttl_files)} TTL files, graph has {len(self.graph)} triples")

    def register_namespace(self, prefix: str, uri: str) -> None:
        """Register a namespace for use in queries.

        Args:
            prefix: Prefix name (e.g., 'motif')
            uri: Namespace URI (e.g., 'https://ns.onnx.cloud/motif#')
        """
        self.graph.bind(prefix, Namespace(uri))
        self.namespaces[prefix] = Namespace(uri)
        logger.debug(f"Registered namespace {prefix}: {uri}")

    def execute_query(self, sparql: str) -> Result:
        """Execute SPARQL query on the graph.

        Args:
            sparql: SPARQL query string

        Returns:
            rdflib.query.Result with query results

        Raises:
            Exception: If query fails
        """
        try:
            result = self.graph.query(sparql)
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def execute_query_file(self, query_path: Path) -> Result:
        """Execute SPARQL query from file.

        Args:
            query_path: Path to .sparql file

        Returns:
            rdflib.query.Result with query results
        """
        with open(query_path, "r") as f:
            sparql = f.read()
        logger.debug(f"Executing query from {query_path.name}")
        return self.execute_query(sparql)

    def results_to_dicts(self, result: Result) -> List[Dict[str, Any]]:
        """Convert SPARQL result to list of dictionaries.

        Adds both local name and full URI (as <var>_uri) for URIRef values.

        Args:
            result: SPARQL query result

        Returns:
            List of dicts with column names as keys
        """
        dicts = []
        for row in result:
            row_dict = {}
            for var in result.vars:
                value = row[var]
                # Extract local name from URI if applicable and also include full URI
                if isinstance(value, rdflib.URIRef):
                    local = self._extract_localname(value)
                    row_dict[str(var)] = local
                    row_dict[f"{str(var)}_uri"] = str(value)
                elif isinstance(value, Literal):
                    row_dict[str(var)] = str(value)
                else:
                    row_dict[str(var)] = str(value) if value else None
            dicts.append(row_dict)
        return dicts

    def get_resource_info(self, subject_or_label) -> Optional[Dict[str, Any]]:
        """Return rdfs:label and skos:definition for a subject or label.

        Args:
            subject_or_label: URIRef, Node or label string

        Returns:
            Dict with keys 'label' and 'comment' or None if not found
        """
        subj = None
        if isinstance(subject_or_label, str):
            # Try to find resource by exact label first
            matches = self.find_resources_by_label(subject_or_label)
            if matches:
                subj = matches[0]
            else:
                # Fallback: assume it's a URI string
                try:
                    subj = rdflib.URIRef(subject_or_label)
                except Exception:
                    return None
        else:
            subj = subject_or_label

        label = None
        comment = None
        for o in self.graph.objects(subj, rdflib.RDFS.label):
            label = str(o)
            break
        for o in self.graph.objects(subj, rdflib.RDFS.comment):
            comment = str(o)
            break

        if label or comment:
            return {"label": label, "comment": comment}
        return None

    @staticmethod
    def _extract_localname(uri: rdflib.URIRef) -> str:
        """Extract local name from URIRef.

        Args:
            uri: RDF URIRef

        Returns:
            Local name part of URI (after # or /)
        """
        uri_str = str(uri)
        if "#" in uri_str:
            return uri_str.split("#")[-1]
        return uri_str.split("/")[-1]

    def get_motif_properties(self, motif_uri: str) -> Dict[str, Any]:
        """Get all properties of a motif.

        Args:
            motif_uri: URI reference of the motif

        Returns:
            Dictionary with motif properties
        """
        query = f"""
        PREFIX motif: <https://ns.onnx.cloud/motif#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        
        SELECT ?predicate ?value
        WHERE {{
            ?motif ?predicate ?value .
            FILTER(STR(?motif) = "{motif_uri}")
        }}
        """
        result = self.execute_query(query)
        properties = {}
        for row in result:
            pred = self._extract_localname(row.predicate)
            value = row.value
            if isinstance(value, rdflib.URIRef):
                value = self._extract_localname(value)
            elif isinstance(value, Literal):
                value = str(value)
            properties[pred] = value
        return properties

    def find_resources_by_label(self, label: str) -> List[object]:
        """Find subjects with exact rdfs:label equal to the provided label.

        Args:
            label: Literal label to match

        Returns:
            List of subject nodes matching the label
        """
        results = []
        for subj, _, obj in self.graph.triples((None, rdflib.RDFS.label, None)):
            if str(obj) == label:
                results.append(subj)
        return results

    def _parse_io_list(self, s: str) -> List[Dict[str, str]]:
        """Parse an ONNX-style inputs/outputs string into structured list.

        Example:
            "A:  (required); B:  (required)" ->
            [{"name": "A", "desc": "(required)"}, {"name": "B", "desc": "(required)"}]
        """
        parts = [p.strip() for p in s.split(";") if p.strip()]
        items = []
        for p in parts:
            if ":" in p:
                name, rest = p.split(":", 1)
                items.append({"name": name.strip(), "desc": rest.strip()})
            else:
                items.append({"name": p, "desc": ""})
        return items

    def get_operator_spec(self, subject_or_label) -> Optional[Dict[str, Any]]:
        """Return a structured operator spec for an ONNX operator resource.

        Args:
            subject_or_label: RDF subject node or operator label string

        Returns:
            Dict with keys: label, domain, sinceVersion, inputs (list), outputs (list), attributes (str)
        """
        logger.debug(f"get_operator_spec called with argument: {subject_or_label!r}")
        # Resolve label to subject if needed
        subj = None
        # rdflib.URIRef is a subclass of str; check for URIRef first
        if isinstance(subject_or_label, rdflib.URIRef):
            subj = subject_or_label
        elif isinstance(subject_or_label, str):
            matches = self.find_resources_by_label(subject_or_label)
            if not matches:
                logger.debug("get_operator_spec: no matches for label")
                return None
            subj = matches[0]
        else:
            subj = subject_or_label
        logger.debug(f"get_operator_spec: resolved subj = {subj!r}")

        # Debug: log subject we're examining
        logger.debug(f"get_operator_spec: resolving subject {subj}")
        # Collect candidate literals for common predicates used in operator specs
        label = None
        domain = None
        domain_iri = None
        since = None
        inputs = None
        outputs = None
        attributes = None

        inputs_struct: List[Dict[str, Any]] = []
        outputs_struct: List[Dict[str, Any]] = []
        attributes_struct: List[Dict[str, Any]] = []

        for p, o in self.graph.predicate_objects(subj):
            local = self._extract_localname(p)
            if local == "label" and label is None:
                label = str(o)
            elif local in ("domain", "opset_domain") and domain is None:
                # domain may be an IRI or a literal; if it's an IRI, capture both IRI and a readable label
                if isinstance(o, rdflib.URIRef):
                    domain_iri = str(o)
                    try:
                        from urllib.parse import urlparse, unquote

                        parsed = urlparse(domain_iri)
                        candidate = parsed.fragment or parsed.path.split("/")[-1]
                        candidate = unquote(candidate).replace("_", ".")
                        domain = candidate
                    except Exception:
                        domain = str(o)
                else:
                    domain = str(o)
            elif local in ("sinceVersion", "since") and since is None:
                since = str(o)
            elif local == "inputs" and inputs is None:
                inputs = str(o)
            elif local == "outputs" and outputs is None:
                outputs = str(o)
            elif local == "attributes" and attributes is None:
                attributes = str(o)
            elif local == "hasInput":
                # o is a blank node or resource describing the input
                inp: Dict[str, Any] = {}
                for ip, io in self.graph.predicate_objects(o):
                    il = self._extract_localname(ip)
                    if il in ("name", "label"):
                        inp["name"] = str(io)
                    elif il in ("types", "type"):
                        inp["types"] = str(io)
                    elif il in ("required", "isRequired"):
                        if isinstance(io, Literal):
                            # Literal to Python bool
                            try:
                                inp["required"] = bool(io)
                            except Exception:
                                inp["required"] = str(io).lower() in ("true", "1")
                        else:
                            inp["required"] = str(io).lower() in ("true", "1")
                    elif il in ("desc", "description"):
                        inp["desc"] = str(io)
                inputs_struct.append(inp)
            elif local == "hasOutput":
                outp: Dict[str, Any] = {}
                for op, oo in self.graph.predicate_objects(o):
                    ol = self._extract_localname(op)
                    if ol in ("name", "label"):
                        outp["name"] = str(oo)
                    elif ol in ("types", "type"):
                        outp["types"] = str(oo)
                    elif ol in ("desc", "description"):
                        outp["desc"] = str(oo)
                outputs_struct.append(outp)
            elif local == "hasAttribute":
                attr: Dict[str, Any] = {}
                for ap, ao in self.graph.predicate_objects(o):
                    al = self._extract_localname(ap)
                    if al in ("name", "label"):
                        attr["name"] = str(ao)
                    elif al in ("attrType", "type"):
                        attr["type"] = str(ao)
                    elif al in ("default", "default_value"):
                        # Convert typed RDF Literals to Python values where possible
                        if isinstance(ao, Literal):
                            try:
                                attr["default"] = ao.toPython()
                            except Exception:
                                attr["default"] = str(ao)
                        else:
                            # Best-effort parse common embedded representations
                            s = str(ao)
                            m_f = re.search(r"\bf:\s*([+-]?[0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)", s)
                            m_i = re.search(r"\bi:\s*([+-]?[0-9]+)", s)
                            if m_f:
                                attr["default"] = float(m_f.group(1))
                            elif m_i:
                                attr["default"] = int(m_i.group(1))
                            elif s.strip().lower() in ("true", "false"):
                                attr["default"] = s.strip().lower() == "true"
                            else:
                                attr["default"] = s
                attributes_struct.append(attr)

        # Prefer structured blank-node representations if present, otherwise fall back
        inputs_parsed = self._parse_io_list(inputs) if inputs else []
        outputs_parsed = self._parse_io_list(outputs) if outputs else []

        spec = {
            "label": label,
            "domain": domain,
            "domain_iri": domain_iri,
            "sinceVersion": None,
            "inputs_raw": inputs,
            "outputs_raw": outputs,
            "attributes_raw": attributes,
            # Use structured parsed nodes when available
            "inputs": inputs_struct if inputs_struct else inputs_parsed,
            "outputs": outputs_struct if outputs_struct else outputs_parsed,
            "attributes": attributes_struct if attributes_struct else (attributes or []),
        }

        # coerce sinceVersion to int if possible
        if since is not None:
            try:
                spec["sinceVersion"] = int(since)
            except Exception:
                spec["sinceVersion"] = str(since)

        logger.debug(f"get_operator_spec: built spec for {subj}: {spec}")

        # If find_resources_by_label returned both motif semantics and onnx operator,
        # prefer the onnx operator subject if available
        # (caller passed a label string; matches may include multiple subjects)
        if isinstance(subject_or_label, str):
            matches = self.find_resources_by_label(subject_or_label)
            # Prefer subject whose URI contains 'onnx' or 'ops'
            from urllib.parse import urlparse
            for m in matches:
                parsed = urlparse(str(m))
                path_parts = [p for p in parsed.path.split('/') if p]
                # Prefer subjects whose path contains 'onnx' or 'ops' (e.g., /onnx#Add)
                if any(seg.lower() in ("onnx", "ops") for seg in path_parts):
                    logger.debug(f"get_operator_spec: preferring ONNX subject {m}")
                    # recompute spec for preferred subject
                    return self.get_operator_spec(m)

        return spec

    def graph_stats(self) -> Dict[str, int]:
        """Get basic statistics about the loaded graph.

        Returns:
            Dictionary with graph statistics
        """
        return {
            "triples": len(self.graph),
            "subjects": len(set(self.graph.subjects())),
            "predicates": len(set(self.graph.predicates())),
            "objects": len(set(self.graph.objects())),
        }
