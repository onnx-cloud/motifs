# 02 — Typed Reality: Making Meaning Explicit

Three properties define a tensor: its element type, its shape, and its semantic meaning. Traditional machine learning treats only the first two. Semantics remains implicit, often a comment in a README.

Typed Reality proposes that semantics should be explicit and machine-checkable. A temperature measurement has a unit. A class index should never be averaged. A sensor reading in RGB space is not the same as a sensor reading in HSV space.

This is not a radical idea. It is standard engineering practice in signal processing, control systems, and physics simulations. The cost is verbosity. The benefit is that the compiler can detect violations automatically, and training procedures can enforce constraints that preserve meaning.