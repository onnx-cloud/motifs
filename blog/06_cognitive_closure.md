# 06 — Cognitive Closure: Reasoning About Learning

What if systems that learn can also reason about what they learn? 

Cognitive Closure is the discipline of maintaining semantic contracts during training—not just for parameters, but across the entire system: sensors, operators, parameters, and actuators.

## The Gap Between Practice and Principle

Current machine learning treats sensors, operators, and actuators as implementation details. A trained system is valid if it achieves low loss on a held-out test set. Whether its learned parameters preserve sensor calibration, operator invariants, or actuator specifications is not checked. This works poorly when:

- **Fine-tuning breaks invariants**: A model trained for one sensor modality is adapted (via LoRA or other methods) for another. There is no way to verify that the base model's learned operators remain valid under the new sensor inputs.
- **Composition assumptions are violated**: A robotics stack combines a perception module (produces normalized embeddings) with a control module (expects normalized embeddings). During training, the perception module learns parameters that corrupt this assumption, and the mismatch is discovered only at deployment.
- **Optimization violates domain constraints**: A model is trained to produce probabilities, but unconstrained backpropagation pushes logits beyond the range where softmax is numerically stable. Clipping is added post-hoc, breaking gradients.
- **Calibration degrades silently**: A sensor is calibrated once; learned parameters are then optimized without maintaining the calibration bounds. The system drifts out of specification without warning.

State of the art has no mechanism to detect or prevent these violations. Engineers resort to:

- Manual inspection of parameter distributions
- Post-hoc clipping and renormalization (which breaks gradients)
- Extensive testing on held-out data (which may not cover edge cases)
- Careful documentation of assumptions (which is brittle and human-dependent)

None of these scale. As systems grow more complex—more sensors, more operators composed together, more fine-tuning steps—the number of potential violations grows combinatorially.

## Bridging to Cognitive Closure

Cognitive Closure makes contract violations detectable and preventable. The idea is not new in traditional engineering (control systems, signal processing). The challenge is integrating it into gradient-based learning.

The challenge is systemic. A neural network is not a black box of parameters. It is a composition of:

- **Sensors**: specifications of what the system observes (ranges, units, bit depth, or more broadly: a corpus of empirical grounding such as research literature, executable experiments, or validation suites)
- **Operators**: computational units that transform signals (layers, attention heads, motifs)
- **Parameters**: learnable state (weights, biases, and increasingly, low-rank adaptations like LoRAs)
- **Actuators**: specifications of what the system produces (output ranges, probability distributions, control signals)

Unconstrained training violates contracts at every level. A sensor declares what it observes—whether physical measurements in specified ranges, or a corpus of claims extracted from research and experiments. 

Optimization might push learned parameters to exploit edge cases not covered by the empirical grounding. 

An operator assumes its inputs satisfy certain invariants, but backpropagation allows upstream learning to violate these. An actuator must produce outputs that remain faithful to the system's specification, but unconstrained gradient updates corrupt this fidelity. 

A LoRA is meant to constrain parameter updates to a safe subspace, but optimization can still drive the base model out of its intended operating region.

Cognitive Closure integrates three mechanisms:

**Typed Reasoning About Operators**: Each operator carries a semantic specification: what input types it accepts, what invariants it maintains, what output guarantees it provides. During compilation, these specifications are checked. If operator A produces output with shape [batch, 512] but operator B requires shape [batch, 256, 2], the compiler detects this mismatch. If A assumes input is in [-1, 1] but upstream learning might produce values in [-10, 10], the compiler inserts a projection or raises an error.

**Sensor and Actuator Contracts**: Sensors declare observation constraints that must be maintained throughout training. If a calibration parameter is learned, its updates are constrained to keep sensor readings within specified bounds. Actuators declare output constraints that must be satisfied. If the system must produce a valid probability distribution, projections are inserted before the output. These constraints are not post-hoc corrections—they are integrated into the learning procedure itself.

**LoRA-Aware Parameter Updates**: Low-rank adaptations (and similar parameter-efficient methods) already constrain parameter space. Cognitive Closure extends this by reasoning about what constraints the base model needs and what constraints LoRAs impose. If the base model is trained on one sensor configuration and a LoRA fine-tunes for a different one, the compiler verifies that the combined system remains semantically coherent. If a LoRA violates operator invariants, training is halted with a diagnostic.

**Verification**: The combined system (sensors, operators, LoRAs, projections, actuators) is analyzed statically. Proofs establish feasibility: starting from valid sensor readings, all computations maintain type contracts, and all produced actions are within actuator specifications. This is stronger than parameter-space constraints alone—it reasons about the entire data flow.

The cost is compilation complexity and runtime projections. The benefit is that trained systems provably satisfy their semantic contracts: sensors read within bounds, operators compose correctly, LoRAs refine within safe subspaces, and actuators produce valid outputs.

We want to extend optimization into a system-wide discipline.