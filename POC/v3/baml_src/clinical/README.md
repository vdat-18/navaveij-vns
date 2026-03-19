# Clinical BAML Domain

This directory contains the BAML definitions for the Navaveij clinical reasoning engine.

## Structure

- `entities.baml`: Domain models (Classes) for medical recommendations and safety checks. Note: the `Tier` enum is defined in `recommendation_output.baml` and shared across this domain.
- `recommendation_output.baml`: Output types and `GenerateRecommendation` function for producing structured patient checkup recommendations.
- `safety_critic.baml`: Function and prompt for the Safety Critic agent.

## Usage

These functions are called from the Python orchestrator via the generated `baml_client`.
