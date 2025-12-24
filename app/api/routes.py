from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.audit import log_generation
from app.schemas.treatment_summary import (
    TreatmentSummaryRequest,
    TreatmentSummaryResponse,
)
from app.schemas.placeholders import (
    InsuranceSummaryRequest,
    InsuranceSummaryResponse,
    ProgressNotesRequest,
    ProgressNotesResponse,
)
from app.services.openai_service import generate_treatment_summary

router = APIRouter()


@router.post(
    "/generate-treatment-summary",
    response_model=TreatmentSummaryResponse,
    summary="Generate Treatment Summary",
    description="Generate a treatment summary document based on structured case data.",
    tags=["Treatment Summary"],
)
async def create_treatment_summary(
    request: TreatmentSummaryRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TreatmentSummaryResponse:
    """
    Generate a treatment summary for a dental case.
    
    This endpoint accepts structured case data and generates a professional
    treatment summary document using AI, adhering to strict clinical
    communication guidelines.
    """
    try:
        result = await generate_treatment_summary(request)

        await log_generation(
            session=session,
            user_id=user_id,
            document_type="treatment_summary",
            input_data=request.model_dump(),
            generated_text=result.output.model_dump(),
            tokens_used=result.tokens_used,
            generation_time_ms=result.generation_time_ms,
            status="success",
        )

        return TreatmentSummaryResponse(
            success=True,
            document=result.output,
            metadata={
                "tokens_used": result.tokens_used,
                "generation_time_ms": result.generation_time_ms,
                "audience": request.audience.value,
                "tone": request.tone.value,
            },
        )

    except Exception as e:
        await log_generation(
            session=session,
            user_id=user_id,
            document_type="treatment_summary",
            input_data=request.model_dump(),
            generated_text={},
            status="error",
            error_message=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate treatment summary: {str(e)}",
        )


@router.post(
    "/generate-insurance-summary",
    response_model=InsuranceSummaryResponse,
    summary="Generate Insurance Summary (Coming Soon)",
    description="Placeholder endpoint for insurance summary generation.",
    tags=["Insurance Summary"],
)
async def create_insurance_summary(
    request: InsuranceSummaryRequest,
    user_id: str = Depends(get_current_user),
) -> InsuranceSummaryResponse:
    """
    Placeholder for insurance summary generation.
    
    This module is under development and will be available in a future release.
    """
    return InsuranceSummaryResponse(
        success=True,
        message="Module coming soon",
        module="insurance-summary",
    )


@router.post(
    "/generate-progress-notes",
    response_model=ProgressNotesResponse,
    summary="Generate Progress Notes (Coming Soon)",
    description="Placeholder endpoint for progress notes generation.",
    tags=["Progress Notes"],
)
async def create_progress_notes(
    request: ProgressNotesRequest,
    user_id: str = Depends(get_current_user),
) -> ProgressNotesResponse:
    """
    Placeholder for progress notes generation.
    
    This module is under development and will be available in a future release.
    """
    return ProgressNotesResponse(
        success=True,
        message="Module coming soon",
        module="progress-notes",
    )
