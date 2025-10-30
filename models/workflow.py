from __future__ import annotations
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Any, Optional, Union, Literal
import yaml
import os

class Agent(BaseModel):
    model: str
    provider: Literal["openai", "anthropic", "local"]
    prompt: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class AgentStep(BaseModel):
    type: Literal["agent"]
    step: str
    agent: str
    prompt: Optional[str] = None  # Override agent prompt if specified
    context: Optional[str] = None
    save_to: Optional[str] = None
    max_retries: int = 3

class ConditionalStep(BaseModel):
    type: Literal["conditional"]
    step: str
    if_: str = Field(alias="if")
    then: List[Step]
    else_: Optional[List[Step]] = None

class InteractionStep(BaseModel):
    type: Literal["interaction"]
    step: str
    ask_user: Dict[str, Any]  # Complex structure for user questions
    save_to: str  # Variable name to save responses
    provider: Optional[str] = "console"  # Input provider to use
    timeout: Optional[int] = None  # Timeout in seconds

Step = Union[AgentStep, ConditionalStep, InteractionStep]

class Workflow(BaseModel):
    version: str = "0.1"
    name: str
    agents: Dict[str, Agent]
    workflow: List[Step]

    def __init__(self, **data):
        super().__init__(**data)
        self._validate_agent_references()

    def _validate_agent_references(self):
        """Validate that all agent references in steps exist."""
        for step in self.workflow:
            if isinstance(step, AgentStep):
                if step.agent not in self.agents:
                    raise ValueError(f"Agent '{step.agent}' referenced in step '{step.step}' not found in workflow agents")

    @classmethod
    def from_yaml(cls, file_path: str) -> Workflow:
        """Load workflow from YAML file with error handling."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Workflow file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax in {file_path}: {e}")

        if data is None:
            raise ValueError(f"Empty YAML file: {file_path}")

        try:
            return cls.model_validate(data)
        except ValidationError as e:
            raise ValueError(f"Invalid workflow structure in {file_path}: {e}")

    def to_json(self) -> str:
        """Serialize workflow to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> Workflow:
        """Deserialize workflow from JSON string."""
        return cls.model_validate_json(json_str)