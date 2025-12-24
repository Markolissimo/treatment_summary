# API Routes Module

## Purpose

This module contains all FastAPI endpoint definitions for the BiteSoft AI Document Generation System. It serves as the HTTP interface layer that receives client requests, orchestrates business logic, and returns structured responses.

## Contents

- **`routes.py`** - Main API router with all endpoint definitions

## Architecture

The API layer follows a clean architecture pattern:
1. Receives HTTP requests with validated Pydantic schemas
2. Extracts user authentication via dependency injection
3. Calls service layer for business logic
4. Logs all operations to audit database
5. Returns structured responses or error messages

## Endpoints

### Active Endpoints

#### `POST /api/v1/generate-treatment-summary`
Generates a professional treatment summary document from structured case data.

**Input:** `TreatmentSummaryRequest` (Pydantic model)

**Note:** All fields are optional with sensible defaults. Schema may evolve with portal UI.

**Minimal request (all defaults):**
```json
{}
```

**Full request with patient details:**
```json
{
  "patient_name": "John Smith",
  "practice_name": "BiteSoft Orthodontics",
  "patient_age": 16,
  "treatment_type": "clear aligners",
  "area_treated": "both",
  "duration_range": "4-6 months",
  "case_difficulty": "moderate",
  "monitoring_approach": "mixed",
  "attachments": "some",
  "whitening_included": true,
  "dentist_note": "Patient prefers discreet treatment",
  "audience": "patient",
  "tone": "reassuring"
}
```

**Output:** `TreatmentSummaryResponse`
```json
{
  "success": true,
  "document": {
    "title": "Your Clear Aligner Treatment Plan",
    "summary": "...",
    "key_points": ["...", "..."],
    "next_steps": ["...", "..."],
    "care_instructions": ["...", "..."]
  },
  "metadata": {
    "tokens_used": 450,
    "generation_time_ms": 1250,
    "audience": "patient",
    "tone": "reassuring"
  }
}
```

**Process Flow:**
1. Validate request schema
2. Extract user_id from Bearer token (or use dev default)
3. Call `generate_treatment_summary()` service
4. Log generation event to audit database
5. Return structured response with metadata

**Error Handling:**
- Invalid schema → 422 Unprocessable Entity
- OpenAI API failure → 500 Internal Server Error (logged to audit)
- Missing auth token → 401 Unauthorized (in production mode)

### Placeholder Endpoints

#### `POST /api/v1/generate-insurance-summary`
**Status:** Coming Soon  
**Returns:** `{"success": true, "message": "Module coming soon", "module": "insurance-summary"}`

#### `POST /api/v1/generate-progress-notes`
**Status:** Coming Soon  
**Returns:** `{"success": true, "message": "Module coming soon", "module": "progress-notes"}`

## Dependencies

### Internal
- `app.core.security` - Authentication dependency (`get_current_user`)
- `app.db.database` - Database session dependency (`get_session`)
- `app.db.audit` - Audit logging utility (`log_generation`)
- `app.schemas.treatment_summary` - Request/response models
- `app.schemas.placeholders` - Placeholder module schemas
- `app.services.openai_service` - AI generation service

### External
- `fastapi` - Web framework and routing
- `sqlalchemy.ext.asyncio.AsyncSession` - Async database sessions

## How It Works

### Request Lifecycle

```
Client Request
    ↓
FastAPI Router (routes.py)
    ↓
Dependency Injection:
  - get_current_user() → user_id
  - get_session() → db_session
    ↓
Service Layer:
  - generate_treatment_summary()
    ↓
Audit Logging:
  - log_generation() → SQLite
    ↓
Response Serialization
    ↓
Client Response
```

### Authentication Flow

```python
# Development Mode (no token)
user_id = "dev_user_001"

# Production Mode (with Bearer token)
Authorization: Bearer <token>
    ↓
get_current_user() validates JWT
    ↓
user_id = "user_abc123"
```

### Error Handling Pattern

```python
try:
    result = await generate_treatment_summary(request)
    await log_generation(status="success", ...)
    return success_response
except Exception as e:
    await log_generation(status="error", error_message=str(e))
    raise HTTPException(500, detail=f"Failed: {str(e)}")
```

## Usage Example

```python
from app.api.routes import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/v1")
```

## Testing

```bash
# Test with minimal request (all defaults)
curl -X POST "http://localhost:8000/api/v1/generate-treatment-summary" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token_123" \
  -d '{}'

# Test with full patient details
curl -X POST "http://localhost:8000/api/v1/generate-treatment-summary" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token_123" \
  -d '{
    "patient_name": "Jane Doe",
    "patient_age": 25,
    "treatment_type": "clear aligners",
    "area_treated": "both",
    "duration_range": "6-8 months",
    "case_difficulty": "simple",
    "monitoring_approach": "remote",
    "attachments": "none",
    "whitening_included": false,
    "audience": "patient",
    "tone": "concise"
  }'
```

## Future Enhancements

- Rate limiting per user
- Request caching for identical inputs
- Batch generation endpoints
- Webhook notifications for long-running generations
- API versioning strategy (v2, v3)
