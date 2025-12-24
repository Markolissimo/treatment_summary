from pydantic import BaseModel, Field
from typing import Optional


class InsuranceSummaryRequest(BaseModel):
    """Placeholder input schema for insurance summary generation."""

    patient_id: str = Field(..., description="Patient identifier")
    treatment_code: Optional[str] = Field(default=None, description="Treatment code")
    # Additional fields to be defined in Module 2


class InsuranceSummaryResponse(BaseModel):
    """Placeholder response for insurance summary."""

    success: bool = True
    message: str = "Module coming soon"
    module: str = "insurance-summary"


class ProgressNotesRequest(BaseModel):
    """Placeholder input schema for progress notes generation."""

    patient_id: str = Field(..., description="Patient identifier")
    visit_date: Optional[str] = Field(default=None, description="Date of visit")
    # Additional fields to be defined in Module 3


class ProgressNotesResponse(BaseModel):
    """Placeholder response for progress notes."""

    success: bool = True
    message: str = "Module coming soon"
    module: str = "progress-notes"
