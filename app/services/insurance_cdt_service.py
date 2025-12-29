"""CDT code selection service for Insurance Summary.

Based on Insurance Summary Generator V1 Specification section 4.
Deterministic rules - no guessing, only explicitly flagged inputs generate codes.
"""

from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import CDTCode
from app.schemas.enums import InsuranceTier, AgeGroup
from app.schemas.insurance_summary import DiagnosticAssets


class InsuranceCDTResult:
    """Result of Insurance CDT code selection."""

    def __init__(
        self,
        codes: List[dict],
        notes: Optional[str] = None,
    ):
        self.codes = codes
        self.notes = notes

    def to_list(self) -> List[dict]:
        """Convert to list for API responses."""
        return self.codes

    def get_code_strings(self) -> List[str]:
        """Get just the code strings for output."""
        return [c["code"] for c in self.codes]


async def get_cdt_code_description(
    session: AsyncSession,
    code: str,
) -> Optional[str]:
    """Fetch CDT code description from database."""
    stmt = select(CDTCode).where(CDTCode.code == code)
    result = await session.execute(stmt)
    cdt_code = result.scalars().first()
    return cdt_code.description if cdt_code else None


async def select_insurance_cdt_codes(
    session: AsyncSession,
    tier: InsuranceTier,
    age_group: AgeGroup,
    diagnostic_assets: DiagnosticAssets,
    retainers_included: bool = True,
) -> InsuranceCDTResult:
    """
    Select appropriate CDT codes for insurance summary based on V1 specification.

    CDT Logic Rules (v1):
    
    Primary Orthodontic Code:
    - Express/Mild: D8010 (limited orthodontic treatment)
    - Moderate/Complex:
        - Adolescent → D8080 (comprehensive orthodontic treatment, adolescent)
        - Adult → D8090 (comprehensive orthodontic treatment, adult)

    Retainers:
    - If retainers_included = true → bundled (no separate code)
    - Do NOT include D8680 unless explicitly billed separately (out of scope v1)

    Diagnostics (only if explicitly flagged):
    - Intraoral photos → D0350
    - Panoramic X-ray → D0330
    - FMX → D0210
    
    No guessing. If not flagged → not included.

    Args:
        session: Database session
        tier: Insurance tier (express_mild, moderate, complex)
        age_group: Patient age group (adolescent, adult)
        diagnostic_assets: Diagnostic assets flags
        retainers_included: Whether retainers are bundled

    Returns:
        InsuranceCDTResult with list of codes and descriptions
    """
    codes = []
    notes_parts = []

    # Primary Orthodontic Code selection
    if tier == InsuranceTier.EXPRESS_MILD:
        primary_code = "D8010"
        notes_parts.append("Limited orthodontic treatment (express/mild tier)")
    elif tier in [InsuranceTier.MODERATE, InsuranceTier.COMPLEX]:
        if age_group == AgeGroup.ADOLESCENT:
            primary_code = "D8080"
            notes_parts.append(f"Comprehensive orthodontic treatment, adolescent ({tier.value} tier)")
        else:  # ADULT
            primary_code = "D8090"
            notes_parts.append(f"Comprehensive orthodontic treatment, adult ({tier.value} tier)")
    else:
        primary_code = None
        notes_parts.append("No primary code - unknown tier")

    # Add primary code with description
    if primary_code:
        description = await get_cdt_code_description(session, primary_code)
        codes.append({
            "code": primary_code,
            "description": description or f"Primary orthodontic code",
            "category": "primary"
        })

    # Diagnostic codes - ONLY if explicitly flagged
    diagnostic_map = {
        "intraoral_photos": ("D0350", "Oral/facial photographic images"),
        "panoramic_xray": ("D0330", "Panoramic radiographic image"),
        "fmx": ("D0210", "Intraoral - complete series of radiographic images"),
    }

    for asset_key, (code, default_desc) in diagnostic_map.items():
        if getattr(diagnostic_assets, asset_key, False):
            description = await get_cdt_code_description(session, code) or default_desc
            codes.append({
                "code": code,
                "description": description,
                "category": "diagnostic"
            })

    # Retainers note (bundled, not separate code in v1)
    if retainers_included:
        notes_parts.append("Retainers bundled in treatment (not billed separately)")

    return InsuranceCDTResult(
        codes=codes,
        notes="; ".join(notes_parts) if notes_parts else None,
    )


def format_cdt_codes_for_output(cdt_result: InsuranceCDTResult) -> str:
    """Format CDT codes for inclusion in the summary output.
    
    Returns formatted string like:
    Referenced CDT codes (for administrative reference):
    D8090 – Comprehensive orthodontic treatment (adult)
    D0350 – Oral/facial photographic images
    """
    if not cdt_result.codes:
        return ""
    
    lines = ["Referenced CDT codes (for administrative reference):"]
    for code_info in cdt_result.codes:
        lines.append(f"{code_info['code']} – {code_info['description']}")
    
    return "\n".join(lines)
