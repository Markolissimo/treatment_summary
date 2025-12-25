from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
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
    seed: Optional[int] = Field(
        default=None,
        description="Seed value used for LLM generation",
    )
    is_regenerated: bool = Field(
        default=False,
        description="Whether this is a regenerated version",
    )
    previous_version_uuid: Optional[str] = Field(
        default=None,
        index=True,
        description="UUID of the previous version if this is a regeneration",
    )


class CDTCode(SQLModel, table=True):
    """CDT (Current Dental Terminology) code definitions."""

    __tablename__ = "cdt_codes"

    code: str = Field(
        primary_key=True,
        description="CDT code (e.g., D8010, D8080, D8090)",
        max_length=10,
    )
    description: str = Field(
        ...,
        description="Human-readable description of the CDT code",
        max_length=500,
    )
    category: str = Field(
        ...,
        description="Category of the code (e.g., 'orthodontic', 'diagnostic', 'retention')",
        max_length=50,
        index=True,
    )
    is_primary: bool = Field(
        default=True,
        description="Whether this is a primary treatment code or an add-on/supporting code",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this code is currently active for use",
        index=True,
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes or usage guidelines",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the code was added",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the code was last updated",
    )


class CDTRule(SQLModel, table=True):
    """Rules for mapping case attributes to CDT codes."""

    __tablename__ = "cdt_rules"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier for the rule",
    )
    tier: str = Field(
        ...,
        description="Case tier (e.g., 'express', 'mild', 'moderate', 'complex')",
        max_length=50,
        index=True,
    )
    age_group: str = Field(
        ...,
        description="Age group ('adolescent' or 'adult')",
        max_length=20,
        index=True,
    )
    cdt_code: str = Field(
        ...,
        description="CDT code to assign",
        max_length=10,
        index=True,
    )
    priority: int = Field(
        default=0,
        description="Priority order (higher = higher priority)",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this rule is currently active",
        index=True,
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about this rule",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the rule was created",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the rule was last updated",
    )
