"""Seed script to populate CDT codes and rules based on client documentation."""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_engine as engine
from app.db.models import CDTCode, CDTRule
from sqlmodel import SQLModel, select


async def seed_cdt_data():
    """Populate CDT codes and rules from client documentation."""
    
    async with AsyncSession(engine) as session:
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        print("Seeding CDT codes...")
        
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
            # Check if code already exists
            stmt = select(CDTCode).where(CDTCode.code == code_data["code"])
            result = await session.execute(stmt)
            existing = result.scalars().first()
            
            if not existing:
                code = CDTCode(**code_data)
                session.add(code)
                print(f"  Added: {code_data['code']} - {code_data['description']}")
            else:
                print(f"  Skipped (exists): {code_data['code']}")
        
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
                print(f"  Added: {code_data['code']} - {code_data['description']}")
            else:
                print(f"  Skipped (exists): {code_data['code']}")
        
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
                print(f"  Added: {code_data['code']} - {code_data['description']}")
            else:
                print(f"  Skipped (exists): {code_data['code']}")
        
        await session.commit()
        
        print("\nSeeding CDT rules...")
        
        # Rules based on client documentation:
        # 1. If Tier = Express/Mild → D8010
        # 2. If Tier = Moderate/Complex → choose D8080 vs D8090 based on age_group
        
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
            # Check if rule already exists
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
                print(f"  Added: {rule_data['tier']} + {rule_data['age_group']} → {rule_data['cdt_code']}")
            else:
                print(f"  Skipped (exists): {rule_data['tier']} + {rule_data['age_group']}")
        
        await session.commit()
        
        print("\n✅ CDT data seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_cdt_data())
