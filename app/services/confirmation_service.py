"""Service for handling document confirmations."""

import json
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db.models import DocumentConfirmation, AuditLog, DOCUMENT_VERSIONS
from app.core.phi_utils import prepare_audit_data


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
