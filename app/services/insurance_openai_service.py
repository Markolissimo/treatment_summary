"""OpenAI service for Insurance Summary generation.

Based on Insurance Summary Generator V1 Specification.
Generates conservative, admin-facing summaries for insurance documentation.
"""

import time
import logging
from typing import Optional
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.prompts import INSURANCE_SUMMARY_SYSTEM_PROMPT
from app.core.text_utils import normalize_to_ascii
from app.schemas.insurance_summary import (
    InsuranceSummaryRequest,
    InsuranceSummaryOutput,
)
from app.db.models import AuditLog

settings = get_settings()
logger = logging.getLogger(__name__)


class InsuranceGenerationResult(BaseModel):
    """Result wrapper for Insurance AI generation."""

    output: InsuranceSummaryOutput
    tokens_used: int
    generation_time_ms: int
    seed: int


def build_insurance_summary_user_prompt(request: InsuranceSummaryRequest) -> str:
    """Build the user prompt from the insurance summary request."""
    prompt_parts = [
        "Generate an insurance summary with the following case details:",
        "",
        f"**Tier:** {request.tier.value}",
        f"**Arches:** {request.arches.value}",
        f"**Age Group:** {request.age_group.value}",
        f"**Retainers Included:** {'Yes (bundled)' if request.retainers_included else 'No'}",
        f"**Monitoring Approach:** {request.monitoring_approach.value}",
        "",
        "**Diagnostic Assets:**",
    ]
    
    # List diagnostic assets
    if request.diagnostic_assets.intraoral_photos:
        prompt_parts.append("- Intraoral photos: Yes")
    else:
        prompt_parts.append("- Intraoral photos: No")
        
    if request.diagnostic_assets.panoramic_xray:
        prompt_parts.append("- Panoramic X-ray: Yes")
    else:
        prompt_parts.append("- Panoramic X-ray: No")
        
    if request.diagnostic_assets.fmx:
        prompt_parts.append("- FMX (Full Mouth X-rays): Yes")
    else:
        prompt_parts.append("- FMX: No")
    
    if request.notes:
        prompt_parts.extend([
            "",
            f"**Additional Notes:** {request.notes}",
        ])
    
    prompt_parts.extend([
        "",
        "Generate the insurance summary following all guidelines. Remember:",
        "- Use neutral, factual, non-promissory language",
        "- Do NOT include diagnosis language or medical necessity statements",
        "- Do NOT promise coverage or guarantee reimbursement",
        "- Do NOT include pricing information",
        "- Reference that this is for administrative/insurance documentation purposes",
        "- Mention retention is included if retainers are bundled",
    ])
    
    return "\n".join(prompt_parts)


async def generate_insurance_summary(
    request: InsuranceSummaryRequest,
    api_key: Optional[str] = None,
    seed_override: Optional[int] = None,
    session: Optional[AsyncSession] = None,
) -> InsuranceGenerationResult:
    """
    Generate an insurance summary using OpenAI GPT-4 with structured outputs.
    
    Args:
        request: The insurance summary request with case details
        api_key: Optional API key override (uses settings if not provided)
        seed_override: Optional seed override
        session: Optional database session for querying previous seed values
    
    Returns:
        InsuranceGenerationResult with the structured output and metadata
    """
    client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)

    user_prompt = build_insurance_summary_user_prompt(request)
    
    # Seed handling for regeneration
    if seed_override is not None:
        seed = seed_override
    elif request.is_regeneration and request.previous_version_uuid and session:
        stmt = select(AuditLog).where(AuditLog.id == request.previous_version_uuid)
        result = await session.execute(stmt)
        previous_audit = result.scalar_one_or_none()
        if previous_audit and previous_audit.seed is not None:
            seed = previous_audit.seed + 1
            logger.info(f"Insurance regeneration: incrementing seed from {previous_audit.seed} to {seed}")
        else:
            seed = settings.insurance_summary_seed + 1
            logger.warning(f"Insurance regeneration: previous seed not found, using default + 1: {seed}")
    elif request.is_regeneration:
        seed = settings.insurance_summary_seed + 1
        logger.info(f"Insurance regeneration without previous UUID: using default + 1: {seed}")
    else:
        seed = settings.insurance_summary_seed
        logger.info(f"New insurance generation: using initial seed: {seed}")

    start_time = time.time()

    response = await client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": INSURANCE_SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format=InsuranceSummaryOutput,
        temperature=0.5,  # Lower temperature for more consistent, conservative output
        max_tokens=1500,
        seed=seed,
    )

    end_time = time.time()
    generation_time_ms = int((end_time - start_time) * 1000)

    parsed_output = response.choices[0].message.parsed
    
    # Normalize unicode characters to ASCII
    if parsed_output:
        parsed_output.insurance_summary = normalize_to_ascii(parsed_output.insurance_summary)
        parsed_output.disclaimer = normalize_to_ascii(parsed_output.disclaimer)

    tokens_used = response.usage.total_tokens if response.usage else 0

    return InsuranceGenerationResult(
        output=parsed_output,
        tokens_used=tokens_used,
        generation_time_ms=generation_time_ms,
        seed=seed,
    )
