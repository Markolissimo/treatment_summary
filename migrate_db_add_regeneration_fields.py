"""
Database migration script to add regeneration tracking fields.

This script adds the following fields to the audit_logs table:
- seed: int (nullable) - Seed value used for LLM generation
- is_regenerated: bool (default False) - Whether this is a regenerated version
- previous_version_uuid: str (nullable, indexed) - UUID of the previous version

Run this script once to migrate your existing database:
    python migrate_db_add_regeneration_fields.py
"""

import asyncio
import sqlite3
from app.core.config import get_settings

settings = get_settings()


def migrate_sqlite_database():
    """Migrate SQLite database to add new regeneration fields."""
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "seed" not in columns:
            print("Adding 'seed' column...")
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN seed INTEGER")
            print("✓ Added 'seed' column")
        else:
            print("✓ 'seed' column already exists")
        
        if "is_regenerated" not in columns:
            print("Adding 'is_regenerated' column...")
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN is_regenerated BOOLEAN DEFAULT 0")
            print("✓ Added 'is_regenerated' column")
        else:
            print("✓ 'is_regenerated' column already exists")
        
        if "previous_version_uuid" not in columns:
            print("Adding 'previous_version_uuid' column...")
            cursor.execute("ALTER TABLE audit_logs ADD COLUMN previous_version_uuid TEXT")
            print("✓ Added 'previous_version_uuid' column")
            
            print("Creating index on 'previous_version_uuid'...")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_previous_version_uuid ON audit_logs (previous_version_uuid)")
            print("✓ Created index on 'previous_version_uuid'")
        else:
            print("✓ 'previous_version_uuid' column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Regeneration Tracking Fields")
    print("=" * 60)
    print()
    
    migrate_sqlite_database()
    
    print()
    print("=" * 60)
    print("Migration complete. You can now use the regeneration feature!")
    print("=" * 60)
