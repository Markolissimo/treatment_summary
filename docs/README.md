# Documentation Index

**Version 0.2.0** | December 29, 2025

This directory contains all project documentation organized by category.

## Deployment Documentation

Located in `deployment/`:

- **[README.md](deployment/README.md)** - Complete deployment guide for Docker Compose
  - Environment setup
  - Building and starting services
  - Database management
  - Troubleshooting
  - Production recommendations

- **[cdt-setup.md](deployment/cdt-setup.md)** - CDT mapping system setup guide
  - Quick start instructions
  - Database seeding
  - Admin panel access
  - API testing examples

## Feature Documentation

Located in `features/`:

- **[cdt-mapping.md](features/cdt-mapping.md)** - CDT code mapping system
  - Architecture overview
  - Database models
  - Selection logic
  - Admin panel usage
  - Extensibility guide

- **[prompt-structure.md](features/prompt-structure.md)** - Prompt engineering and API design
  - System prompt architecture
  - Hard restrictions and guardrails
  - User prompt construction
  - API design philosophy
  - Output structure

- **[regeneration.md](features/regeneration.md)** - Regeneration feature
  - Seed-based generation
  - Version tracking
  - API usage examples
  - Database schema
  - Best practices

## Client Documentation

Located in root `docs/` folder:

- **ai_features_portal.txt** - Client specifications for AI features
- **bitesoft – Treatment Summary AI (v1 Requirements).txt** - Project requirements
- **LITSLINK_Proposal_Clinical Documentation Automation_v.2.0..txt** - Project proposal

## Quick Links

### Getting Started
1. [Main README](../README.md) - Project overview and quick start
2. [Deployment Guide](deployment/README.md) - Deploy with Docker
3. [CDT Setup](deployment/cdt-setup.md) - Set up CDT mapping

### Development
1. [Prompt Structure](features/prompt-structure.md) - Understand AI prompts
2. [CDT Mapping](features/cdt-mapping.md) - Work with CDT codes
3. [Regeneration](features/regeneration.md) - Implement regeneration

### API Reference
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Admin Panel: http://localhost:8000/admin
