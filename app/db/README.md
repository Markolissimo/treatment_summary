# Database Module

## Purpose

This module handles all database operations including schema definitions, connection management, and audit logging. It provides a persistent record of every document generation event for compliance, debugging, and analytics.

## Contents

- **`models.py`** - SQLModel table definitions
- **`database.py`** - Database connection and session management
- **`audit.py`** - Audit logging utility functions

## Files Overview

### `models.py`

**Purpose:** Defines the database schema using SQLModel (combines SQLAlchemy + Pydantic).

---

#### `AuditLog` Table

**Purpose:** Records every document generation event with full metadata.

**Schema:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `str` | Primary Key | UUID v4 identifier |
| `user_id` | `str` | Indexed | User who initiated generation |
| `document_type` | `str` | Indexed | Type (e.g., "treatment_summary") |
| `document_version` | `str` | - | Schema version (default: "1.0") |
| `input_data` | `str` | - | JSON string of request data |
| `generated_text` | `str` | - | JSON string of generated document |
| `model_used` | `str` | - | AI model used (default: "gpt-4o") |
| `tokens_used` | `int` | Nullable | Total tokens consumed |
| `generation_time_ms` | `int` | Nullable | Generation time in milliseconds |
| `created_at` | `datetime` | - | Timestamp (UTC) |
| `status` | `str` | - | "success" or "error" |
| `error_message` | `str` | Nullable | Error details if failed |

**SQLModel Definition:**
```python
class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: str = Field(..., index=True)
    document_type: str = Field(..., index=True)
    # ... other fields
```

**Why SQLModel?**
- Combines SQLAlchemy (ORM) + Pydantic (validation)
- Type-safe database operations
- Auto-generates Pydantic models from tables
- Async support via SQLAlchemy 2.0

**Indexes:**
- `user_id` - Fast queries by user
- `document_type` - Fast queries by document type
- `created_at` - Implicit index for time-based queries

---

### `database.py`

**Purpose:** Manages database connections and provides session dependencies.

---

#### `async_engine`

**Purpose:** Async SQLAlchemy engine for database connections.

```python
async_engine = create_async_engine(
    settings.database_url,  # "sqlite+aiosqlite:///./bitesoft_audit.db"
    echo=settings.debug,    # Log SQL queries in debug mode
    future=True,            # Use SQLAlchemy 2.0 API
)
```

**Connection String Format:**
- SQLite: `sqlite+aiosqlite:///./database.db`
- PostgreSQL: `postgresql+asyncpg://user:pass@host/db`
- MySQL: `mysql+aiomysql://user:pass@host/db`

---

#### `AsyncSessionLocal`

**Purpose:** Session factory for creating database sessions.

```python
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects accessible after commit
)
```

---

#### `init_db()`

**Purpose:** Initialize database and create all tables.

```python
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**When Called:** On application startup (in `main.py` lifespan handler).

**What It Does:**
1. Connects to database
2. Creates `audit_logs` table if it doesn't exist
3. Runs migrations (if any)

---

#### `get_session()`

**Purpose:** FastAPI dependency for injecting database sessions.

```python
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

**Usage in Routes:**
```python
@router.post("/endpoint")
async def my_endpoint(session: AsyncSession = Depends(get_session)):
    # session is automatically managed
    # - Opened before request
    # - Committed on success
    # - Rolled back on error
    # - Closed after request
```

---

### `audit.py`

**Purpose:** High-level utility for logging generation events.

---

#### `log_generation()`

**Purpose:** Creates an audit log entry for a document generation event.

**Signature:**
```python
async def log_generation(
    session: AsyncSession,
    user_id: str,
    document_type: str,
    input_data: dict,
    generated_text: dict,
    model_used: str = "gpt-4o",
    tokens_used: Optional[int] = None,
    generation_time_ms: Optional[int] = None,
    status: str = "success",
    error_message: Optional[str] = None,
) -> AuditLog
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session` | `AsyncSession` | ✅ | Database session |
| `user_id` | `str` | ✅ | User identifier |
| `document_type` | `str` | ✅ | Type (e.g., "treatment_summary") |
| `input_data` | `dict` | ✅ | Request data |
| `generated_text` | `dict` | ✅ | Generated document |
| `model_used` | `str` | ❌ | AI model (default: "gpt-4o") |
| `tokens_used` | `int` | ❌ | Token count |
| `generation_time_ms` | `int` | ❌ | Generation time |
| `status` | `str` | ❌ | "success" or "error" |
| `error_message` | `str` | ❌ | Error details |

**Returns:** The created `AuditLog` entry

**How It Works:**
```python
# 1. Create AuditLog object
audit_entry = AuditLog(
    user_id=user_id,
    document_type=document_type,
    input_data=json.dumps(input_data),      # dict → JSON string
    generated_text=json.dumps(generated_text),
    # ... other fields
)

# 2. Add to session
session.add(audit_entry)

# 3. Commit to database
await session.commit()

# 4. Refresh to get DB-generated values
await session.refresh(audit_entry)

# 5. Return the entry
return audit_entry
```

**Usage in Routes:**
```python
@router.post("/generate-treatment-summary")
async def create_treatment_summary(
    request: TreatmentSummaryRequest,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await generate_treatment_summary(request)
        
        # Log success
        await log_generation(
            session=session,
            user_id=user_id,
            document_type="treatment_summary",
            input_data=request.model_dump(),
            generated_text=result.output.model_dump(),
            tokens_used=result.tokens_used,
            generation_time_ms=result.generation_time_ms,
            status="success",
        )
        
        return TreatmentSummaryResponse(...)
        
    except Exception as e:
        # Log failure
        await log_generation(
            session=session,
            user_id=user_id,
            document_type="treatment_summary",
            input_data=request.model_dump(),
            generated_text={},
            status="error",
            error_message=str(e),
        )
        raise
```

---

## Data Flow

```
API Request
    ↓
get_session() dependency
    ↓
AsyncSession created
    ↓
Business logic executes
    ↓
log_generation() called
    ↓
AuditLog entry created
    ↓
session.commit()
    ↓
Data persisted to SQLite
    ↓
Session closed automatically
```

## Database Lifecycle

```
Application Startup
    ↓
init_db() called
    ↓
Tables created (if not exist)
    ↓
Application ready
    ↓
[Requests handled]
    ↓
Application Shutdown
    ↓
Connections closed
```

## Dependencies

### Internal
- `app.core.config` - Database URL from settings

### External
- `sqlmodel` - ORM + Pydantic integration
- `sqlalchemy` - Database toolkit
- `aiosqlite` - Async SQLite driver

## Usage Examples

### Initialize Database
```python
from app.db.database import init_db

# On startup
await init_db()
```

### Log a Generation Event
```python
from app.db.audit import log_generation
from app.db.database import get_session

async def my_route(session: AsyncSession = Depends(get_session)):
    await log_generation(
        session=session,
        user_id="user_123",
        document_type="treatment_summary",
        input_data={"treatment_type": "clear aligners"},
        generated_text={"title": "Your Treatment Plan"},
        tokens_used=450,
        generation_time_ms=1250,
    )
```

### Query Audit Logs
```python
from sqlmodel import select
from app.db.models import AuditLog

async def get_user_history(user_id: str, session: AsyncSession):
    statement = select(AuditLog).where(AuditLog.user_id == user_id)
    results = await session.execute(statement)
    logs = results.scalars().all()
    return logs
```

### Query by Date Range
```python
from datetime import datetime, timedelta

async def get_recent_logs(session: AsyncSession):
    cutoff = datetime.utcnow() - timedelta(days=7)
    statement = select(AuditLog).where(AuditLog.created_at >= cutoff)
    results = await session.execute(statement)
    return results.scalars().all()
```

## Compliance & Analytics

### Audit Trail
Every generation is logged with:
- **Who:** `user_id`
- **What:** `document_type`, `input_data`, `generated_text`
- **When:** `created_at`
- **How:** `model_used`, `tokens_used`, `generation_time_ms`
- **Result:** `status`, `error_message`

### Use Cases
1. **Compliance:** Prove what was generated and when
2. **Debugging:** Reproduce errors with exact input data
3. **Analytics:** Track usage patterns, popular features
4. **Billing:** Calculate costs based on token usage
5. **Performance:** Monitor generation times

### Example Queries

**Total generations per user:**
```python
from sqlalchemy import func

statement = select(
    AuditLog.user_id,
    func.count(AuditLog.id).label("count")
).group_by(AuditLog.user_id)
```

**Average generation time:**
```python
statement = select(
    func.avg(AuditLog.generation_time_ms)
).where(AuditLog.status == "success")
```

**Error rate:**
```python
total = select(func.count(AuditLog.id))
errors = select(func.count(AuditLog.id)).where(AuditLog.status == "error")
error_rate = errors / total
```

## Database Migrations

For production, use Alembic for schema migrations:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migration
alembic upgrade head
```

## Future Enhancements

- **Soft Deletes:** Add `deleted_at` column instead of hard deletes
- **Partitioning:** Partition by date for large datasets
- **Archiving:** Move old logs to cold storage
- **Indexes:** Add composite indexes for common queries
- **Replication:** Set up read replicas for analytics
- **Encryption:** Encrypt sensitive fields at rest
