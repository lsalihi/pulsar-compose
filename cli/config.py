import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class CLIConfig(BaseModel):
    """Configuration for Pulsar CLI."""
    default_provider: str = "openai"
    history_dir: str = "~/.pulsar/history"
    workflow_dir: str = "~/.pulsar/workflows"
    log_level: str = "INFO"
    enable_progress: bool = True
    max_history: int = 100
    plugins: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def load(cls) -> "CLIConfig":
        """Load configuration from file or create default."""
        config_path = Path.home() / ".pulsar" / "config.yml"

        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                return cls(**data)
            except Exception:
                # Fall back to defaults if config is invalid
                pass

        # Create default config
        config = cls()
        config.save()
        return config

    def save(self) -> None:
        """Save configuration to file."""
        config_dir = Path.home() / ".pulsar"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.yml"

        with open(config_path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)

    @property
    def history_path(self) -> Path:
        """Get expanded history directory path."""
        return Path(self.history_dir).expanduser()

    @property
    def workflow_path(self) -> Path:
        """Get expanded workflow directory path."""
        return Path(self.workflow_dir).expanduser()

# Global config instance
config = CLIConfig.load()