# CDT Code Mapping System

## Overview

The CDT (Current Dental Terminology) mapping system provides deterministic code selection for insurance documentation and claim support. This implementation is based on client-provided specifications and follows a simple tier + age-based logic.

## Architecture

### Database Models

#### `CDTCode`
Stores CDT code definitions with descriptions and metadata.

**Fields:**
- `code` (Primary Key): CDT code (e.g., D8010, D8080, D8090)
- `description`: Human-readable description
- `category`: Code category (orthodontic, diagnostic, retention)
- `is_primary`: Whether this is a primary treatment code
- `is_active`: Whether the code is currently active
- `notes`: Additional usage guidelines
- `created_at`, `updated_at`: Timestamps

#### `CDTRule`
Defines mapping rules from case attributes to CDT codes.

**Fields:**
- `id` (Primary Key): UUID
- `tier`: Case tier (express, mild, moderate, complex)
- `age_group`: Age group (adolescent, adult)
- `cdt_code`: CDT code to assign
- `priority`: Priority order (higher = higher priority)
- `is_active`: Whether the rule is active
- `notes`: Additional notes
- `created_at`, `updated_at`: Timestamps

### Selection Logic

The `select_cdt_codes()` service function implements the following priority logic:

1. **If Tier = Express/Mild → D8010** (Limited orthodontic treatment)
2. **If Tier = Moderate/Complex → D8080 (Adolescent) or D8090 (Adult)**

Age determination follows CDT standards:
- **Adolescent**: < 18 years old
- **Adult**: ≥ 18 years old

### Seeded Data

#### Primary Orthodontic Codes

| Code | Description | Tier | Age Group |
|------|-------------|------|-----------|
| D8010 | Limited orthodontic treatment | Express, Mild | Both |
| D8080 | Comprehensive orthodontic treatment – adolescent dentition | Moderate, Complex | Adolescent |
| D8090 | Comprehensive orthodontic treatment – adult dentition | Moderate, Complex | Adult |

#### Supporting Diagnostic Codes

| Code | Description | Category |
|------|-------------|----------|
| D0330 | Panoramic radiograph | Diagnostic |
| D0210 | Intraoral complete series of radiographic images (FMX) | Diagnostic |
| D0350 | Oral/facial photographic images | Diagnostic |
| D0470 | Diagnostic casts | Diagnostic |

#### Retention Code

| Code | Description | Category |
|------|-------------|----------|
| D8680 | Orthodontic retention (completion of active treatment) | Retention |

## Usage

### 1. Seed the Database

Run the seed script to populate initial CDT codes and rules:

```bash
python seed_cdt_data.py
```

This will create:
- 3 primary orthodontic codes
- 4 diagnostic/supporting codes
- 1 retention code
- 8 mapping rules (4 tiers × 2 age groups)

### 2. API Integration

The CDT selection is automatically integrated into the `/api/v1/generate-treatment-summary` endpoint.

**Request:**
```json
{
  "tier": "moderate",
  "patient_age": 25,
  "treatment_type": "clear aligners",
  "area_treated": "both",
  "duration_range": "6-9 months"
}
```

**Response:**
```json
{
  "success": true,
  "document": { ... },
  "cdt_codes": {
    "primary_code": "D8090",
    "primary_description": "Comprehensive orthodontic treatment – adult dentition",
    "suggested_add_ons": [],
    "notes": "Selected based on tier=moderate, age_group=adult"
  }
}
```

### 3. Admin Panel

Access the admin panel at `/admin` to manage CDT codes and rules:

- **CDT Codes**: View, create, edit, and deactivate codes
- **CDT Rules**: Manage tier + age → code mappings
- **Audit Logs**: View generation history (read-only)

The admin panel uses `sqladmin` for automatic CRUD interface generation.

## Service API

### `select_cdt_codes()`

```python
from app.services.cdt_service import select_cdt_codes

result = await select_cdt_codes(
    session=session,
    tier="moderate",           # express, mild, moderate, complex
    patient_age=25,            # Age in years
    diagnostic_assets=None,    # Optional: {photos: True, xray: True, ...}
    retainers_included=False,  # Optional: Include retention code
)

# Access results
print(result.primary_code)        # "D8090"
print(result.primary_description) # "Comprehensive orthodontic treatment – adult dentition"
print(result.suggested_add_ons)   # List of add-on codes
print(result.notes)               # Selection notes
```

## Extensibility

### Adding New Codes

1. **Via Admin Panel**: Navigate to `/admin` → CDT Codes → Create
2. **Via Database**: Insert into `cdt_codes` table
3. **Via Seed Script**: Add to `seed_cdt_data.py` and re-run

### Adding New Rules

1. **Via Admin Panel**: Navigate to `/admin` → CDT Rules → Create
2. **Via Database**: Insert into `cdt_rules` table
3. **Via Seed Script**: Add to `seed_cdt_data.py` and re-run

### Custom Logic

For more complex selection logic beyond tier + age:

1. Modify `app/services/cdt_service.py`
2. Add new fields to `CDTRule` model
3. Update the query logic in `select_cdt_codes()`

## Important Notes

### Compliance

- **Not Automatic Billing**: This system provides code suggestions for documentation and claim support. Final code selection must be reviewed and approved by the treating dentist.
- **Payer Variations**: CDT codes may vary by payer and state. Rules can be customized per practice.
- **Whitening Exclusion**: Whitening is not part of CDT claim logic (kept separate).
- **Monitoring/DM**: Generally not a CDT code; described in narrative if needed.

### Data Fields for Rules

The system expects these input fields:
- `tier` (required): express, mild, moderate, complex
- `patient_age` (required): Age in years
- `diagnostic_assets` (optional): Flags for photos, xray, fmx, casts
- `retainers_included` (optional): Boolean

### Priority Ordering

Rules are evaluated by priority (descending). Higher priority rules take precedence when multiple rules match.

## Future Enhancements

Potential extensions for Module 2 (Insurance Summary):

1. **Payer-Specific Rules**: Add `payer_id` field to rules
2. **State-Specific Rules**: Add `state` field to rules
3. **Diagnostic Asset Mapping**: Automatic add-on selection based on available assets
4. **Fee Schedules**: Link codes to fee information (non-patient-facing)
5. **Claim Templates**: Generate insurance claim narratives with CDT codes

## Testing

Run tests to verify CDT logic:

```bash
pytest tests/test_cdt_service.py -v
```

## Troubleshooting

### No CDT Code Returned

**Cause**: No matching rule found for tier + age_group combination.

**Solution**: 
1. Check if tier is correctly normalized (lowercase)
2. Verify patient_age is provided
3. Check if matching rule exists in `cdt_rules` table
4. Verify rule is active (`is_active = True`)

### Wrong Code Selected

**Cause**: Multiple rules match, priority ordering issue.

**Solution**:
1. Check rule priorities in admin panel
2. Ensure higher priority for more specific rules
3. Review rule `notes` for selection logic

### Admin Panel Not Loading

**Cause**: `sqladmin` not installed or engine not configured.

**Solution**:
```bash
pip install sqladmin>=0.16.0
```

Verify `setup_admin()` is called in `app/main.py`.
