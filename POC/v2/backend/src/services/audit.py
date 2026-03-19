import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shared.settings import settings


class AuditLogger:
    """Handles immutable recording of AI decisions with SHA-256 hash chaining."""

    def __init__(self):
        """Initializes logging paths."""
        self.log_file_jsonl = Path(settings.audit_log_path)
        self.log_file_json = self.log_file_jsonl.with_suffix(".json")
        self.log_file_jsonl.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Retrieves last hash from JSONL."""
        if not self.log_file_jsonl.exists() or self.log_file_jsonl.stat().st_size == 0:
            return "0" * 64
        try:
            with open(self.log_file_jsonl, encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
                return json.loads(lines[-1]).get("current_hash", "0" * 64) if lines else "0" * 64
        except Exception:
            return "0" * 64

    def _write_json_array(self, payload: dict[str, Any]) -> None:
        """Updates JSON array file."""
        entries = []
        if self.log_file_json.exists() and self.log_file_json.stat().st_size > 0:
            with open(self.log_file_json, encoding="utf-8") as f:
                entries = json.load(f)
        entries.append(payload)
        with open(self.log_file_json, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)

    def log_recommendation(
        self, patient_id: str, masked_context: dict[str, Any], ai_output: dict[str, Any], model_id: str
    ) -> str:
        """Logs recommendation."""
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
        curr_h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        payload["current_hash"] = curr_h
        with open(self.log_file_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        self._write_json_array(payload)
        self.last_hash = curr_h
        return curr_h

    def log_decision(
        self, patient_id: str, recommendation_hash: str, decision: str, physician_id: str, notes: str = ""
    ) -> str:
        """Logs physician decision."""
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "who": {"patient_id": patient_id, "physician_id": physician_id},
            "what": {"event": "PROVISIONING_DECISION", "recommendation_reference_hash": recommendation_hash},
            "why": {"decision": decision, "notes": notes},
            "metadata": {"environment": settings.environment},
            "previous_hash": self.last_hash,
        }
        curr_h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        payload["current_hash"] = curr_h
        with open(self.log_file_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        self._write_json_array(payload)
        self.last_hash = curr_h
        return curr_h

    def get_logs(self) -> list[dict[str, Any]]:
        """Retrieves audit logs."""
        if not self.log_file_json.exists():
            return []
        try:
            with open(self.log_file_json, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
