"""Configuration and setup utilities."""

from pathlib import Path
import yaml
from typing import Dict, Any

_config_cache = None


def get_project_root() -> Path:
    """Detect project root (contains ttl/ or .github/)."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "ttl").exists() or (current / ".github").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_project_config() -> Dict[str, Any]:
    """Load project configuration from config/motif-models.yaml."""
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    root = get_project_root()
    candidates = ["motif-models.yaml", "motifs-matter.yaml", "motifs-matter.yml"]
    config_path = None
    for name in candidates:
        p = root / "config" / name
        if p.exists():
            config_path = p
            break

    if config_path is None:
        raise FileNotFoundError(f"Configuration file not found in config/: tried {candidates}")

    with open(config_path) as f:
        _config_cache = yaml.safe_load(f)

    return _config_cache


def get_paths() -> Dict[str, Path]:
    """Get all project paths from configuration."""
    config = load_project_config()
    root = get_project_root()
    
    paths = {}
    for key, value in config.get("paths", {}).items():
        paths[key] = root / value
    
    return paths


def get_chart_config() -> Dict[str, Any]:
    """Get chart generation configuration."""
    config = load_project_config()
    return config.get("charting", {})


def get_report_config() -> Dict[str, Any]:
    """Get report generation configuration."""
    config = load_project_config()
    return config.get("reporting", {})


def validate_paths() -> Dict[str, Path]:
    """Validate and resolve all project paths."""
    return get_paths()


def load_chart_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate chart configuration."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Validate required fields
    required = {"title", "query", "vega"}
    if not required.issubset(set(config.keys())):
        raise ValueError(f"Config missing required fields: {required - set(config.keys())}")
    
    return config
