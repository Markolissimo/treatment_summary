# BiteSoft AI Document Generation System

**Version 0.2.0** | December 29, 2025

AI-powered service for generating professional orthodontic documentation including treatment summaries and insurance summaries.

---

## 📋 Version History

| Version | Date | Module | Description |
|---------|------|--------|-------------|
| **0.2.0** | Dec 29, 2025 | Project | Added Insurance Summary module, security hardening, confirmation tracking |
| **0.1.0** | Dec 29, 2025 | Insurance Summary | Initial release: deterministic CDT logic, conservative tone, admin-facing |
| **0.2.0** | Dec 26, 2025 | Treatment Summary | Production hardening: JWT auth, CORS config, PHI redaction, CDT validation |
| **0.1.0** | Dec 25, 2025 | Treatment Summary | Initial release: patient-facing summaries with AI generation |

---

## 🚀 Quick Start

### Local Development (SQLite)

```bash
# 1. Clone and setup
git clone <repository-url>
cd treatment-summary-ai
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Run the server
uvicorn app.main:app --reload

# 4. Access the application
# API Docs: http://localhost:8000/docs
# Admin Panel: http://localhost:8000/admin
# Streamlit Demo: streamlit run scripts/demo/streamlit_demo.py
```

### Docker Deployment (PostgreSQL)

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env and set OPENAI_API_KEY and DATABASE_URL

# 2. Start services
docker-compose up -d --build

# 3. Verify deployment
curl http://localhost:8000/health
```

See [Deployment Guide](docs/deployment/README.md) for detailed instructions.

---

## 📦 Features

### Treatment Summary (v0.2.0)
✅ **Patient-facing treatment explanations**
- AI-generated summaries with multiple tone options (concise, casual, reassuring, clinical)
- Audience targeting (patient or internal/staff)
- Flexible input schema with sensible defaults
- CDT code selection based on tier and age
- Regeneration support with seed-based versioning
- Audit logging and confirmation tracking

### Insurance Summary (v0.1.0)
✅ **Admin-facing insurance documentation**
- Conservative, neutral tone (no diagnosis, no coverage promises)
- Deterministic CDT code selection (D8010, D8080, D8090)
- Diagnostic asset tracking (D0350, D0330, D0210)
- Required disclaimer for compliance
- Regeneration support with version tracking

### Security & Compliance (v0.2.0)
✅ **Production-ready hardening**
- JWT authentication with debug bypass
- CORS configuration (environment-based)
- PHI redaction toggles
- Document confirmation tracking
- Enhanced CDT rule validation
- Schema versioning in audit logs

---

## 🏗️ Architecture

```
BiteSoft AI Document Generation System
│
├── app/                          # Main application code
│   ├── api/                      # FastAPI routes and endpoints
│   ├── core/                     # Configuration, prompts, security
│   ├── db/                       # Database models and utilities
│   ├── schemas/                  # Pydantic request/response models
│   └── services/                 # Business logic and AI orchestration
│
├── docs/                         # Documentation
│   ├── deployment/               # Deployment guides
│   └── features/                 # Feature documentation
│
├── scripts/                      # Utility scripts
│   ├── demo/                     # Streamlit demo application
│   ├── migration/                # Database migration scripts
│   └── testing/                  # Testing utilities
│
└── tests/                        # Test suite
```

See [app/README.md](app/README.md) for detailed module documentation.

---

## 🔌 API Endpoints

| Endpoint | Status | Module | Description |
|----------|--------|--------|-------------|
| `POST /api/v1/generate-treatment-summary` | ✅ Active | Treatment v0.2.0 | Generate patient-facing treatment summary |
| `POST /api/v1/generate-insurance-summary` | ✅ Active | Insurance v0.1.0 | Generate admin-facing insurance summary |
| `POST /api/v1/documents/{id}/confirm` | ✅ Active | Confirmation v0.2.0 | Confirm generated document |
| `POST /api/v1/generate-progress-notes` | 🚧 Planned | Progress Notes | Coming in future release |
| `GET /health` | ✅ Active | System | Health check endpoint |
| `GET /admin` | ✅ Active | Admin | CDT codes and audit log management |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICK_START.md](QUICK_START.md) | Fast deployment guide |
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/deployment/README.md](docs/deployment/README.md) | Docker deployment guide |
| [docs/features/insurance-summary.md](docs/features/insurance-summary.md) | Insurance Summary specification |
| [docs/features/cdt-mapping.md](docs/features/cdt-mapping.md) | CDT code mapping system |
| [docs/features/regeneration.md](docs/features/regeneration.md) | Regeneration feature guide |
| [docs/BACKEND_COMPLETENESS_UPDATES.md](docs/BACKEND_COMPLETENESS_UPDATES.md) | v0.2.0 security updates |

---

## 🛡️ What This System Is

- **Administrative Support Tool** - Assists dentists with documentation
- **Time Saver** - Reduces admin time by 10-20 minutes per case
- **Standardization Tool** - Ensures consistent, professional language
- **Compliance Helper** - Uses conservative, legally safe wording

## ❌ What This System Is NOT

- **NOT a diagnosis tool** - Does not diagnose conditions
- **NOT a treatment planner** - Does not decide treatment
- **NOT a guarantee** - Does not promise outcomes or coverage
- **NOT a claim submission** - Does not file insurance claims
- **NOT a replacement for dentist judgment** - Dentist remains decision-maker

---

## 🔐 Security Features (v0.2.0)

- **JWT Authentication** - Validates portal tokens (with debug bypass for development)
- **CORS Protection** - Environment-based origin restrictions
- **PHI Redaction** - Configurable redaction of protected health information
- **Audit Trail** - Complete logging of all document generations
- **Confirmation Tracking** - Records dentist approval before finalization
- **Schema Versioning** - Tracks document schema versions for compliance

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run Streamlit demo
streamlit run scripts/demo/streamlit_demo.py
```

See [tests/README.md](tests/README.md) for comprehensive testing documentation.

---

## 🔧 Configuration

Key environment variables (see `.env.example` for full list):

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./bitesoft_ai.db  # Local dev
# DATABASE_URL=postgresql+asyncpg://user:pass@host/db  # Production

# Security
SECRET_KEY=your-secret-key
ENABLE_AUTH_BYPASS=true  # Set to false in production
CORS_ORIGINS=*  # Set to specific origins in production

# PHI Handling
STORE_FULL_AUDIT_DATA=true
REDACT_PHI_FIELDS=false
```

---

## 📊 Module Versions

### Treatment Summary v0.2.0
- **Status**: Production Ready
- **Features**: AI generation, multiple tones, CDT codes, regeneration, confirmation tracking
- **Security**: JWT auth, PHI redaction, enhanced validation
- **Last Updated**: December 26, 2025

### Insurance Summary v0.1.0
- **Status**: Production Ready
- **Features**: Conservative summaries, deterministic CDT logic, diagnostic assets, disclaimers
- **Security**: Same security layer as Treatment Summary
- **Last Updated**: December 29, 2025

### Progress Notes
- **Status**: Planned
- **Target**: Future release

---

## 🚦 Deployment Status

- ✅ **Local Development**: Fully functional with SQLite
- ✅ **Docker Compose**: Production-ready with PostgreSQL
- 🚧 **AWS Deployment**: Planned (ECS/Lambda)
- 🚧 **Portal Integration**: In progress (portal team)

---

## 🤝 Integration

### Portal Integration Points

1. **Authentication**: Portal passes JWT token in `Authorization: Bearer <token>` header
2. **API Calls**: Portal calls `/api/v1/generate-treatment-summary` or `/api/v1/generate-insurance-summary`
3. **Document Display**: Portal displays editable summary text to dentist
4. **Confirmation**: Portal calls `/api/v1/documents/{id}/confirm` when dentist approves
5. **PDF Generation**: Portal handles PDF generation and email delivery

### Example API Call

```bash
curl -X POST http://localhost:8000/api/v1/generate-insurance-summary \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <portal-jwt-token>" \
  -d '{
    "tier": "moderate",
    "arches": "both",
    "age_group": "adult",
    "retainers_included": true,
    "diagnostic_assets": {
      "intraoral_photos": true,
      "panoramic_xray": true,
      "fmx": false
    }
  }'
```

---

## 📈 Roadmap

### v0.3.0 (Planned)
- Progress Notes module
- Multi-language support
- Enhanced CDT rule management
- Performance optimizations

### v0.4.0 (Planned)
- AWS deployment
- Advanced analytics dashboard
- Batch processing
- Custom branding options

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Switch to SQLite for local development
# Edit app/core/config.py line 23:
database_url: str = "sqlite+aiosqlite:///./bitesoft_ai.db"
```

### OpenAI API Errors
```bash
# Verify API key in .env
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Port Conflicts
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead of 8000
```

---

## 📞 Support

- **Documentation**: See `docs/` directory
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin
- **Issues**: Contact development team

---

## 📄 License

Proprietary - BiteSoft Technologies

---

**Project Version**: 0.2.0  
**Last Updated**: December 29, 2025  
**Python Version**: 3.11+  
**FastAPI Version**: 0.109.0+  
**OpenAI Model**: GPT-4o
