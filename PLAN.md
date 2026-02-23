# Remediation Plan for Motif Models Project

- ⚠️ PAPER.md outlines 6 possible themes but lacks execution
- fuse compiler exists elswhere

**Strategic Recommendation:** **Focus on Theme 1+2 hybrid** ("Generative Algebra of Computation Motifs for ML Compilers")
- Strongest theoretical foundation (algebra already in TTL)
- Most novel systems angle (IR abstraction gap between MLIR/TVM and architecture-level)
- Measurable empirical validation (benchmarks on real models)
- Highest venue relevance (MLSys, OSDI, PLDI)

## 📋 Detailed Action Items (Prioritized)
### Phase 1: Theory Solidification (Weeks 1-2) — **CRITICAL PATH**
#### 1.1 Formalize Generative Algebra Framework
**Current State:** Generative algebra exists in SPARQL/TTL but not in LaTeX/paper form  
**Action:**
```
1. Read ttl/motifs/index.ttl and SPARQL queries to extract:
   - Formal definition of B* (16 primitives)
   - Definition of composition operators (4 operators: Seq, Par, Conditional, Loop)
   - How B* + operators generate common motifs (representative examples)
   - Edge cases and limitations (motifs requiring specialized handling)

2. Write LaTeX Theory Section (2-3 pages):
   Definition: "Generative basis: Set of 16 primitives + composition operators"
   Properties:
   - Inductively defined: primitives are base cases
   - Closed under composition: any sequence/parallel/conditional/loop of primitives is valid
   - Empirical coverage: shown to generate 100+ motifs in real-world models
   - Extensibility: framework accommodates new primitives when needed
   - Known limitations: document gaps and special cases

3. Appendix: List of 16 primitives with signatures
   Format: Table with columns [Name | Signature | Rank | Role in IR | Known Limitations]
```
**Owner:** You (paper writing)  
**Deliverable:** `papers/generative_algebra.tex` (LaTeX snippet for PAPER.md)  
**Blocking:** Nothing; can start immediately  
**Success Criteria:** Definitions are mathematically clear, coverage claims are empirically grounded, limitations are acknowledged, aligns with TTL definitions

#### 1.2 Define Motif Algebra with Semantics
**Current State:** Composition operators exist in concept but not formally specified  
**Action:**
```
1. Define 4 composition operators formally:
   Sequential(M1, M2):    Sequential composition (M1's output → M2's input)
   Parallel(M1, M2):    Parallel composition (independent branches)
   Conditional(M, P):     Conditional (guard + motif)
   Iterative(M, I):     Iterative (body + condition)

2. Specify algebraic properties (need ./sparql/semantics/):
   - Seq: associative? [YES if I/O match]
   - Par: commutative? [YES by definition]
   - Identity elements?
   - Distributes over other ops?

3. Formalize semantics (abstract):
   Each motif M has a semantic function sem(M) : (Tensor^|I|) → Tensor^|O|
   Compositionality: sem(Seq(M1,M2)) = sem(M2) ∘ sem(M1)
   Note: Semantics may not be unique (multiple implementations per motif)

4. Use decidable logic framework (e.g., QF_LIA + uninterpreted functions):
   For Theme 3 (verification) downstream
```
**Owner:** You (theory)  
**Deliverable:** `papers/algebra_semantics.tex`  
**Blocking:** Theory section of paper  
**Success Criteria:** Algebra fits in 1-2 pages, properties are clear, connects to existing compiler theory literature

### Phase 2: Systems Implementation (Weeks 2-5) — **LONGEST PHASE**
#### 2.1 Build ONNX → Motif IR Lowering Pass
**Current State:** No lowering algorithm exists  
**Action:**
```
1. Design lowering algorithm (on whiteboard first):
   Input: ONNX computational graph (nodes, edges, attributes)
   Output: Motif IR (motif composition tree + lowered assignments)

   Algorithm outline:
   a) Build ONNX graph data structure (adjacency list + metadata)
   b) Pattern matching: identify subgraphs matching known motifs
      - Start with largest motifs (greedy top-down)
      - Use heuristic: maximize motif coverage (minimize uncovered ops)
   c) Assign uncovered ops to motifs:
      - Single ops → primitive motifs (Convolution, Attention, etc.)
      - Groups of ops → composite motifs (Residual, etc.)
   d) Emit motif composition tree

   Complexity: NP-hard in general (graph isomorphism); use heuristics + greedy

2. Implement in Python:
   Location: src/compiler/onnx_to_motif.py
   
   class MotifLowering:
       def lower_onnx(self, onnx_model_path: str) -> MotifCompositionTree:
           """Parse ONNX, detect motifs, return IR"""
           
   Key functions:
   - parse_onnx(path) → Graph
   - pattern_match(graph) → [(motif, subgraph_id)]
   - build_composition_tree(matches) → CompositionTree
   - validate_coverage(tree, original_graph) → bool

3. Test on 3 baseline models:
   - GPT2 (transformer: Attention + FFN blocks)
   - ResNet50 (CNN: Residual blocks)
   - GCN (graph: graph convolution motif)
   
   Expected outputs: JSON serialization of composition trees

4. Implement motif pattern library:
   Location: src/compiler/motif_patterns.py
   
   Define regex-like patterns for:
   - Attention (Multi-Head-Attention + Layer Norm)
   - Residual (Conv + Add + Activation)
   - Concat (multiple inputs → cat)
   - Scan (loop body)
   etc.
   
   Pattern = (required_ops, edges, optional_attrs)
```
**Owner:** You (implementation)  
**Deliverable:** 
- `src/compiler/onnx_to_motif.py` (lowering algorithm)
- `src/compiler/motif_patterns.py` (pattern library)
- `tests/test_lowering.py` (unit tests)
- `papers/figures/lowering_example.pdf` (GPT2 example breakdown)

**Blocking:** Optimization passes (Phase 2.2), benchmarking (Phase 3.1)  
**Success Criteria:** 
- ✅ Algorithm identifies motifs in GPT2, ResNet, GCN on representative test cases
- ✅ Coverage ≥ 85% on tested models (≤15% ops unmatched)
- ✅ Unit tests pass
- ✅ Failures/edge cases are documented

#### 2.2 Implement Motif-Level Optimization Passes
**Current State:** No optimization rules exist  
**Action:**
```
1. Define optimization rules at motif level (not op level):

   Rule 1: Attention Fusion
   Pattern: Seq(Attention, LayerNorm, FFN)
   Rewrite: Fused_Attention_FFN (new primitive? or composite)
   Benefit: Reduce memory bandwidth (fewer reads of hidden states)
   
   Rule 2: Residual Memory Reuse
   Pattern: Parallel(Residual_A, Residual_B) + Add
   Rewrite: Interleave computation to keep activations in L3 cache
   Benefit: 20-30% memory bandwidth reduction
   
   Rule 3: Graph Parallelism
   Pattern: Par(M1, M2) where Rank(M1) ≤ 4, Rank(M2) ≤ 4
   Rewrite: Thread-level parallelism (e.g., task stealing)
   Benefit: Reduced latency on multi-core
   
   Rule 4: Loop Unrolling
   Pattern: Loop(M, I=fixed_constant)
   Rewrite: Unroll loop body I times
   Benefit: Better instruction-level parallelism
   
2. Implement in Python:
   Location: src/compiler/motif_optimizer.py
   
   class MotifOptimizer:
       def apply_rules(self, composition_tree: CompositionTree) -> CompositionTree:
           """Bottom-up rewrite pass applying fusion/unrolling rules"""
           
   Key methods:
   - find_patterns(tree, pattern) → [matches]
   - apply_rewrite(match, rule) → new_tree
   - validate_correctness(original, rewritten) → bool

3. Validate correctness of rewrites:
   - Semantic preservation: sem(original) == sem(rewritten)
   - Use property-based testing (Hypothesis library)
   - For Theme 3 (formal verification): sketch Z3 proof

4. Instrument to extract optimization metrics:
   - Memory bandwidth reduction (estimate)
   - Parallelism degree
   - Register pressure
```
**Owner:** You (compiler passes)  
**Deliverable:**
- `src/compiler/motif_optimizer.py` (optimization rules)
- `tests/test_optimizer.py` (correctness validation)
- `papers/figures/optimization_passes.pdf` (before/after examples)

**Blocking:** Benchmarking (Phase 3.1)  
**Success Criteria:**
- ✅ At least 3 fusion rules implemented
- ✅ Rewrites preserve semantics (validated by tests)
- ✅ Fusion reduces estimated memory bandwidth by ≥15%

#### 2.3 Implement Motif IR Code Generator
**Current State:** No codegen exists  
**Action:**
```
1. Design code generation targets (pick 1-2 for MVP):
   Target 1: PyTorch eager (reference implementation, easy to validate)
   Target 2: ONNX (compatibility with existing runtimes)
   
   Lower Priority (post-paper):
   - MLIR (for integration with LLVM ecosystem)
   - Triton (for GPU kernels, matches inference optimization theme)

2. Implement PyTorch codegen:
   Location: src/compiler/codegen_torch.py
   
   class TorchCodegen:
       def generate(self, composition_tree: CompositionTree) -> str:
           """Emit Python code calling torch.* operations"""
           
   For each motif node in tree:
   - Emit corresponding torch ops (torch.nn.* or functional)
   - Thread through input/output tensors
   - Handle control flow (conditional, loop)

3. Implement ONNX codegen:
   Location: src/compiler/codegen_onnx.py
   
   Convert composition tree → ONNX graph
   (Simpler: mostly 1-to-1 mapping from motif to ONNX opset)

4. Add round-trip validation:
   Original ONNX → Motif IR → PyTorch codegen → execute & check correctness
```
**Owner:** You (code generation)  
**Deliverable:**
- `src/compiler/codegen_torch.py`
- `src/compiler/codegen_onnx.py`
- `tests/test_codegen.py` (round-trip validation)

**Blocking:** Benchmarking  
**Success Criteria:**
- ✅ Generated PyTorch code produces numerically correct outputs
- ✅ Round-trip validation passes on 3 test models

### Phase 3: Validation & Benchmarking (Weeks 5-7)
#### 3.1 Run End-to-End Benchmarks
**Current State:** No benchmarks; no performance data  
**Action:**
```
1. Select 3 representative models:
   - GPT2-small (transformers: Attention + FFN)
   - ResNet50 (CNNs: Residual blocks)
   - GCN (graphs: graph convolution)

2. Setup benchmark pipeline:
   Location: benchmarks/end_to_end.py
   
   For each model:
     a) Baseline: run original ONNX/PyTorch (measure latency, memory)
     b) Motif IR: lower to IR, apply optimizations, codegen, run
     c) Measure:
        - Latency (ms per inference, averaged over 100 runs)
        - Memory peak (MB)
        - Memory bandwidth (estimated)
        - Compilation time (time to lower + optimize + codegen)
     d) Report: speedup vs baseline

3. Implement benchmark harness:
   ```python
   class Benchmark:
       def run(self, model_name, batch_size, num_runs=100):
           baseline_latency = run_baseline(model_name, batch_size, num_runs)
           motif_latency = run_motif_ir(model_name, batch_size, num_runs)
           return {
               'baseline': baseline_latency,
               'motif_ir': motif_latency,
               'speedup': baseline_latency / motif_latency,
               'memory_reduction': (baseline_memory - motif_memory) / baseline_memory
           }
   ```

4. Target results (realistic expectations):
   - Latency speedup: 5-15% (memory-bound workloads benefit most)
   - Memory bandwidth: 15-25% reduction (fusion wins)
   - Compilation overhead: <5% of first-run latency

5. Statistical rigor:
   - Use 100 warmup runs, then 100 timed runs
   - Report mean ± stdev
   - Test on same hardware (pin to specific CPU core)
```
**Owner:** You (benchmarking)  
**Deliverable:**
- `benchmarks/end_to_end.py`
- `papers/figures/speedup_chart.json` (Vega-Lite bar chart)
- `papers/tables/benchmark_results.tex` (LaTeX table)

**Blocking:** Results section of paper  
**Success Criteria:**
- ✅ Speedup ≥ 5% on at least one model
- ✅ Benchmark is statistically rigorous (error bars, multiple runs)
- ✅ Results fit in paper table (Model | Baseline | Motif IR | Speedup | Memory)

#### 3.2 Motif Detection Validation
**Current State:** Lowering algorithm built but not validated at scale  
**Action:**
```
1. Run lowering on all 69 models in models.ttl:
   Goal: Verify coverage, identify edge cases
   
   For each model:
   - Attempt lowering
   - Record: motif coverage %, uncovered ops
   - Log any errors
   
2. Generate coverage report:
   Location: tmp/coverage_report.json
   
   {
     "total_models": 69,
     "successful": 65,
     "failed": 4,
     "mean_coverage": 87.3,
     "by_category": {
       "Cognition": {"mean_coverage": 92.1, ...},
       "Topology": {"mean_coverage": 85.2, ...},
       ...
     }
   }

3. Analyze failures:
   - Document unsupported ops
   - Design workarounds or extensions to motif catalog
   - Update TTL if needed (new primitive motifs?)

4. Create visualization:
   - Histogram: motif coverage distribution
   - Heatmap: coverage by model category
   - Table: models with lowest/highest coverage
```
**Owner:** You (validation)  
**Deliverable:**
- `tmp/coverage_report.json`
- `papers/figures/coverage_distribution.json` (chart)
- List of unhandled edge cases

**Blocking:** Coverage claims in paper  
**Success Criteria:**
- ✅ ≥ 85% of models achieve ≥ 85% motif coverage
- ✅ Document and explain failures (edge cases, unhandled ops)
- ✅ Quantify limitations by model category

### Phase 4: Paper Writing & Submission (Weeks 7-10)
#### 4.1 Rewrite Introduction & Thesis
**Current State:** PAPER.md outlines themes but no coherent narrative  
**Action:**
```
New Introduction (~2 pages):

1. Motivation (1 page):
   - Current ML IRs occupy two extremes:
     * Low-level (ONNX ops, XLA HLO): too fine-grained for high-level optimization
     * High-level (model architecture): too coarse for compilation
   - Motif IR: sweet spot abstraction level
   - Analogy: Assembly vs. functions in traditional compilers
   
2. Thesis statement (clear, 1-2 sentences):
   "We introduce a generative framework of 16 primitives and composition 
   operators that models common ML computation patterns. A motif-aware 
   compiler targeting this abstraction achieves 5-15% latency speedups 
   on transformers and CNNs while exposing parallelism bounds and memory 
   reuse opportunities."

3. Contributions (bulleted):
   - Formal algebraic framework (16 primitives, compositional operators, semantics)
   - Practical IR design (ONNX lowering, optimization passes)
   - End-to-end compilation pipeline
   - Empirical validation on 50+ model architectures
   - Open-source infrastructure

4. Related work (paragraph):
   Compare with MLIR (too low-level), TVM (op-level fusion), 
   Halide (domain-specific), Relay (lacks motif structure)
```
**Owner:** You (writing)  
**Deliverable:** `PAPER.md` section 1 (new version)  
**Blocking:** Entire paper  
**Success Criteria:** Thesis is clear, novel contribution is obvious, related work differentiation is crisp

#### 4.2 Assemble Paper Structure
**Current State:** Outline exists but not written  
**Action:**
```
PAPER.md outline (12 pages target):

1. Introduction (2 pp) — NEW
   Motivation, thesis, contributions, roadmap

2. Background (1 p)
   ML graphs, ONNX/PyTorch, compilation challenges
   [Can adapt from existing CHARTING.md or WIKI.md]

3. Motif Algebra (2 pp)
   Formal definitions, 16 primitives (table), composition operators,
   semantics, generative properties
   [Use papers/generative_algebra.tex + papers/algebra_semantics.tex]

4. Motif IR Design (1.5 pp)
   Lowering algorithm, pattern matching, coverage model
   Figure: lowering example (GPT2)

5. Optimization Passes (1.5 pp)
   Fusion rules, parallelism extraction, memory planning
   Figure: before/after optimization

6. Evaluation (2 pp)
   - Experiments: 3 models (latency, memory)
   - Motif coverage: 69 models, 87% mean
   - Compilation overhead
   - Case study: FlashAttention rewrite (Theme 3 teaser)
   Tables/Figures: speedup chart, coverage heatmap

7. Related Work (1 p)
   MLIR, TVM, Relay, Halide, existing fusion techniques

8. Discussion & Future Work (0.5 p)
   - Verification integration (Theme 3)
   - Inference optimizations (Theme 5)
   - Knowledge graph queries (Theme 6)

9. Conclusion (0.5 p)

Appendices:
   A. Primitives catalog (16 primitives, signatures, examples)
   B. Composition rules (supported combinations, examples)
   C. Benchmark details (hardware, configuration)
   D. Coverage by model category (successes + known limitations)
```
**Owner:** You (organization + writing)  
**Deliverable:** Complete PAPER.md (draft)  
**Blocking:** Submission  
**Success Criteria:** Paper is self-contained, all figures referenced, word count ~6000-8000 (12 pages @ 500 wds/page)

#### 4.3 Generate Publication-Quality Figures
**Current State:** Some charts exist but may not be publication-ready  
**Action:**
```
Required figures (use existing charts/ + new):

1. Periodic Table of Motifs (centerpiece)
   Source: algebraic_structure.yaml (likely exists)
   Polish: Increase resolution, improve color palette, add legend
   
2. Derivation Tree Example
   Source: derivation_tree.yaml
   Show: How ResNet or GPT2 decomposes into primitives
   
3. Lowering Pipeline Diagram
   Source: NEW — create in Graphviz or Inkscape
   Show: ONNX graph → pattern matching → motif tree → optimizations → codegen
   
4. Speedup Bar Chart
   Source: papers/figures/speedup_chart.json (from Phase 3.1)
   Models: GPT2, ResNet, GCN
   Compare: Baseline vs Motif IR
   
5. Coverage Heatmap
   Source: papers/figures/coverage_distribution.json
   X-axis: Models
   Y-axis: Coverage %
   Color: Category (Cognition, Topology, etc.)
   
6. Optimization Before/After
   Source: Create example (small motif composition)
   Show: Original vs fused version, memory bandwidth savings

Command to regenerate:
   make charts
   (ensure all .yaml configs are correct)
```
**Owner:** You (charting/visualization)  
**Deliverable:** 6+ high-quality figures in `papers/figures/`  
**Blocking:** Final paper PDF  
**Success Criteria:** Figures are publication-ready, labeled, captioned, 300+ DPI

#### 4.4 Compile Final Paper PDF
**Current State:** LaTeX infrastructure exists but incomplete  
**Action:**
```
1. Check Makefile.paper:
   - Verify pdflatex/biber setup
   - Ensure all .tex includes are correct
   
2. Write/compile main LaTeX file:
   Location: papers/motif_models.tex
   
   Structure:
   \documentclass{article}
   \usepackage{...}
   
   \title{A Generative Algebra of Computation Motifs for ML Compilers}
   \author{[Your Name(s)]}
   
   \input{sections/introduction}
   \input{sections/background}
   ...
   
3. Include figures and tables:
   \includegraphics{figures/periodic_table.pdf}
   \input{tables/benchmark_results}
   
4. Compile:
   make pdf
   
5. Review and polish:
   - Check figure quality, captions
   - Verify references and citations
   - Proofread for typos

6. Target length: 12 pages (fits OSDI/MLSys/PLDI guidelines)
```
**Owner:** You (LaTeX + editing)  
**Deliverable:** `papers/motif_models.pdf`  
**Success Criteria:** PDF is polished, professionally formatted, ready for submission

### Phase 5: Open-Source Release & Community Engagement (Weeks 10-12)
#### 5.1 Package Artifacts for Release
**Current State:** Code exists but not packaged for distribution  
**Action:**
```
1. Organize repo structure:
   - Move compiler code to top-level src/compiler/ (already done?)
   - Add README to compiler/ with API docs
   - Create examples/ with Jupyter notebooks:
     * example_gpt2_lowering.ipynb
     * example_optimization_pass.ipynb
     * example_benchmark.ipynb

2. Write documentation:
   - `COMPILER.md`: How to lower ONNX to motif IR
   - `API.md`: Python API reference for MotifLowering, MotifOptimizer, etc.
   - `MOTIF_CATALOG.md`: Curated list of all motifs + signatures

3. Create Docker image:
   Dockerfile with all dependencies
   docker run -v $PWD:/work motif-models make charts

4. Set up CI/CD:
   GitHub Actions workflow to:
   - Run pytest on every PR
   - Generate figures
   - Validate TTL with SHACL
   - Build Docker image
```
**Owner:** You (DevOps/packaging)  
**Deliverable:**
- `src/compiler/README.md`
- `COMPILER.md`
- `API.md`
- `Dockerfile`
- `.github/workflows/ci.yml`

**Blocking:** Public release  
**Success Criteria:** Repository is well-organized, documented, CI passes

#### 5.2 Prepare Supplementary Material
**Current State:** N/A  
**Action:**
```
1. Supplementary document:
   - Full motif catalog (all 100+ motifs with signatures)
   - Proof details (full formal proof, not just sketch)
   - Additional benchmarks (ablations, sensitivity analysis)
   - FAQ: common questions about motif composition

2. Code artifact:
   - Commit to GitHub (public or conference artifact track)
   - Tag release (v1.0)
   - Include instructions: "How to reproduce figures"

3. Data artifact:
   - Export all benchmark results as CSV
   - Include ONNX models used (or links to HuggingFace)
   - SPARQL query cookbook (20+ examples)

4. Licenses:
   - Ensure consistent licensing (MIT, Apache 2.0, etc.)
   - Add LICENSE file to repo
```
**Owner:** You (documentation)  
**Deliverable:** 
- Supplementary PDF
- GitHub release tag
- `SUPPLEMENTARY.md`

## 🏗️ Success Criteria & Milestones
### Milestone 1: Theory Formalized (End of Week 2)
- [ ] Generative algebra formally stated in LaTeX
- [ ] Algebra semantics defined (composition operators + properties)
- [ ] Both integrated into PAPER.md
### Milestone 2: Compiler MVP (End of Week 5)
- [ ] ONNX → Motif IR lowering algorithm implemented
- [ ] Pattern library defined (≥10 motif patterns)
- [ ] Optimization passes (≥3 fusion rules)
- [ ] Code generator (PyTorch + ONNX)
- [ ] Round-trip validation: ONNX → IR → code → correctness ✅
### Milestone 3: Benchmarks & Validation (End of Week 7)
- [ ] End-to-end benchmarks on 3 models
- [ ] ≥5% latency speedup demonstrated
- [ ] Coverage validation on 69 models (≥85% mean coverage)
- [ ] Coverage report + visualizations
### Milestone 4: Paper Complete (End of Week 10)
- [ ] PAPER.md fully written (12 pages)
- [ ] All figures generated + publication quality
- [ ] LaTeX PDF compiled and polished
- [ ] Ready for submission
### Milestone 5: Release Ready (End of Week 12)
- [ ] Repository well-documented
- [ ] CI/CD passing
- [ ] Supplementary material prepared
- [ ] Ready for conference submission

## 🎯 Key Insights & Strategic Advice
### 1. **Algebra is Your Core Strength**
The generative algebra (16 primitives + composition operators → 100+ empirical motifs) is your **novel theoretical framework**. This differentiates you from MLIR/TVM/Halide, which are pragmatic but not algebraically principled. Lead with this in the paper.

**Action:** Invest time in formalizing the algebra (Phase 1.1). This becomes the centerpiece of the theory section and justifies the entire endeavor. Avoid over-claiming completeness; emphasize empirical coverage and extensibility.
### 2. **Compilation is Your Practical Differentiator**
MLIR exists, but it operates at op-level. Your motif-level abstraction is simpler for high-level reasoning but rich enough for real optimizations. This is your **systems contribution**.

**Action:** The lowering pass + optimization rules (Phase 2.1-2.2) must work end-to-end and show real speedups. Even 5-10% is credible; 15%+ is excellent.
### 3. **Benchmarks Are Non-Negotiable**
Without benchmarks, this is a nice taxonomy. With benchmarks, it's a **systems paper** with practical impact.

**Action:** Phase 3.1 is not optional. Pick conservative targets (GPT2, ResNet, GCN) and make sure you can justify the speedups (fusion, parallelism, memory reuse).
### 4. **The Knowledge Graph Angle (Theme 6) Is Underexploited**
You have a rich RDF ontology + 69 models in TTL. This is perfect for **SPARQL-driven insights**. Consider adding a "Queries that answer real questions" section to your paper or supplementary.

**Example queries:**
- Which motifs support data parallelism?
- Which models share the most motifs?
- Which motifs require specialized hardware?

**Action:** Create a 10-query cookbook (takes 1-2 hours). Include results as a table in the paper or supplementary. This appeals to semantic web audiences and practitioners.
### 5. **Verification (Theme 3) Is a Future Direction, Not Phase 1**
Formal verification is interesting but orthogonal to the main systems contribution. Mention it as future work or a 1-page sketch, but don't let it block the paper.

**Action:** Skip Theme 3 for the initial submission. Save it for a follow-up paper ("Motif-Driven Equivalence Checking").
### 6. **Inference Optimization (Theme 5) Is a Great Add-On**
If you finish early, adding a section on KV-cache or speculative decoding using motif patterns is compelling and timely (LLM inference is hot).

**Action:** This could be a 1-page case study: "Motif-Guided KV-Cache Design." Optional for initial submission but high-impact if included.
### 7. **Publication Strategy**
**Primary venue:** MLSys 2025 or OSDI 2025 (if timelines align)
**Backup venues:** PLDI 2025 (theory angle), NeurIPS 2025 (empirical angle), ASPLOS 2026

**Why MLSys:** Combines theory (algebra) + systems (compiler) + empirics (benchmarks). Perfect fit.

**Submission checklist:**
- Title: "A Generative Algebra of Computation Motifs for ML Compilers"
- Abstract: <250 words, lead with thesis
- Paper: 12 pages + 4 pages supplementary
- Figures: 6+ high-quality visuals
- Benchmarks: 3 models, statistical rigor
- Code artifact: GitHub link
### 8. **Risk Mitigation**
**Risk:** Speedups are <5% or don't materialize.
**Mitigation:** Emphasize theoretical contribution (generative algebra framework) and infrastructure (SPARQL queries, TTL ontology). Systems contribution is a bonus, not the core.

**Risk:** Lowering algorithm doesn't scale to 69 models.
**Mitigation:** Document edge cases, propose extensions to motif catalog, quantify where it works (e.g., 85% transformers vs. 72% GNNs).

**Risk:** Timeline slips.
**Mitigation:** Prioritize Phase 1 (theory) → Phase 3.1 (benchmarks) → Phase 4 (paper). If needed, drop Phase 2.2 (optimization passes) and submit with lowering only.

## 📊 Effort Estimation

| Phase | Tasks | Effort (Days) | Owner |
|-------|-------|---------------|-------|
| 1 (Theory) | Generative algebra, algebra semantics | 8-10 | You |
| 2.1 (Lowering) | ONNX→IR, pattern library, tests | 12-15 | You |
| 2.2 (Optimizer) | Fusion rules, correctness validation | 8-10 | You |
| 2.3 (Codegen) | PyTorch + ONNX codegen | 8-10 | You |
| 3.1 (Benchmarks) | Benchmark harness, 3 models | 10-12 | You |
| 3.2 (Validation) | Coverage analysis, 69 models | 5-7 | You |
| 4 (Paper) | Writing, figures, PDF | 15-20 | You |
| 5 (Release) | Packaging, docs, CI/CD | 8-10 | You |
| **Total** | | **74-94 days** (~12-14 weeks) | |

**Compressed timeline** (parallel work + focus): **8-10 weeks possible** if you dedicate full-time effort.

## 🚀 Concrete Steps (This Week — Day-by-Day, actionable)

**Day 1 (0.5-1d): Extract primitives & scaffold LaTeX** 🔧
- Files: `ttl/motifs/index.ttl`, create `papers/generative_algebra.tex`
- Actions:
  1. Inspect `ttl/motifs/index.ttl` and list the 16 primitives and their signatures.
  2. Create `papers/generative_algebra.tex` with a one-page table: [Name | Signature | Short description | Known limitations].
  3. Add a minimal unit test: `tests/test_generative_algebra.py` asserting the file exists and contains each primitive name.
- Commands:
  - Edit files in editor, then run `pytest -q tests/test_generative_algebra.py`.
- Acceptance criteria: file exists, test passes, table lists all primitives.

**Day 2 (0.5-1d): Formalize composition operators & semantics** 📐
- Files: create `papers/algebra_semantics.tex`, update `PAPER.md` section draft
- Actions:
  1. Write formal definitions for Seq, Par, Cond, Loop (1–2 paragraphs each).
  2. Add a short example decomposition (e.g., Residual = Seq(Conv, Add)) and note non-uniqueness of implementations.
  3. Add tests: `tests/test_algebra_semantics.py` checks for presence of operator names and example strings in the .tex file.
- Commands:
  - `pytest -q tests/test_algebra_semantics.py`
- Acceptance criteria: file contains operator definitions and example; tests pass.

**Day 3 (1d): Lowering skeleton + ONNX test harness** 🛠️
- Files: `src/compiler/onnx_to_motif.py`, `tests/test_lowering.py`
- Actions:
  1. Add `MotifLowering` class with methods: `parse_onnx(path)`, `pattern_match(graph)` (skeleton; no heavy logic yet).
  2. Add a test `tests/test_lowering.py::test_parse_onnx_smoke` that loads a small ONNX (use sample or construct with onnx.helper) and asserts `parse_onnx` returns a Graph-like object.
  3. Ensure `onnx` is available in the venv; if not, `pip install onnx` in the project's venv.
- Commands:
  - `./venv/bin/python -m pip install onnx --upgrade`
  - `pytest -q tests/test_lowering.py::test_parse_onnx_smoke`
- Acceptance criteria: tests pass locally; no external downloads required for the smoke test.

**Day 4 (1d): Implement two core patterns (Attention, Residual)** ⚙️
- Files: `src/compiler/motif_patterns.py`, extend `tests/test_lowering.py`
- Actions:
  1. Implement pattern templates for Attention and Residual motifs (required ops + simple edge shape).
  2. Create small synthetic ONNX graphs in tests that match these patterns and assert `pattern_match` finds them.
  3. Add JSON emitter `src/compiler/emit_composition.py` to serialize a small composition tree to `tmp/<model>_composition.json`.
- Commands:
  - `pytest -q tests/test_lowering.py::test_pattern_attention tests/test_lowering.py::test_pattern_residual`
- Acceptance criteria: both pattern tests pass and `tmp/<model>_composition.json` is produced for synthetic graphs.

**Day 5 (1d): Run lowering on GPT2 & produce coverage report** ✅
- Files: `scripts/run_lowering_coverage.py` (new), output `tmp/coverage_report.json`
- Actions:
  1. Use the lowering implementation to lower a small GPT2 ONNX (or a minimal transformer test graph) and emit composition JSON.
  2. Run the lowering across `ttl/models/models.ttl` entries (start with a subset if needed) and collect motif coverage stats (% ops matched).
  3. Write a small summary `tmp/coverage_report.json` with fields: model, coverage, unmatched_ops_sample.
- Commands:
  - `python scripts/run_lowering_coverage.py --models ttl/models/models.ttl --out tmp/coverage_report.json`
  - `cat tmp/coverage_report.json | jq .` (inspect)
- Acceptance criteria: `tmp/coverage_report.json` exists, average coverage ≥ 65% (initial target), and edge cases logged.

**Ongoing (Days 6+): Harden, tests, and CI** 🔁
- Tasks:
  - Add tests for round-trip correctness when codegen exists (later).
  - Add SHACL validation step to CI: ensure `make shacl` passes before merging changes to TTL.
  - Update `PAPER.md` with initial results and placeholders for figures.
- Commands:
  - `pytest -q` (full test suite)
  - `make shacl` (validate TTL)
  - `make charts` (regenerate figures)
- Acceptance criteria: test suite green (or limited, documented failures), `tmp/coverage_report.json` available, and new tests included in repo.

**Commit / PR etiquette:**
- Make small, focused commits per day. Include tests with every non-trivial change. Create a draft PR titled: "feat: generative algebra + lowering skeleton" and request review.

**Notes & Owners:**
- Owner: You (primary) — delegate small tasks to collaborators if available.
- Time estimates: This week-focused plan totals ~5-6 days of focused work.

**Success looks like:** By end of week, `papers/generative_algebra.tex` and `papers/algebra_semantics.tex` exist, basic lowering detects Attention/Residual on synthetic & GPT2 test graph, and `tmp/coverage_report.json` is produced.


## 📚 References & Resources

- **TTL Ontology:** `ttl/motifs/index.ttl` (schema), `ttl/models/models.ttl` (catalog)
- **Existing Queries:** `sparql/` directory (study for Phase 5.2)
- **Charting Setup:** `CHARTING.md`, `src/charting/chart_generator.py`
- **Benchmark Baselines:** `tests/test_chart_generator.py` (testing patterns)
- **Related Work:** MLIR papers (https://arxiv.org/abs/2002.11054), TVM paper, Halide, Relay


**Status:** Plan updated to remove completeness claims; ready for execution.  
**Next Review:** After Milestone 1 completion (Week 2).

