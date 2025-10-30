import importlib
import pkgutil
from typing import Dict, Any, List
from pathlib import Path
import click

class PluginManager:
    """Manages CLI plugins."""

    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.commands: List[click.Command] = []

    def load_plugins(self):
        """Load plugins from configuration."""
        from .config import config

        for plugin_name, plugin_config in config.plugins.items():
            try:
                self._load_plugin(plugin_name, plugin_config)
            except Exception as e:
                click.echo(f"Failed to load plugin {plugin_name}: {e}", err=True)

    def _load_plugin(self, name: str, config: Dict[str, Any]):
        """Load a single plugin."""
        module_path = config.get("module")
        if not module_path:
            return

        try:
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, config.get("class", "Plugin"))
            plugin_instance = plugin_class(**config.get("kwargs", {}))

            self.plugins[name] = plugin_instance

            # If plugin has commands, add them
            if hasattr(plugin_instance, "get_commands"):
                commands = plugin_instance.get_commands()
                self.commands.extend(commands)

        except ImportError:
            click.echo(f"Plugin module {module_path} not found", err=True)
        except AttributeError as e:
            click.echo(f"Plugin class not found in {module_path}: {e}", err=True)

    def get_commands(self) -> List[click.Command]:
        """Get all plugin commands."""
        return self.commands

# Global plugin manager
plugin_manager = PluginManager()