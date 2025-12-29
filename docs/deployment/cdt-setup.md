# CDT Mapping Setup Guide

## Quick Start

Follow these steps to set up the CDT mapping system:

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the new `sqladmin>=0.16.0` dependency for the admin panel.

### 2. Seed the Database

Run the seed script to populate CDT codes and rules:

```bash
python seed_cdt_data.py
```

**Expected Output:**
```
Seeding CDT codes...
  Added: D8010 - Limited orthodontic treatment
  Added: D8080 - Comprehensive orthodontic treatment – adolescent dentition
  Added: D8090 - Comprehensive orthodontic treatment – adult dentition
  Added: D0330 - Panoramic radiograph
  Added: D0210 - Intraoral complete series of radiographic images (FMX)
  Added: D0350 - Oral/facial photographic images
  Added: D0470 - Diagnostic casts
  Added: D8680 - Orthodontic retention (completion of active treatment)

Seeding CDT rules...
  Added: express + adolescent → D8010
  Added: express + adult → D8010
  Added: mild + adolescent → D8010
  Added: mild + adult → D8010
  Added: moderate + adolescent → D8080
  Added: moderate + adult → D8090
  Added: complex + adolescent → D8080
  Added: complex + adult → D8090

✅ CDT data seeding complete!
```

### 3. Start the FastAPI Server

```bash
uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000`

### 4. Access the Admin Panel

Navigate to: **http://localhost:8000/admin**

You can now manage:
- **CDT Codes**: View and edit code definitions
- **CDT Rules**: Manage tier + age → code mappings
- **Audit Logs**: View generation history (read-only)

### 5. Test the API

#### Using cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/generate-treatment-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "moderate",
    "patient_age": 25,
    "treatment_type": "clear aligners",
    "area_treated": "both",
    "duration_range": "6-9 months",
    "case_difficulty": "moderate",
    "monitoring_approach": "mixed",
    "attachments": "some",
    "audience": "patient",
    "tone": "reassuring"
  }'
```

#### Expected Response (excerpt):

```json
{
  "success": true,
  "document": {
    "summary": "...",
    "key_points": [...],
    "next_steps": [...]
  },
  "cdt_codes": {
    "primary_code": "D8090",
    "primary_description": "Comprehensive orthodontic treatment – adult dentition",
    "suggested_add_ons": [],
    "notes": "Selected based on tier=moderate, age_group=adult"
  },
  "uuid": "...",
  "seed": 42
}
```

### 6. Test with Streamlit Demo

```bash
streamlit run streamlit_demo.py
```

The demo now includes:
- **Case Tier** dropdown for CDT mapping
- **CDT Code Suggestions** display in the output panel

## Database Schema

### New Tables

#### `cdt_codes`
- `code` (PK): CDT code (e.g., D8010)
- `description`: Human-readable description
- `category`: orthodontic, diagnostic, retention
- `is_primary`: Primary treatment code vs add-on
- `is_active`: Active status
- `notes`: Usage guidelines
- `created_at`, `updated_at`: Timestamps

#### `cdt_rules`
- `id` (PK): UUID
- `tier`: express, mild, moderate, complex
- `age_group`: adolescent, adult
- `cdt_code`: CDT code to assign
- `priority`: Priority order (higher = higher priority)
- `is_active`: Active status
- `notes`: Rule notes
- `created_at`, `updated_at`: Timestamps

## API Changes

### Request Schema

Added `tier` field to `TreatmentSummaryRequest`:

```json
{
  "tier": "moderate",  // NEW: express, mild, moderate, complex
  "patient_age": 25,
  "treatment_type": "clear aligners",
  ...
}
```

### Response Schema

Added `cdt_codes` field to `TreatmentSummaryResponse`:

```json
{
  "success": true,
  "document": {...},
  "cdt_codes": {  // NEW
    "primary_code": "D8090",
    "primary_description": "Comprehensive orthodontic treatment – adult dentition",
    "suggested_add_ons": [],
    "notes": "Selected based on tier=moderate, age_group=adult"
  },
  ...
}
```

## CDT Selection Logic

Based on client documentation (`docs/ai_features_portal.txt`):

1. **If Tier = Express/Mild → D8010** (Limited orthodontic treatment)
2. **If Tier = Moderate/Complex → D8080 (Adolescent) or D8090 (Adult)**

Age determination:
- **Adolescent**: < 18 years old
- **Adult**: ≥ 18 years old

## Admin Panel Features

### CDT Codes Management
- View all codes with filtering and search
- Create new codes
- Edit existing codes (description, category, active status)
- Deactivate codes (soft delete)

### CDT Rules Management
- View all rules with filtering and search
- Create new rules (tier + age_group → code)
- Edit rule priority and active status
- Deactivate rules

### Audit Logs (Read-Only)
- View all generation events
- Filter by user, document type, status
- See seed values and regeneration tracking

## Troubleshooting

### Issue: Seed script fails with "table already exists"

**Solution:** The script checks for existing data and skips duplicates. If you need to reset:

```bash
# Delete the database file
rm bitesoft_audit.db

# Re-run the seed script
python seed_cdt_data.py
```

### Issue: Admin panel shows 404

**Solution:** Ensure `sqladmin` is installed and `setup_admin()` is called in `app/main.py`:

```bash
pip install sqladmin>=0.16.0
```

Verify in `app/main.py`:
```python
from app.admin import setup_admin
setup_admin(app, engine)
```

### Issue: CDT codes not returned in API response

**Possible causes:**
1. No `tier` or `patient_age` provided in request
2. No matching rule in database
3. Rule is inactive (`is_active = False`)

**Solution:** Check the `cdt_codes.notes` field in the response for selection details.

## Next Steps

### For Production Deployment

1. **Switch to PostgreSQL**: Update `database_url` in `.env` or config
2. **Run Migrations**: Use Alembic for schema migrations
3. **Secure Admin Panel**: Add authentication to `/admin` endpoint
4. **Customize Rules**: Add payer-specific or state-specific rules via admin panel

### For Insurance Module (Module 2)

The CDT system is ready for expansion:
- Add `payer_id` field to `CDTRule` for payer-specific mappings
- Add `state` field for state-specific rules
- Implement diagnostic asset flags in request schema
- Add `retainers_included` flag to request schema

## Documentation

- **CDT_MAPPING.md**: Detailed architecture and usage guide
- **docs/ai_features_portal.txt**: Client-provided CDT mapping specifications
- **app/services/cdt_service.py**: Service implementation
- **app/admin.py**: Admin panel configuration

## Support

For questions or issues, refer to:
- API documentation: http://localhost:8000/docs
- Admin panel: http://localhost:8000/admin
- Project README: README.md
