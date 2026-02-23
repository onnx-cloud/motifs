#!/usr/bin/env python3
"""Migrate literal motif:hasSemantics and motif:hasConstraint values to IRIs.

Usage:
  venv/bin/python scripts/migrate_semantics_constraints.py [--apply]

If --apply is provided, files are edited in-place and a TTL file
`ttl/motifs/generated_semantics_constraints.ttl` is written with the
new `motif:Sem_*` and `motif:Constraint_*` nodes. Without --apply, a
report is printed showing proposed changes.
"""
from pathlib import Path
import re
import argparse

ROOT = Path('.')
TTL_GLOB = 'ttl/**/*.ttl'
OUT = Path('ttl/motifs/generated_semantics_constraints.ttl')

re_sem = re.compile(r'(motif:hasSemantics)\s+(""".*?"""|".*?"(?:@[a-zA-Z\-]+)?)(\s*;)', flags=re.S)
re_con = re.compile(r'(motif:hasConstraint)\s+(""".*?"""|".*?"(?:@[a-zA-Z\-]+)?)(\s*;)', flags=re.S)

def slugify(s):
    s = s.strip()
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    if len(s) > 60:
        s = s[:60].rstrip("_")
    return s or 'x'


def find_literals():
    files = list(ROOT.glob(TTL_GLOB))
    sem_map = {}
    con_map = {}
    occurrences = []
    for f in files:
        try:
            text = f.read_text(encoding='utf-8')
        except Exception:
            continue
        for m in re_sem.finditer(text):
            lit = m.group(2)
            occurrences.append((f, 'sem', m.group(0), lit))
            if lit not in sem_map:
                slug = 'Sem_' + slugify(lit.replace('"', '').replace('"""', ''))
                # ensure uniqueness
                base = slug
                i = 1
                while slug in sem_map.values():
                    slug = f"{base}_{i}"
                    i += 1
                sem_map[lit] = slug
        for m in re_con.finditer(text):
            lit = m.group(2)
            occurrences.append((f, 'con', m.group(0), lit))
            if lit not in con_map:
                slug = 'Constraint_' + slugify(lit.replace('"', '').replace('"""', ''))
                base = slug
                i = 1
                while slug in con_map.values():
                    slug = f"{base}_{i}"
                    i += 1
                con_map[lit] = slug
    return sem_map, con_map, occurrences


def generate_definitions(sem_map, con_map):
    lines = []
    lines.append('@prefix motif: <https://ns.onnx.cloud/motifs#> .')
    lines.append('@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .')
    lines.append('@prefix skos: <http://www.w3.org/2004/02/skos/core#> .')
    lines.append('')
    for lit, slug in sem_map.items():
        label = lit.strip()
        lines.append(f'motif:{slug} a motif:Semantics ;')
        lines.append(f'  skos:prefLabel {label} ;')
        lines.append(f'  rdfs:comment "Auto-generated from literal motif:hasSemantics; verify text and usage."@en .')
        lines.append('')
    for lit, slug in con_map.items():
        label = lit.strip()
        lines.append(f'motif:{slug} a motif:Constraint ;')
        lines.append(f'  skos:prefLabel {label} ;')
        lines.append(f'  rdfs:comment "Auto-generated from literal motif:hasConstraint; verify text and usage."@en .')
        lines.append('')
    return '\n'.join(lines)


def apply_changes(sem_map, con_map, occurrences):
    # Edit files in place
    updated_files = set()
    for f, typ, original, lit in occurrences:
        txt = f.read_text(encoding='utf-8')
        if typ == 'sem':
            slug = sem_map[lit]
            replacement = f'motif:hasSemantics motif:{slug} ;'
        else:
            slug = con_map[lit]
            replacement = f'motif:hasConstraint motif:{slug} ;'
        if original in txt:
            txt2 = txt.replace(original, replacement)
            if txt2 != txt:
                f.write_text(txt2, encoding='utf-8')
                updated_files.add(str(f))
    # write definitions
    defs = generate_definitions(sem_map, con_map)
    if defs.strip():
        OUT.write_text(defs, encoding='utf-8')
    return sorted(updated_files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Apply changes in place and write generated TTL')
    args = ap.parse_args()

    sem_map, con_map, occurrences = find_literals()
    if not occurrences:
        print('No literal motif:hasSemantics or motif:hasConstraint values found.')
        return

    print(f'Found {len(occurrences)} literal occurrences across files.')
    # list a summary
    for f, typ, original, lit in occurrences:
        kind = 'Semantics' if typ == 'sem' else 'Constraint'
        target = sem_map.get(lit) if typ == 'sem' else con_map.get(lit)
        print(f'{f}: {kind} -> motif:{target} (from {lit.strip()[:60]!r})')

    if args.apply:
        updated = apply_changes(sem_map, con_map, occurrences)
        print('\nApplied changes to files:')
        for u in updated:
            print('-', u)
        print(f'Wrote definitions to {OUT}')
        print('\nPlease review generated semantics/constraints in ttl/motifs/generated_semantics_constraints.ttl and adjust labels/comments to be precise where needed.')
    else:
        print('\nRun with --apply to perform the migration and write definitions.')

if __name__ == '__main__':
    main()
