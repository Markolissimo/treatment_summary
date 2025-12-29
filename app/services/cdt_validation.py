"""Validation utilities for CDT rules and codes."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.db.models import CDTCode, CDTRule
from app.schemas.enums import CaseTier, AgeGroup


async def validate_cdt_code_exists(
    session: AsyncSession,
    cdt_code: str,
) -> bool:
    """
    Validate that a CDT code exists in the database.
    
    Args:
        session: Database session
        cdt_code: CDT code to validate
        
    Returns:
        bool: True if code exists and is active
        
    Raises:
        HTTPException: If code doesn't exist or is inactive
    """
    stmt = select(CDTCode).where(CDTCode.code == cdt_code)
    result = await session.execute(stmt)
    code = result.scalar_one_or_none()
    
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CDT code '{cdt_code}' does not exist",
        )
    
    if not code.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CDT code '{cdt_code}' is not active",
        )
    
    return True


def validate_tier_value(tier: str) -> bool:
    """
    Validate that tier is in allowed values.
    
    Args:
        tier: Tier value to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        HTTPException: If tier is invalid
    """
    tier_lower = tier.lower()
    allowed_tiers = [t.value for t in CaseTier]
    
    if tier_lower not in allowed_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier '{tier}'. Allowed values: {', '.join(allowed_tiers)}",
        )
    
    return True


def validate_age_group_value(age_group: str) -> bool:
    """
    Validate that age_group is in allowed values.
    
    Args:
        age_group: Age group value to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        HTTPException: If age_group is invalid
    """
    age_group_lower = age_group.lower()
    allowed_age_groups = [a.value for a in AgeGroup]
    
    if age_group_lower not in allowed_age_groups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid age_group '{age_group}'. Allowed values: {', '.join(allowed_age_groups)}",
        )
    
    return True


async def validate_cdt_rule(
    session: AsyncSession,
    tier: str,
    age_group: str,
    cdt_code: str,
) -> bool:
    """
    Validate a complete CDT rule before creation/update.
    
    Args:
        session: Database session
        tier: Case tier
        age_group: Age group
        cdt_code: CDT code to assign
        
    Returns:
        bool: True if all validations pass
        
    Raises:
        HTTPException: If any validation fails
    """
    # Validate tier
    validate_tier_value(tier)
    
    # Validate age_group
    validate_age_group_value(age_group)
    
    # Validate CDT code exists
    await validate_cdt_code_exists(session, cdt_code)
    
    return True


async def check_duplicate_rule(
    session: AsyncSession,
    tier: str,
    age_group: str,
    exclude_id: Optional[str] = None,
) -> Optional[CDTRule]:
    """
    Check if a rule already exists for the given tier + age_group combination.
    
    Args:
        session: Database session
        tier: Case tier
        age_group: Age group
        exclude_id: Rule ID to exclude from check (for updates)
        
    Returns:
        CDTRule if duplicate found, None otherwise
    """
    stmt = (
        select(CDTRule)
        .where(CDTRule.tier == tier.lower())
        .where(CDTRule.age_group == age_group.lower())
        .where(CDTRule.is_active == True)
    )
    
    if exclude_id:
        stmt = stmt.where(CDTRule.id != exclude_id)
    
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
