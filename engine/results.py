from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime

class StepResult(BaseModel):
    """Result of executing a single step."""
    step_name: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float  # seconds
    started_at: datetime
    completed_at: datetime
    retries: int = 0
    metadata: Dict[str, Any] = {}

class ExecutionResult(BaseModel):
    """Result of executing a complete workflow."""
    workflow_name: str
    success: bool
    final_state: Dict[str, Any]
    step_results: List[StepResult]
    total_execution_time: float
    started_at: datetime
    completed_at: datetime
    error: Optional[str] = None
    execution_history: List[Dict[str, Any]] = []