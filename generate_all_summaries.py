"""
Script to automatically generate treatment summaries for all input combinations.

This script generates summaries for all combinations of key parameters and saves
them to the outputs folder in the same JSON format as the Streamlit download button.

Usage:
    python generate_all_summaries.py
"""

import asyncio
import json
import os
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Dict, Any

from app.core.config import get_settings
from app.schemas.treatment_summary import (
    TreatmentSummaryRequest,
    TreatmentType,
    AreaTreated,
    CaseDifficulty,
    MonitoringApproach,
    Attachments,
    Audience,
    Tone,
)
from app.services.openai_service import generate_treatment_summary


OUTPUT_DIR = Path(__file__).parent / "outputs"


def get_all_combinations() -> list[Dict[str, Any]]:
    """Generate all combinations of input parameters."""
    
    treatment_types = [t.value for t in TreatmentType]
    areas_treated = [a.value for a in AreaTreated]
    duration_ranges = ["4-6 months", "6-9 months", "9-12 months", "12-18 months"]
    case_difficulties = [c.value for c in CaseDifficulty]
    monitoring_approaches = [m.value for m in MonitoringApproach]
    attachments_options = [a.value for a in Attachments]
    whitening_options = [True, False]
    audiences = [a.value for a in Audience]
    tones = [t.value for t in Tone]
    
    combinations = []
    
    for combo in product(
        treatment_types,
        areas_treated,
        duration_ranges,
        case_difficulties,
        monitoring_approaches,
        attachments_options,
        whitening_options,
        audiences,
        tones,
    ):
        combinations.append({
            "treatment_type": combo[0],
            "area_treated": combo[1],
            "duration_range": combo[2],
            "case_difficulty": combo[3],
            "monitoring_approach": combo[4],
            "attachments": combo[5],
            "whitening_included": combo[6],
            "audience": combo[7],
            "tone": combo[8],
        })
    
    return combinations


def create_output_filename(params: Dict[str, Any], index: int) -> str:
    """Create a descriptive filename for the output JSON."""
    treatment = params["treatment_type"].replace(" ", "_")
    area = params["area_treated"]
    difficulty = params["case_difficulty"]
    audience = params["audience"]
    tone = params["tone"]
    whitening = "whitening" if params["whitening_included"] else "no_whitening"
    
    filename = f"{index:04d}_{treatment}_{area}_{difficulty}_{audience}_{tone}_{whitening}.json"
    return filename


async def generate_and_save_summary(
    params: Dict[str, Any],
    index: int,
    total: int,
) -> tuple[bool, str]:
    """Generate a single summary and save it to file."""
    try:
        request = TreatmentSummaryRequest(**params)
        
        print(f"[{index + 1}/{total}] Generating: {params['treatment_type']} | "
              f"{params['area_treated']} | {params['case_difficulty']} | "
              f"{params['audience']} | {params['tone']} | "
              f"whitening={params['whitening_included']}")
        
        result = await generate_treatment_summary(request)
        
        response_data = {
            "success": True,
            "document": result.output.model_dump(),
            "metadata": {
                "tokens_used": result.tokens_used,
                "generation_time_ms": result.generation_time_ms,
                "audience": params["audience"],
                "tone": params["tone"],
                "generated_at": datetime.now().isoformat(),
            },
            "input_parameters": params,
        }
        
        filename = create_output_filename(params, index)
        filepath = OUTPUT_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Saved to: {filename}")
        return True, filename
        
    except Exception as e:
        error_msg = f"  ✗ Error: {str(e)}"
        print(error_msg)
        return False, str(e)


async def generate_all_summaries():
    """Main function to generate all summary combinations."""
    
    settings = get_settings()
    
    if not settings.openai_api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key before running this script.")
        return
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR.absolute()}\n")
    
    combinations = get_all_combinations()
    total = len(combinations)
    
    print(f"Total combinations to generate: {total}\n")
    print("=" * 80)
    
    start_time = datetime.now()
    successful = 0
    failed = 0
    
    for index, params in enumerate(combinations):
        success, result = await generate_and_save_summary(params, index, total)
        
        if success:
            successful += 1
        else:
            failed += 1
        
        await asyncio.sleep(0.5)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 80)
    print(f"\nGeneration complete!")
    print(f"  Total: {total}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Average time per summary: {duration / total:.2f} seconds")
    print(f"\nOutputs saved to: {OUTPUT_DIR.absolute()}")
    
    summary_file = OUTPUT_DIR / "_generation_summary.json"
    summary_data = {
        "generation_date": start_time.isoformat(),
        "total_combinations": total,
        "successful": successful,
        "failed": failed,
        "duration_seconds": duration,
        "average_time_per_summary": duration / total if total > 0 else 0,
    }
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"Summary saved to: {summary_file.name}")


if __name__ == "__main__":
    asyncio.run(generate_all_summaries())
