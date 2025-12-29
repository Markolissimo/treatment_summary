# Scripts Directory

**Version 0.2.0** | December 29, 2025

This directory contains utility scripts for development, testing, and maintenance.

## Demo Scripts

Located in `demo/`:

- **streamlit_demo.py** - Interactive Streamlit demo application
  - Visual UI for testing API
  - Real-time generation
  - JSON response viewer
  - Regeneration support
  
  **Usage:**
  ```bash
  # Start FastAPI server first
  uvicorn app.main:app --reload
  
  # Then run demo (from project root)
  streamlit run scripts/demo/streamlit_demo.py
  ```

## Testing Scripts

Located in `testing/`:

- **test_docker_generation.py** - Test Docker deployment
  - Verifies API is running in Docker
  - Tests treatment summary generation
  - Validates response structure
  
  **Usage:**
  ```bash
  # Ensure Docker containers are running
  docker-compose up -d
  
  # Run test (from project root)
  python scripts/testing/test_docker_generation.py
  ```

- **generate_all_summaries.py** - Batch generation utility
  - Generate multiple summaries with different parameters
  - Test tone and audience variations
  - Performance testing
  
  **Usage:**
  ```bash
  python scripts/testing/generate_all_summaries.py
  ```

## Migration Scripts

Located in `migration/`:

- **migrate_db_add_regeneration_fields.py** - Database migration
  - Adds regeneration fields to audit_logs table
  - Safe for existing databases
  - Preserves existing data
  
  **Usage:**
  ```bash
  python scripts/migration/migrate_db_add_regeneration_fields.py
  ```

## Notes

- All scripts should be run from the **project root directory**
- Ensure virtual environment is activated before running scripts
- Check that required dependencies are installed (`pip install -r requirements.txt`)
