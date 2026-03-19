import json
import asyncio
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

from baml_client.async_client import b

# Set up paths
BASE_DIR = Path(__file__).parent.parent
STORE_DIR = BASE_DIR / "assets/synthesis/generated/SeniorCancerScreeningGap"

async def enrich_record(record_path: Path):
    logger.info(f"Enriching Senior: {record_path.name}")
    
    with open(record_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    try:
        enrichment = await b.EnrichHealthyPatientRecord(data)
        
        if not enrichment:
            logger.warning(f"AI returned empty enrichment for {record_path.name}")
            return

        # 1. Chief Complaint
        if enrichment.chief_complaint:
            data["clinical_signals"]["chief_complaint"] = enrichment.chief_complaint
            
        # 2. Behavioral Flags - Occupational (Retirement & Computer Use)
        occ = data["clinical_signals"]["behavioral_flags"].get("occupational", {})
        if enrichment.occupational_tags:
            current_tags = set(occ.get("tags", []))
            for t in enrichment.occupational_tags:
                current_tags.add(t)
            occ["tags"] = list(current_tags)
        
        # In Seniors, we prioritize 'is_retired'
        if enrichment.is_retired:
             occ["retired_status"] = True
             if "Retired" not in occ.get("tags", []):
                  occ.setdefault("tags", []).append("Retired")

        occ["computer_hours_per_day"] = enrichment.computer_hours_per_day
        occ["stress_level"] = enrichment.stress_level
        data["clinical_signals"]["behavioral_flags"]["occupational"] = occ
        
        # 3. Behavioral Flags - Smoking (Former Smoker Logic)
        smoking = data["clinical_signals"]["behavioral_flags"].get("smoking")
        if smoking:
             if enrichment.smoking_pack_years:
                  smoking["pack_years"] = enrichment.smoking_pack_years
                  if smoking["status"] == "never" and enrichment.smoking_pack_years > 0:
                       smoking["status"] = "former"
             
             if enrichment.quit_years_ago:
                  smoking["quit_years_ago"] = enrichment.quit_years_ago
                  smoking["status"] = "former"
             
        # 4. Behavioral Flags - Alcohol
        alcohol = data["clinical_signals"]["behavioral_flags"].get("alcohol", {})
        alcohol["units_per_week"] = enrichment.alcohol_units_per_week
        data["clinical_signals"]["behavioral_flags"]["alcohol"] = alcohol

        # 5. Reproductive History Detail
        if enrichment.reproductive_history:
            data["clinical_signals"]["reproductive_history_detail"] = enrichment.reproductive_history.model_dump()
        
        # 6. Vaccination Gaps
        if enrichment.suggested_vaccines:
            current_vaccines = data["clinical_signals"].get("vaccination_gaps", [])
            current_vax_ids = {v["vaccine_id"] for v in current_vaccines}
            
            for vax in enrichment.suggested_vaccines:
                if vax.vaccine_id not in current_vax_ids:
                    current_vaccines.append(vax.model_dump())
            
            data["clinical_signals"]["vaccination_gaps"] = current_vaccines

        # Save back
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.success(f"Successfully enriched Senior: {record_path.name}")
        
    except Exception as e:
        logger.error(f"Failed to enrich Senior {record_path.name}: {e}")

async def main():
    if not STORE_DIR.exists():
        logger.error(f"Directory not found: {STORE_DIR}")
        return
        
    files = sorted(list(STORE_DIR.glob("record_*.json")))
    for f in files:
        await enrich_record(f)
        
    logger.info("Senior Enrichment complete.")

if __name__ == "__main__":
    asyncio.run(main())
