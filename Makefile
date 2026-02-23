# Makefile for Motif Models repository
# Targets: make pdf, make charts, make clean, make help

SHELL := /bin/bash
PAPER_DIR = papers/motif-models
PAPER_TEX = $(PAPER_DIR)/index.tex
PAPER_PDF = motif-models.pdf
SITE_OUT = ./tmp/site

# Paper source files (include all tex, bib, and style files so changes trigger rebuild)
MOTIF_MODELS_SRC := $(shell find papers/motif-models -type f \( -name '*.tex' -o -name '*.bib' -o -name '*.sty' \))
TYPED_REALITY_SRC := $(shell find papers/typed-reality -type f \( -name '*.tex' -o -name '*.bib' -o -name '*.sty' \))


# Virtual environment
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Fuse output override (use: make fusion FUSE_OUT=/path/to/out)
FUSE_OUT ?= ./tmp/fuse

.PHONY: pdf clean help charts report figures clean-charts venv install-charting clean-venv fusion clean-fusion

help:
	@echo "Motif Models — Makefile targets:"
	@echo ""
	@echo "Setup:"
	@echo "  make venv            Create Python virtual environment"
	@echo "  make install-charting Install charting tool dependencies"
	@echo ""
	@echo "Documentation:"
	@echo "  make pdf             Compile LaTeX papers (generates motif-models.pdf and typed-reality.pdf)"
	@echo ""
	@echo "Charts & Figures:"
	@echo "  make charts          Generate all Vega-Lite charts"
	@echo "  make docs            Generate HTML documentation site"
	@echo "  make report          Generate HTML analysis report"
	@echo "  make figures         Generate both charts and report"
	@echo ""
	@echo "Code Generation:"
	@echo "  make fusion          Generate .fuse snippets from motif ontology"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           Remove build artifacts"
	@echo "  make clean-charts    Remove generated chart files"
	@echo "  make clean-docs      Remove generated documentation"
	@echo "  make clean-fusion    Remove generated .fuse snippets"
	@echo "  make clean-venv      Remove virtual environment"
	@echo "  make help            Show this help message"

# Create and maintain virtual environment
$(VENV)/bin/activate:
	@echo "Creating Python virtual environment..."
	python3 -m venv $(VENV)
	@echo "✓ Virtual environment created at $(VENV)/"
	@echo "To activate: source $(VENV)/bin/activate"

venv: $(VENV)/bin/activate

install-charting: venv
	@echo "Installing charting dependencies..."
	$(PIP) install --upgrade pip setuptools wheel > /dev/null 2>&1
	$(PIP) install -q rdflib pyyaml pystache vl-convert-python
	@echo "✓ Charting dependencies installed"

install-opset: venv
	@echo "Installing ONNX tooling..."
	$(PIP) install -q onnx
	@echo "✓ ONNX installed"

install-shacl: venv
	@echo "Installing SHACL validator (pyshacl)..."
	$(PIP) install -q pyshacl rdflib
	@echo "✓ pyshacl installed"

opset: install-opset
	@echo "Generating ONNX opset TTL..."
	@$(PYTHON) src/onnx/opset_to_ttl.py
	@echo "✓ opset TTL generated to ttl/onnx/"

shacl: install-shacl
	@echo "Running SHACL validation over TTL motifs..."
	@$(PYTHON) scripts/run_shacl.py
	@echo "SHACL validation completed"

clean-opset:
	@rm -f ttl/onnx/opset.ttl || true
	@echo "✓ Removed generated opset TTL (ttl/onnx/opset.ttl)"

# PDF compilation target: build PDFs for every paper in ./papers/* that has an index.tex
PAPERS := $(shell for d in papers/*; do [ -f $$d/index.tex ] && basename $$d; done)
PAPER_PDFS := $(addsuffix .pdf,$(PAPERS))

# Verbose toggle: run with VERBOSE=1 to see pdflatex/biber output
ifdef VERBOSE
	LATEX_QUIET :=
else
	LATEX_QUIET := > /dev/null 2>&1
endif


# Build all papers, continue when one fails and report summary
.PHONY: pdf
pdf:
	@failed=0; \
	for p in $(PAPERS); do \
		printf "Building %s...\n" $$p; \
		if $(CURDIR)/scripts/build_paper.sh $$p $(CURDIR) $(if $(VERBOSE),,quiet) ; then \
			printf " ✓ %s built\n" $$p; \
		else \
			printf " ✗ %s failed\n" $$p; failed=1; \
		fi; \
	done; \
	if [ $$failed -eq 1 ]; then \
		echo "One or more papers failed to build."; false; \
	else \
		echo "All papers built successfully."; \
	fi

# Per-paper build: a generic pattern rule to build any paper under papers/* with an index.tex
# Each paper's sources (tex/bib/sty) are implicitly watched via the PAPERS variable

%.pdf:
	@paper=$$(basename $@ .pdf) ; \
	if [ -f papers/$$paper/index.tex ]; then \
		mkdir -p tmp/$$paper ; \
		# Use helper script to perform build
		$(CURDIR)/scripts/build_paper.sh $$paper $(CURDIR) $(if $(VERBOSE),,quiet) ; \
	else \
		echo "No paper directory for $@" ; exit 1 ; \
	fi

# Chart generation
charts: install-charting
	@echo "Generating Vega-Lite charts from SPARQL queries..."
	@$(PYTHON) -c "import sys; sys.path.insert(0, '.'); from src.charting.chart_generator import ChartGenerator; from pathlib import Path; gen = ChartGenerator(); [gen.write_output(gen.process_config(gen.load_config(p)), Path('papers/figures'), formats=['json', 'html', 'png']) for p in sorted(Path('charts').glob('*.yaml'))]"
	@echo "✓ Charts generated to papers/figures/"

# List available papers
papers:
	@echo "Available papers:"
	@for p in $(PAPERS); do echo " - $$p"; done

# full micro-site generation
full-site: install-charting figures fusion opset

# Run inference SPARQL CONSTRUCT queries and write TTL outputs to ttl/infer
.PHONY: infer
infer: venv
	@echo "Running inference queries and writing TTL to ttl/infer/"
	@PYTHONPATH=. $(PYTHON) src/infer/run_inference.py --sparql-dir sparql/infer --out ttl/infer --ttl-dir ttl
	@echo "✓ Inferred TTL written to ttl/infer/"


# dev-time re-generation
site: 
	@echo "Generating WIKI..."
	@PYTHONPATH=. $(PYTHON) src/wiki/generator.py --config config/wiki.yaml --output $(SITE_OUT)
	@echo "✓ Documentation generated to $(SITE_OUT)/"

report: charts
	@echo "Generating HTML report..."
	@$(PYTHON) src/charting/generate_report.py
	@echo "✓ Report generated to papers/motif_analysis_report.html"

figures: report

# Fuse snippet generation
fusion: install-charting
	@echo "Generating .fuse snippets from motif ontology..."
	@PYTHONPATH=. $(PYTHON) src/fuse_generator.py \
		--ttl-dir ttl \
		--sparql-dir sparql \
		--output-dir $(FUSE_OUT) \
		--template src/template/fuse-motifs.mustache \
		--summary -v
	@echo "✓ Fuse snippets generated to $(FUSE_OUT)/"

# Cleanup targets
clean-fusion:
	@rm -f $(FUSE_OUT)/*.fuse
	@echo "✓ Removed generated .fuse snippets"

clean-charts:
	@rm -f papers/figures/*.json papers/figures/*.html papers/figures/*.png papers/figures/*.data.json
	@echo "✓ Removed generated chart files"

clean-docs:
	@rm -rf docs/motifs docs/onnx docs/domains docs/use-cases docs/categories docs/figures
	@rm -f docs/index.html
	@rm -rf $(SITE_OUT)
	@echo "✓ Removed generated documentation"

clean-venv:
	@rm -rf $(VENV)
	@echo "✓ Removed virtual environment ($(VENV)/)"

clean: clean-charts clean-fusion clean-docs
	@rm -rf tmp/motif-models tmp/typed-reality || true ; \
	rm -f *.aux *.bbl *.bcf *.blg *.fdb_latexmk *.fls *.log *.out *.run.xml *.toc && \
	echo "✓ Cleaned LaTeX build artifacts (motif-models)" ; \
	cd ../typed-reality && \
	rm -f *.aux *.bbl *.bcf *.blg *.fdb_latexmk *.fls *.log *.out *.run.xml *.toc && \
	echo "✓ Cleaned LaTeX build artifacts (typed-reality)" ; \
	cd  && \
	rm -f motif-models.pdf typed-reality.pdf && \
	echo "✓ Removed root PDFs" && \
	rm -f papers/motif_analysis_report.html && \
		echo "✓ Removed generated report" && \
		rm -f ttl/onnx/opset.ttl || true && \
		echo "✓ Removed ttl/onnx/opset.ttl"
