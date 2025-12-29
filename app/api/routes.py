from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_session
from app.db.audit import log_generation
from app.schemas.treatment_summary import (
    TreatmentSummaryRequest,
    TreatmentSummaryResponse,
)
from app.schemas.insurance_summary import (
    InsuranceSummaryRequest,
    InsuranceSummaryResponse,
)
from app.schemas.placeholders import (
    ProgressNotesRequest,
    ProgressNotesResponse,
)
from app.schemas.confirmation import (
    DocumentConfirmationRequest,
    DocumentConfirmationResponse,
)
from app.services.openai_service import generate_treatment_summary
from app.services.cdt_service import select_cdt_codes
from app.services.insurance_openai_service import generate_insurance_summary
from app.services.insurance_cdt_service import select_insurance_cdt_codes
from app.services.confirmation_service import confirm_document

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
        result = await generate_treatment_summary(request, session=session)

        # Select CDT codes if tier and patient_age are provided
        cdt_result = None
        if request.tier or request.patient_age:
            cdt_result = await select_cdt_codes(
                session=session,
                tier=request.tier.value if request.tier else None,
                patient_age=request.patient_age,
                diagnostic_assets=None,  # TODO: Add diagnostic_assets to request schema if needed
                retainers_included=False,  # TODO: Add retainers_included to request schema if needed
            )

        audit_entry = await log_generation(
            session=session,
            user_id=user_id,
            document_type="treatment_summary",
            input_data=request.model_dump(),
            generated_text=result.output.model_dump(),
            tokens_used=result.tokens_used,
            generation_time_ms=result.generation_time_ms,
            status="success",
            seed=result.seed,
            is_regenerated=request.is_regeneration or False,
            previous_version_uuid=request.previous_version_uuid,
        )

        return TreatmentSummaryResponse(
            success=True,
            document=result.output,
            metadata={
                "tokens_used": result.tokens_used,
                "generation_time_ms": result.generation_time_ms,
                "audience": request.audience.value,
                "tone": request.tone.value,
                "seed": result.seed,
                "document_version": audit_entry.document_version,
            },
            uuid=audit_entry.id,
            is_regenerated=request.is_regeneration or False,
            previous_version_uuid=request.previous_version_uuid,
            seed=result.seed,
            cdt_codes=cdt_result.to_dict() if cdt_result else None,
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
    summary="Generate Insurance Summary",
    description="Generate an insurance summary document for administrative support.",
    tags=["Insurance Summary"],
)
async def create_insurance_summary(
    request: InsuranceSummaryRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> InsuranceSummaryResponse:
    """
    Generate an insurance summary for a dental case.
    
    This endpoint generates a conservative, admin-facing insurance summary
    for documentation purposes. It is NOT a diagnosis, claim submission,
    or guarantee of coverage.
    
    CDT codes are selected deterministically based on:
    - Tier: express_mild → D8010, moderate/complex → D8080 (adolescent) or D8090 (adult)
    - Diagnostic assets: Only explicitly flagged assets generate codes
    """
    try:
        # Generate insurance summary using AI
        result = await generate_insurance_summary(request, session=session)

        # Select CDT codes deterministically
        cdt_result = await select_insurance_cdt_codes(
            session=session,
            tier=request.tier,
            age_group=request.age_group,
            diagnostic_assets=request.diagnostic_assets,
            retainers_included=request.retainers_included,
        )

        # Log generation to audit
        audit_entry = await log_generation(
            session=session,
            user_id=user_id,
            document_type="insurance_summary",
            input_data=request.model_dump(),
            generated_text=result.output.model_dump(),
            tokens_used=result.tokens_used,
            generation_time_ms=result.generation_time_ms,
            status="success",
            seed=result.seed,
            is_regenerated=request.is_regeneration or False,
            previous_version_uuid=request.previous_version_uuid,
        )

        return InsuranceSummaryResponse(
            success=True,
            document=result.output,
            cdt_codes=cdt_result.to_list(),
            metadata={
                "tokens_used": result.tokens_used,
                "generation_time_ms": result.generation_time_ms,
                "tier": request.tier.value,
                "age_group": request.age_group.value,
                "seed": result.seed,
                "document_version": audit_entry.document_version,
                "cdt_notes": cdt_result.notes,
            },
            uuid=audit_entry.id,
            is_regenerated=request.is_regeneration or False,
            previous_version_uuid=request.previous_version_uuid,
            seed=result.seed,
        )

    except Exception as e:
        await log_generation(
            session=session,
            user_id=user_id,
            document_type="insurance_summary",
            input_data=request.model_dump(),
            generated_text={},
            status="error",
            error_message=str(e),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insurance summary: {str(e)}",
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


@router.post(
    "/documents/{generation_id}/confirm",
    response_model=DocumentConfirmationResponse,
    summary="Confirm Generated Document",
    description="Record dentist confirmation of a generated document before PDF generation.",
    tags=["Document Confirmation"],
)
async def confirm_generated_document(
    generation_id: str,
    request: DocumentConfirmationRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DocumentConfirmationResponse:
    """
    Confirm a generated document.
    
    This endpoint records that a dentist has reviewed and confirmed a generated
    document. Confirmation is required before PDF generation.
    
    Args:
        generation_id: ID of the generation event (from TreatmentSummaryResponse.uuid)
        request: Confirmation request with optional edited payload and notes
        user_id: Current authenticated user
        session: Database session
        
    Returns:
        DocumentConfirmationResponse with confirmation details
    """
    try:
        confirmation = await confirm_document(
            session=session,
            generation_id=generation_id,
            user_id=user_id,
            confirmed_payload=request.confirmed_payload,
            notes=request.notes,
        )
        
        return DocumentConfirmationResponse(
            success=True,
            confirmation_id=confirmation.id,
            generation_id=confirmation.generation_id,
            user_id=confirmation.user_id,
            document_type=confirmation.document_type,
            document_version=confirmation.document_version,
            confirmed_at=confirmation.confirmed_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm document: {str(e)}",
        )
