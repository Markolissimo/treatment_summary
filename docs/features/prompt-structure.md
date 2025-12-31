# Prompt Structure & API Approach (v1)

## Overview

This document outlines the prompt engineering strategy and API design for the BiteSoft AI Treatment Summary Generator v1.

## System Prompt Architecture

### Core Components

The system prompt (`TREATMENT_SUMMARY_SYSTEM_PROMPT`) is structured in three layers:

#### 1. **Role Definition**
```
You are a professional orthodontic treatment summary writer...
```
- Establishes AI's expertise and purpose
- Sets professional tone baseline
- Defines output expectations

#### 2. **Hard Restrictions (Non-Negotiable)**

These guardrails are **NEVER violated** regardless of input:

| Restriction | Rationale | Example Violations |
|-------------|-----------|-------------------|
| **No Diagnosis** | Legal/compliance | "diagnose," "malocclusion," "disease," "pathology" |
| **No Guarantees** | Liability protection | "will fix," "guaranteed results," "perfect smile" |
| **No Financials** | Scope separation | "$5000," "insurance covers," "payment plan" |
| **No Legal Claims** | Liability protection | Insurance claims, legal statements |
| **No New Facts** | Input integrity | Do not infer or add clinical facts beyond inputs |
| **Fact Integrity** | Trust/accuracy | Clinical facts must remain constant across tones |

#### 3. **Patient-Facing Rules**

| Rule | Description |
|------|-------------|
| **No Jargon** | Use plain language suitable for laypeople |
| **Explanatory Only** | No directives or instructions (summaries explain, not instruct) |
| **Exclusions** | No mention of elastics, auxiliaries, or conditional appliances unless explicitly instructed |
| **Inclusions** | Extras like whitening framed as "included" only, not outcomes |

**Implementation:**
```python
# In prompts.py
TREATMENT_SUMMARY_SYSTEM_PROMPT = """
HARD RESTRICTIONS (NEVER VIOLATE):
1. NO DIAGNOSIS: Never use diagnostic or pathology language
2. NO GUARANTEES: Never promise outcomes (use "expected," "may," "typically")
3. NO FINANCIALS: Never mention pricing, costs, fees, or insurance claims
4. NO LEGAL CLAIMS: Never make legal or insurance-related statements
5. NO NEW FACTS: Do not infer or add clinical facts beyond provided inputs
6. FACT INTEGRITY: Clinical facts stay constant regardless of tone
"""
```

#### 4. **Adaptive Controls**

Dynamic parameters that adjust output style:

**Audience Adaptation:**
- `patient` → Friendly, accessible language
- `internal` → Clinical terminology, detailed notes

**Tone Adaptation:**
- `concise` → Short, direct, plain language
- `casual` → Warm, conversational, professional
- `reassuring` → Calm, confidence-building, expectation-setting
- `clinical` → Neutral, professional, suitable for records

**Important:** Facts must never change between tones — only language style.

## User Prompt Construction

### Template Structure

```python
def build_treatment_summary_user_prompt(request: TreatmentSummaryRequest) -> str:
    """
    Builds structured prompt from case data.
    Format: Markdown-style key-value pairs for clarity.
    """
    prompt_parts = [
        "Generate a treatment summary with the following case details:",
        "",
    ]
    
    # Patient context (if provided)
    if request.patient_name:
        prompt_parts.append(f"**Patient Name:** {request.patient_name}")
    if request.practice_name:
        prompt_parts.append(f"**Practice Name:** {request.practice_name}")
    if request.patient_age is not None:
        category = get_patient_category(request.patient_age)
        prompt_parts.append(f"**Patient Age:** {request.patient_age} ({category})")
    
    # Clinical data (always included with defaults)
    prompt_parts.extend([
        f"**Treatment Type:** {request.treatment_type.value}",
        f"**Area Treated:** {request.area_treated.value}",
        f"**Expected Duration:** {request.duration_range}",
        f"**Case Difficulty:** {request.case_difficulty.value}",
        f"**Monitoring Approach:** {request.monitoring_approach.value}",
        f"**Attachments:** {request.attachments.value}",
        f"**Whitening Included:** {'Yes' if request.whitening_included else 'No'}",
    ])
    
    # Optional dentist note
    if request.dentist_note:
        prompt_parts.append(f"**Dentist Note:** {request.dentist_note}")
    
    # Output controls
    prompt_parts.extend([
        "",
        f"**Target Audience:** {request.audience.value}",
        f"**Desired Tone:** {request.tone.value}",
        "",
        "Please generate the treatment summary following all guidelines and restrictions.",
    ])
    
    return "\n".join(prompt_parts)
```

### Example Prompts

**Minimal (all defaults):**
```
Generate a treatment summary with the following case details:

**Treatment Type:** clear aligners
**Area Treated:** both
**Expected Duration:** 4-6 months
**Case Difficulty:** moderate
**Monitoring Approach:** mixed
**Attachments:** some
**Whitening Included:** No

**Target Audience:** patient
**Desired Tone:** reassuring

Please generate the treatment summary following all guidelines and restrictions.
```

**With Patient Details:**
```
Generate a treatment summary with the following case details:

**Patient Name:** Sarah Johnson
**Practice Name:** BiteSoft Orthodontics
**Patient Age:** 16 (adolescent)
**Treatment Type:** clear aligners
**Area Treated:** both
**Expected Duration:** 6-8 months
**Case Difficulty:** simple
**Monitoring Approach:** remote
**Attachments:** none
**Whitening Included:** Yes
**Dentist Note:** Patient is highly motivated and tech-savvy

**Target Audience:** patient
**Desired Tone:** casual

Please generate the treatment summary following all guidelines and restrictions.
```

## API Design Philosophy

### 1. **JSON In → JSON Out**

Clean, predictable contract:

**Input:**
```json
{
  "patient_age": 25,
  "treatment_type": "clear aligners",
  "tone": "reassuring"
}
```

**Output:**
```json
{
  "success": true,
  "document": {
    "title": "Your Clear Aligner Treatment Plan",
    "summary": "..."
  },
  "metadata": {
    "tokens_used": 450,
    "generation_time_ms": 1250
  }
}
```

### 2. **Structured Outputs Enforcement**

Using OpenAI's beta structured outputs feature:

```python
response = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": TREATMENT_SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ],
    response_format=TreatmentSummaryOutput,  # Pydantic schema
    temperature=0.7,
    max_tokens=2000,
)

# Guaranteed to match schema - no parsing errors
output: TreatmentSummaryOutput = response.choices[0].message.parsed
```

**Benefits:**
- No JSON parsing errors
- No schema validation failures
- Type-safe output
- Reliable production use

### 3. **Flexible Schema with Defaults**

All fields optional to support evolving portal UI:

```python
class TreatmentSummaryRequest(BaseModel):
    treatment_type: Optional[TreatmentType] = Field(default=TreatmentType.CLEAR_ALIGNERS)
    area_treated: Optional[AreaTreated] = Field(default=AreaTreated.BOTH)
    # ... all fields have sensible defaults
```

**Rationale:**
- Portal UI may change during development
- Allows minimal requests: `{}`
- Reduces integration friction
- Backward compatible as fields are added

### 4. **Audit Trail**

Every generation logged to SQLite:

```python
await log_generation(
    session=session,
    user_id=user_id,
    document_type="treatment_summary",
    input_data=request.model_dump(),
    output_data=result.output.model_dump(),
    tokens_used=result.tokens_used,
    generation_time_ms=result.generation_time_ms,
    status="success",
)
```

**Use Cases:**
- Compliance and legal protection
- Debugging and error reproduction
- Usage analytics and billing
- Performance monitoring

## Age Threshold Logic (CDT)

### Implementation

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

### Usage in Prompts

```
**Patient Age:** 16 (adolescent)
```

This allows GPT-4 to:
- Adjust language appropriateness
- Consider developmental factors
- Tailor expectations and timelines
- Personalize care instructions

## Output Structure

### Schema Definition

```python
class TreatmentSummaryOutput(BaseModel):
    title: str                          # Brief, engaging title
    summary: str                        # Main narrative (200-400 words)
```

### Design Rationale

| Field | Purpose | Portal Use |
|-------|---------|------------|
| `title` | Email subject line | Email header |
| `summary` | Main body text | Email body |

**Portal Integration:**
Portal team can:
- Insert into email templates
- Display in patient dashboard
- Format with custom CSS
- Add send buttons and triggers

## v1 Scope Boundaries

### ✅ In Scope (AI Team)

1. **AI Logic**
   - Prompt engineering
   - Guardrail enforcement
   - Tone/audience adaptation
   - Age-based personalization

2. **API Layer**
   - FastAPI endpoints
   - Request validation
   - Response formatting
   - Error handling

3. **Data Layer**
   - Audit logging
   - Metadata tracking
   - Database schema

4. **Deployment**
   - Docker containerization
   - Local server setup
   - API documentation

### ❌ Out of Scope (Portal Team)

1. **Email System**
   - Send triggers
   - Email templates (HTML/CSS)
   - SMTP integration
   - Delivery tracking

2. **UI Components**
   - Send buttons
   - Form inputs
   - Patient dashboards
   - Admin panels

3. **Portal Integration**
   - Authentication flow
   - User management
   - Frontend wiring
   - State management

## Performance Targets

### Latency
- **Target:** < 3 seconds per generation
- **Typical:** 1-2 seconds with GPT-4o
- **Optimization:** Consider caching for identical requests

### Cost
- **Typical:** 300-600 tokens per summary
- **Cost:** ~$0.01-0.03 per summary (GPT-4o pricing)
- **Budget:** Monitor via audit logs

### Reliability
- **Target:** 99.9% success rate
- **Error Handling:** Graceful degradation
- **Retry Logic:** Future enhancement

## Testing Strategy

### Unit Tests
```python
@pytest.mark.asyncio
async def test_generate_treatment_summary():
    request = TreatmentSummaryRequest(
        treatment_type="clear aligners",
        patient_age=16,
        tone="casual"
    )
    result = await generate_treatment_summary(request)
    
    assert result.output.title
    assert "adolescent" in str(result.output)  # Age category used
    assert result.tokens_used > 0
```

### Integration Tests
- Test full API flow
- Verify audit logging
- Check error handling
- Validate schema enforcement

### Manual Testing
- Use Streamlit demo
- Test edge cases
- Verify tone variations
- Check guardrail compliance

## Future Enhancements

### v1.1 (Quick Wins)
1. Multi-language support
2. Additional tone presets
3. Reading level control
4. Summary length options

### v2.0 (Advanced)
1. Before/after predictions
2. FAQ generation
3. Treatment timeline descriptions
4. Comparison mode (aligners vs braces)
5. Risk/benefit analysis

### v3.0 (AI-Powered Features)
1. Voice/video script generation
2. Sentiment analysis
3. Smart tone recommendations
4. A/B testing framework
5. Batch processing

## Questions & Clarifications

**Q: Should we include patient photos/scans?**  
A: Out of scope for v1. Portal team handles media.

**Q: What about multi-step treatment plans?**  
A: Future enhancement. v1 focuses on single treatment summaries.

**Q: How do we handle errors in production?**  
A: All errors logged to audit table. Portal team decides retry logic.

**Q: Can we customize prompts per practice?**  
A: Future enhancement. v1 uses single prompt template.

## Ready for Implementation

This prompt structure and API approach provides:
- ✅ Clear separation of concerns (AI vs Portal)
- ✅ Flexible, evolvable schema
- ✅ Strong guardrails and compliance
- ✅ Production-ready architecture
- ✅ Comprehensive audit trail
- ✅ Scalable foundation for future features

**Next Steps:**
1. Review and approve prompt structure
2. Test with sample cases
3. Validate output quality
4. Begin portal integration planning
