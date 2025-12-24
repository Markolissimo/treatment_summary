import json
import time
from typing import Optional
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.prompts import TREATMENT_SUMMARY_SYSTEM_PROMPT
from app.core.utils import get_patient_category
from app.schemas.treatment_summary import (
    TreatmentSummaryRequest,
    TreatmentSummaryOutput,
)

settings = get_settings()


class GenerationResult(BaseModel):
    """Result wrapper for AI generation."""

    output: TreatmentSummaryOutput
    tokens_used: int
    generation_time_ms: int


def build_treatment_summary_user_prompt(request: TreatmentSummaryRequest) -> str:
    """Build the user prompt from the treatment summary request."""
    prompt_parts = [
        "Generate a treatment summary with the following case details:",
        "",
    ]
    
    if request.patient_name:
        prompt_parts.append(f"**Patient Name:** {request.patient_name}")
    
    if request.practice_name:
        prompt_parts.append(f"**Practice Name:** {request.practice_name}")
    
    if request.patient_age is not None:
        patient_category = get_patient_category(request.patient_age)
        prompt_parts.append(f"**Patient Age:** {request.patient_age} ({patient_category})")
    
    prompt_parts.extend([
        f"**Treatment Type:** {request.treatment_type.value}",
        f"**Area Treated:** {request.area_treated.value}",
        f"**Expected Duration:** {request.duration_range}",
        f"**Case Difficulty:** {request.case_difficulty.value}",
        f"**Monitoring Approach:** {request.monitoring_approach.value}",
        f"**Attachments:** {request.attachments.value}",
        f"**Whitening Included:** {'Yes' if request.whitening_included else 'No'}",
    ])

    if request.dentist_note:
        prompt_parts.append(f"**Dentist Note:** {request.dentist_note}")

    prompt_parts.extend([
        "",
        f"**Target Audience:** {request.audience.value}",
        f"**Desired Tone:** {request.tone.value}",
        "",
        "Please generate the treatment summary following all guidelines and restrictions.",
    ])

    return "\n".join(prompt_parts)


async def generate_treatment_summary(
    request: TreatmentSummaryRequest,
    api_key: Optional[str] = None,
) -> GenerationResult:
    """
    Generate a treatment summary using OpenAI GPT-4 with structured outputs.
    
    Args:
        request: The treatment summary request with case details
        api_key: Optional API key override (uses settings if not provided)
    
    Returns:
        GenerationResult with the structured output and metadata
    """
    client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)

    user_prompt = build_treatment_summary_user_prompt(request)

    start_time = time.time()

    response = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": TREATMENT_SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format=TreatmentSummaryOutput,
        temperature=0.7,
        max_tokens=2000,
    )

    end_time = time.time()
    generation_time_ms = int((end_time - start_time) * 1000)

    parsed_output = response.choices[0].message.parsed

    tokens_used = response.usage.total_tokens if response.usage else 0

    return GenerationResult(
        output=parsed_output,
        tokens_used=tokens_used,
        generation_time_ms=generation_time_ms,
    )
