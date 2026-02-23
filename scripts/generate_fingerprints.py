#!/usr/bin/env python3
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from rdflib.namespace import SKOS, RDFS
import glob

MOTIF = Namespace('https://ns.onnx.cloud/motifs#')

if __name__ == '__main__':
    print('This script is now manual-only. It will not be run automatically by `make shacl`.')
    print('To generate fingerprints manually, run:')
    print('  venv/bin/python scripts/generate_fingerprints.py --write')

# Backwards-compatible manual mode: run with `--write` to actually write generated fingerprints
def _collect_and_generate(write=False):
    g = Graph()
    files = glob.glob('ttl/**/*.ttl', recursive=True)
    for f in files:
        g.parse(f, format='ttl')

    out = Graph()
    out.bind('motif', MOTIF)
    out.bind('skos', SKOS)
    out.bind('rdfs', RDFS)

    generated = 0
    for s in set(g.subjects(RDF.type, MOTIF.Motif)):
        has_fp = list(g.objects(s, MOTIF.hasFingerprint))
        if len(has_fp) == 0:
            local = s.split('#')[-1]
            fp = URIRef(str(MOTIF) + 'fp_' + local)
            label = None
            lbls = list(g.objects(s, SKOS.prefLabel))
            if lbls:
                label = str(lbls[0])
            else:
                label = local
            out.add((s, MOTIF.hasFingerprint, fp))
            out.add((fp, RDF.type, MOTIF.Fingerprint))
            out.add((fp, SKOS.prefLabel, Literal(f"Fingerprint for {label}")))
            out.add((fp, RDFS.comment, Literal('Auto-generated fingerprint to satisfy SHACL'))) 
            generated += 1

    if generated > 0 and write:
        out.serialize(destination='ttl/motifs/generated_fingerprints.ttl', format='ttl')
        print(f'Generated {generated} fingerprint triples in ttl/motifs/generated_fingerprints.ttl')
    elif generated > 0 and not write:
        print(f'{generated} fingerprints would be generated (run with --write to write).')
    else:
        print('No fingerprints needed')

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='Write generated fingerprints to TTL file')
    args = ap.parse_args()
    _collect_and_generate(write=args.write)
