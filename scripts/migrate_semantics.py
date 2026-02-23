#!/usr/bin/env python3
"""Migrate literal motif:hasSemantics values to motif:Sem_<Motif> IRIs and generate ttl/motifs/semantics.ttl.

Usage:
  python scripts/migrate_semantics.py [--apply]

Without --apply this performs a dry-run and reports planned replacements.
"""
import re
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
TTL_DIR = ROOT / 'ttl'
SEM_FILE = TTL_DIR / 'motifs' / 'semantics.ttl'

sem_map = {}
re_has_sem = re.compile(r'motif:hasSemantics\s+"([^"]+)"\s*;')
re_subject = re.compile(r'^\s*(motif:\w+)')

files_to_edit = []

for p in TTL_DIR.rglob('*.ttl'):
    if p.name == 'semantics.ttl':
        continue
    text = p.read_text()
    if 'motif:hasSemantics "' in text:
        files_to_edit.append(p)

planned = []

for p in files_to_edit:
    lines = p.read_text().splitlines()
    for i, ln in enumerate(lines):
        if 'motif:hasSemantics' in ln and '"' in ln:
            m = re_has_sem.search(ln)
            if not m:
                continue
            sem_text = m.group(1).strip()
            # find subject by looking up to 10 lines above for motif:Name
            subj = None
            for j in range(i, max(-1, i-11), -1):
                s = lines[j]
                msub = re_subject.match(s)
                if msub:
                    candidate = msub.group(1)  # e.g., motif:FeedbackLoop
                    subj = candidate.split(':',1)[1]
                    break
            if not subj:
                # fallback: construct slug from sem_text
                subj = re.sub(r'[^A-Za-z0-9]+','_', sem_text)[:40]
            sem_name = f'Sem_{subj}'
            planned.append((p, i, sem_text, subj, sem_name))
            sem_map[sem_name] = sem_text

if not planned:
    print('No literal motif:hasSemantics occurrences found. Nothing to do.')
    exit(0)

print('Found %d occurrences to migrate across %d files' % (len(planned), len(set(p for p,_,_,_,_ in planned))))
for p,i,sem_text,subj,sem_name in planned[:20]:
    print('-', p.relative_to(ROOT), '->', sem_name, ':', repr(sem_text[:80]))

ap = argparse.ArgumentParser()
ap.add_argument('--apply', action='store_true')
args = ap.parse_args()

if not args.apply:
    print('\nDry-run mode: to apply changes, re-run with --apply')
    exit(0)

# Apply changes: 1) write semantics.ttl, 2) replace occurrences in files

# Write semantics file
lines_out = [
    '@prefix skos: <http://www.w3.org/2004/02/skos/core#> .',
    '@prefix motif: <https://ns.onnx.cloud/motif#> .',
    '',
    '# Auto-generated semantics resources (migrated from literal hasSemantics)',
]
for sem_name, sem_text in sorted(sem_map.items()):
    lines_out.append(f'motif:{sem_name} a motif:Semantics ;')
    lines_out.append(f'  skos:definition "{sem_text}"@en .')
    lines_out.append('')

SEM_FILE.parent.mkdir(parents=True, exist_ok=True)
SEM_FILE.write_text('\n'.join(lines_out))
print('Wrote', SEM_FILE.relative_to(ROOT))

# Replace in files (make a backup)
for p,i,sem_text,subj,sem_name in planned:
    text = p.read_text()
    old = f'motif:hasSemantics "{sem_text}" ;'
    new = f'motif:hasSemantics motif:{sem_name} ;'
    if old in text:
        text = text.replace(old, new)
        p.write_text(text)
        print('Updated', p.relative_to(ROOT))
    else:
        print('Warning: expected snippet not found in', p)

print('Migration complete. Please run `make shacl` and review any remaining violations.')
