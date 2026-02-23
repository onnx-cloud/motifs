#!/usr/bin/env python3
from pathlib import Path
p = Path('ttl/shacl/motif_shapes.ttl')
s = p.read_bytes()
old = b'Values of motif:* predicates must be IRIs, not literal\ns.'
if old in s:
    s = s.replace(old, b'Values of motif:* predicates must be IRIs, not literals.')
    p.write_bytes(s)
    print('Fixed split sh:message in motif_shapes.ttl')
else:
    print('No split message found')
