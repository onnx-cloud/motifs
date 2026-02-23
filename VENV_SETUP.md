# Virtual Environment Setup in Makefile
## Overview

The Makefile now automatically manages a Python virtual environment for the charting and experimentation tools.
## Key Features

✅ **Automatic venv creation** — First `make install-charting` creates `venv/`  
✅ **Dependency management** — `rdflib` and `pyyaml` installed in venv  
✅ **Consistent execution** — All chart/report generation uses venv Python  
✅ **Clean removal** — `make clean-venv` removes the venv  
## Usage
### Initial Setup
```bash
make install-charting    # Creates venv/ and installs dependencies
```
### Generate Charts & Reports
```bash
make charts              # Uses venv automatically
make report              # Uses venv automatically
make figures             # Both charts + report
```
### Manual venv Activation (optional)
```bash
source venv/bin/activate
python src/charting/chart_generator.py --help
deactivate
```
### Cleanup
```bash
make clean-venv         # Remove venv/
make clean-charts       # Remove generated figures
make clean              # Remove everything
```
## Makefile Implementation

The Makefile defines:
- `VENV := venv` — Virtual environment directory
- `PYTHON := $(VENV)/bin/python` — Python interpreter in venv
- `PIP := $(VENV)/bin/pip` — Pip installer in venv

All chart/report commands use `$(PYTHON)` and `$(PIP)` instead of system Python.
## Benefits

1. **Isolation** — Project dependencies don't affect system Python
2. **Reproducibility** — Same environment across machines
3. **Clean state** — Remove with `make clean-venv` if needed
4. **No manual activation** — Makefile handles it automatically
5. **CI/CD friendly** — Works in automated build pipelines
## Example Workflow

```bash
# First time
make figures              # Creates venv, installs, generates everything

# Subsequent times (venv reused)
make figures              # Faster, skips venv creation

# Update dependencies (if requirements change)
make clean-venv
make install-charting     # Fresh venv with updated packages

# Cleanup
make clean                # Removes venv, charts, reports, build artifacts
```
## Files Generated

- `venv/` — Virtual environment directory
- `papers/figures/*.json` — Vega-Lite chart specifications
- `papers/figures/*.html` — Standalone chart viewers
- `papers/motif_analysis_report.html` — Comprehensive HTML report
## Notes

- The venv is `.gitignore`'d (not committed to repo)
- Python version is automatically detected (uses `python3 -m venv`)
- Works on macOS, Linux, and Windows (with minor shell adjustments)
