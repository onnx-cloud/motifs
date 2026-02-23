# Use Cases Ontology

This directory contains SKOS/RDF definitions linking real-world ML/AI use cases to computation graph motifs defined in `../motifs/`.
## Structure

| File | Domain | Use Cases |
|------|--------|-----------|
| [index.ttl](index.ttl) | — | Core ontology: `UseCase` class, properties, domain concepts |
| [nlp.ttl](nlp.ttl) | Natural Language Processing | Transformer, Autoregressive Decoding, Beam Search, Token Embedding, etc. |
| [vision.ttl](vision.ttl) | Computer Vision | Image Classification, Object Detection, Segmentation, ViT, etc. |
| [generative.ttl](generative.ttl) | Generative Models | Diffusion, VAE, GAN, Text-to-Image, Style Transfer, etc. |
| [moe.ttl](moe.ttl) | Mixture of Experts | Sparse MoE, Top-K Gating, Expert Parallelism, Load Balancing, etc. |
| [distributed.ttl](distributed.ttl) | Distributed Computing | Data/Tensor/Pipeline Parallelism, ZeRO, Gradient Checkpointing, etc. |
| [rl.ttl](rl.ttl) | Reinforcement Learning | Policy Gradient, Actor-Critic, Experience Replay, MCTS, PPO, etc. |
| [inference.ttl](inference.ttl) | Inference Optimization | KV-Cache, Paged Attention, Speculative Decoding, Quantization, etc. |
| [graph-ml.ttl](graph-ml.ttl) | Graph ML | Message Passing, Graph Attention, Pooling, Node Classification, etc. |
| [multimodal.ttl](multimodal.ttl) | Multimodal | Cross-Attention, CLIP, VQA, Image Captioning, VLM, etc. |
| [retrieval.ttl](retrieval.ttl) | Retrieval & Recommendation | Dense Retrieval, RAG, Two-Tower, Collaborative Filtering, etc. |
## Design Principles

1. **URIs over strings**: All motif references use `motif:` namespace URIs (e.g., `motif:Attention`) rather than string literals
2. **SKOS vocabulary**: Each use case has `skos:prefLabel` and `skos:definition`
3. **Primary motif**: `motif:primaryMotif` identifies the dominant pattern
4. **Multiple motifs**: `motif:usesMotif` lists all relevant motifs (including primary)
5. **Domain tagging**: `motif:hasDomain` links to application domain concepts
## Namespaces

```turtle
@prefix motif: <https://ns.onnx.cloud/motif#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
```
## Example Query

Find all use cases using the Attention motif:

```sparql
PREFIX motif: <https://ns.onnx.cloud/motif#>
PREFIX motif: <https://ns.onnx.cloud/motifs/use-cases#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?usecase ?label ?definition
WHERE {
  ?usecase motif:usesMotif motif:Attention ;
           skos:prefLabel ?label ;
           skos:definition ?definition .
}
```
## Extending

To add a new use case:

```turtle
motif:MyNewUseCase a motif:UseCase, skos:Concept ;
  skos:inScheme motif:UseCaseScheme ;
  skos:prefLabel "My New Use Case"@en ;
  skos:definition "Brief description of what this use case does."@en ;
  motif:hasDomain motif:SomeDomain ;
  motif:primaryMotif motif:SomeMotif ;
  motif:usesMotif motif:SomeMotif ;
  motif:usesMotif motif:AnotherMotif .
```
