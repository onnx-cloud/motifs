# 03 — Motif Models: A Vocabulary for Graphs

Across different neural architectures, certain patterns appear repeatedly: data flow splits and recombines (fork-join), information gating, attention mechanisms, skip connections. These patterns carry semantic significance beyond their syntactic structure.

Motifs are named, formally-defined graph patterns. Each motif has a canonical implementation, a signature describing its input/output types and shapes, and a traceable connection to silicon-native operators.

The value of a motif taxonomy is not novelty but precision. It allows engineers and machines to reason about transformations and optimizations at a higher level, to identify fusion opportunities, and to specify semantic constraints on rewrites.