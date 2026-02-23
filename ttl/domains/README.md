# Industrial Domains Ontology

This directory contains SKOS/RDF definitions linking real-world industrial, commercial, and scientific domain applications to computation graph motifs.
## Structure

```
domains/
├── index.ttl              # Core ontology: Application class, IndustryDomain, properties
├── README.md
├── agriculture/           # Agriculture & Food
│   └── index.ttl
├── automotive/            # Automotive & Transportation
│   └── index.ttl
├── energy/                # Energy & Utilities
│   └── index.ttl
├── finance/               # Finance & Trading
│   └── index.ttl
├── healthcare/            # Healthcare & Life Sciences
│   └── index.ttl
├── legal/                 # Legal & Compliance
│   └── index.ttl
├── manufacturing/         # Manufacturing & Industrial
│   └── index.ttl
├── media/                 # Media & Entertainment
│   └── index.ttl
├── retail/                # Retail & E-Commerce
│   └── index.ttl
├── science/               # Scientific Research
│   └── index.ttl
├── security/              # Security & Defense
│   └── index.ttl
└── telecom/               # Telecommunications
    └── index.ttl
```
## Domain Summary

| Domain | Applications | Key Motifs |
|--------|--------------|------------|
| **Healthcare** | Medical Imaging, Drug Discovery, Genomics, Protein Folding | Attention, Scan, Residual, Gather/Scatter |
| **Finance** | Algorithmic Trading, Fraud Detection, Risk Modeling | Scan, Attention, Loop, If |
| **Manufacturing** | Defect Detection, Predictive Maintenance, Robotics | Scan, Residual, ForkJoin, Loop |
| **Automotive** | Autonomous Driving, LiDAR Processing, Motion Planning | Attention, Concat, Gather, Scan |
| **Retail** | Recommendations, Demand Forecasting, Visual Search | Attention, EmbeddingLookup, Scan |
| **Energy** | Grid Forecasting, Renewable Prediction, Smart Grid | Scan, Attention, Loop, Gather |
| **Media** | Content Recommendation, Video Generation, TTS | Attention, Scan, Loop, Sampler |
| **Agriculture** | Crop Monitoring, Yield Prediction, Precision Irrigation | Map, Scan, Loop, ForkJoin |
| **Security** | Surveillance, Threat Detection, Cybersecurity | Scan, ForkJoin, If, EarlyExit |
| **Science** | Climate Modeling, Particle Physics, Materials Discovery | Attention, Gather/Scatter, Loop |
| **Telecom** | Network Optimization, Signal Processing, QoS | Gather/Scatter, Linear, Scan |
| **Legal** | Contract Analysis, E-Discovery, Compliance | Attention, VectorSearch, Map |
## Design Principles

1. **URIs over strings**: All motif references use `motif:` namespace URIs
2. **SKOS vocabulary**: Each application has `skos:prefLabel` and `skos:definition`
3. **Primary motif**: `motif:primaryMotif` identifies the dominant pattern
4. **Multiple motifs**: `motif:usesMotif` lists all relevant motifs
5. **Domain tagging**: `motif:belongsTo` links to industry domain
6. **Use case linking**: `motif:relatedUseCase` connects to technical use cases in `../use-cases/`
## Namespaces

```turtle
@prefix motif: <https://ns.onnx.cloud/motif#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
```
## Example Queries
### Find all applications using Attention motif:

```sparql
PREFIX motif: <https://ns.onnx.cloud/motif#>
PREFIX motif: <https://ns.onnx.cloud/motif#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?app ?label ?industry
WHERE {
  ?app motif:usesMotif motif:Attention ;
       skos:prefLabel ?label ;
       motif:belongsTo ?industry .
}
```
### Find all Healthcare applications:

```sparql
PREFIX motif: <https://ns.onnx.cloud/motif#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?app ?label ?definition
WHERE {
  ?app motif:belongsTo motif:Healthcare ;
       skos:prefLabel ?label ;
       skos:definition ?definition .
}
```
### Cross-reference domains with technical use cases:

```sparql
PREFIX motif: <https://ns.onnx.cloud/motif#>
PREFIX motif: <https://ns.onnx.cloud/motif#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?domainApp ?domainLabel ?useCase ?useCaseLabel
WHERE {
  ?domainApp motif:relatedUseCase ?useCase ;
             skos:prefLabel ?domainLabel .
  ?useCase skos:prefLabel ?useCaseLabel .
}
```
## Extending

To add a new domain application:

```turtle
motif:MyNewApplication a motif:Application, skos:Concept ;
  skos:inScheme motif:ApplicationScheme ;
  skos:prefLabel "My New Application"@en ;
  skos:definition "Brief description of this industrial application."@en ;
  motif:belongsTo motif:SomeDomain ;
  motif:primaryMotif motif:SomeMotif ;
  motif:usesMotif motif:SomeMotif ;
  motif:usesMotif motif:AnotherMotif ;
  motif:relatedUseCase motif:SomeUseCase .
```
## Relationship to Use Cases

The `../use-cases/` directory contains **technical** ML patterns (e.g., "Transformer", "Diffusion Denoising").  
This `domains/` directory contains **industrial applications** of those patterns (e.g., "Protein Structure Prediction", "Fraud Detection").

The `motif:relatedUseCase` property links industrial applications back to the underlying technical patterns they employ.
