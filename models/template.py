from jinja2 import Template, StrictUndefined
from typing import Dict, Any, Optional

class TemplateRenderer:
    """Template rendering system using Jinja2 for {{variables}}."""

    def render(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render template string with given context variables."""
        try:
            template = Template(template_str, undefined=StrictUndefined)
            return template.render(**context)
        except Exception as e:
            raise ValueError(f"Template rendering failed: {e}")

    def render_with_fallback(self, template_str: Optional[str], context: Dict[str, Any], fallback: str = "") -> str:
        """Render template if present, otherwise return fallback."""
        if template_str:
            return self.render(template_str, context)
        return fallback