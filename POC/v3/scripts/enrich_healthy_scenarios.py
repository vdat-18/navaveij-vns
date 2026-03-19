import json
import asyncio
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from baml_client.async_client import b
from baml_client.types import SignalStoreRecord

# Set up paths
BASE_DIR = Path(__file__).parent.parent
STORE_DIR = BASE_DIR / "assets/synthesis/generated/HealthyRoutineCheckup"

async def enrich_record(record_path: Path):
    logger.info(f"Enriching: {record_path.name}")
    
    with open(record_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Use BAML to get enriched fields
    try:
        # Pass the data as a dict, BAML will parse it into SignalStoreRecord if modeled correctly
        # Or we can just pass the JSON string. Since we have the model, we can try using it.
        # But BAML functions take the BAML type.
        
        # BAML b.EnrichHealthyPatientRecord expects SignalStoreRecord
        # The generated client has a way to parse python dict into baml models
        
        enrichment = await b.EnrichHealthyPatientRecord(data)
        
        if not enrichment:
            logger.warning(f"AI returned empty enrichment for {record_path.name}")
            return

        # 1. Chief Complaint
        if enrichment.chief_complaint:
            data["clinical_signals"]["chief_complaint"] = enrichment.chief_complaint
            
        # 2. Behavioral Flags - Occupational
        occ = data["clinical_signals"]["behavioral_flags"].get("occupational", {})
        if enrichment.occupational_tags:
            current_tags = set(occ.get("tags", []))
            for t in enrichment.occupational_tags:
                current_tags.add(t)
            occ["tags"] = list(current_tags)
            
        occ["computer_hours_per_day"] = enrichment.computer_hours_per_day
        occ["night_shift_worker"] = enrichment.night_shift_worker
        occ["factory_chemical_exposure"] = enrichment.factory_chemical_exposure
        data["clinical_signals"]["behavioral_flags"]["occupational"] = occ
        
        # 3. Behavioral Flags - Smoking
        smoking = data["clinical_signals"]["behavioral_flags"].get("smoking")
        if smoking and enrichment.smoking_pack_years is not None:
             smoking["pack_years"] = enrichment.smoking_pack_years
             
        # 4. Behavioral Flags - Alcohol
        alcohol = data["clinical_signals"]["behavioral_flags"].get("alcohol", {})
        alcohol["units_per_week"] = enrichment.alcohol_units_per_week
        data["clinical_signals"]["behavioral_flags"]["alcohol"] = alcohol
        
        # 5. Reproductive History Detail
        if enrichment.reproductive_history:
            # We add it as a new detail object to clinical_signals
            data["clinical_signals"]["reproductive_history_detail"] = enrichment.reproductive_history.model_dump()

        # 6. Suggested Vaccines
        if enrichment.suggested_vaccines:
            current_vaccines = data["clinical_signals"].get("vaccination_gaps", [])
            current_vax_ids = {v["vaccine_id"] for v in current_vaccines}
            
            for vax in enrichment.suggested_vaccines:
                if vax.vaccine_id not in current_vax_ids:
                    # BAML pydantic models to dict
                    current_vaccines.append(vax.model_dump())
            
            data["clinical_signals"]["vaccination_gaps"] = current_vaccines

        # Save back
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.success(f"Successfully enriched: {record_path.name}")
        
    except Exception as e:
        logger.error(f"Failed to enrich {record_path.name}: {e}")

async def main():
    if not STORE_DIR.exists():
        logger.error(f"Directory not found: {STORE_DIR}")
        return
        
    for f in STORE_DIR.glob("record_*.json"):
        await enrich_record(f)
    logger.info("Enrichment complete.")

if __name__ == "__main__":
    asyncio.run(main())
