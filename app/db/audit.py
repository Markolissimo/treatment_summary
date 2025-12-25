import json
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog


async def log_generation(
    session: AsyncSession,
    user_id: str,
    document_type: str,
    input_data: dict,
    generated_text: dict,
    model_used: str = "gpt-4o",
    tokens_used: Optional[int] = None,
    generation_time_ms: Optional[int] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    seed: Optional[int] = None,
    is_regenerated: bool = False,
    previous_version_uuid: Optional[str] = None,
) -> AuditLog:
    """
    Log a document generation event to the audit database.
    
    Args:
        session: Database session
        user_id: ID of the user who initiated the generation
        document_type: Type of document (e.g., "treatment_summary")
        input_data: The input request data as a dictionary
        generated_text: The generated document as a dictionary
        model_used: AI model used for generation
        tokens_used: Total tokens consumed
        generation_time_ms: Generation time in milliseconds
        status: Status of the generation ("success" or "error")
        error_message: Error message if generation failed
        seed: Seed value used for LLM generation
        is_regenerated: Whether this is a regenerated version
        previous_version_uuid: UUID of the previous version if regeneration
    
    Returns:
        The created AuditLog entry
    """
    audit_entry = AuditLog(
        user_id=user_id,
        document_type=document_type,
        input_data=json.dumps(input_data),
        generated_text=json.dumps(generated_text),
        model_used=model_used,
        tokens_used=tokens_used,
        generation_time_ms=generation_time_ms,
        status=status,
        error_message=error_message,
        seed=seed,
        is_regenerated=is_regenerated,
        previous_version_uuid=previous_version_uuid,
        created_at=datetime.utcnow(),
    )
    
    session.add(audit_entry)
    await session.commit()
    await session.refresh(audit_entry)
    
    return audit_entry
