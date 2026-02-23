#!/usr/bin/env python3
import re
from pathlib import Path
p=Path('ttl/opset/onnx.ttl')
s=p.read_text()
import re
from pathlib import Path
p=Path('ttl/opset/onnx.ttl')
s=p.read_text()

def repl(m):
    return '"' + m.group(1) + '"'

new=re.sub(r'\"([^\"]+)\"{2,}', repl, s)
if new!=s:
    p.write_text(new)
    print('Fixed stray extra quotes after quoted names')
else:
    print('No stray patterns found')
