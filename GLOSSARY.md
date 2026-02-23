# Glossary — Plain-language terms

- **Operator**
  - A function or operation in a model (e.g., `Add`, `Conv`, `MatMul`).
  - How we use it: An operator type describes what a node does.

- **Node**
  - A single instance of an operator inside a model graph (one step in the computation).
  - How we use it: Each node becomes a resource (an `onnx:Node`) that lists its inputs, outputs, and domain.

- **Graph**
  - The network of nodes—this is basically the model or a sub-part of the model.
  - How we use it: A graph groups nodes together and shows the high-level inputs and outputs for the model.

- **Motif**
  - A named pattern or building block used in analyses and documentation (for example, a common arrangement of nodes). Think of motifs as reusable model fragments.
  - How we use it: We identify motifs with `motif:<Name>` and link them to their onnx/operator representations when possible.

- **Input / Output**
  - The named data items that flow into or out of a node or graph (for example, `tokens` or `hidden_states`).
  - How we use it: We describe inputs/outputs with small helper objects (`onnx:OperatorInput` and `onnx:OperatorOutput`) that include name, whether the input is required, and its order.

- **Attribute**
  - A configuration value or parameter of an operator (for example, `kernel_size@` or `axis@`).
  - How we use it: We record attribute name, type, and default value when it helps people reproduce or understand the operator.

- **Domain**
  - The namespace or source of an operator (for example, `ai.onnx` or `cloud.onnx` vs a custom extension domain).
  - How we use it: Each node lists its domain so consumers know the operator's origin and meaning.

