# Application Module Documentation

**Version 0.2.0** | December 31, 2025

This directory contains the core application code for the BiteSoft AI Document Generation System.

---

## 📁 Module Structure

```
app/
├── api/              # API routes and endpoints
├── core/             # Configuration, prompts, security
├── db/               # Database models and utilities
├── schemas/          # Pydantic request/response models
├── services/         # Business logic and AI orchestration
└── main.py           # FastAPI application entry point
```

---

## 🔌 API Module (`api/`)

**Purpose**: HTTP interface layer for all endpoints

### Key Files
- `routes.py` - All API endpoint definitions

### Active Endpoints

#### Treatment Summary (v0.2.0)
```python
POST /api/v1/generate-treatment-summary
```
- Generates patient-facing treatment summaries
- Supports multiple tones and audiences
- CDT code selection based on tier and age
- Regeneration support with seed versioning

#### Insurance Summary (v0.1.0)
```python
POST /api/v1/generate-insurance-summary
```
- Generates admin-facing insurance documentation
- Conservative, neutral tone
- Deterministic CDT code logic
- Required compliance disclaimers

#### Document Confirmation (v0.2.0)
```python
POST /api/v1/documents/{generation_id}/confirm
```
- Records dentist confirmation
- Tracks confirmed payload
- Links to audit log entry

### Architecture Pattern
```
Client Request
    ↓
FastAPI Router (routes.py)
    ↓
Dependency Injection:
  - get_current_user() → user_id
  - get_session() → db_session
    ↓
Service Layer
    ↓
Audit Logging
    ↓
Response Serialization
    ↓
Client Response
```

---

## ⚙️ Core Module (`core/`)

**Purpose**: Foundation layer with configuration, prompts, and security

### Key Files

#### `config.py` - Application Settings
```python
class Settings(BaseSettings):
    # Application
    app_name: str = "BiteSoft AI Document Generation System"
    app_version: str = "0.2.0"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    # Database
    database_url: str
    
    # Security (v0.2.0)
    secret_key: str
    enable_auth_bypass: bool = True
    cors_origins: str = "*"
    
    # PHI Handling (v0.2.0)
    store_full_audit_data: bool = True
    redact_phi_fields: bool = False
```

**Features**:
- Environment variable management via Pydantic Settings
- Cached via `@lru_cache` for performance
- Reads from `.env` file with fallback defaults

#### `prompts.py` - AI System Prompts

**Treatment Summary Prompt**:
- Hard restrictions (no diagnosis, no guarantees, no financials)
- Tone adaptation (concise, casual, reassuring, clinical)
- Audience targeting (patient, internal)
- Few-shot examples

**Insurance Summary Prompt** (v0.1.0):
- Conservative, neutral tone
- No diagnosis or coverage promises
- Administrative support focus
- Required disclaimers

#### `security.py` - Authentication (v0.2.0)

```python
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials]
) -> str:
    """
    JWT validation with debug bypass.
    Production: Validates portal JWT tokens
    Development: Returns dev_user_001 if no token
    """
```

**Features**:
- JWT token validation (issuer, audience, signature, expiry)
- Debug bypass for local development
- Extracts user_id for audit logging

#### `phi_utils.py` - PHI Redaction (v0.2.0)

```python
def redact_phi_from_dict(data: dict) -> dict:
    """Redact PHI fields based on configuration"""

def prepare_audit_data(data: dict) -> dict:
    """Prepare data for audit logging with PHI handling"""
```

#### `text_utils.py` - Text Processing

```python
def normalize_to_ascii(text: str) -> str:
    """Normalize unicode characters to ASCII"""
```

---

## 🗄️ Database Module (`db/`)

**Purpose**: Data persistence and audit logging

### Key Files

#### `models.py` - SQLModel Definitions

**AuditLog Table**:
```python
class AuditLog(SQLModel, table=True):
    id: str                    # UUID v4
    user_id: str              # User identifier
    document_type: str        # "treatment_summary" | "insurance_summary"
    document_version: str     # Schema version (v0.2.0)
    input_data: str           # JSON string of input request
    output_data: str          # JSON string of document output
    tokens_used: int
    generation_time_ms: int
    created_at: datetime
    status: str               # "success" | "error"
    seed: Optional[int]       # For regeneration (v0.2.0)
    is_regenerated: bool      # Regeneration flag (v0.2.0)
    previous_version_uuid: Optional[str]  # Version chain (v0.2.0)
```

**CDTCode Table**:
```python
class CDTCode(SQLModel, table=True):
    id: int
    code: str                 # e.g., "D8080"
    description: str
    category: str
    is_active: bool
```

**CDTRule Table** (v0.2.0 - Enhanced):
```python
class CDTRule(SQLModel, table=True):
    id: int
    tier: str                 # Validated enum
    age_group: str            # Validated enum (v0.2.0)
    cdt_code_id: int         # FK to CDTCode (v0.2.0)
    priority: int
    is_active: bool
```

**DocumentConfirmation Table** (v0.2.0):
```python
class DocumentConfirmation(SQLModel, table=True):
    id: str
    audit_log_id: str         # FK to AuditLog
    user_id: str
    confirmed_at: datetime
    confirmed_payload: str    # Final edited JSON
```

**Document Versions** (v0.2.0):
```python
DOCUMENT_VERSIONS = {
    "treatment_summary": "1.0",
    "insurance_summary": "1.0",
    "progress_notes": "1.0",
}
```

#### `database.py` - Connection Management

```python
async_engine = create_async_engine(database_url)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession)

async def init_db():
    """Initialize database and create tables"""

async def get_session() -> AsyncSession:
    """FastAPI dependency for database sessions"""
```

#### `audit.py` - Audit Logging (v0.2.0 - Enhanced)

```python
async def log_generation(
    session: AsyncSession,
    user_id: str,
    document_type: str,
    input_data: dict,
    output_data: dict,
    tokens_used: Optional[int] = None,
    generation_time_ms: Optional[int] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    seed: Optional[int] = None,
    is_regenerated: bool = False,
    previous_version_uuid: Optional[str] = None,
) -> AuditLog
```

**Features**:
- PHI redaction based on configuration
- Schema versioning
- Regeneration tracking
- Complete audit trail

---

## 📋 Schemas Module (`schemas/`)

**Purpose**: Pydantic models for request/response validation

### Key Files

#### `enums.py` - Controlled Vocabularies

**Treatment Summary Enums**:
- `TreatmentType`, `AreaTreated`, `CaseDifficulty`
- `MonitoringApproach`, `Attachments`
- `Audience`, `Tone`
- `CaseTier`, `AgeGroup` (v0.2.0)

**Insurance Summary Enums** (v0.1.0):
- `InsuranceTier` (express_mild, moderate, complex)
- `Arches` (upper, lower, both)

#### `treatment_summary.py` - Treatment Summary Schemas

```python
class TreatmentSummaryRequest(BaseModel):
    # All fields optional with defaults
    treatment_type: TreatmentType = TreatmentType.CLEAR_ALIGNERS
    area_treated: AreaTreated = AreaTreated.BOTH
    duration_range: str = "4-6 months"
    # ... more fields
    audience: Audience = Audience.PATIENT
    tone: Tone = Tone.REASSURING
    
    # Regeneration (v0.2.0)
    is_regeneration: Optional[bool] = False
    previous_version_uuid: Optional[str] = None

class TreatmentSummaryOutput(BaseModel):
    title: str
    summary: str

class TreatmentSummaryResponse(BaseModel):
    success: bool = True
    document: TreatmentSummaryOutput
    cdt_codes: dict
    metadata: dict
    uuid: Optional[str]  # v0.2.0
    is_regenerated: bool  # v0.2.0
    seed: Optional[int]  # v0.2.0
```

#### `insurance_summary.py` - Insurance Summary Schemas (v0.1.0)

```python
class DiagnosticAssets(BaseModel):
    intraoral_photos: bool = False
    panoramic_xray: bool = False
    fmx: bool = False

class InsuranceSummaryRequest(BaseModel):
    tier: InsuranceTier
    arches: Arches = Arches.BOTH
    age_group: AgeGroup
    retainers_included: bool = True
    diagnostic_assets: DiagnosticAssets
    monitoring_approach: MonitoringApproach
    notes: Optional[str] = None
    
    # Regeneration
    is_regeneration: Optional[bool] = False
    previous_version_uuid: Optional[str] = None

class InsuranceSummaryOutput(BaseModel):
    insurance_summary: str
    disclaimer: str  # Required disclaimer text

class InsuranceSummaryResponse(BaseModel):
    success: bool = True
    document: InsuranceSummaryOutput
    cdt_codes: List[str]  # List of CDT code strings
    metadata: dict
    uuid: Optional[str]
    is_regenerated: bool
    seed: Optional[int]
```

#### `confirmation.py` - Confirmation Schemas (v0.2.0)

```python
class DocumentConfirmationRequest(BaseModel):
    generation_id: str
    confirmed_payload: dict

class DocumentConfirmationResponse(BaseModel):
    success: bool
    confirmation_id: str
    confirmed_at: datetime
```

---

## 🔧 Services Module (`services/`)

**Purpose**: Business logic and AI orchestration

### Key Files

#### `openai_service.py` - Treatment Summary Generation

```python
async def generate_treatment_summary(
    request: TreatmentSummaryRequest,
    api_key: Optional[str] = None,
    seed_override: Optional[int] = None,
    session: Optional[AsyncSession] = None,
) -> GenerationResult
```

**Features**:
- OpenAI Structured Outputs for reliable JSON
- Prompt building from case data
- Token usage tracking
- Generation time measurement
- Seed-based regeneration (v0.2.0)

#### `insurance_openai_service.py` - Insurance Summary Generation (v0.1.0)

```python
async def generate_insurance_summary(
    request: InsuranceSummaryRequest,
    api_key: Optional[str] = None,
    seed_override: Optional[int] = None,
    session: Optional[AsyncSession] = None,
) -> InsuranceGenerationResult
```

**Features**:
- Conservative tone enforcement
- Neutral, factual language
- Required disclaimer inclusion
- Seed-based regeneration

#### `cdt_service.py` - Treatment CDT Selection

```python
async def select_cdt_codes(
    session: AsyncSession,
    tier: CaseTier,
    patient_age: Optional[int],
) -> CDTResult
```

**Logic**:
- Tier-based primary code selection
- Age-based categorization (adolescent <18, adult ≥18)
- Database-driven rules with priority ordering

#### `insurance_cdt_service.py` - Insurance CDT Selection (v0.1.0)

```python
async def select_insurance_cdt_codes(
    session: AsyncSession,
    tier: InsuranceTier,
    age_group: AgeGroup,
    diagnostic_assets: DiagnosticAssets,
    retainers_included: bool,
) -> InsuranceCDTResult
```

**Logic**:
- Express/Mild → D8010
- Moderate/Complex + Adolescent → D8080
- Moderate/Complex + Adult → D8090
- Diagnostic codes only if explicitly flagged
- No guessing - explicit inputs only

#### `cdt_validation.py` - CDT Validation (v0.2.0)

```python
async def validate_cdt_code_exists(session: AsyncSession, code: str) -> bool
def validate_tier_value(tier: str) -> bool
def validate_age_group_value(age_group: str) -> bool
async def validate_cdt_rule(session: AsyncSession, rule: CDTRule) -> List[str]
async def check_duplicate_rule(session: AsyncSession, rule: CDTRule) -> bool
```

#### `confirmation_service.py` - Document Confirmation (v0.2.0)

```python
async def confirm_document(
    session: AsyncSession,
    generation_id: str,
    user_id: str,
    confirmed_payload: dict,
) -> DocumentConfirmation

async def is_document_confirmed(
    session: AsyncSession,
    generation_id: str,
) -> bool
```

---

## 🚀 Main Application (`main.py`)

**Purpose**: FastAPI application entry point

```python
app = FastAPI(
    title="BiteSoft AI Document Generation System",
    version="0.2.0",
    description="AI-powered orthodontic documentation",
)

# Lifespan: Database initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# CORS middleware (v0.2.0)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api/v1")

# Admin panel
admin = Admin(app, async_engine)
admin.add_view(AuditLogAdmin)
admin.add_view(CDTCodeAdmin)
admin.add_view(CDTRuleAdmin)
admin.add_view(DocumentConfirmationAdmin)  # v0.2.0
```

---

## 🔄 Data Flow

### Treatment Summary Generation
```
1. Client → POST /api/v1/generate-treatment-summary
2. FastAPI validates TreatmentSummaryRequest
3. get_current_user() extracts user_id from JWT
4. get_session() provides database session
5. generate_treatment_summary() calls OpenAI
6. select_cdt_codes() determines CDT codes
7. log_generation() creates audit entry
8. TreatmentSummaryResponse returned to client
```

### Insurance Summary Generation (v0.1.0)
```
1. Client → POST /api/v1/generate-insurance-summary
2. FastAPI validates InsuranceSummaryRequest
3. Authentication and session injection
4. generate_insurance_summary() calls OpenAI
5. select_insurance_cdt_codes() determines codes
6. log_generation() creates audit entry
7. InsuranceSummaryResponse returned to client
```

### Document Confirmation (v0.2.0)
```
1. Client → POST /api/v1/documents/{id}/confirm
2. FastAPI validates DocumentConfirmationRequest
3. confirm_document() creates confirmation record
4. Links to audit log entry
5. DocumentConfirmationResponse returned
```

---

## 🧪 Testing

Each module has corresponding tests in `tests/`:
- `test_api.py` - API endpoint tests
- `test_core_*.py` - Core module tests
- `test_schemas.py` - Schema validation tests
- `test_database.py` - Database and audit tests
- `test_services.py` - Service layer tests

---

## 📊 Version Summary

| Module | Version | Status | Key Features |
|--------|---------|--------|--------------|
| **API** | 0.2.0 | Production | Treatment, Insurance, Confirmation endpoints |
| **Core** | 0.2.0 | Production | JWT auth, CORS, PHI redaction |
| **Database** | 0.2.0 | Production | Audit logs, CDT codes, confirmations, versioning |
| **Schemas** | 0.2.0 | Production | Treatment, Insurance, Confirmation models |
| **Services** | 0.2.0 | Production | OpenAI integration, CDT selection, validation |

---

**Last Updated**: December 31, 2025  
**Application Version**: 0.2.0
