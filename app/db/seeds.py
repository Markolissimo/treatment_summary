"""Database seeding logic."""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.database import async_engine as engine
from app.db.models import CDTCode, CDTRule

logger = logging.getLogger(__name__)


async def seed_cdt_data():
    """Populate CDT codes and rules from client documentation."""
    logger.info("Starting CDT data seeding check...")
    
    async with AsyncSession(engine) as session:
        # Primary orthodontic codes
        primary_codes = [
            {
                "code": "D8010",
                "description": "Limited orthodontic treatment",
                "category": "orthodontic",
                "is_primary": True,
                "notes": "Use for minor alignment / short duration (Express/Mild tier)",
            },
            {
                "code": "D8080",
                "description": "Comprehensive orthodontic treatment – adolescent dentition",
                "category": "orthodontic",
                "is_primary": True,
                "notes": "Default comprehensive tier for adolescents (Moderate/Complex)",
            },
            {
                "code": "D8090",
                "description": "Comprehensive orthodontic treatment – adult dentition",
                "category": "orthodontic",
                "is_primary": True,
                "notes": "Default comprehensive tier for adults (Moderate/Complex)",
            },
        ]
        
        for code_data in primary_codes:
            stmt = select(CDTCode).where(CDTCode.code == code_data["code"])
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if not existing:
                code = CDTCode(**code_data)
                session.add(code)
                logger.info(f"Added CDT Code: {code_data['code']}")
        
        # Diagnostic/supporting codes
        diagnostic_codes = [
            {
                "code": "D0330",
                "description": "Panoramic radiograph",
                "category": "diagnostic",
                "is_primary": False,
                "notes": "Common add-on for insurance documentation",
            },
            {
                "code": "D0210",
                "description": "Intraoral complete series of radiographic images (FMX)",
                "category": "diagnostic",
                "is_primary": False,
                "notes": "Full mouth x-ray series",
            },
            {
                "code": "D0350",
                "description": "Oral/facial photographic images",
                "category": "diagnostic",
                "is_primary": False,
                "notes": "Clinical photography",
            },
            {
                "code": "D0470",
                "description": "Diagnostic casts",
                "category": "diagnostic",
                "is_primary": False,
                "notes": "If applicable",
            },
        ]
        
        for code_data in diagnostic_codes:
            stmt = select(CDTCode).where(CDTCode.code == code_data["code"])
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if not existing:
                code = CDTCode(**code_data)
                session.add(code)
                logger.info(f"Added CDT Code: {code_data['code']}")
        
        # Retention code
        retention_codes = [
            {
                "code": "D8680",
                "description": "Orthodontic retention (completion of active treatment)",
                "category": "retention",
                "is_primary": False,
                "notes": "If billed separately",
            },
        ]
        
        for code_data in retention_codes:
            stmt = select(CDTCode).where(CDTCode.code == code_data["code"])
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if not existing:
                code = CDTCode(**code_data)
                session.add(code)
                logger.info(f"Added CDT Code: {code_data['code']}")
        
        await session.commit()
        
        # Rules based on client documentation
        rules = [
            # Express tier
            {
                "tier": "express",
                "age_group": "adolescent",
                "cdt_code": "D8010",
                "priority": 100,
                "notes": "Express tier always uses D8010 regardless of age",
            },
            {
                "tier": "express",
                "age_group": "adult",
                "cdt_code": "D8010",
                "priority": 100,
                "notes": "Express tier always uses D8010 regardless of age",
            },
            # Mild tier
            {
                "tier": "mild",
                "age_group": "adolescent",
                "cdt_code": "D8010",
                "priority": 100,
                "notes": "Mild tier always uses D8010 regardless of age",
            },
            {
                "tier": "mild",
                "age_group": "adult",
                "cdt_code": "D8010",
                "priority": 100,
                "notes": "Mild tier always uses D8010 regardless of age",
            },
            # Moderate tier
            {
                "tier": "moderate",
                "age_group": "adolescent",
                "cdt_code": "D8080",
                "priority": 90,
                "notes": "Moderate tier for adolescents uses D8080",
            },
            {
                "tier": "moderate",
                "age_group": "adult",
                "cdt_code": "D8090",
                "priority": 90,
                "notes": "Moderate tier for adults uses D8090",
            },
            # Complex tier
            {
                "tier": "complex",
                "age_group": "adolescent",
                "cdt_code": "D8080",
                "priority": 80,
                "notes": "Complex tier for adolescents uses D8080 (same as moderate)",
            },
            {
                "tier": "complex",
                "age_group": "adult",
                "cdt_code": "D8090",
                "priority": 80,
                "notes": "Complex tier for adults uses D8090 (same as moderate)",
            },
        ]
        
        for rule_data in rules:
            stmt = (
                select(CDTRule)
                .where(CDTRule.tier == rule_data["tier"])
                .where(CDTRule.age_group == rule_data["age_group"])
            )
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if not existing:
                rule = CDTRule(**rule_data)
                session.add(rule)
                logger.info(f"Added CDT Rule: {rule_data['tier']} + {rule_data['age_group']}")
        
        await session.commit()
        logger.info("CDT data seeding check complete.")
