# Navaveij Inference Orchestrator

The Inference Orchestrator is the central "brain" of the Navaveij Health Checkup Recommendation system. It coordinates the data flow between clinical tools, privacy layers, and AI models.

## Overview

This component implements a **Hybrid ReAct Loop** that ensures all clinical recommendations are based on verified medical signals while maintaining strict patient privacy.

### Key Capabilities

- **PII Masking & Rehydration**: Automatically pseudonymizes sensitive data (Name, DOB, MRN) before sending it to Cloud AI providers, and restores it for the final report.
- **Baseline Orchestration**: Automatically executes a mandatory set of MCP tools to gather a "5-Dimensional" view of the patient's health.
- **Pluggable AI Gateway**: Supports multiple LLM providers (OpenAI, Anthropic, etc.) through a unified interface.
- **MCP Integration**: Connects seamlessly to the local Clinical MCP Server via `stdio` transport.

## Project Structure

- `agents/orchestrator.py`: The core engine managing the reasoning loop via BAML.
- `privacy/`:
    - `masking.py`: Logic for converting sensitive data into tokens.
    - `rehydration.py`: Logic for restoring tokens to original values.
- `safety/`:
    - `validator.py`: Implements the `ClinicalSafetyGuard` for AI response verification.
- `logger/`:
    - `audit.py`: Implements a 5-dimensional audit logger for compliance.

## Usage

### Prerequisites

- Ensure the [Clinical MCP Server](../mcp_server/README.md) is configured.
- Environment variables (in `.env`):
    - `LLM_MODEL`: The model name (e.g., `llama-3.2-3b-instruct`).
    - `LLM_BASE_URL`: OpenAI-compatible endpoint.
    - `LLM_API_KEY`: API key if required.

### Installation

```bash
uv sync
baml-cli generate
```

### Running the Orchestrator (Integration Test)

```bash
PYTHONPATH=. uv run python test_orchestrator.py
```

## How It Works (The Clinical reasoning Loop)

1.  **Phase 1 — Discovery**: Calls MCP tools to build a health context snapshot.
2.  **Phase 2 — Transformation**: Masks PII to ensure privacy before cloud processing.
3.  **Phase 3 — Recommendation**: Engages BAML to generate a structured recommendation.
4.  **Phase 4 — Safety Audit**: A secondary AI "Critic" validates the recommendation.
5.  **Phase 5 — Traceability**: Records an immutable audit log and rehydrates data for the final output.

## Coding Standards

- **Ruff**: Enforced formatting and linting.
- **BAML**: Type-safe LLM outputs and schema enforcement.
- **Loguru**: Structured logging.
