# Typed Reality — Types, EBNF, and Worked Examples

## ✨ Summary
A compact, practical revision of the Typed Reality type system: formal syntax (EBNF), semantic domains, core typing rules, and worked examples for Linear, Attention, Softmax, and sensor/actuator bindings. Use this as a canonical reference for implementation, tests, and paper edits.

---

## Design Goals ✅
- **Preserve semantics** from sensors to actuators (Measurement, Distribution, Enum, Structured)
- **Statically check** DType, Shape, and Semantics where possible
- **Generate runtime assertions** only when necessary (symbolic analysis / elision)
- **Make knowledge-realm crossings explicit** via bridge morphs

---

## Notation (informal)
- Tensor type: `Tensor<DType, Shape, Semantics>`
- Short form in AST: ``DType[DimList] Sem`` (e.g. ``f32[B,T,D] ⊥``)
- Semantic tags: Atomic `⊥`, Measurement `M{...}`, Distribution `D{...}`, Enum `E{...}`, Structured `{...}`

---

## EBNF (core)
```
Type        ::= DType '[' DimList ']' SemSpec
DType       ::= 'f16' | 'f32' | 'f64' | 'i32' | 'i64' | 'bool' | ...
DimList     ::= Dim (',' Dim)*
Dim         ::= Integer | Symbol | Range
Range       ::= '[' Integer ',' Integer ']'   ; symbolic ranges allowed
SemSpec     ::= '⊥' | 'M' '{' MSpec '}' | 'D' '{' DSpec '}' | 'E' '{' ESpec '}' | '{' FieldList '}'
MSpec       ::= IRI (',' 'unit:' Unit)? (',' Range)? (',' 'frame:' IRI)?
DSpec       ::= kind (',' 'support:' Support)? (',' Range)?
ESpec       ::= VocabIRI (',' 'size:' Integer)?
FieldList   ::= Field (',' Field)* ; Field ::= name ':' Type

Morph       ::= 'morph' IDENT '(' ParamList ')' '->' Type '{' Body '}'
ParamList   ::= Param (',' Param)* ; Param ::= name ':' Type
```

---

## Semantic Domains (short)
- **Atomic (⊥)**: latent vectors, no semantic commitments
- **Measurement (M{iri, unit, [min,max], frame})**: grounded physical quantities
- **Distribution (D{kind, support, [min,max]})**: logits or normalized probabilities (explicitly annotated)
- **Enum (E{vocabIRI, size})**: discrete, finite symbolic vocabularies
- **Structured**: product types of named fields (use for complex sensors)

> Note: Distinguish `D{logits}` (unnormalized) vs `D{categorical,[0,1]}` (normalized). Softmax is the canonical bridge.

---

## Subtyping & Compatibility (rules)
- Symbolic dim ⊑ concrete dim when symbol can be instantiated consistently
- Range narrowing: `[a,b]` ⊑ `[a',b']` if `[a,b] ⊆ [a',b']`
- `D{logits}` --Softmax--> `D{categorical,[0,1]}` (explicit conversion)
- `E{V1}` compatible with `E{V2}` only if `V1 ⊆ V2` or explicit mapping morph exists
- Units must match or require an explicit conversion morph (no implicit unit conversion)

---

## Typing Judgments (compact)
- Form: `Γ ⊢ M : (T_in) → (T_out)`  meaning morph `M` accepts `T_in` and produces `T_out` when `Γ` holds.

Example rules:
- Linear: given `x: f32[B,T,D] ⊥` and `W: f32[D,D_out] ⊥` then `Linear(x,W) -> f32[B,T,D_out] ⊥` if dims align (D matches)
- Attention: inputs `Q,K,V: f32[B,H,T,D] ⊥` → output `f32[B,H,T,D] ⊥` with `chk: shape(Q,K), shape(K,V)`
- Softmax: `logits: f32[B,C] ⊥` with annotation `Softmax` yields `f32[B,C] D{categorical,[0,1]}` plus a runtime or proven normalization invariant

---

## Morph EBNF (example)
```
morph Softmax(logits: f32[B,C] ⊥) -> f32[B,C] D{categorical,[0,1]} {
  chk: norm(logits) // compiler enforces or inserts op graph to assert
}
```

---

## Worked Examples

1) Linear (project tokens to embedding)
```
morph Embed(tokens: i32[B,T] E{BPE50k}) -> f32[B,T,D] ⊥ {
  // lookup table semantics; vocabulary bounds enforced
}
```
- Type checker asserts tokens ∈ [0, 49999] at compile-time when vocab known; else runtime Assert node included.

2) Attention
```
morph Attention(q,k,v: f32[B,H,T,D] ⊥) -> f32[B,H,T,D] ⊥ {
  chk: shape(q,k), shape(k,v)
}
```
- Shapes unify (symbolic dims refined). No semantic crossing.

3) Softmax (logits → categorical distribution)
```
morph Softmax(logits: f32[B,C] ⊥) -> f32[B,C] D{categorical,[0,1]} {
  chk: normalized // compiler can replace with Assert(normalize) or prove elidable
}
```
- Lowering: emit ONNX Softmax op and optionally an Assert for sum ≈ 1 if not provably normalized.

4) Camera sensor
```
morph CameraRGB() -> f32[B,3,H,W] M{radiance, unit:srgb, [0,1], frame:camera}
```
- Lowering: tensor + metadata, with Clip/Assert to `[0,1]` if required.

5) Fusion + Action (mini pipeline):
- `CameraRGB` M → `ConvStem` ⊥ → `image_emb` ⊥
- `Token` E → `Embed` ⊥ → `text_emb` ⊥
- `X = Concat([image_emb,text_emb])` ⊥ → `Transformer` ⊥ → `logits` ⊥ → `Softmax` → action_probs D{categorical}
- `Controller` Sample(action_probs) → Motor command M{steering, deg, [-30,30]}`

---

## ONNX Lowering Notes 🔧
- **Measurement** → Tensor + `Clip`/`Assert` nodes for range/unit checks
- **Enum** → `int` tensor + bounds/vocab check
- **Distribution{normalized}** → Softmax or derived op + optional precision Assert
- **Assertion Elision**: run symbolic interval and normalization analysis; remove redundant Asserts

---

## Tests & Implementation Checklist ✅
- [ ] Unit tests for shape unification and symbolic dim refinement
- [ ] Semantic mismatch tests (enum vs measurement, atomic vs enum concat)
- [ ] Softmax normalization proof / fallback Assert tests
- [ ] ONNX lowering smoke test that includes Assert nodes for enums/measurements

---

## Links / TODO
- See `./todo/TR.md` for prioritized paper changes and PoC tasks.
- Suggested next step: land a short PR clarifying Distribution/Softmax semantics and add the Softmax example to the paper.

---

*File generated for implementation reference and to feed into tests, examples, and the paper edits.*
