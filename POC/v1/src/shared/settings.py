"""Project settings loaded from environment/.env via Pydantic Settings."""

from abc import ABC
from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class ProjectBaseSettings(BaseSettings, ABC):
    """Base settings with common Pydantic configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class LogLevel(str, Enum):
    """Supported log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LLMSettings(ProjectBaseSettings):
    """Configuration for any OpenAI-compatible LLM provider (Cloud or Local)."""

    llm_api_key: str | None = "no-key-required"
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = "gemini-1.5-flash"
    llm_provider: str = "openai"


class MCPSettings(ProjectBaseSettings):
    """MCP Server connection settings."""

    mcp_server_command: str = "uv"
    mcp_server_args: list[str] = ["run", "python", "-m", "src.mcp_server.server"]


class ProjectSettings(LLMSettings, MCPSettings):
    """Aggregate project settings."""

    environment: str = "dev"
    log_level: LogLevel = LogLevel.INFO
    audit_log_path: str = "logs/audit.jsonl"
    patient_token_secret_salt: str = "navavej-clinical-recommendation-engine-secret-salt-2026"


settings = ProjectSettings()
