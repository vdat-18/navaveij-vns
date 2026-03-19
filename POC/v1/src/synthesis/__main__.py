import argparse
import asyncio

# Ensure we can import from the parent package if needed
# But since we use -m, it should be fine.
from dotenv import load_dotenv
from loguru import logger

from src.synthesis.orchestrator import SynthesisOrchestrator

# Load environment variables from .env
load_dotenv()


async def main():
    parser = argparse.ArgumentParser(description="Navaveij Clinical Data Synthesizer")
    parser.add_argument("--count", type=int, default=1, help="Number of records to generate per scenario")
    parser.add_argument(
        "--scenario", type=str, default=None, help="Specific scenario to generate (e.g. HealthyRoutineCheckup)"
    )
    parser.add_argument("--output", type=str, default="assets/synthesis", help="Output directory")

    args = parser.parse_args()

    logger.info("Initializing Navaveij Synthesis Engine...")
    orchestrator = SynthesisOrchestrator(output_dir=args.output)

    await orchestrator.generate_all_scenarios(count_per_scenario=args.count, scenario_name=args.scenario)
    logger.success("All synthesis tasks completed!")


if __name__ == "__main__":
    asyncio.run(main())
