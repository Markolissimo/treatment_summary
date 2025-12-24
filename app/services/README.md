# Services Module

## Purpose

This module contains the business logic layer that orchestrates AI generation, external API calls, and data transformations. It isolates complex operations from the API layer, making the codebase more maintainable and testable.

## Contents

- **`openai_service.py`** - OpenAI GPT-4 integration with structured outputs

## Files Overview

### `openai_service.py`

**Purpose:** Wrapper for OpenAI API calls with structured output enforcement and prompt building.

---

## Key Components

### 1. `GenerationResult` Model

**Purpose:** Internal data structure for AI generation results.

```python
class GenerationResult(BaseModel):
    output: TreatmentSummaryOutput      # The structured document
    tokens_used: int                     # Total tokens consumed
    generation_time_ms: int              # Time taken in milliseconds
```

**Why?** Separates the AI output from metadata, making it easier to log and track performance.

---

### 2. `build_treatment_summary_user_prompt()`

**Purpose:** Constructs the user prompt from structured case data.

**Input:** `TreatmentSummaryRequest`

**Output:** Formatted string prompt

**How It Works:**
```python
def build_treatment_summary_user_prompt(request: TreatmentSummaryRequest) -> str:
    prompt_parts = [
        "Generate a treatment summary with the following case details:",
        "",
    ]
    
    # Add patient details if provided
    if request.patient_name:
        prompt_parts.append(f"**Patient Name:** {request.patient_name}")
    if request.practice_name:
        prompt_parts.append(f"**Practice Name:** {request.practice_name}")
    if request.patient_age is not None:
        category = get_patient_category(request.patient_age)
        prompt_parts.append(f"**Patient Age:** {request.patient_age} ({category})")
    
    prompt_parts.extend([
        f"**Treatment Type:** {request.treatment_type.value}",
        f"**Area Treated:** {request.area_treated.value}",
        f"**Expected Duration:** {request.duration_range}",
        # ... more fields
        "",
        f"**Target Audience:** {request.audience.value}",
        f"**Desired Tone:** {request.tone.value}",
    ])
    return "\n".join(prompt_parts)
```

**Example Output (with patient details):**
```
Generate a treatment summary with the following case details:

**Patient Name:** John Smith
**Practice Name:** BiteSoft Orthodontics
**Patient Age:** 16 (adolescent)
**Treatment Type:** clear aligners
**Area Treated:** both
**Expected Duration:** 6-8 months
**Case Difficulty:** moderate
**Monitoring Approach:** mixed
**Attachments:** some
**Whitening Included:** Yes
**Dentist Note:** Patient is highly motivated

**Target Audience:** patient
**Desired Tone:** reassuring

Please generate the treatment summary following all guidelines and restrictions.
```

**Why Structured Prompts?**
- Consistent format for GPT-4
- Easy to debug and modify
- Clear separation of data fields
- Readable for humans reviewing logs

---

### 3. `generate_treatment_summary()`

**Purpose:** Main function that calls OpenAI API with structured outputs.

**Signature:**
```python
async def generate_treatment_summary(
    request: TreatmentSummaryRequest,
    api_key: Optional[str] = None,
) -> GenerationResult
```

**Parameters:**
- `request` - Validated case data
- `api_key` - Optional API key override (uses settings if not provided)

**Returns:** `GenerationResult` with output and metadata

**How It Works:**

```python
# 1. Initialize OpenAI client
client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)

# 2. Build user prompt from case data
user_prompt = build_treatment_summary_user_prompt(request)

# 3. Start timer
start_time = time.time()

# 4. Call OpenAI with structured outputs
response = await client.beta.chat.completions.parse(
    model=settings.openai_model,  # "gpt-4o"
    messages=[
        {"role": "system", "content": TREATMENT_SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ],
    response_format=TreatmentSummaryOutput,  # ← Enforces schema
    temperature=0.7,
    max_tokens=2000,
)

# 5. Calculate generation time
end_time = time.time()
generation_time_ms = int((end_time - start_time) * 1000)

# 6. Extract parsed output (guaranteed to match schema)
parsed_output = response.choices[0].message.parsed

# 7. Extract token usage
tokens_used = response.usage.total_tokens if response.usage else 0

# 8. Return result with metadata
return GenerationResult(
    output=parsed_output,
    tokens_used=tokens_used,
    generation_time_ms=generation_time_ms,
)
```

---

## OpenAI Structured Outputs

### What Are Structured Outputs?

OpenAI's Structured Outputs feature (beta) forces GPT-4 to return JSON that **exactly matches** a Pydantic schema. This eliminates:
- JSON parsing errors
- Missing required fields
- Type mismatches
- Schema validation failures

### How It Works

```python
# Define the schema
class TreatmentSummaryOutput(BaseModel):
    title: str
    summary: str
    key_points: list[str]
    next_steps: list[str]

# Pass schema to OpenAI
response = await client.beta.chat.completions.parse(
    response_format=TreatmentSummaryOutput,  # ← Magic happens here
)

# Output is guaranteed to match
output: TreatmentSummaryOutput = response.choices[0].message.parsed
```

### Benefits

1. **Type Safety** - No manual JSON parsing
2. **Reliability** - No schema validation errors
3. **Simplicity** - Direct Pydantic object access
4. **Performance** - No retry loops for malformed JSON

---

## Data Flow

```
TreatmentSummaryRequest (from API)
    ↓
build_treatment_summary_user_prompt()
    ↓
User prompt string
    ↓
OpenAI API call with:
  - System prompt (guardrails)
  - User prompt (case data)
  - Response format (schema)
    ↓
GPT-4 generates structured JSON
    ↓
Parsed into TreatmentSummaryOutput
    ↓
Wrapped in GenerationResult
    ↓
Returned to API layer
```

## Error Handling

```python
try:
    result = await generate_treatment_summary(request)
except openai.APIError as e:
    # OpenAI API error (rate limit, invalid key, etc.)
    raise HTTPException(500, f"OpenAI API error: {str(e)}")
except openai.APIConnectionError as e:
    # Network error
    raise HTTPException(503, "Failed to connect to OpenAI")
except Exception as e:
    # Unexpected error
    raise HTTPException(500, f"Generation failed: {str(e)}")
```

## Dependencies

### Internal
- `app.core.config` - Settings (API key, model name)
- `app.core.prompts` - System prompts with guardrails
- `app.core.utils` - Utility functions (age threshold logic)
- `app.schemas.treatment_summary` - Input/output schemas

### External
- `openai` - OpenAI Python SDK (async client)
- `pydantic` - Data validation
- `time` - Performance measurement

## Configuration

### Model Selection
```python
# In .env
OPENAI_MODEL=gpt-4o

# Or override in code
result = await generate_treatment_summary(
    request,
    api_key="sk-custom-key"
)
```

### Generation Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `temperature` | `0.7` | Balance creativity and consistency |
| `max_tokens` | `2000` | Limit response length |
| `response_format` | `TreatmentSummaryOutput` | Enforce schema |

**Temperature Guide:**
- `0.0-0.3` - Very consistent, less creative
- `0.4-0.7` - Balanced (recommended)
- `0.8-1.0` - More creative, less predictable

## Usage Examples

### Basic Usage
```python
from app.services.openai_service import generate_treatment_summary
from app.schemas.treatment_summary import TreatmentSummaryRequest

request = TreatmentSummaryRequest(
    treatment_type="clear aligners",
    area_treated="both",
    duration_range="6-8 months",
    case_difficulty="simple",
    monitoring_approach="remote",
    attachments="none",
    whitening_included=False,
    audience="patient",
    tone="casual",
)

result = await generate_treatment_summary(request)

print(result.output.title)           # "Your Clear Aligner Journey"
print(result.tokens_used)            # 450
print(result.generation_time_ms)     # 1250
```

### With Custom API Key
```python
result = await generate_treatment_summary(
    request,
    api_key="sk-custom-key-for-testing"
)
```

### In API Route
```python
@router.post("/generate-treatment-summary")
async def create_treatment_summary(request: TreatmentSummaryRequest):
    result = await generate_treatment_summary(request)
    
    # Log to audit database
    await log_generation(
        tokens_used=result.tokens_used,
        generation_time_ms=result.generation_time_ms,
        generated_text=result.output.model_dump(),
    )
    
    return TreatmentSummaryResponse(
        success=True,
        document=result.output,
        metadata={
            "tokens_used": result.tokens_used,
            "generation_time_ms": result.generation_time_ms,
        }
    )
```

## Performance Metrics

Typical performance (GPT-4o):
- **Tokens:** 300-600 tokens per summary
- **Time:** 1-3 seconds per generation
- **Cost:** ~$0.01-0.03 per summary (at current pricing)

## Testing

```python
import pytest
from app.services.openai_service import generate_treatment_summary

@pytest.mark.asyncio
async def test_generate_treatment_summary():
    request = TreatmentSummaryRequest(
        treatment_type="clear aligners",
        area_treated="both",
        duration_range="6 months",
        case_difficulty="simple",
        monitoring_approach="remote",
        attachments="none",
        whitening_included=False,
        audience="patient",
        tone="concise",
    )
    
    result = await generate_treatment_summary(request)
    
    assert result.output.title
    assert result.output.summary
    assert len(result.output.key_points) >= 1
    assert result.tokens_used > 0
    assert result.generation_time_ms > 0
```

## Future Enhancements

- **Caching:** Cache identical requests to reduce API calls
- **Retry Logic:** Exponential backoff for transient failures
- **Streaming:** Stream responses for real-time UX
- **Batch Processing:** Generate multiple summaries in parallel
- **Model Fallback:** Try GPT-4o-mini if GPT-4o fails
- **Prompt Versioning:** A/B test different prompt variations
