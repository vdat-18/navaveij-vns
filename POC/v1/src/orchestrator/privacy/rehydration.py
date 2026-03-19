"""PII Rehydration module for restoring original values from pseudonymized tokens."""

from typing import Any

from loguru import logger


class PIIRehydrator:
    """Restores original PII values into the structured AI output before dashboard delivery."""

    def __init__(self, rehydration_map: dict[str, str]):
        """Initialize the rehydrator with a specific request-scoped mapping."""
        self.rehydration_map = rehydration_map

    def rehydrate(self, data: Any) -> Any:
        """Recursively replace tokens with original values in dictionaries and lists."""
        if isinstance(data, str):
            if original_value := self.rehydration_map.get(data):
                logger.debug(f"Rehydrated token '{data}' back to original value")
                return original_value
            return data

        if isinstance(data, dict):
            return {key: self.rehydrate(value) for key, value in data.items()}

        if isinstance(data, list):
            return [self.rehydrate(item) for item in data]

        return data
