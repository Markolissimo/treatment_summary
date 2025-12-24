# Core Configuration Module

## Purpose

This module contains the core configuration, system prompts, and security utilities that form the foundation of the BiteSoft AI Document Generation System. It centralizes all environment-based settings, AI prompt engineering, and authentication logic.

## Contents

- **`config.py`** - Application settings and environment configuration
- **`prompts.py`** - System prompts with clinical guardrails
- **`security.py`** - Authentication and authorization utilities
- **`utils.py`** - Utility functions (age threshold logic for CDT)

## Files Overview

### `config.py`

**Purpose:** Centralized configuration management using Pydantic Settings.

**Key Components:**

```python
class Settings(BaseSettings):
    # Application
    app_name: str
    app_version: str
    debug: bool
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
```

**How It Works:**
1. Reads from `.env` file (via `pydantic-settings`)
2. Falls back to default values if env vars not set
3. Cached via `@lru_cache` for performance
4. Accessed globally via `get_settings()`

**Usage:**
```python
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)
```

**Environment Variables:**
- `OPENAI_API_KEY` - OpenAI API key (required)
- `OPENAI_MODEL` - Model to use (default: gpt-4o)
- `DATABASE_URL` - SQLite connection string
- `SECRET_KEY` - JWT signing key (change in production!)
- `DEBUG` - Enable debug mode (default: false)

---

### `prompts.py`

**Purpose:** System prompts that enforce clinical communication guardrails.

**Key Components:**

#### `TREATMENT_SUMMARY_SYSTEM_PROMPT`

A comprehensive system prompt that instructs GPT-4 on:

**Hard Restrictions (NEVER VIOLATE):**
1. **NO DIAGNOSIS** - Avoid terms like "malocclusion," "disease," "pathology"
2. **NO GUARANTEES** - Never promise outcomes (use "expected," "may," "typically")
3. **NO FINANCIALS** - Never mention pricing, costs, insurance claims
4. **FACT INTEGRITY** - Clinical facts stay constant regardless of tone

**Output Requirements:**
- Adapt tone: concise, casual, reassuring, or clinical
- Adapt audience: patient-facing or internal/clinical staff
- Maintain professionalism and clarity

**Tone Guidelines:**
- **Concise:** Brief, bullet-style
- **Casual:** Friendly, conversational
- **Reassuring:** Warm, supportive
- **Clinical:** Professional, detailed, formal

**How It Works:**
```python
# System prompt sets the rules
messages = [
    {"role": "system", "content": TREATMENT_SUMMARY_SYSTEM_PROMPT},
    {"role": "user", "content": user_prompt_with_case_data}
]

# GPT-4 generates response following the guardrails
response = await client.chat.completions.create(...)
```

**Placeholder Prompts:**
- `INSURANCE_SUMMARY_SYSTEM_PROMPT` - For Module 2
- `PROGRESS_NOTES_SYSTEM_PROMPT` - For Module 3

---

### `security.py`

**Purpose:** Authentication and authorization middleware.

**Key Components:**

#### `get_current_user()` Dependency

**Current Implementation (Development Mode):**
```python
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    if credentials is None:
        return "dev_user_001"  # Development default
    
    token = credentials.credentials
    return f"user_{token[:8]}"  # Placeholder extraction
```

**How It Works:**
1. FastAPI injects `HTTPAuthorizationCredentials` from `Authorization: Bearer <token>` header
2. If no token provided → returns default dev user
3. If token provided → extracts user_id (placeholder logic)
4. Returns `user_id` string for audit logging

**Production Implementation (TODO):**
```python
from jose import jwt, JWTError

async def get_current_user(credentials: HTTPAuthorizationCredentials) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

**Usage in Routes:**
```python
@router.post("/generate-treatment-summary")
async def create_treatment_summary(
    request: TreatmentSummaryRequest,
    user_id: str = Depends(get_current_user),  # Injected here
):
    # user_id is now available for audit logging
    await log_generation(user_id=user_id, ...)
```

## Dependencies

### Internal
- None (this is the foundation layer)

### External
- `pydantic-settings` - Environment variable management
- `functools.lru_cache` - Settings caching
- `fastapi.security.HTTPBearer` - Bearer token extraction
- `python-jose` - JWT encoding/decoding (for production auth)

## Configuration Flow

```
.env file
    ↓
Settings class (config.py)
    ↓
@lru_cache decorator
    ↓
get_settings() function
    ↓
Used throughout application
```

## Security Flow

```
HTTP Request with Authorization header
    ↓
HTTPBearer extracts token
    ↓
get_current_user() dependency
    ↓
Validates token (production) or returns dev user
    ↓
user_id injected into route handler
    ↓
Used for audit logging
```

## Prompt Engineering Flow

```
Case data (treatment_type, duration, etc.)
    ↓
User prompt builder (in services/)
    ↓
Combined with TREATMENT_SUMMARY_SYSTEM_PROMPT
    ↓
Sent to GPT-4
    ↓
Response follows guardrails
```

## Usage Examples

### Configuration
```python
from app.core.config import get_settings

settings = get_settings()
print(settings.openai_model)  # "gpt-4o"
print(settings.debug)          # False
```

### Prompts
```python
from app.core.prompts import TREATMENT_SUMMARY_SYSTEM_PROMPT

messages = [
    {"role": "system", "content": TREATMENT_SUMMARY_SYSTEM_PROMPT},
    {"role": "user", "content": "Generate summary for..."}
]
```

### Security
```python
from app.core.security import get_current_user
from fastapi import Depends

@router.post("/endpoint")
async def my_endpoint(user_id: str = Depends(get_current_user)):
    print(f"Request from: {user_id}")
```

---

### `utils.py`

**Purpose:** Utility functions for business logic.

**Key Components:**

#### `get_patient_category()`

**Purpose:** Determine patient category based on age threshold for CDT logic.

```python
def get_patient_category(age: int | None) -> Literal["adolescent", "adult", "unknown"]:
    """
    CDT Logic:
    - Adolescent: under 18
    - Adult: 18 and over
    """
    if age is None:
        return "unknown"
    return "adolescent" if age < 18 else "adult"
```

**Usage:**
```python
from app.core.utils import get_patient_category

category = get_patient_category(16)  # "adolescent"
category = get_patient_category(25)  # "adult"
category = get_patient_category(None)  # "unknown"
```

## Future Enhancements

- **Config:** Add feature flags, rate limits, model temperature settings
- **Prompts:** A/B testing framework for prompt variations
- **Security:** Full JWT implementation with refresh tokens, role-based access control (RBAC)
- **Utils:** Expand with more CDT logic, validation helpers, data transformations
