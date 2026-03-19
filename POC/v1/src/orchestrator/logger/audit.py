"""5-Dimensional Audit Logger with cryptographic hash chaining for immutability."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from src.shared.settings import settings


class AuditLogger:
    """Handles immutable recording of AI decisions using a SHA-256 hash chain."""

    def __init__(self):
        """Initialize log files and retrieve the last known hash to maintain the chain."""
        self.log_file_jsonl = Path(settings.audit_log_path)
        self.log_file_json = self.log_file_jsonl.with_suffix(".json")

        self.log_file_jsonl.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Read the last line of the JSONL log file to extract the previous entry's hash."""
        if not self.log_file_jsonl.exists() or self.log_file_jsonl.stat().st_size == 0:
            return "0" * 64

        with open(self.log_file_jsonl, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            return "0" * 64

        last_line = json.loads(lines[-1])
        return last_line.get("current_hash", "0" * 64)

    def _write_json_array(self, payload: dict[str, Any]) -> None:
        """Update the JSON array file by appending the new entry."""
        entries = []
        if self.log_file_json.exists() and self.log_file_json.stat().st_size > 0:
            with open(self.log_file_json, encoding="utf-8") as f:
                entries = json.load(f)

        entries.append(payload)
        with open(self.log_file_json, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    def log_recommendation(
        self,
        patient_id: str,
        masked_context: dict[str, Any],
        ai_output: dict[str, Any],
        model_id: str,
    ) -> None:
        """Record a hash-chained audit entry to both JSONL and JSON formats."""
        timestamp = datetime.now(timezone.utc).isoformat()

        payload = {
            "timestamp": timestamp,
            "who": {"patient_id": patient_id},
            "what": {"input_context_snapshot": masked_context},
            "why": {
                "reasoning_trace": ai_output.get("reasoning_trace"),
                "decision": ai_output.get("ai_recommended_tier"),
            },
            "how": {"model_provider": settings.llm_provider, "model_id": model_id},
            "confidence": ai_output.get("confidence_score"),
            "metadata": {"environment": settings.environment},
            "previous_hash": self.last_hash,
        }

        # Calculate current hash
        payload_str = json.dumps(payload, sort_keys=True)
        current_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
        payload["current_hash"] = current_hash

        # Write to JSONL (append-only)
        with open(self.log_file_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

        # Write to JSON (array format)
        self._write_json_array(payload)

        self.last_hash = current_hash
        logger.info(f"Dual audit log written for patient: {patient_id}")
