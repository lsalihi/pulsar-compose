from __future__ import annotations
from typing import Dict, Any, List, Optional, Union
import asyncio
from datetime import datetime
from .template import TemplateRenderer

class StateManager:
    """State manager for Pulsar workflow execution with advanced features."""

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        self._state: Dict[str, Any] = initial_state or {}
        self._history: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._renderer = TemplateRenderer()
        self._render_depth = 0  # Prevent infinite recursion in templates

    async def set(self, key: str, value: Any) -> None:
        """Set a value in the state using dot notation for nested access."""
        async with self._lock:
            self._set_nested(self._state, key, value)

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state using dot notation for nested access."""
        async with self._lock:
            return self._get_nested(self._state, key, default)

    async def render_template(self, template: str) -> str:
        """Render a template string with state variables."""
        if self._render_depth > 10:  # Prevent infinite recursion
            raise ValueError("Template rendering depth exceeded (possible circular reference)")

        self._render_depth += 1
        try:
            # Use the nested state structure for template rendering
            context = self._state.copy()
            result = self._renderer.render(template, context)
            return result
        finally:
            self._render_depth -= 1

    async def update_from_agent_output(self, step_name: str, output: Any) -> None:
        """Update state with agent output and record in execution history."""
        async with self._lock:
            self._set_nested(self._state, step_name, output)
            self._history.append({
                "step": step_name,
                "output": output,
                "timestamp": datetime.now().isoformat()
            })

    async def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the execution history of all steps."""
        async with self._lock:
            return self._history.copy()

    async def get_state_snapshot(self) -> Dict[str, Any]:
        """Get a deep copy of the current state."""
        async with self._lock:
            return self._deep_copy(self._state)

    def _set_nested(self, data: Dict[str, Any], key: str, value: Any) -> None:
        """Set a nested value using dot notation.
        This mutates the original data structure, creating intermediate dicts/lists as needed.
        """
        keys = key.split('.')
        current: Union[Dict[str, Any], List[Any]] = data
        parent: Optional[Union[Dict[str, Any], List[Any]]] = None
        parent_key: Optional[Union[str, int]] = None

        # Traverse all but the final key, creating containers as needed
        for k in keys[:-1]:
            if k.isdigit():
                idx = int(k)
                if not isinstance(current, list):
                    # Convert parent slot into a list
                    new_list: List[Any] = []
                    if parent is None:
                        # When at root, ensure data becomes a dict with numeric key only through a named key.
                        # This case is unlikely for our workflows; safeguard by resetting current reference.
                        current = new_list
                    else:
                        parent[parent_key] = new_list  # type: ignore[index]
                        current = new_list
                # Grow list with dict placeholders
                while len(current) <= idx:
                    current.append({})  # type: ignore[attr-defined]
                parent = current
                parent_key = idx
                current = current[idx]  # type: ignore[index]
            else:
                if not isinstance(current, dict):
                    # Convert parent slot into a dict
                    new_dict: Dict[str, Any] = {}
                    if parent is None:
                        # At root, ensure current is a dict
                        current = new_dict
                    else:
                        parent[parent_key] = new_dict  # type: ignore[index]
                        current = new_dict
                if k not in current:
                    current[k] = {}  # type: ignore[index]
                parent = current
                parent_key = k
                current = current[k]  # type: ignore[index]

        # Apply final key
        final_key = keys[-1]
        if final_key.isdigit():
            idx = int(final_key)
            if not isinstance(current, list):
                new_list2: List[Any] = []
                if parent is None:
                    current = new_list2
                else:
                    parent[parent_key] = new_list2  # type: ignore[index]
                    current = new_list2
            while len(current) <= idx:
                current.append(None)  # type: ignore[attr-defined]
            current[idx] = value  # type: ignore[index]
        else:
            if not isinstance(current, dict):
                new_dict2: Dict[str, Any] = {}
                if parent is None:
                    current = new_dict2
                else:
                    parent[parent_key] = new_dict2  # type: ignore[index]
                    current = new_dict2
            current[final_key] = value  # type: ignore[index]

    def _get_nested(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get a nested value using dot notation."""
        keys = key.split('.')
        current = data

        for k in keys:
            if isinstance(current, dict):
                if k not in current:
                    return default
                current = current[k]
            elif isinstance(current, list):
                if not k.isdigit():
                    return default
                idx = int(k)
                if idx >= len(current):
                    return default
                current = current[idx]
            else:
                return default

        return current

    def _flatten_state(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested state for template rendering."""
        result = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten_state(value, full_key))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        result.update(self._flatten_state(item, f"{full_key}.{i}"))
                    else:
                        result[f"{full_key}.{i}"] = item
            else:
                result[full_key] = value
        return result

    def _deep_copy(self, obj: Any) -> Any:
        """Create a deep copy of an object."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj