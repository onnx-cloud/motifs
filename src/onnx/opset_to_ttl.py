"""Generate Turtle (TTL) descriptions for ONNX operator schemas.

Writes a single file to `ttl/onnx/opset.ttl` describing each operator
from the installed ONNX Python runtime. Includes inputs, outputs,
attributes (excluding string attributes), and allowed element types
for tensor arguments. Designed to be run from the project root and is
idempotent.
"""
import os
import sys
from datetime import date
from urllib.parse import quote
import re

OUT_DIR = os.path.join("ttl", "opset")


def _ttl_literal(value):
    """Return a TTL literal representation for simple Python values."""
    if value is None:
        return None
    if isinstance(value, bool):
        return ("\"true\"^^xsd:boolean" if value else "\"false\"^^xsd:boolean")
    if isinstance(value, int) and not isinstance(value, bool):
        return f"\"{value}\"^^xsd:integer"
    if isinstance(value, float):
        # Use double for floats
        return f"\"{value}\"^^xsd:double"
    # Fallback to a quoted string. If the string contains newlines, emit a triple-quoted literal.
    s = str(value)
    if '\n' in s:
        # escape triple-quotes inside the content
        s_safe = s.replace('"""', '\\"\\"\\"')
        return f'"""{s_safe}"""'
    return f'"{safe_str(s)}"'
OUT_FILE = os.path.join(OUT_DIR, "onnx.ttl")

PREFIXES = """@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix onnx: <https://ns.onnx.cloud/onnx#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

"""


def safe_str(x):
    s = str(x)
    # Escape backslashes first
    s = s.replace('\\', '\\\\')
    # Escape triple quotes to avoid terminating triple-quoted literals
    s = s.replace('"""', '\\\"\\\"\\\"')
    s = s.replace('"', '\\"')
    # Represent newlines as escape sequences in single-line literals
    s = s.replace('\n', '\\n')
    return s


def main():
    try:
        import onnx
    except Exception as e:
        print("Error: ONNX not available. Install with `pip install onnx`.")
        raise

    # Try to get all schemas using available APIs
    try:
        schemas = list(onnx.defs.get_all_schemas())
    except Exception:
        try:
            schemas = list(onnx.defs.get_all_schemas_with_history())
        except Exception:
            print("Unable to iterate ONNX schemas in this ONNX version.")
            raise

    os.makedirs(OUT_DIR, exist_ok=True)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("""
# ONNX operator schemas — generated from runtime
# generated: %s
# onnx version: %s

""" % (date.today().isoformat(), getattr(onnx, "__version__", "unknown")))
        f.write(PREFIXES)

        seen = set()
        # Sort schemas for reproducible output
        def sort_key(s):
            return (getattr(s, "domain", ""), s.name if hasattr(s, "name") else str(s))

        for s in sorted(schemas, key=sort_key):
            # modern schema objects have .name, .domain, .since_version
            name = getattr(s, "name", None)
            if name is None:
                continue
            domain = getattr(s, "domain", "") or "ai.onnx"
            key = (domain, name)
            if key in seen:
                continue
            seen.add(key)

            since = getattr(s, "since_version", None)

            # Start operator entry
            label = f"onnx:{name}"
            f.write(f"{label} a onnx:Operator ;\n")
            f.write(f"  skos:prefLabel \"{safe_str(name)}\" ;\n")
            # Also include rdfs:label for compatibility with consumers/tests
            f.write(f"  rdfs:label \"{safe_str(name)}\" ;\n")
            # Represent domain as an IRI (encoded) for better machine consumption
            domain_iri = f"https://ns.onnx.cloud/onnx/domain/{quote(domain, safe='')}"
            f.write(f"  onnx:domain <{domain_iri}> ;\n")
            if since is not None:
                try:
                    si = int(since)
                    f.write(f"  onnx:sinceVersion \"{si}\"^^xsd:integer ;\n")
                except Exception:
                    f.write(f"  onnx:sinceVersion \"{safe_str(since)}\" ;\n")
            # Inputs
            in_lines = []
            try:
                inputs = getattr(s, "inputs", [])
                for arg in inputs:
                    arg_name = getattr(arg, "name", "")
                    type_str = getattr(arg, "typeStr", "")
                    opt = getattr(arg, "option", None)
                    opt_flag = "optional" if opt and str(opt).lower().find("optional") != -1 else "required"
                    # map type param to allowed types if present
                    types = []
                    tc = getattr(s, "type_constraints", [])
                    for t in tc:
                        if getattr(t, "type_param_str", None) == type_str:
                            types = getattr(t, "allowed_type_strs", []) or []
                    if not types:
                        types = [type_str] if type_str else []
                    in_lines.append(f"{arg_name}: {','.join(types)} ({opt_flag})")
            except Exception:
                pass

            if in_lines:
                # Write structured input blank nodes for machine consumption
                for il in in_lines:
                    try:
                        name_part, rest = il.split(":", 1)
                        types_part = ""
                        req = False
                        if "(" in rest:
                            types_raw, maybe_req = rest.split("(", 1)
                            types_part = types_raw.strip()
                            if "required" in maybe_req:
                                req = True
                        else:
                            types_part = rest.strip()
                    except Exception:
                        name_part = il
                        types_part = ""
                        req = False

                    f.write("  onnx:hasInput [ a onnx:OperatorInput ; onnx:name \"" + safe_str(name_part.strip()) + "\" ;")
                    if types_part:
                        f.write(" onnx:types \"" + safe_str(types_part) + "\" ;")
                    f.write(" onnx:required \"" + ("true" if req else "false") + "\"^^xsd:boolean ] ;\n")

            # Outputs
            out_lines = []
            try:
                outputs = getattr(s, "outputs", [])
                for arg in outputs:
                    arg_name = getattr(arg, "name", "")
                    type_str = getattr(arg, "typeStr", "")
                    tc = getattr(s, "type_constraints", [])
                    types = []
                    for t in tc:
                        if getattr(t, "type_param_str", None) == type_str:
                            types = getattr(t, "allowed_type_strs", []) or []
                    if not types:
                        types = [type_str] if type_str else []
                    out_lines.append(f"{arg_name}: {','.join(types)}")
            except Exception:
                pass

            if out_lines:
                for ol in out_lines:
                    try:
                        name_part, rest = ol.split(":", 1)
                        types_part = rest.strip()
                    except Exception:
                        name_part = ol
                        types_part = ""
                    f.write("  onnx:hasOutput [ a onnx:OperatorOutput ; onnx:name \"" + safe_str(name_part.strip()) + "\" ;")
                    if types_part:
                        f.write(" onnx:types \"" + safe_str(types_part) + "\" ;")
                    f.write(" ] ;\n")

            # Attributes (exclude string attributes)
            attr_lines = []
            try:
                attrs = getattr(s, "attributes", {})
                if isinstance(attrs, dict):
                    items = attrs.items()
                else:
                    items = list(attrs)
                for k, v in items:
                    # v may be an OpSchema.Attribute
                    attr_type = getattr(v, "type", None)
                    # Some runtimes expose enum int values; try to get name
                    attr_type_name = None
                    try:
                        attr_type_name = getattr(v, "type", None)
                        # if enum object
                        if hasattr(attr_type_name, "name"):
                            attr_type_name = attr_type_name.name
                        elif isinstance(attr_type_name, int):
                            # map ints to rough names using AttributeProto enum if available
                            from onnx import AttributeProto

                            mapping = {getattr(AttributeProto, n): n for n in dir(AttributeProto) if n.isupper()}
                            attr_type_name = mapping.get(attr_type_name, str(attr_type_name))
                    except Exception:
                        attr_type_name = str(attr_type)

                    # Skip string attributes
                    if attr_type_name and str(attr_type_name).lower().find("string") != -1:
                        continue

                    default = getattr(v, "default_value", None)
                    # Keep the raw default where possible for typed TTL emission; try to extract numeric values
                    default_val = None
                    if default is not None:
                        try:
                            if isinstance(default, (int, float, bool)):
                                default_val = default
                            else:
                                dstr = str(default)
                                # Try to extract float 'f: 1.23' or int 'i: 2' patterns common in AttributeProto repr
                                m_f = re.search(r"\bf:\s*([+-]?[0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)", dstr)
                                m_i = re.search(r"\bi:\s*([+-]?[0-9]+)", dstr)
                                if m_f:
                                    default_val = float(m_f.group(1))
                                elif m_i:
                                    default_val = int(m_i.group(1))
                                elif dstr.strip().lower() in ("true", "false"):
                                    default_val = dstr.strip().lower() == "true"
                                else:
                                    default_val = dstr
                        except Exception:
                            default_val = str(default)
                    attr_lines.append((k, attr_type_name, default_val))
            except Exception:
                try:
                    # older API: s.attributes is dict of name->AttributeProto
                    for k, v in getattr(s, "attributes", {}).items():
                        # best-effort
                        tname = getattr(v, "type", "")
                        if isinstance(tname, int):
                            tname = str(tname)
                        if str(tname).lower().find("string") != -1:
                            continue
                        attr_lines.append((k, tname, ""))
                except Exception:
                    pass

            if attr_lines:
                for (attr_name, attr_type, default_raw) in attr_lines:
                    f.write("  onnx:hasAttribute [ a onnx:OperatorAttribute ; onnx:name \"" + safe_str(attr_name) + "\" ;")
                    if attr_type:
                        f.write(" onnx:attrType \"" + safe_str(str(attr_type)) + "\" ;")
                    if default_raw is not None:
                        lit = _ttl_literal(default_raw)
                        if lit is not None:
                            f.write(" onnx:default " + lit + " ;")
                    f.write(" ] ;\n")

            # Close entry
            f.write("  .\n\n")

            # Write per-operator TTL file (one file per operator) so consumers
            # can track operators individually. Use domain sanitized for path.
            try:
                domain_safe = domain.replace('.', '_').replace('/', '_')
                op_dir = os.path.join("ttl", "onnx", "operators", domain_safe)
                os.makedirs(op_dir, exist_ok=True)
                op_path = os.path.join(op_dir, f"{name}.ttl")
                with open(op_path, "w", encoding="utf-8") as opf:
                    opf.write("""
# ONNX operator schema — per-operator file
# generated: %s
# onnx version: %s

""" % (date.today().isoformat(), getattr(onnx, "__version__", "unknown")))
                    opf.write(PREFIXES)
                    opf.write(f"onnx:{name} a onnx:Operator ;\n")
                    opf.write(f"  rdfs:label \"{safe_str(name)}\" ;\n")
                    domain_iri = f"https://ns.onnx.cloud/onnx/domain/{quote(domain, safe='')}"
                    opf.write(f"  onnx:domain <{domain_iri}> ;\n")
                    if since is not None:
                        s_val = str(since).strip()
                        if s_val.isdigit():
                            opf.write(f"  onnx:sinceVersion \"{int(s_val)}\"^^xsd:integer ;\n")
                        else:
                            try:
                                opf.write(f"  onnx:sinceVersion \"{int(float(s_val))}\"^^xsd:integer ;\n")
                            except Exception:
                                opf.write(f"  onnx:sinceVersion \"{safe_str(since)}\" ;\n")
                    # Inputs as structured blank nodes for better machine consumption
                    for il in in_lines:
                        try:
                            name_part, rest = il.split(":", 1)
                            types_part = ""
                            req = False
                            if "(" in rest:
                                types_raw, maybe_req = rest.split("(", 1)
                                types_part = types_raw.strip()
                                if "required" in maybe_req:
                                    req = True
                            else:
                                types_part = rest.strip()
                        except Exception:
                            name_part = il
                            types_part = ""
                            req = False
                        opf.write(f"  onnx:hasInput [ a onnx:OperatorInput ; onnx:name \"{safe_str(name_part.strip())}\" ;")
                        if types_part:
                            opf.write(f" onnx:types \"{safe_str(types_part)}\" ;")
                        opf.write(f" onnx:required \"{('true' if req else 'false')}\"^^xsd:boolean ] ;\n")
                    for ol in out_lines:
                        try:
                            name_part, rest = ol.split(":", 1)
                            types_part = rest.strip()
                        except Exception:
                            name_part = ol
                            types_part = ""
                        opf.write(f"  onnx:hasOutput [ a onnx:OperatorOutput ; onnx:name \"{safe_str(name_part.strip())}\" ;")
                        if types_part:
                            opf.write(f" onnx:types \"{safe_str(types_part)}\" ;")
                        opf.write(" ] ;\n")
                    for (attr_name, attr_type, default_raw) in attr_lines:
                        opf.write(f"  onnx:hasAttribute [ a onnx:OperatorAttribute ; onnx:name \"{safe_str(attr_name)}\" ;")
                        if attr_type:
                            opf.write(f" onnx:attrType \"{safe_str(str(attr_type))}\" ;")
                        if default_raw is not None:
                            lit = _ttl_literal(default_raw)
                            if lit is not None:
                                opf.write(f" onnx:default {lit} ;")
                        opf.write(" ] ;\n")
                    opf.write("  .\n")
            except Exception as e:
                print(f"Warning: could not write per-operator file for {name}: {e}")

    print(f"Wrote operands TTL to {OUT_FILE}")

    # Also write a copy to the canonical path expected by tests: ttl/onnx/opset.ttl
    try:
        canonical_dir = os.path.join("ttl", "onnx")
        os.makedirs(canonical_dir, exist_ok=True)
        canonical_path = os.path.join(canonical_dir, "opset.ttl")
        with open(OUT_FILE, "r", encoding="utf-8") as srcf:
            data = srcf.read()
        with open(canonical_path, "w", encoding="utf-8") as dstf:
            dstf.write(data)
        print(f"Also wrote canonical opset to {canonical_path}")
    except Exception as e:
        print(f"Warning: could not write canonical opset copy: {e}")


if __name__ == "__main__":
    main()
