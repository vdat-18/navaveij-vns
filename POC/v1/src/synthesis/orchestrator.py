"""Orchestrates the hybrid synthesis of Signal Store records.

Uses a Seed-based approach (Perturbation) combined with a Self-Correction loop
(Critique & Fix) to ensure high-fidelity clinical data generation.
"""

import asyncio
import json
from pathlib import Path

from loguru import logger

from baml_client.async_client import b
from baml_client.types import ClinicalScenario, SignalStoreRecord
from src.synthesis.validator import validate_signal_store_record


class SynthesisOrchestrator:
    """Orchestrates the generation of synthetic Signal Store records using LLMs.

    Implements a hybrid strategy:
    1. Loads a 'Golden Seed' record for the scenario.
    2. Perturbs the seed to create a realistic variation.
    3. Runs a self-correction loop (Critique & Fix) for medical accuracy.
    """

    def __init__(self, output_dir: str | None = None):
        """Initialize the orchestrator."""
        self.base_output_dir = Path(output_dir or "assets/synthesis/generated")
        self.seed_dir = Path("assets/synthesis/seeds")
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_all_scenarios(self, count_per_scenario: int = 1, scenario_name: str | None = None) -> None:
        """Generate records for clinical scenarios."""
        all_scenarios = [
            ClinicalScenario.HealthyRoutineCheckup,
            ClinicalScenario.UncontrolledHypertension,
            ClinicalScenario.MetabolicSyndromeRisk,
            ClinicalScenario.SeniorCancerScreeningGap,
        ]

        # Use filtered list if scenario_name is provided
        scenarios = [s for s in all_scenarios if s.value == scenario_name] if scenario_name else all_scenarios

        logger.info(f"Starting hybrid synthesis for {len(scenarios)} scenarios...")
        await asyncio.gather(*(self.generate_scenario(s, count_per_scenario) for s in scenarios))
        logger.success("Hybrid synthesis pipeline completed.")

    async def generate_scenario(self, scenario: ClinicalScenario, count: int = 1) -> None:
        """Generate N variations for a specific scenario."""
        seed_path = self._get_seed_path(scenario)
        with open(seed_path, encoding="utf-8") as f:
            seed_record = SignalStoreRecord.model_validate(json.load(f))

        # Create scenario-specific subdirectory
        scenario_dir = self.base_output_dir / scenario.value
        scenario_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Synthesizing {count} variations for {scenario}...")
        for i in range(count):
            await self._run_hybrid_synthesis(seed_record, scenario, i, scenario_dir)

    async def _run_hybrid_synthesis(
        self, seed: SignalStoreRecord, scenario: ClinicalScenario, index: int, output_path: Path
    ) -> None:
        """Run perturbation and self-correction loop."""
        logger.debug(f"Phase 1: Perturbing {scenario} ({index})")
        variant = await b.PerturbSignalStoreRecord(seed=seed, scenario=scenario)

        logger.debug(f"Phase 2: Correcting {scenario}")
        perfected = await b.CritiqueAndFixRecord(record=variant)

        # Ensure signals_fired and missing_signals are subsets of applicable_signals
        data = perfected.model_dump()
        clinical = data.get("clinical_signals", {})

        # Merge fired/missing into applicable for contract compliance
        clinical["applicable_signals"] = sorted(
            list(
                set(clinical.get("applicable_signals", []))
                | set(clinical.get("signals_fired", []))
                | set(clinical.get("missing_signals", []))
            )
        )

        validate_signal_store_record(data)

        file_path = output_path / f"record_{index:03d}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved: {file_path}")

    def _get_seed_path(self, scenario: ClinicalScenario) -> Path:
        """Map scenario enum to seed file path."""
        # Simple CamelCase to snake_case converter
        name = "".join(["_" + c.lower() if c.isupper() else c for c in scenario.value]).lstrip("_")
        return self.seed_dir / f"{name}_seed.json"
