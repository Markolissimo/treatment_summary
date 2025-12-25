# Regeneration Feature Documentation

## Overview

The regeneration feature allows users to generate alternative versions of treatment summaries with the same input parameters. This is useful when you want to explore different AI-generated variations while maintaining reproducibility through seed tracking.

## Key Features

### 1. Seed-Based Generation
- **Initial Generation**: Uses configured seed value (default: 42)
- **Regeneration**: Increments seed by 1 for each regeneration
- Seeds are tracked in the database and logs for full reproducibility

### 2. Smart Button Toggle
The Streamlit UI automatically switches between "Generate" and "Regenerate" modes:
- **Generate**: Shown when inputs have changed or no previous generation exists
- **Regenerate**: Shown when inputs match the previous generation

### 3. Version Tracking
Each generation is tracked with:
- `uuid`: Unique identifier for the generation
- `is_regenerated`: Boolean flag indicating if this is a regeneration
- `previous_version_uuid`: Links to the previous version (for regenerations)
- `seed`: The seed value used for this generation

## Configuration

Seeds are configured in `app/core/config.py`:

```python
# LLM Seeds for reproducibility
treatment_summary_seed: int = 42
insurance_summary_seed: int = 42
progress_notes_seed: int = 42
```

You can override these in your `.env` file:

```bash
TREATMENT_SUMMARY_SEED=42
INSURANCE_SUMMARY_SEED=42
PROGRESS_NOTES_SEED=42
```

## How It Works

### Generation Flow

1. **First Generation** (inputs: A)
   - Button shows: "🚀 Generate Treatment Summary"
   - Seed used: 42 (from config)
   - Response includes: `uuid`, `seed: 42`, `is_regenerated: false`

2. **Regeneration** (same inputs: A)
   - Button shows: "🔄 Regenerate Treatment Summary"
   - Seed used: 43 (previous seed + 1)
   - Response includes: `uuid`, `seed: 43`, `is_regenerated: true`, `previous_version_uuid`

3. **Multiple Regenerations** (same inputs: A)
   - Each click increments seed: 44, 45, 46...
   - Full version chain is maintained in database

4. **New Generation** (different inputs: B)
   - Button shows: "🚀 Generate Treatment Summary"
   - Seed resets to: 42 (initial seed)
   - Starts a new version chain

### Input Change Detection

The system tracks all input parameters:
- Patient details (name, age, practice)
- Clinical data (treatment type, area, duration, etc.)
- Output controls (audience, tone)
- Dentist notes

Any change to these inputs triggers a new generation (not regeneration).

## API Usage

### Generate Treatment Summary

```python
POST /api/v1/generate-treatment-summary

{
  "treatment_type": "clear aligners",
  "area_treated": "both",
  "duration_range": "4-6 months",
  "case_difficulty": "moderate",
  "monitoring_approach": "mixed",
  "attachments": "some",
  "whitening_included": false,
  "audience": "patient",
  "tone": "reassuring"
}
```

Response:
```json
{
  "success": true,
  "document": { ... },
  "metadata": {
    "tokens_used": 450,
    "generation_time_ms": 1200,
    "seed": 42
  },
  "uuid": "abc-123-def-456",
  "is_regenerated": false,
  "previous_version_uuid": null,
  "seed": 42
}
```

### Regenerate Treatment Summary

```python
POST /api/v1/generate-treatment-summary

{
  "is_regeneration": true,
  "previous_version_uuid": "abc-123-def-456",
  "treatment_type": "clear aligners",
  "area_treated": "both",
  ...
}
```

Response:
```json
{
  "success": true,
  "document": { ... },
  "metadata": {
    "tokens_used": 455,
    "generation_time_ms": 1150,
    "seed": 43
  },
  "uuid": "xyz-789-ghi-012",
  "is_regenerated": true,
  "previous_version_uuid": "abc-123-def-456",
  "seed": 43
}
```

## Database Schema

The `audit_logs` table includes these regeneration fields:

```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    input_data TEXT NOT NULL,
    generated_text TEXT NOT NULL,
    model_used TEXT DEFAULT 'gpt-4o',
    tokens_used INTEGER,
    generation_time_ms INTEGER,
    created_at TIMESTAMP,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    seed INTEGER,                          -- NEW
    is_regenerated BOOLEAN DEFAULT 0,      -- NEW
    previous_version_uuid TEXT,            -- NEW
    INDEX ix_audit_logs_previous_version_uuid (previous_version_uuid)
);
```

## Migration

If you have an existing database, run the migration script:

```bash
python migrate_db_add_regeneration_fields.py
```

This will add the new fields to your existing `audit_logs` table without losing data.

## Logging

Seed values are logged for debugging and audit purposes:

```
INFO: New generation: using initial seed: 42
INFO: Regeneration: incrementing seed from 42 to 43
INFO: Regeneration: incrementing seed from 43 to 44
```

## Use Cases

### 1. Exploring Variations
Generate multiple versions of a summary to find the best wording or style.

### 2. A/B Testing
Compare different AI-generated versions for the same case.

### 3. Quality Assurance
Verify consistency across regenerations with different seeds.

### 4. Reproducibility
Recreate any previous generation using its UUID and seed value.

### 5. Version History
Track the evolution of summaries through the version chain.

## Best Practices

1. **Use Regenerate Sparingly**: Only regenerate when you need an alternative version
2. **Track Important Versions**: Note the UUIDs of versions you want to reference later
3. **Monitor Seed Values**: Check logs to understand which seed produced which output
4. **Clear Version Chains**: Change inputs to start fresh when working on a new case
5. **Database Backups**: Regularly backup your audit database to preserve version history

## Troubleshooting

### Button Doesn't Change to Regenerate
- Ensure inputs haven't changed
- Check that a previous generation exists in session state
- Verify the Streamlit session hasn't been reset

### Seed Not Incrementing
- Check database migration was run successfully
- Verify `previous_version_uuid` is being passed correctly
- Review logs for seed calculation messages

### Version Chain Broken
- Ensure database connection is stable
- Verify audit logs are being saved correctly
- Check that UUIDs are being returned in responses

## Future Enhancements

Potential improvements to the regeneration feature:
- Manual seed override in UI
- Version comparison view
- Seed range exploration (generate multiple versions at once)
- Favorite/bookmark specific versions
- Export version history
