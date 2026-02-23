import re
from pathlib import Path

def test_no_literal_hasConstraint():
    ROOT = Path(__file__).resolve().parents[1]
    ttl_files = list((ROOT / 'ttl').rglob('*.ttl'))
    pattern = re.compile(r'motif:hasConstraint\s+"')
    failures = []
    for p in ttl_files:
        text = p.read_text()
        if pattern.search(text):
            failures.append(str(p.relative_to(ROOT)))
    assert not failures, f'Found literal motif:hasConstraint in files: {failures}'
