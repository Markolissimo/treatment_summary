# Schemas Module

## Purpose

This module contains all Pydantic models that define the structure, validation rules, and documentation for API requests and responses. It serves as the data contract layer between clients and the API.

## Contents

- **`treatment_summary.py`** - Treatment summary request/response schemas
- **`placeholders.py`** - Placeholder schemas for future modules

## Files Overview

### `treatment_summary.py`

**Purpose:** Strict type definitions and validation for treatment summary generation.

#### Enums (Controlled Vocabularies)

```python
class TreatmentType(str, Enum):
    CLEAR_ALIGNERS = "clear aligners"
    TRADITIONAL_BRACES = "traditional braces"
    LINGUAL_BRACES = "lingual braces"
    RETAINERS = "retainers"

class AreaTreated(str, Enum):
    UPPER = "upper"
    LOWER = "lower"
    BOTH = "both"

class CaseDifficulty(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class MonitoringApproach(str, Enum):
    REMOTE = "remote"
    MIXED = "mixed"
    IN_CLINIC = "in-clinic"

class Attachments(str, Enum):
    NONE = "none"
    SOME = "some"
    EXTENSIVE = "extensive"

class Audience(str, Enum):
    PATIENT = "patient"
    INTERNAL = "internal"

class Tone(str, Enum):
    CONCISE = "concise"
    CASUAL = "casual"
    REASSURING = "reassuring"
    CLINICAL = "clinical"
```

**Why Enums?**
- Prevents invalid values at API boundary
- Auto-generates OpenAPI documentation with allowed values
- Type-safe in Python code
- Self-documenting

#### Input Schema: `TreatmentSummaryRequest`

**Purpose:** Validates incoming case data from clients.

**Schema Philosophy:** All fields are **optional with sensible defaults**. This contract may evolve as the portal UI is finalized.

**Fields:**

| Field | Type | Required | Default | Validation | Example |
|-------|------|----------|---------|------------|---------|
| `treatment_type` | `TreatmentType` | ❌ | `"clear aligners"` | Enum | `"clear aligners"` |
| `area_treated` | `AreaTreated` | ❌ | `"both"` | Enum | `"both"` |
| `duration_range` | `str` | ❌ | `"4-6 months"` | 1-50 chars | `"4-6 months"` |
| `case_difficulty` | `CaseDifficulty` | ❌ | `"moderate"` | Enum | `"moderate"` |
| `monitoring_approach` | `MonitoringApproach` | ❌ | `"mixed"` | Enum | `"mixed"` |
| `attachments` | `Attachments` | ❌ | `"some"` | Enum | `"some"` |
| `whitening_included` | `bool` | ❌ | `false` | Boolean | `true` |
| `dentist_note` | `str` | ❌ | `None` | Max 500 chars | `"Patient prefers..."` |
| `audience` | `Audience` | ❌ | `"patient"` | Enum | `"patient"` |
| `tone` | `Tone` | ❌ | `"reassuring"` | Enum | `"reassuring"` |
| `patient_name` | `str` | ❌ | `None` | Max 200 chars | `"John Smith"` |
| `practice_name` | `str` | ❌ | `None` | Max 200 chars | `"BiteSoft Ortho"` |
| `patient_age` | `int` | ❌ | `None` | 0-120 | `16` |

**Validation Rules:**
- All fields are optional with defaults applied if missing
- Enums reject invalid values
- `duration_range` must be 1-50 characters
- `dentist_note` max 500 characters
- `patient_name` and `practice_name` max 200 characters
- `patient_age` used for CDT logic: adolescent (<18) vs adult (≥18)

**Patient Details (for Portal Integration):**
- `patient_name` - Patient name for personalization (portal team will use in their email templates)
- `practice_name` - Practice name (portal team will use in their email templates)
- `patient_age` - Patient age for CDT logic (adolescent <18, adult ≥18)

**Minimal Example (all defaults):**
```json
{}
```

**Full Example with Patient Details:**
```json
{
  "patient_name": "John Smith",
  "practice_name": "BiteSoft Orthodontics",
  "patient_age": 16,
  "treatment_type": "clear aligners",
  "area_treated": "both",
  "duration_range": "6-8 months",
  "case_difficulty": "simple",
  "monitoring_approach": "remote",
  "attachments": "none",
  "whitening_included": false,
  "dentist_note": "Patient is highly motivated",
  "audience": "patient",
  "tone": "casual"
}
```

#### Output Schema: `TreatmentSummaryOutput`

**Purpose:** Defines the structure GPT-4 must return (enforced via Structured Outputs).

**Fields:**

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `title` | `str` | ✅ | - | Brief title for the summary |
| `summary` | `str` | ✅ | - | Main treatment summary text |
| `key_points` | `list[str]` | ✅ | 1-10 items | Key points about treatment |
| `next_steps` | `list[str]` | ✅ | 1-5 items | Next steps for patient/staff |
| `care_instructions` | `list[str]` | ❌ | - | Care instructions (patient-facing) |

**How It Works:**
```python
# OpenAI Structured Outputs enforces this schema
response = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[...],
    response_format=TreatmentSummaryOutput,  # ← Schema enforcement
)

# Response is guaranteed to match the schema
parsed: TreatmentSummaryOutput = response.choices[0].message.parsed
```

**Example Output:**
```json
{
  "title": "Your Clear Aligner Treatment Journey",
  "summary": "You'll be using clear aligners to gently guide your teeth...",
  "key_points": [
    "Treatment duration: 6-8 months",
    "Remote monitoring with occasional check-ins",
    "No attachments needed for this case"
  ],
  "next_steps": [
    "Wear aligners 22 hours per day",
    "Upload progress photos weekly via app",
    "Schedule first check-in in 4 weeks"
  ],
  "care_instructions": [
    "Remove aligners when eating or drinking",
    "Clean aligners daily with soft brush",
    "Store in provided case when not wearing"
  ]
}
```

#### Response Wrapper: `TreatmentSummaryResponse`

**Purpose:** API response envelope with metadata.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Always `true` for successful responses |
| `document` | `TreatmentSummaryOutput` | The generated document |
| `metadata` | `dict` | Generation metadata (tokens, time, etc.) |

**Example:**
```json
{
  "success": true,
  "document": {
    "title": "...",
    "summary": "...",
    "key_points": ["...", "..."],
    "next_steps": ["...", "..."]
  },
  "metadata": {
    "tokens_used": 450,
    "generation_time_ms": 1250,
    "audience": "patient",
    "tone": "reassuring"
  }
}
```

---

### `placeholders.py`

**Purpose:** Stub schemas for future modules (Insurance Summary, Progress Notes).

#### `InsuranceSummaryRequest`
```python
class InsuranceSummaryRequest(BaseModel):
    patient_id: str
    treatment_code: Optional[str] = None
    # Additional fields to be defined in Module 2
```

#### `InsuranceSummaryResponse`
```python
class InsuranceSummaryResponse(BaseModel):
    success: bool = True
    message: str = "Module coming soon"
    module: str = "insurance-summary"
```

#### `ProgressNotesRequest`
```python
class ProgressNotesRequest(BaseModel):
    patient_id: str
    visit_date: Optional[str] = None
    # Additional fields to be defined in Module 3
```

#### `ProgressNotesResponse`
```python
class ProgressNotesResponse(BaseModel):
    success: bool = True
    message: str = "Module coming soon"
    module: str = "progress-notes"
```

## Dependencies

### Internal
- None (this is a pure data layer)

### External
- `pydantic` - Data validation and serialization
- `enum.Enum` - Enumeration base class

## How Validation Works

```
Client sends JSON
    ↓
FastAPI receives request
    ↓
Pydantic validates against TreatmentSummaryRequest
    ↓
✅ Valid: Proceed to route handler
❌ Invalid: Return 422 with validation errors
```

**Example Validation Error:**
```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["body", "tone"],
      "msg": "Input should be 'concise', 'casual', 'reassuring' or 'clinical'",
      "input": "friendly"
    }
  ]
}
```

## OpenAPI Documentation

Pydantic models automatically generate OpenAPI (Swagger) documentation:

- **Field descriptions** → API docs
- **Validation rules** → Schema constraints
- **Examples** → Sample requests in Swagger UI
- **Enums** → Dropdown lists in Swagger UI

## Usage Examples

### In Routes
```python
from app.schemas.treatment_summary import (
    TreatmentSummaryRequest,
    TreatmentSummaryResponse,
)

@router.post("/generate", response_model=TreatmentSummaryResponse)
async def generate(request: TreatmentSummaryRequest):
    # request is validated and typed
    print(request.treatment_type)  # Type: TreatmentType enum
    print(request.tone)            # Type: Tone enum
```

### In Services
```python
from app.schemas.treatment_summary import TreatmentSummaryOutput

response = await client.beta.chat.completions.parse(
    response_format=TreatmentSummaryOutput,  # Enforce schema
)

output: TreatmentSummaryOutput = response.choices[0].message.parsed
```

### Serialization
```python
# Pydantic model → dict
request_dict = request.model_dump()

# Pydantic model → JSON string
request_json = request.model_dump_json()

# dict → Pydantic model
request = TreatmentSummaryRequest(**data)
```

## Best Practices

1. **Use Enums for controlled vocabularies** - Prevents invalid values
2. **Add field descriptions** - Auto-generates API documentation
3. **Set validation constraints** - `min_length`, `max_length`, `ge`, `le`
4. **Provide examples** - Helps API consumers understand expected format
5. **Keep schemas flat** - Avoid deep nesting for simplicity
6. **Version schemas** - Use separate models for v1, v2, etc.

## Future Enhancements

- Add `TreatmentSummaryRequestV2` with additional fields
- Implement schema versioning strategy
- Add custom validators for complex business rules
- Create shared base schemas for common fields
