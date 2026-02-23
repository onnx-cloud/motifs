Below is a **full Hybrid-family EBNF using `morph`** as the core transformation construct, aligned with your Fuse/ONNX-style DSL.
It keeps tensor syntax (`f32[3]`), arrow returns, and graph wiring visually consistent with executable code.

---

# Morph ABI — EBNF

## 1. Lexical

```ebnf
Ident   ::= letter { letter | digit | "_" }
Number  ::= digit { digit }
String  ::= '"' { char } '"'
Bool    ::= "true" | "false"
```

---

## 2. Types

```ebnf
Type ::= TensorType | MorphRef | GraphRef

TensorType ::= DType Shape [Sem]

DType ::= "f16" | "f32" | "f64"
        | "i8"  | "i32" | "i64"
        | "bool"

Shape ::= "[" Dim { "," Dim } "]"
Dim   ::= Number | Ident | "?" | Range
Range ::= Number ".." Number
```

### Semantics (optional suffix)

```ebnf
Sem ::= "⊥"
      | "M" "{" Qty "," Unit "," Frame "," "[" Number "," Number "]" "}"
      | "D" "{" Kind "," Support "}"
      | "E" "{" Vocab "," Number "}"
      | "{" Field { "," Field } "}"

Field ::= Ident ":" Type
Qty   ::= Ident | String
Unit  ::= String
Frame ::= Ident | String
Kind  ::= Ident
Support ::= Ident
Vocab ::= Ident | String
```

**Valid examples**

```
f32[3]
f32[b,768]
i64[1]⊥
f32[n]M{length,"m","world",[0,100]}
```

---

## 3. Morph (Typed Transformation)

```ebnf
MorphDef ::= "morph" Ident Sig MorphBlock

Sig ::= "(" [ Param { "," Param } ] ")" "->" Type
Param ::= Ident ":" Type
```

### Morph Block

```ebnf
MorphBlock ::= "{"
                 { ConstDecl }
                 { WeightDecl }
                 { CheckDecl }
               "}"

ConstDecl  ::= "const" ":" Binding { "," Binding }
WeightDecl ::= "wt"    ":" Binding { "," Binding }
Binding    ::= Ident ":" Type

CheckDecl  ::= "chk" ":" Constraint { "," Constraint }
```

---

## 4. Constraints

```ebnf
Constraint ::= "shape(" Ident "," Ident ")"
             | "dtype(" Ident "," Ident ")"
             | "sem_sub(" Ident "," Ident ")"
             | "range(" Ident "," "[" Number "," Number "]" ")"
             | "norm(" Ident ")"
```

---

## 5. Graph

```ebnf
GraphDef ::= "graph" Ident "(" ")" GraphBlock

GraphBlock ::= "{"
                 { PortDecl }
                 { NodeDecl }
                 { EdgeDecl }
               "}"
```

### Ports

```ebnf
PortDecl ::= "in"  ":" Binding { "," Binding }
           | "out" ":" Binding { "," Binding }
```

### Nodes

```ebnf
NodeDecl ::= "N" ":" Node { "," Node }
Node     ::= Ident ":" (MorphRef | "Const")
MorphRef ::= Ident
GraphRef ::= Ident
```

### Edges

```ebnf
EdgeDecl ::= "E" ":" Edge { "," Edge }

Edge ::= "(" Ref ")" "->" "(" Ref ")" [ ":" Type ]
Ref  ::= Ident "." Ident
```

PragmaKey ::= Ident { "." Ident }
PragmaVal ::= Number | String | Ident
Pragma ::= "@" PragmaKey [ PragmaVal { "," PragmaVal } ]

@fusion 0.7
@domain motift.type.reality
@prefix ex: <urn:example:>

---

# Example 1 — Morph Definition

A LOF-style score morph similar to your cookbook node.

```text
morph lof_score(x: f32[3]) -> f32[1] {
  const: center:f32[3], reference:f32[3], axes:i64[1]
  chk: shape(x,center), dtype(x,reference)
}
```

**Interpretation**

* Input tensor of length 3.
* Output scalar tensor `[1]`.
* Internal constants declared but not operationally specified.
* Constraints enforce compatibility.

---

# Example 2 — Graph / Proof Harness

```text
graph test_lof_score() {
  out: y:f32[1]

  N:
    sample:Const,
    lof:lof_score

  E:
    (sample.out) -> (lof.x) : f32[3],
    (lof.y)      -> (y.in)
}
```

**What this shows**

* `sample` is a constant node.
* `lof` is an instance of the `lof_score` morph.
* Edge syntax mirrors executable DSL wiring.
* Output port typing remains explicit.

---

## Family Resemblance to the DSL

| DSL Concept       | EBNF Term        |
| ----------------- | ---------------- |
| `node`            | `morph` instance |
| `f32[3]`          | `TensorType`     |
| `->`              | `Sig` return     |
| `(a.out)->(b.in)` | `Edge`           |
| `const`           | `ConstDecl`      |

