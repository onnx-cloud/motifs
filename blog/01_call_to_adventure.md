# 01 — The Problem

Tensors in machine learning models encode both data and meaning, but these are handled separately. A number exists; what it represents is elsewhere. This creates silent corruption: a temperature value might accidentally become an index, units vanish, and semantic constraints are lost during optimization.

The core question emerged: can we make the meaning explicit and auditable? Can we build systems where semantics flow through computation as naturally as data does?

This is not a new concern in software. Type systems, unit analysis, and semantic preservation are solved problems in traditional engineering. The challenge is bringing these disciplines into the tensor-centric, gradient-based world of deep learning.