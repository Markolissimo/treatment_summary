# Insurance Summary Generator

## Overview

The Insurance Summary Generator is an administrative support tool for dentists and practice staff. It generates clear, conservative summaries to assist with insurance documentation.

**Important**: This is NOT:
- A diagnosis
- A guarantee of coverage or reimbursement
- A claim submission
- A statement of medical necessity

## Purpose

- Reduce admin time (saves 10-20 minutes per case)
- Standardize insurance-facing language
- Minimize denials caused by wording issues
- Remain legally conservative and dentist-controlled
- Produce PMS-ready documentation

## API Endpoint

### POST `/api/v1/generate-insurance-summary`

Generate an insurance summary document for administrative support.

#### Request Schema

```json
{
  "tier": "express_mild | moderate | complex",
  "arches": "upper | lower | both",
  "age_group": "adolescent | adult",
  "retainers_included": true,
  "diagnostic_assets": {
    "intraoral_photos": true,
    "panoramic_xray": true,
    "fmx": false
  },
  "monitoring_approach": "remote | mixed | in-clinic",
  "notes": "optional dentist/admin note",
  "is_regeneration": false,
  "previous_version_uuid": null
}
```

#### Response Schema

```json
{
  "success": true,
  "document": {
    "insurance_summary": "The patient has been assessed for orthodontic treatment...",
    "disclaimer": "This document is provided for administrative support only..."
  },
  "cdt_codes": [
    {
      "code": "D8090",
      "description": "Comprehensive orthodontic treatment (adult)",
      "category": "primary"
    },
    {
      "code": "D0350",
      "description": "Oral/facial photographic images",
      "category": "diagnostic"
    }
  ],
  "metadata": {
    "tokens_used": 450,
    "generation_time_ms": 2500,
    "tier": "moderate",
    "age_group": "adult",
    "seed": 42,
    "document_version": "1.0",
    "cdt_notes": "Comprehensive orthodontic treatment, adult (moderate tier); Retainers bundled"
  },
  "uuid": "generation-uuid",
  "is_regenerated": false,
  "previous_version_uuid": null,
  "seed": 42
}
```

## CDT Logic Rules (v1)

### Primary Orthodontic Code

| Tier | Age Group | CDT Code | Description |
|------|-----------|----------|-------------|
| Express/Mild | Any | D8010 | Limited orthodontic treatment |
| Moderate | Adolescent | D8080 | Comprehensive orthodontic treatment (adolescent) |
| Moderate | Adult | D8090 | Comprehensive orthodontic treatment (adult) |
| Complex | Adolescent | D8080 | Comprehensive orthodontic treatment (adolescent) |
| Complex | Adult | D8090 | Comprehensive orthodontic treatment (adult) |

### Diagnostic Codes (only if explicitly flagged)

| Asset | CDT Code | Description |
|-------|----------|-------------|
| Intraoral Photos | D0350 | Oral/facial photographic images |
| Panoramic X-ray | D0330 | Panoramic radiographic image |
| FMX | D0210 | Intraoral - complete series of radiographic images |

### Retainers

- If `retainers_included = true` → bundled (no separate code)
- D8680 is NOT included unless explicitly billed separately (out of scope for v1)

**No guessing**: If an asset is not flagged → it's not included in CDT codes.

## Output Content Rules

### The summary MUST:
- Describe treatment in neutral terms
- Explain why orthodontic treatment is being proposed
- List CDT codes as supporting references only
- State that coverage depends on the payer
- Include retention information if retainers are included

### The summary MUST NOT:
- Promise coverage
- State medical necessity
- Include diagnosis language
- Include pricing or benefit estimation

## Required Disclaimer

Every insurance summary includes this disclaimer:

> This document is provided for administrative support only. Coverage and reimbursement are determined solely by the patient's insurance provider. Submission of this information does not guarantee payment or approval.

## Example Outputs

### Example 1 — Moderate Case (Adult)

**Input**: tier=moderate, arches=both, age_group=adult, retainers_included=true, diagnostic_assets={intraoral_photos=true, panoramic_xray=true}

**Output**:
```
Insurance Summary (Draft – Admin Use Only)

The patient has been assessed for orthodontic treatment using clear aligner therapy to address dental alignment concerns. The proposed treatment involves both upper and lower arches and is expected to span a moderate duration.

Standard diagnostic records have been obtained to support treatment planning, including clinical photographs and radiographic imaging. These records are used to document current dental alignment and to assist with treatment planning and monitoring.

The treatment is planned and supervised by a licensed dental professional. Retention is included as part of the overall treatment plan unless otherwise specified. This summary is provided for administrative and insurance documentation purposes only. Final coverage determinations are subject to individual payer policies.

Referenced CDT codes (for administrative reference):
D8090 – Comprehensive orthodontic treatment (adult)
D0350 – Oral/facial photographic images
D0330 – Panoramic radiographic image
```

### Example 2 — Express/Mild Case (Adolescent)

**Input**: tier=express_mild, arches=both, age_group=adolescent, retainers_included=true, diagnostic_assets={intraoral_photos=true}

**Output**:
```
Insurance Summary (Draft – Admin Use Only)

The patient is planned for limited orthodontic treatment using clear aligners to address minor dental alignment concerns. Treatment is limited in scope and duration and focuses on targeted tooth movement.

Diagnostic records, including clinical photographs, have been collected to support treatment planning. These records are intended to document baseline alignment and support administrative review.

Treatment planning and monitoring are overseen by the treating dentist. This document is intended to assist with insurance-related administration and does not represent a guarantee of coverage or benefit eligibility.

Referenced CDT codes (for administrative reference):
D8010 – Limited orthodontic treatment
D0350 – Oral/facial photographic images
```

## Regeneration & Audit

- Dentist can regenerate the summary (seed is incremented for variation)
- Each regeneration produces a new version with new UUID
- Final version must be dentist-approved before use
- All versions are logged in AuditLog for audit trail

## Integration

### Streamlit Demo

Access the Insurance Summary tab in the Streamlit demo:
```bash
streamlit run scripts/demo/streamlit_demo.py
```

### Direct API Call

```bash
curl -X POST http://localhost:8000/api/v1/generate-insurance-summary \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "moderate",
    "arches": "both",
    "age_group": "adult",
    "retainers_included": true,
    "diagnostic_assets": {
      "intraoral_photos": true,
      "panoramic_xray": true,
      "fmx": false
    },
    "monitoring_approach": "mixed"
  }'
```

## Files

### Schemas
- `app/schemas/insurance_summary.py` - Request/Response schemas
- `app/schemas/enums.py` - InsuranceTier, Arches, AgeGroup enums

### Services
- `app/services/insurance_openai_service.py` - AI generation
- `app/services/insurance_cdt_service.py` - CDT code selection

### Prompts
- `app/core/prompts.py` - INSURANCE_SUMMARY_SYSTEM_PROMPT

### Routes
- `app/api/routes.py` - POST /generate-insurance-summary

## Future Extensions (Out of Scope v1)

- Separate retainer billing (D8680)
- CBCT handling
- PMS auto-push
- Insurance pre-check logic

## Success Metric

> Dentists trust it enough to use it daily without fear of insurance issues.

---

**Version**: 1.0  
**Last Updated**: December 29, 2024
