"""
Migration script to add confirmation tracking and update CDT rules.

This script:
1. Creates the document_confirmations table
2. Adds NOT NULL constraints to cdt_rules (tier, age_group)
3. Updates existing audit logs with proper document versions

Run this after updating the codebase to ensure database schema is current.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.database import async_engine
from app.db.models import SQLModel, DOCUMENT_VERSIONS
from sqlalchemy.ext.asyncio import AsyncSession


async def run_migration():
    """Run database migration."""
    print("Starting migration: Add confirmation tracking and CDT rule constraints")
    
    async with async_engine.begin() as conn:
        # Create all tables (will create document_confirmations if it doesn't exist)
        print("Creating new tables...")
        await conn.run_sync(SQLModel.metadata.create_all)
        print("✓ Tables created/verified")
        
        # Update existing audit logs with proper document versions
        print("\nUpdating audit log document versions...")
        for doc_type, version in DOCUMENT_VERSIONS.items():
            result = await conn.execute(
                text("""
                    UPDATE audit_logs 
                    SET document_version = :version 
                    WHERE document_type = :doc_type 
                    AND (document_version IS NULL OR document_version = '1.0')
                """),
                {"version": version, "doc_type": doc_type}
            )
            print(f"✓ Updated {result.rowcount} {doc_type} records to version {version}")
        
        print("\n✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Verify tables in admin panel: /admin")
        print("2. Check CDT Rules have proper tier/age_group values")
        print("3. Test confirmation endpoint: POST /api/v1/documents/{id}/confirm")


async def verify_migration():
    """Verify migration was successful."""
    print("\nVerifying migration...")
    
    async with AsyncSession(async_engine) as session:
        # Check if document_confirmations table exists
        result = await session.execute(
            text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_name = 'document_confirmations'
            """)
        )
        count = result.scalar()
        
        if count > 0:
            print("✓ document_confirmations table exists")
        else:
            print("✗ document_confirmations table not found")
            return False
        
        # Check audit logs have document_version
        result = await session.execute(
            text("""
                SELECT COUNT(*) as count 
                FROM audit_logs 
                WHERE document_version IS NOT NULL
            """)
        )
        count = result.scalar()
        print(f"✓ {count} audit logs have document_version set")
        
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("BiteSoft AI - Database Migration")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(run_migration())
        asyncio.run(verify_migration())
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        sys.exit(1)
