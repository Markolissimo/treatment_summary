"""Schemas for document confirmation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentConfirmationRequest(BaseModel):
    """Request schema for confirming a generated document."""
    
    confirmed_payload: Optional[dict] = Field(
        default=None,
        description="Final edited document content (if modified by dentist)",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional notes from the dentist at confirmation time",
    )


class DocumentConfirmationResponse(BaseModel):
    """Response schema for document confirmation."""
    
    success: bool = True
    confirmation_id: str = Field(
        ...,
        description="Unique identifier for this confirmation",
    )
    generation_id: str = Field(
        ...,
        description="Reference to the original generation event",
    )
    user_id: str = Field(
        ...,
        description="User who confirmed the document",
    )
    document_type: str = Field(
        ...,
        description="Type of document confirmed",
    )
    document_version: str = Field(
        ...,
        description="Version of the document schema",
    )
    confirmed_at: datetime = Field(
        ...,
        description="Timestamp when the document was confirmed",
    )
    is_edited: bool = Field(
        default=False,
        description="Whether the approved content differs from the originally generated content",
    )
    edited_summary: Optional[str] = Field(
        default=None,
        description="Edited summary text (after value from before/after structure)",
    )
    similarity_score: Optional[float] = Field(
        default=None,
        description="Similarity score (0.0-1.0) between original generated summary and approved summary",
    )
    regeneration_history: Optional[List[str]] = Field(
        default=None,
        description="All generation UUIDs for the same user + same inputs",
    )
    message: str = Field(
        default="Document confirmed successfully",
        description="Confirmation message",
    )
