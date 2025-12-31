"""Database migration script to add confirmation audit fields and input_hash.

Adds the following fields to the document_confirmations table:
- is_edited: bool (default False)
- edited_summary: text (nullable)
- similarity_score: float (nullable)
- regeneration_history: text (nullable JSON list)

Adds the following field to the audit_logs table:
- input_hash: text (nullable, indexed) - SHA256 hash for stable regeneration tracking

This script is intended for PostgreSQL deployments (Docker Compose), but it also
supports SQLite for local development.

Run once after pulling code updates:
    python scripts/migration/migrate_db_add_confirmation_audit_fields.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from app.core.config import get_settings
from app.db.database import async_engine
from app.db.models import SQLModel

settings = get_settings()


async def run_migration() -> None:
    print("Starting migration: Add confirmation audit fields and input_hash")

    async with async_engine.begin() as conn:
        # Ensure tables exist
        await conn.run_sync(SQLModel.metadata.create_all)

        db_url = settings.database_url

        if db_url.startswith("sqlite"):
            # SQLite: Add input_hash to audit_logs
            result = await conn.execute(text("PRAGMA table_info(audit_logs)"))
            audit_cols = {row[1] for row in result.fetchall()}
            
            if "input_hash" not in audit_cols:
                await conn.execute(text("ALTER TABLE audit_logs ADD COLUMN input_hash TEXT"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_input_hash ON audit_logs (input_hash)"))
                print("✓ Added input_hash to audit_logs")
            else:
                print("✓ input_hash already exists in audit_logs")
            
            # SQLite: Add confirmation audit fields
            result = await conn.execute(text("PRAGMA table_info(document_confirmations)"))
            existing_cols = {row[1] for row in result.fetchall()}  # row[1] = name

            alter_statements: list[str] = []
            if "is_edited" not in existing_cols:
                alter_statements.append(
                    "ALTER TABLE document_confirmations ADD COLUMN is_edited BOOLEAN DEFAULT 0"
                )
            if "edited_summary" not in existing_cols:
                alter_statements.append(
                    "ALTER TABLE document_confirmations ADD COLUMN edited_summary TEXT"
                )
            if "similarity_score" not in existing_cols:
                alter_statements.append(
                    "ALTER TABLE document_confirmations ADD COLUMN similarity_score REAL"
                )
            if "regeneration_history" not in existing_cols:
                alter_statements.append(
                    "ALTER TABLE document_confirmations ADD COLUMN regeneration_history TEXT"
                )

            for stmt in alter_statements:
                await conn.execute(text(stmt))

        else:
            # PostgreSQL: Add input_hash to audit_logs
            await conn.execute(
                text(
                    "ALTER TABLE audit_logs "
                    "ADD COLUMN IF NOT EXISTS input_hash TEXT"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_audit_logs_input_hash "
                    "ON audit_logs (input_hash)"
                )
            )
            print("✓ Added input_hash to audit_logs")
            
            # PostgreSQL: Add confirmation audit fields
            await conn.execute(
                text(
                    "ALTER TABLE document_confirmations "
                    "ADD COLUMN IF NOT EXISTS is_edited BOOLEAN DEFAULT FALSE"
                )
            )
            await conn.execute(
                text(
                    "ALTER TABLE document_confirmations "
                    "ADD COLUMN IF NOT EXISTS edited_summary TEXT"
                )
            )
            await conn.execute(
                text(
                    "ALTER TABLE document_confirmations "
                    "ADD COLUMN IF NOT EXISTS similarity_score DOUBLE PRECISION"
                )
            )
            await conn.execute(
                text(
                    "ALTER TABLE document_confirmations "
                    "ADD COLUMN IF NOT EXISTS regeneration_history TEXT"
                )
            )
            print("✓ Added confirmation audit fields")

    print("✓ Migration completed successfully")


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Confirmation Audit Fields")
    print("=" * 60)
    print()

    try:
        asyncio.run(run_migration())
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        sys.exit(1)
