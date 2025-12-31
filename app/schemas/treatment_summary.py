from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.enums import (
    TreatmentType,
    AreaTreated,
    CaseDifficulty,
    MonitoringApproach,
    Attachments,
    Audience,
    Tone,
    CaseTier,
)


class TreatmentSummaryRequest(BaseModel):
    """Input schema for treatment summary generation.
    
    Schema is flexible - fields are optional with sensible defaults.
    This contract may evolve as the portal UI is finalized.
    """

    is_regeneration: Optional[bool] = Field(
        default=False,
        description="Whether this is a regeneration request",
    )
    previous_version_uuid: Optional[str] = Field(
        default=None,
        description="UUID of the previous version if regenerating",
    )
    tier: Optional[CaseTier] = Field(
        default=None,
        description="Case tier for CDT code mapping (express/mild/moderate/complex)",
        examples=["moderate"],
    )
    treatment_type: Optional[TreatmentType] = Field(
        default=TreatmentType.CLEAR_ALIGNERS,
        description="Type of orthodontic treatment",
        examples=["clear aligners"],
    )
    area_treated: Optional[AreaTreated] = Field(
        default=AreaTreated.BOTH,
        description="Area of mouth being treated",
        examples=["both"],
    )
    duration_range: Optional[str] = Field(
        default="4-6 months",
        description="Expected treatment duration range",
        examples=["4-6 months", "12-18 months"],
        min_length=1,
        max_length=50,
    )
    case_difficulty: Optional[CaseDifficulty] = Field(
        default=CaseDifficulty.MODERATE,
        description="Complexity level of the case",
        examples=["moderate"],
    )
    monitoring_approach: Optional[MonitoringApproach] = Field(
        default=MonitoringApproach.MIXED,
        description="How the patient will be monitored during treatment",
        examples=["mixed"],
    )
    attachments: Optional[Attachments] = Field(
        default=Attachments.SOME,
        description="Level of attachment usage in treatment",
        examples=["some"],
    )
    whitening_included: Optional[bool] = Field(
        default=False,
        description="Whether whitening is included in the treatment plan",
    )
    dentist_note: Optional[str] = Field(
        default=None,
        description="Optional note from the dentist (1-2 lines)",
        max_length=500,
    )
    audience: Optional[Audience] = Field(
        default=Audience.PATIENT,
        description="Target audience for the summary",
        examples=["patient"],
    )
    tone: Optional[Tone] = Field(
        default=Tone.REASSURING,
        description="Desired tone of the generated summary",
        examples=["reassuring"],
    )
    patient_name: Optional[str] = Field(
        default=None,
        description="Patient name for email template personalization",
        max_length=200,
    )
    practice_name: Optional[str] = Field(
        default=None,
        description="Practice name for email template",
        max_length=200,
    )
    patient_age: Optional[int] = Field(
        default=None,
        description="Patient age for CDT logic (adolescent <18, adult ≥18)",
        ge=0,
        le=120,
    )


class TreatmentSummaryOutput(BaseModel):
    """Structured output schema for GPT-4 response."""

    title: str = Field(
        ...,
        description="A brief title for the treatment summary",
    )
    summary: str = Field(
        ...,
        description="The main treatment summary text",
    )


class TreatmentSummaryResponse(BaseModel):
    """API response wrapper for treatment summary."""

    success: bool = True
    document: TreatmentSummaryOutput
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata about the generation",
    )
    uuid: Optional[str] = Field(
        default=None,
        description="Unique identifier for this generation",
    )
    is_regenerated: bool = Field(
        default=False,
        description="Whether this is a regenerated version",
    )
    previous_version_uuid: Optional[str] = Field(
        default=None,
        description="UUID of the previous version if this is a regeneration",
    )
    seed: Optional[int] = Field(
        default=None,
        description="Seed value used for this generation",
    )
    cdt_codes: Optional[dict] = Field(
        default=None,
        description="CDT code suggestions (primary_code, primary_description, suggested_add_ons, notes)",
    )
