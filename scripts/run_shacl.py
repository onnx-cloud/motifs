#!/usr/bin/env python3
import glob
import sys
import argparse
from pyshacl import validate
from rdflib import Graph

shapes = 'ttl/shacl/motif_shapes.ttl'

parser = argparse.ArgumentParser(description='Run SHACL validation over TTL files.')
parser.add_argument('--skip-opset', action='store_true', help='Skip parsing TTLs under ttl/opset (useful for large problematic opset files)')
args = parser.parse_args()

# Strict parse pass: collect all parse errors across all TTLs
files = glob.glob('ttl/**/*.ttl', recursive=True)
parse_errors = []
G = Graph()
for f in files:
    if args.skip_opset and f.startswith('ttl/opset/'):
        print(f"Skipping {f} (opset) per --skip-opset flag")
        continue
    try:
        G.parse(f, format='ttl')
    except Exception as e:
        parse_errors.append((f, str(e)))

if parse_errors:
    print('Turtle parse errors detected:')
    for f, e in parse_errors:
        print(f'Failed to parse {f}: {e}')
    print('\nSHACL validation aborted due to parse errors')
    sys.exit(2)

# All TTLs parsed successfully, run SHACL
conforms, results_graph, results_text = validate(G, shacl_graph=shapes, shacl_graph_format='ttl', advanced=True, abort_on_error=False)
print(results_text)
if not conforms:
    print('SHACL validation failed')
    sys.exit(1)
print('SHACL validation passed')
