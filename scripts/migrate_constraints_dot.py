#!/usr/bin/env python3
"""Second-pass fixer: convert motif:hasConstraint "..." . (dot-terminated) to IRIs.
Appends new constraints to ttl/motifs/constraints.ttl (if missing).
"""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
TTL_DIR = ROOT / 'ttl'
CONSTRAINTS_FILE = TTL_DIR / 'motifs' / 'constraints.ttl'

re_has_con_dot = re.compile(r'motif:hasConstraint\s+"([^"]+)"\s*\.')
re_subject = re.compile(r'^\s*(motif:\w+)')

planned = []
con_map = {}
for p in TTL_DIR.rglob('*.ttl'):
    text = p.read_text()
    for m in re_has_con_dot.finditer(text):
        con_text = m.group(1).strip()
        # locate subject by scanning up
        lines = text.splitlines()
        idx = text[:m.start()].count('\n')
        subj = None
        for j in range(idx, max(-1, idx-11), -1):
            s = lines[j]
            msub = re_subject.match(s)
            if msub:
                candidate = msub.group(1)
                subj = candidate.split(':',1)[1]
                break
        if not subj:
            subj = re.sub(r'[^A-Za-z0-9]+','_', con_text)[:40]
        con_name = f'Constraint_{subj}'
        planned.append((p, con_text, subj, con_name))
        con_map[con_name] = con_text

if not planned:
    print('No dot-terminated motif:hasConstraint literals found.')
    exit(0)

print('Found %d dot-terminated constraint literals to migrate.' % len(planned))
for p,con_text,subj,con_name in planned[:20]:
    print('-', p.relative_to(ROOT), '->', con_name, ':', repr(con_text[:80]))

# Append new constraints if not present
existing = CONSTRAINTS_FILE.read_text() if CONSTRAINTS_FILE.exists() else ''
new_entries = []
for con_name,con_text in con_map.items():
    if f'motif:{con_name}' not in existing:
        new_entries.append(f'motif:{con_name} a motif:Constraint ;\n  skos:definition "{con_text}"@en .\n')

if new_entries:
    CONSTRAINTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CONSTRAINTS_FILE.open('a') as fh:
        fh.write('\n# Appended by migrate_constraints_dot.py\n')
        for e in new_entries:
            fh.write(e)
    print('Appended %d entries to %s' % (len(new_entries), CONSTRAINTS_FILE.relative_to(ROOT)))

# Replace occurrences in files
for p,con_text,subj,con_name in planned:
    text = p.read_text()
    old = f'motif:hasConstraint "{con_text}" .'
    new = f'motif:hasConstraint motif:{con_name} .'
    if old in text:
        text = text.replace(old, new)
        p.write_text(text)
        print('Updated', p.relative_to(ROOT))
    else:
        # fallback: replace any occurrence matching pattern
        text2 = re.sub(re.escape(f'motif:hasConstraint "{con_text}"') + r'\s*\.', f'motif:hasConstraint motif:{con_name} .', text)
        if text2 != text:
            p.write_text(text2)
            print('Updated (regex) ', p.relative_to(ROOT))
        else:
            print('Warning: could not replace in', p)

print('Second-pass migration complete. Run `make shacl` again.')
