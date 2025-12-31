"""
Migration script to rename generated_text column to output_data in audit_logs table.

This migration aligns the database schema with the logical naming convention:
- input_data (what goes in)
- output_data (what comes out)

Each document type stores its specific output structure in output_data:
- treatment_summary: {"treatment_summary": {...}}
- insurance_summary: {"insurance_summary": str, "cdt_codes": List[str]}
"""

import sqlite3
import sys
from pathlib import Path


def migrate_sqlite_database(db_path: str = "bitesoft_audit.db"):
    """Rename generated_text column to output_data in SQLite database."""
    
    print(f"Starting migration on database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(audit_logs)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        if "generated_text" in columns and "output_data" not in columns:
            print("Renaming 'generated_text' column to 'output_data'...")
            cursor.execute("ALTER TABLE audit_logs RENAME COLUMN generated_text TO output_data")
            print("✓ Successfully renamed column")
        elif "output_data" in columns:
            print("✓ Column 'output_data' already exists (migration already applied)")
        else:
            print("⚠ Warning: Neither 'generated_text' nor 'output_data' column found")
        
        conn.commit()
        conn.close()
        
        print("✓ Migration completed successfully")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def migrate_postgresql_database(connection_string: str):
    """Rename generated_text column to output_data in PostgreSQL database."""
    
    try:
        import psycopg2
        
        print(f"Starting PostgreSQL migration...")
        
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'audit_logs'
        """)
        columns = {row[0] for row in cursor.fetchall()}
        
        if "generated_text" in columns and "output_data" not in columns:
            print("Renaming 'generated_text' column to 'output_data'...")
            cursor.execute("ALTER TABLE audit_logs RENAME COLUMN generated_text TO output_data")
            print("✓ Successfully renamed column")
        elif "output_data" in columns:
            print("✓ Column 'output_data' already exists (migration already applied)")
        else:
            print("⚠ Warning: Neither 'generated_text' nor 'output_data' column found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ PostgreSQL migration completed successfully")
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Rename generated_text to output_data")
    print("=" * 60)
    print()
    
    # Default to SQLite
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "bitesoft_audit.db"
    
    # Check if it's a PostgreSQL connection string
    if db_path.startswith("postgresql://") or db_path.startswith("postgres://"):
        success = migrate_postgresql_database(db_path)
    else:
        success = migrate_sqlite_database(db_path)
    
    sys.exit(0 if success else 1)
