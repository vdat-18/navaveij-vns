# Clinical BAML Domain

This directory contains the BAML definitions for the Navaveij clinical reasoning engine.

## Structure

- `entities.baml`: Domain models (Enums, Classes) for medical recommendations and safety checks.
- `orchestrator.baml`: Function and prompt for generating patient checkup recommendations.
- `safety_critic.baml`: Function and prompt for the Safety Critic agent.

## Usage

These functions are called from the Python orchestrator via the generated `baml_client`.
