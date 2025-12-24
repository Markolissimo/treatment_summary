from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class AuditLog(SQLModel, table=True):
    """Audit log for tracking all document generation events."""

    __tablename__ = "audit_logs"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier for the audit log entry",
    )
    user_id: str = Field(
        ...,
        index=True,
        description="User who initiated the generation",
    )
    document_type: str = Field(
        ...,
        index=True,
        description="Type of document generated (e.g., treatment_summary)",
    )
    document_version: str = Field(
        default="1.0",
        description="Version of the document schema",
    )
    input_data: str = Field(
        ...,
        description="JSON string of the input request data",
    )
    generated_text: str = Field(
        ...,
        description="JSON string of the generated document",
    )
    model_used: str = Field(
        default="gpt-4o",
        description="AI model used for generation",
    )
    tokens_used: Optional[int] = Field(
        default=None,
        description="Total tokens consumed in the generation",
    )
    generation_time_ms: Optional[int] = Field(
        default=None,
        description="Time taken to generate the document in milliseconds",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the generation event",
    )
    status: str = Field(
        default="success",
        description="Status of the generation (success, error)",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if generation failed",
    )
