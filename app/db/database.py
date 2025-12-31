from sqlmodel import SQLModel, create_engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize the database and create all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

        # Best-effort schema upgrades for SQLite (dev DB) to avoid breaking existing DB files.
        # SQLModel doesn't auto-migrate columns.
        try:
            if settings.database_url.startswith("sqlite"):
                # Add input_hash to audit_logs
                result = await conn.execute(text("PRAGMA table_info(audit_logs)"))
                audit_cols = {row[1] for row in result.fetchall()}
                
                if "input_hash" not in audit_cols:
                    await conn.execute(text("ALTER TABLE audit_logs ADD COLUMN input_hash TEXT"))
                    await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_audit_logs_input_hash ON audit_logs (input_hash)"))
                
                # Add confirmation audit fields to document_confirmations
                result = await conn.execute(text("PRAGMA table_info(document_confirmations)"))
                existing_cols = {row[1] for row in result.fetchall()}  # row[1] = name

                alter_statements = []
                if "is_edited" not in existing_cols:
                    alter_statements.append("ALTER TABLE document_confirmations ADD COLUMN is_edited BOOLEAN DEFAULT 0")
                if "edited_summary" not in existing_cols:
                    alter_statements.append("ALTER TABLE document_confirmations ADD COLUMN edited_summary TEXT")
                if "similarity_score" not in existing_cols:
                    alter_statements.append("ALTER TABLE document_confirmations ADD COLUMN similarity_score REAL")
                if "regeneration_history" not in existing_cols:
                    alter_statements.append("ALTER TABLE document_confirmations ADD COLUMN regeneration_history TEXT")

                for stmt in alter_statements:
                    await conn.execute(text(stmt))
        except Exception:
            # Never block startup due to best-effort migration failures.
            pass


async def get_session() -> AsyncSession:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        yield session
