"""CDT code selection and mapping service."""

from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import CDTCode, CDTRule
from app.core.utils import get_patient_category


class CDTSelectionResult:
    """Result of CDT code selection."""

    def __init__(
        self,
        primary_code: Optional[str] = None,
        primary_description: Optional[str] = None,
        suggested_add_ons: Optional[List[dict]] = None,
        notes: Optional[str] = None,
    ) -> None:
        self.primary_code: Optional[str] = primary_code
        self.primary_description: Optional[str] = primary_description
        self.suggested_add_ons: List[dict] = suggested_add_ons or []
        self.notes: Optional[str] = notes

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "primary_code": self.primary_code,
            "primary_description": self.primary_description,
            "suggested_add_ons": self.suggested_add_ons,
            "notes": self.notes,
        }


async def select_cdt_codes(
    session: AsyncSession,
    tier: Optional[str] = None,
    patient_age: Optional[int] = None,
    diagnostic_assets: Optional[Dict[str, bool]] = None,
    retainers_included: bool = False,
) -> CDTSelectionResult:
    """
    Select appropriate CDT codes based on case attributes.

    Priority logic (from client documentation):
    1. If Tier = Express/Mild → D8010
    2. If Tier = Moderate/Complex → choose D8080 vs D8090 based on age_group

    Args:
        session: Database session
        tier: Case tier (express, mild, moderate, complex)
        patient_age: Patient age for adolescent/adult determination
        diagnostic_assets: Optional dict with granular flags:
            - intraoral_photos: bool (maps to D0350)
            - panoramic_xray: bool (maps to D0330)
            - fmx: bool (maps to D0210)
            - diagnostic_casts: bool (maps to D0470)
        retainers_included: Whether retainers are included in treatment

    Returns:
        CDTSelectionResult with primary code and suggested add-ons
    """
    # Determine age group
    age_group = get_patient_category(patient_age)

    # If no tier provided, return empty result
    if not tier:
        return CDTSelectionResult(
            notes="No tier provided - CDT code selection requires case tier"
        )

    # Normalize tier to lowercase for comparison
    tier_lower = tier.lower()

    # Query for matching rule
    # Priority logic: Express/Mild → D8010, Moderate/Complex → D8080/D8090
    stmt = (
        select(CDTRule)
        .where(CDTRule.tier == tier_lower)
        .where(CDTRule.age_group == age_group)
        .where(CDTRule.is_active == True)
        .order_by(CDTRule.priority.desc())
    )

    result = await session.execute(stmt)
    rule = result.scalars().first()

    if not rule:
        # Fallback: if no exact match, return note
        return CDTSelectionResult(
            notes=f"No CDT rule found for tier={tier_lower}, age_group={age_group}"
        )

    # Get the CDT code details
    code_stmt = select(CDTCode).where(CDTCode.code == rule.cdt_code)
    code_result = await session.execute(code_stmt)
    cdt_code = code_result.scalars().first()

    primary_description = cdt_code.description if cdt_code else None


    suggested_add_ons = []
    diagnostic_map = {
        "intraoral_photos": "D0350",
        "panoramic_xray": "D0330",
        "fmx": "D0210",
        "diagnostic_casts": "D0470"
    }

    if diagnostic_assets:
        for asset_key, cdt_code_str in diagnostic_map.items():
            if diagnostic_assets.get(asset_key) is True:
                # Fetch code description from DB
                d_stmt = select(CDTCode).where(CDTCode.code == cdt_code_str)
                d_result = await session.execute(d_stmt)
                d_code = d_result.scalars().first()
                
                if d_code:
                    suggested_add_ons.append({
                        "code": d_code.code,
                        "description": d_code.description
                    })

    return CDTSelectionResult(
        primary_code=rule.cdt_code,
        primary_description=primary_description,
        suggested_add_ons=suggested_add_ons,
        notes=f"Selected based on tier={tier_lower}, age_group={age_group}",
    )
