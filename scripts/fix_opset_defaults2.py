#!/usr/bin/env python3
from pathlib import Path
p = Path('ttl/opset/onnx.ttl')
s = p.read_text()
new = s.replace('onnx:default """"', 'onnx:default ""')
if new != s:
    p.write_text(new)
    print('Replaced quadruple quotes with double quotes in onnx.ttl')
else:
    print('No quadruple quotes found')
