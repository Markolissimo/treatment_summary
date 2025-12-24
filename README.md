# BiteSoft AI Document Generation System

AI service for generating patient-friendly orthodontic treatment summaries and clinical documents.

## What This Feature Is

The Treatment Summary AI generates a **clear, patient-friendly explanation** of an aligner treatment plan using structured inputs that are provided or approved by the dentist. It is designed to support:
- **Patient communication** within the provider portal
- **Internal documentation** for dentist/staff records

**The dentist remains the clinical decision-maker at all times.**

## What This Feature Is NOT

- ❌ It does **NOT** diagnose
- ❌ It does **NOT** decide treatment
- ❌ It does **NOT** generate staging or clinical plans
- ❌ It does **NOT** guarantee outcomes
- ❌ It does **NOT** infer details beyond the provided inputs
- ❌ It does **NOT** provide pricing or financial information

## Features

- **Treatment Summary Generation** - Generate professional treatment summaries from structured case data
- **OpenAI GPT-4 Integration** - Uses structured outputs for reliable JSON responses
- **Flexible Schema** - Optional fields with sensible defaults; contract may evolve with portal UI
- **Patient Personalization** - Supports patient names and practice info for portal integration
- **Age-Based CDT Logic** - Adolescent (<18) vs Adult (≥18) categorization
- **Audit Logging** - SQLite-based logging of all generation events
- **Strict Guardrails** - No diagnosis terms, no guarantees, no financials
- **Docker Ready** - Containerized FastAPI application for easy deployment

## v1 Scope

**What's Included:**
✅ AI logic for generating treatment summary text
✅ FastAPI endpoints that return editable JSON output
✅ Structured input validation and defaults
✅ Audit logging and metadata tracking
✅ Docker deployment configuration

**What's NOT Included (Portal Team Handles):**
❌ Email automation or send triggers
❌ UI components or send buttons
❌ Email service integration
❌ Frontend/portal wiring

**Note:** The AI-generated summary text will be inserted into the portal's existing/future email flow. Email functionality is handled separately by the portal team.

## Project Structure

```
app/
├── api/           # Endpoint definitions
│   └── routes.py
├── core/          # Configuration, prompts, security
│   ├── config.py
│   ├── prompts.py
│   └── security.py
├── db/            # Database models and utilities
│   ├── audit.py
│   ├── database.py
│   └── models.py
├── schemas/       # Pydantic models
│   ├── treatment_summary.py
│   └── placeholders.py
├── services/      # Business logic and AI orchestration
│   └── openai_service.py
└── main.py        # FastAPI application entry point
```

## Deployment (v1)

### Current State
- Portal is running on local/self-hosted server (not AWS yet)
- AI service runs as Dockerized FastAPI application
- Portal calls API locally during development
- Future: Deploy to AWS (ECS/Lambda) when infrastructure is ready

### Docker Deployment (Recommended)

1. **Build the Docker image**
   ```bash
   docker build -t bitesoft-ai .
   ```

2. **Run the container**
   ```bash
   docker run -d -p 8000:8000 --env-file .env bitesoft-ai
   ```

3. **Access API docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development Setup

1. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # Linux/macOS
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access API docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

| Endpoint | Status | Description |
|----------|--------|-------------|
| `POST /api/v1/generate-treatment-summary` | ✅ Active | Generate treatment summary |
| `POST /api/v1/generate-insurance-summary` | 🚧 Placeholder | Coming soon |
| `POST /api/v1/generate-progress-notes` | 🚧 Placeholder | Coming soon |

## Schema Contract (v1)

### Input Schema
The JSON schema is **flexible and may evolve** as the portal UI is finalized. All fields are optional with sensible defaults:

**Clinical Data:**
- `treatment_type` - Type of treatment (default: "clear aligners")
- `area_treated` - Area treated (default: "both")
- `duration_range` - Expected duration (default: "4-6 months")
- `case_difficulty` - Complexity level (default: "moderate")
- `monitoring_approach` - Monitoring method (default: "mixed")
- `attachments` - Attachment usage (default: "some")
- `whitening_included` - Whitening included (default: false)
- `dentist_note` - Optional dentist note

**Context Controls:**
- `audience` - Target audience: patient/internal (default: "patient")
- `tone` - Desired tone: concise/casual/reassuring/clinical (default: "reassuring")

**Patient Details:**
- `patient_name` - Patient name for personalization (portal will use in email templates)
- `practice_name` - Practice name (portal will use in email templates)
- `patient_age` - Patient age for CDT logic (adolescent <18, adult ≥18)

### Example Request

**Minimal request (all defaults):**
```bash
curl -X POST "http://localhost:8000/api/v1/generate-treatment-summary" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Full request with patient details:**
```bash
curl -X POST "http://localhost:8000/api/v1/generate-treatment-summary" \
  -H "Content-Type: application/json" \
  -d '{
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
    "audience": "patient",
    "tone": "reassuring"
  }'
```

## Hard Restrictions (AI Guardrails)

1. **No Diagnosis** - Never uses diagnostic or pathology language (e.g., "diagnose," "malocclusion," "disease")
2. **No Guarantees** - Never promises outcomes or specific results
3. **No Financials** - Never includes pricing, payment amounts, costs, fees, or insurance claims
4. **No Legal Claims** - Never makes legal or insurance-related statements
5. **No New Facts** - Does not infer or add clinical facts beyond provided inputs
6. **Fact Integrity** - Clinical facts remain constant regardless of tone

### Patient-Facing Rules
- **No Jargon** - Plain language suitable for laypeople
- **Explanatory Only** - No directives or instructions (summaries explain, not instruct)
- **Exclusions** - No mention of elastics, auxiliaries, or conditional appliances unless explicitly instructed
- **Inclusions** - Extras like whitening framed as "included" only, not outcomes

## Audience & Tone Controls

### Audience
- **Patient** - Patient-facing summaries (plain language, no jargon)
- **Internal** - Dentist/staff records (clinical, professional)

### Tone Options
- **Concise** - Short, direct, plain language
- **Casual** - Warm, conversational, professional
- **Reassuring** - Calm, confidence-building, expectation-setting
- **Clinical** - Neutral, professional, suitable for records

**Important:** Facts must never change between tones — only language style.

## Example Treatment Summaries

### Patient | Reassuring
> Based on your assessment, this is a mild alignment case that can be treated using clear aligners across both the upper and lower teeth.
> Treatment is expected to take approximately 4–6 months, with most progress monitored remotely to reduce the need for frequent in-office visits.
> This treatment also includes whitening as part of your overall smile plan.

### Patient | Concise
> This treatment uses clear aligners to straighten both upper and lower teeth.
> Estimated treatment time is 4–6 months, with progress primarily monitored remotely.
> Whitening is included as part of your treatment package.

### Patient | Casual
> We'll be using clear aligners to gently straighten your teeth over about 4–6 months.
> Most of your progress will be checked remotely, with in-clinic visits only if needed.
> Whitening is included as part of your overall treatment.

### Internal | Clinical
> Moderate aligner case involving both arches. Estimated duration 6–9 months.
> Mixed monitoring approach planned with attachments required. Whitening included.

## Age Threshold Logic (CDT)

- **Adolescent:** Under 18 years old
- **Adult:** 18 years and over
- Can be refined in future versions if needed

## Optional Demo Component

**Streamlit Prototype:**
A separate Streamlit demo app (`streamlit_demo.py`) is included for validation and demonstration purposes, but it is **not mandatory** for production. The core API works independently.

**To run the demo:**
```bash
# Install demo dependencies (optional)
pip install -r requirements-demo.txt

# Start FastAPI server in one terminal
uvicorn app.main:app --reload

# Start Streamlit demo in another terminal
streamlit run streamlit_demo.py
```

**Demo Features:**
- Interactive UI for testing all input parameters
- Real-time API calls to local FastAPI server
- JSON response viewer and download
- API health check
- Visual demonstration of AI capabilities

## Next Steps (Post v1)

- Portal integration testing (portal team handles email UI)
- Insurance module extension
- AWS deployment (ECS/Lambda)
- Progress notes module

## Feature Enhancement Ideas

### Immediate Enhancements (v1.1+)
1. **Multi-language Support** - Generate summaries in Spanish, French, etc.
2. **Tone Presets** - Add "motivational," "technical," "simplified" tones
3. **Reading Level Control** - Adjust complexity (Grade 6, Grade 10, Professional)
4. **Summary Length Options** - Short (100 words), Medium (250 words), Detailed (500+ words)
5. **Custom Branding** - Include practice-specific messaging/taglines

### Advanced Features (v2+)
6. **Before/After Predictions** - AI-generated treatment outcome descriptions
7. **FAQ Generation** - Auto-generate common patient questions and answers
8. **Treatment Timeline** - Visual timeline description ("Week 1-4: Initial alignment...")
9. **Comparison Mode** - "Why clear aligners vs braces for your case"
10. **Risk/Benefit Analysis** - Balanced overview of treatment considerations
11. **Post-Treatment Care Plans** - Retention phase guidance
12. **Patient Education Content** - Bite science, oral health tips
13. **Voice/Video Script Generation** - Scripts for video explanations
14. **Multi-format Export** - PDF, HTML, plain text variations
15. **A/B Testing Framework** - Test different prompt strategies
16. **Sentiment Analysis** - Ensure positive, encouraging tone
17. **Compliance Checking** - Auto-verify no prohibited terms used
18. **Template Library** - Pre-built templates for common scenarios
19. **Smart Suggestions** - AI recommends best tone/audience based on case
20. **Batch Processing** - Generate summaries for multiple patients at once
