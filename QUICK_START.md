# ⚡ Quick Start Guide - BiteSoft AI

**For experienced DevOps/Portal team members**

## Prerequisites
- Docker & Docker Compose installed
- OpenAI API key ready
- Port 8000 available

## Deploy in 5 Steps

### 1. Get OpenAI API Key
https://platform.openai.com/api-keys

### 2. Configure Environment
```bash
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY
```

### 3. Start Services
```bash
docker-compose up -d --build
```

### 4. Verify
```bash
# Check status
docker-compose ps

# Test health
curl http://localhost:8000/health

# View docs
open http://localhost:8000/docs
```

### 5. Test API
```bash
curl -X POST "http://localhost:8000/api/v1/generate-treatment-summary" \
  -H "Content-Type: application/json" \
  -d '{"tier": "moderate", "patient_age": 25, "treatment_type": "clear aligners"}'
```

## Common Commands

```bash
# View logs
docker-compose logs -f api

# Restart
docker-compose restart

# Stop
docker-compose stop

# Backup database
docker-compose exec db pg_dump -U postgres bitesoft_ai > backup.sql

# Reset everything
docker-compose down -v && docker-compose up -d --build
```

## Troubleshooting

**Port conflict?** Edit `docker-compose.yml`, change `"8000:8000"` to `"8080:8000"`

**API key error?** Check `.env` file has `OPENAI_API_KEY=sk-...`

**Database issues?** Run `docker-compose restart db && docker-compose restart api`

## Integration

**Endpoint:** `POST http://YOUR_SERVER:8000/api/v1/generate-treatment-summary`

**Docs:** http://YOUR_SERVER:8000/docs

**Admin:** http://YOUR_SERVER:8000/admin

---

**Need more details?** See `DEPLOYMENT_HANDOFF.md`
