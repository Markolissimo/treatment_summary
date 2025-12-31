"""Service for handling document confirmations."""

import json
import difflib
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db.models import DocumentConfirmation, AuditLog, DOCUMENT_VERSIONS
from app.core.phi_utils import prepare_audit_data

logger = logging.getLogger(__name__)


def _extract_summary_text(document_type: str, payload: dict) -> Optional[str]:
    """Extract the summary text from payload based on document type."""
    if not isinstance(payload, dict):
        return None
    
    if document_type == "insurance_summary":
        value = payload.get("insurance_summary")
        return value if isinstance(value, str) else None
    elif document_type == "treatment_summary":
        value = payload.get("treatment_summary")
        return value if isinstance(value, str) else None
    
    # Fallback for legacy or unknown types
    value = payload.get("summary")
    return value if isinstance(value, str) else None


def _similarity(a: Optional[str], b: Optional[str]) -> Optional[float]:
    """Calculate similarity ratio between two strings using SequenceMatcher.
    
    Args:
        a: First string to compare
        b: Second string to compare
        
    Returns:
        Similarity score between 0.0 and 1.0, or None if either string is empty
    """
    if not a or not b:
        return None
    a_norm = a.strip()
    b_norm = b.strip()
    if not a_norm or not b_norm:
        return None
    return float(difflib.SequenceMatcher(a=a_norm, b=b_norm).ratio())


async def confirm_document(
    session: AsyncSession,
    generation_id: str,
    user_id: str,
    confirmed_payload: Optional[dict] = None,
    notes: Optional[str] = None,
) -> DocumentConfirmation:
    """
    Record dentist confirmation of a generated document.
    
    Args:
        session: Database session
        generation_id: ID of the generation event (AuditLog.id)
        user_id: ID of the user confirming the document
        confirmed_payload: Final edited document content (if modified)
        notes: Optional notes from the dentist
        
    Returns:
        DocumentConfirmation: The created confirmation record
        
    Raises:
        HTTPException: If generation_id not found or already confirmed
    """
    # Verify the generation exists
    stmt = select(AuditLog).where(AuditLog.id == generation_id)
    result = await session.execute(stmt)
    audit_log = result.scalar_one_or_none()
    
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation ID {generation_id} not found",
        )
    
    # Check if already confirmed
    check_stmt = select(DocumentConfirmation).where(
        DocumentConfirmation.generation_id == generation_id
    )
    check_result = await session.execute(check_stmt)
    existing_confirmation = check_result.scalar_one_or_none()
    
    if existing_confirmation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document already confirmed at {existing_confirmation.confirmed_at}",
        )
    
    # Get document version
    document_version = DOCUMENT_VERSIONS.get(audit_log.document_type, "1.0")

    # Parse original generated payload from audit log
    original_payload: dict = {}
    try:
        parsed = json.loads(audit_log.output_data) if audit_log.output_data else {}
        if isinstance(parsed, dict):
            original_payload = parsed
    except Exception:
        original_payload = {}

    original_summary = _extract_summary_text(audit_log.document_type, original_payload)

    approved_payload = confirmed_payload if confirmed_payload else original_payload
    approved_summary = _extract_summary_text(audit_log.document_type, approved_payload)

    is_edited = False
    if original_summary is not None and approved_summary is not None:
        is_edited = approved_summary != original_summary
    elif confirmed_payload is not None:
        # If dentist sent an explicit payload but we can't extract summaries, treat as edited
        is_edited = True

    similarity_score = _similarity(original_summary, approved_summary)

    # Store before/after summary text
    edited_summary_str = None
    if is_edited and original_summary is not None and approved_summary is not None:
        edited_summary_str = prepare_audit_data({
            "before": original_summary,
            "after": approved_summary
        })

    # Regeneration history: trace back through previous_version_uuid chain
    # Only build chain if this generation has a previous_version_uuid (i.e., it's a regeneration)
    regen_history_ids: list[str] = []
    try:
        # Only trace back if this generation is actually a regeneration
        if audit_log.previous_version_uuid:
            # Walk backwards through the chain via previous_version_uuid
            chain: list[str] = [generation_id]
            current_uuid = audit_log.previous_version_uuid
            
            while current_uuid:
                # Fetch the previous audit log
                prev_stmt = select(AuditLog.id, AuditLog.previous_version_uuid).where(AuditLog.id == current_uuid)
                prev_result = await session.execute(prev_stmt)
                prev_row = prev_result.first()
                
                if prev_row and prev_row[0]:
                    chain.append(prev_row[0])
                    current_uuid = prev_row[1]  # Continue to the next previous
                else:
                    break
            
            # Reverse to get chronological order (oldest first)
            chain.reverse()
            regen_history_ids = chain
            logger.info(f"Regeneration history: found chain of {len(regen_history_ids)} generations")
        else:
            logger.info(f"No previous_version_uuid found, this is not a regeneration - history will be empty")
    except Exception as e:
        logger.error(f"Error fetching regeneration history: {e}")
        regen_history_ids = []
    
    # Prepare confirmed payload (apply PHI redaction if configured)
    confirmed_payload_str = None
    if confirmed_payload:
        confirmed_payload_str = prepare_audit_data(confirmed_payload)
    
    # Create confirmation record
    confirmation = DocumentConfirmation(
        generation_id=generation_id,
        user_id=user_id,
        document_type=audit_log.document_type,
        document_version=document_version,
        confirmed_at=datetime.utcnow(),
        confirmed_payload=confirmed_payload_str,
        is_edited=is_edited,
        edited_summary=edited_summary_str,
        similarity_score=similarity_score,
        regeneration_history=json.dumps(regen_history_ids),
        notes=notes,
    )
    
    session.add(confirmation)
    await session.commit()
    await session.refresh(confirmation)
    
    return confirmation


async def get_confirmation_status(
    session: AsyncSession,
    generation_id: str,
) -> Optional[DocumentConfirmation]:
    """
    Check if a document has been confirmed.
    
    Args:
        session: Database session
        generation_id: ID of the generation event
        
    Returns:
        DocumentConfirmation if confirmed, None otherwise
    """
    stmt = select(DocumentConfirmation).where(
        DocumentConfirmation.generation_id == generation_id
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def is_document_confirmed(
    session: AsyncSession,
    generation_id: str,
) -> bool:
    """
    Check if a document has been confirmed (simple boolean check).
    
    Args:
        session: Database session
        generation_id: ID of the generation event
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    confirmation = await get_confirmation_status(session, generation_id)
    return confirmation is not None
