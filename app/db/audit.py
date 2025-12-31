import json
import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog, DOCUMENT_VERSIONS
from app.core.phi_utils import prepare_audit_data


def compute_input_hash(input_data: dict) -> str:
    """Compute SHA256 hash of canonicalized input data for stable regeneration tracking."""
    # Exclude regeneration-only fields so that "generate" and "regenerate" with the same
    # clinical inputs share the same hash.

    exclude_keys = {
        "is_regeneration",
        "previous_version_uuid",
    }

    filtered_input = {k: v for k, v in input_data.items() if k not in exclude_keys}
    canonical_json = json.dumps(filtered_input, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()


async def log_generation(
    session: AsyncSession,
    user_id: str,
    document_type: str,
    input_data: dict,
    output_data: dict,
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
    
    Automatically applies PHI redaction if configured and uses proper
    document versioning from DOCUMENT_VERSIONS.
    
    Args:
        session: Database session
        user_id: ID of the user who initiated the generation
        document_type: Type of document (e.g., "treatment_summary")
        input_data: The input request data as a dictionary
        output_data: The generated document output as a dictionary
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
    # Get proper document version
    document_version = DOCUMENT_VERSIONS.get(document_type, "1.0")
    
    # Compute input hash for stable regeneration tracking
    input_hash = compute_input_hash(input_data)
    
    # Apply PHI redaction if configured
    input_data_str = prepare_audit_data(input_data)
    output_data_str = prepare_audit_data(output_data)
    
    audit_entry = AuditLog(
        user_id=user_id,
        document_type=document_type,
        document_version=document_version,
        input_data=input_data_str,
        input_hash=input_hash,
        output_data=output_data_str,
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
