"""Schemas for Insurance Summary generation.

Based on Insurance Summary Generator V1 Specification.
This module is an administrative support tool for dentists and practice staff.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.enums import InsuranceTier, Arches, AgeGroup, MonitoringApproach


class DiagnosticAssets(BaseModel):
    """Diagnostic assets available for the case.
    
    Only explicitly flagged assets will be included in CDT codes.
    No guessing - if not flagged, not included.
    """
    
    intraoral_photos: bool = Field(
        default=False,
        description="Intraoral photos available (maps to D0350)",
    )
    panoramic_xray: bool = Field(
        default=False,
        description="Panoramic X-ray available (maps to D0330)",
    )
    fmx: bool = Field(
        default=False,
        description="Full mouth X-rays available (maps to D0210)",
    )


class InsuranceSummaryRequest(BaseModel):
    """Input schema for insurance summary generation.
    
    Based on V1 Specification section 3. Inputs are simple, explicit,
    and provided by the portal. No inference.
    """
    
    is_regeneration: Optional[bool] = Field(
        default=False,
        description="Whether this is a regeneration request",
    )
    previous_version_uuid: Optional[str] = Field(
        default=None,
        description="UUID of the previous version if regenerating",
    )
    tier: InsuranceTier = Field(
        ...,
        description="Case tier: express_mild, moderate, or complex",
        examples=["moderate"],
    )
    arches: Arches = Field(
        default=Arches.BOTH,
        description="Arches being treated: upper, lower, or both",
        examples=["both"],
    )
    age_group: AgeGroup = Field(
        ...,
        description="Patient age group: adolescent (<18) or adult (≥18)",
        examples=["adult"],
    )
    retainers_included: bool = Field(
        default=True,
        description="Whether retainers are included in treatment (bundled, not billed separately)",
    )
    diagnostic_assets: DiagnosticAssets = Field(
        default_factory=DiagnosticAssets,
        description="Diagnostic assets available - only flagged assets generate CDT codes",
    )
    monitoring_approach: MonitoringApproach = Field(
        default=MonitoringApproach.MIXED,
        description="Monitoring approach: remote, hybrid/mixed, or in_clinic",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional dentist/admin note",
        max_length=500,
    )


class InsuranceSummaryOutput(BaseModel):
    """Structured output schema for GPT-4 response.
    
    The AI returns editable text only. No automation.
    Tone must be: factual, neutral, non-promissory.
    """
    
    insurance_summary: str = Field(
        ...,
        description="The generated insurance summary text (admin use only)",
    )
    disclaimer: str = Field(
        default="This document is provided for administrative support only. Coverage and reimbursement are determined solely by the patient's insurance provider. Submission of this information does not guarantee payment or approval.",
        description="Required disclaimer (always included)",
    )


class InsuranceSummaryResponse(BaseModel):
    """API response wrapper for insurance summary."""
    
    success: bool = True
    document: InsuranceSummaryOutput = Field(
        ...,
        description="The generated insurance summary document",
    )
    cdt_codes: List[str] = Field(
        default_factory=list,
        description="List of CDT code strings (e.g., ['D8080', 'D0350', 'D0330'])",
    )
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
