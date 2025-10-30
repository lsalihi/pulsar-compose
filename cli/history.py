import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from .config import config
from engine.results import ExecutionResult

class ExecutionHistory:
    """Manages execution history persistence."""

    def __init__(self):
        self.history_dir = config.history_path
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def save_execution(self, workflow_name: str, result: ExecutionResult) -> str:
        """Save execution result and return run ID."""
        run_id = str(uuid.uuid4())

        execution_data = {
            "run_id": run_id,
            "workflow_name": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "result": result.model_dump()
        }

        history_file = self.history_dir / f"{run_id}.json"
        with open(history_file, 'w') as f:
            json.dump(execution_data, f, indent=2, default=str)

        # Clean up old history files if exceeding max
        self._cleanup_old_history()

        return run_id

    def get_execution(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get execution data by run ID."""
        history_file = self.history_dir / f"{run_id}.json"
        if not history_file.exists():
            return None

        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def list_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent executions."""
        executions = []

        for history_file in sorted(self.history_dir.glob("*.json"), reverse=True):
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    executions.append(data)
                    if len(executions) >= limit:
                        break
            except Exception:
                continue

        return executions

    def get_execution_result(self, run_id: str) -> Optional[ExecutionResult]:
        """Get ExecutionResult object for run ID."""
        data = self.get_execution(run_id)
        if not data or "result" not in data:
            return None

        try:
            return ExecutionResult(**data["result"])
        except Exception:
            return None

    def _cleanup_old_history(self) -> None:
        """Remove old history files beyond max_history limit."""
        history_files = sorted(self.history_dir.glob("*.json"), key=lambda x: x.stat().st_mtime)

        if len(history_files) > config.max_history:
            files_to_remove = history_files[:len(history_files) - config.max_history]
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                except Exception:
                    pass