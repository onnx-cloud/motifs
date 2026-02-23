#!/usr/bin/env python3
"""Migrate literal motif:hasConstraint values to motif:Constraint_<Motif> IRIs and append to ttl/motifs/semantics.ttl (or new constraints.ttl).

Usage:
  python scripts/migrate_constraints.py [--apply]

This will create ttl/motifs/constraints.ttl with motif:Constraint_<Name> definitions and replace literal hasConstraint values with IRIs.
"""
import re
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
TTL_DIR = ROOT / 'ttl'
CONSTRAINTS_FILE = TTL_DIR / 'motifs' / 'constraints.ttl'

re_has_con = re.compile(r'motif:hasConstraint\s+"([^"]+)"\s*([;\.])')
re_subject = re.compile(r'^\s*(motif:\w+)')

files_to_edit = []
for p in TTL_DIR.rglob('*.ttl'):
    if p.name == 'constraints.ttl':
        continue
    text = p.read_text()
    if 'motif:hasConstraint "' in text:
        files_to_edit.append(p)

planned = []
con_map = {}
for p in files_to_edit:
    lines = p.read_text().splitlines()
    for i, ln in enumerate(lines):
        if 'motif:hasConstraint' in ln and '"' in ln:
            m = re_has_con.search(ln)
            if not m:
                continue
            con_text = m.group(1).strip()
            punct = m.group(2)
            subj = None
            for j in range(i, max(-1, i-11), -1):
                s = lines[j]
                msub = re_subject.match(s)
                if msub:
                    candidate = msub.group(1)
                    subj = candidate.split(':',1)[1]
                    break
            if not subj:
                subj = re.sub(r'[^A-Za-z0-9]+','_', con_text)[:40]
            con_name = f'Constraint_{subj}'
            planned.append((p, i, con_text, subj, con_name, punct))
            con_map[con_name] = con_text

if not planned:
    print('No literal motif:hasConstraint occurrences found. Nothing to do.')
    exit(0)

print('Found %d occurrences to migrate across %d files' % (len(planned), len(set(p for p,_,_,_,_ in planned))))
for p,i,con_text,subj,con_name in planned[:20]:
    print('-', p.relative_to(ROOT), '->', con_name, ':', repr(con_text[:80]))

ap = argparse.ArgumentParser()
ap.add_argument('--apply', action='store_true')
args = ap.parse_args()

if not args.apply:
    print('\nDry-run mode: to apply changes, re-run with --apply')
    exit(0)

# Write constraints file
# Merge with existing constraints file if present, avoid duplicating
CONSTRAINTS_FILE.parent.mkdir(parents=True, exist_ok=True)
existing = CONSTRAINTS_FILE.read_text() if CONSTRAINTS_FILE.exists() else ''
lines_out = []
if not existing:
    lines_out.extend([
        '@prefix skos: <http://www.w3.org/2004/02/skos/core#> .',
        '@prefix motif: <https://ns.onnx.cloud/motif#> .',
        '',
        '# Auto-generated constraint resources (migrated from literal hasConstraint)',
    ])

added = 0
for con_name, con_text in sorted(con_map.items()):
    if f'motif:{con_name}' in existing:
        continue
    lines_out.append(f'motif:{con_name} a motif:Constraint ;')
    lines_out.append(f'  skos:definition "{con_text}"@en .')
    lines_out.append('')
    added += 1

if lines_out:
    # Append to file
    with CONSTRAINTS_FILE.open('a') as fh:
        if not existing:
            fh.write('\n'.join(lines_out))
        else:
            fh.write('\n# Appended by migrate_constraints.py\n')
            fh.write('\n'.join(lines_out))
    if existing:
        print('Appended %d new entries to %s' % (added, CONSTRAINTS_FILE.relative_to(ROOT)))
    else:
        print('Wrote', CONSTRAINTS_FILE.relative_to(ROOT))
else:
    print('No new entries to add to', CONSTRAINTS_FILE.relative_to(ROOT))

# Replace in files
for p,i,con_text,subj,con_name,punct in planned:
    text = p.read_text()
    old = f'motif:hasConstraint "{con_text}" {punct}'
    new = f'motif:hasConstraint motif:{con_name} {punct}'
    if old in text:
        text = text.replace(old, new)
        p.write_text(text)
        print('Updated', p.relative_to(ROOT))
    else:
        # fallback: replace any occurrence matching pattern
        pattern = re.compile(re.escape(f'motif:hasConstraint "{con_text}"') + r'\s*[;\.]')
        new2 = f'motif:hasConstraint motif:{con_name} {punct}'
        newtext = pattern.sub(new2, text)
        if newtext != text:
            p.write_text(newtext)
            print('Updated (regex) ', p.relative_to(ROOT))
        else:
            print('Warning: expected snippet not found in', p)
print('Migration complete. Please run `make shacl` and review any remaining violations.')
