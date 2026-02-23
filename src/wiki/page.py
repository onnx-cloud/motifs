"""Page rendering utilities used by the wiki generator."""
from __future__ import annotations

from typing import Optional, Dict
import jinja2


class PageRenderer:
    """Render pages using Jinja2 when available, otherwise a simple fallback."""

    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir
        self._env = None
        loader = jinja2.FileSystemLoader(template_dir) if template_dir else None
        self._env = jinja2.Environment(loader=loader)

    def precompile_templates(self) -> None:
        """Precompile templates (noop in this minimal implementation)."""
        return

    def render_string(self, template_str: str, context: Optional[Dict] = None) -> str:
        """Render a template string with the provided context."""
        context = context or {}
        # Prefer Python-style formatting for templates that use {var} placeholders
        import re
        if re.search(r"\{[^{}]+\}", template_str):
            try:
                return template_str.format(**context)
            except Exception:
                pass
        if self._env is not None:
            tmpl = self._env.from_string(template_str)
            return tmpl.render(**context)
        # Final fallback
        return template_str
    def render(self, template_name: str, context: Optional[Dict] = None) -> str:
        """Render a named template from `template_dir` if possible."""
        context = context or {}
        if self._env is not None and self._env.loader is not None:
            tmpl = self._env.get_template(template_name)
            return tmpl.render(**context)
        raise RuntimeError("Templates not available and no template_dir provided")
