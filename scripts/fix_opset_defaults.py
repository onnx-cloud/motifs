#!/usr/bin/env python3
import re
from pathlib import Path
p = Path('ttl/opset/onnx.ttl')
s = p.read_text()
# Find onnx:default "..." ; where the string contains newlines
pattern = re.compile(r'(onnx:default\s*")(.+?)("\s*;\s*\])', re.DOTALL)

def repl(m):
    prefix = m.group(1)
    body = m.group(2)
    suffix = m.group(3)
    # If body contains a newline, convert to triple-quoted string
    if '\n' in body:
        # strip leading/trailing whitespace/newlines
        newbody = body.strip('\n')
        # escape triple quotes if any (unlikely)
        newbody = newbody.replace('"""', '\\"\\"\\"')
        return 'onnx:default """' + newbody + '""" ; ]'
    else:
        return m.group(0)

new = pattern.sub(repl, s)
if new != s:
    p.write_text(new)
    print('Fixed onnx:default multiline values in', p)
else:
    print('No fixes necessary')
