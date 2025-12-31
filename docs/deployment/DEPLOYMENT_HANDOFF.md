# 🚀 BiteSoft AI - Deployment Handoff Guide

**For Portal Team / DevOps**

This guide provides step-by-step instructions to deploy the BiteSoft AI Treatment Summary service on your local/self-hosted server.

---

## 📋 What You're Deploying

A **Dockerized FastAPI service** that generates AI-powered treatment summaries. Your portal will call this API locally to generate documents.

**Key Points:**
- ✅ Fully containerized with Docker
- ✅ No AWS or cloud dependencies
- ✅ Runs on your existing server
- ✅ PostgreSQL database included
- ✅ Automatic setup and seeding

---

## ⚙️ Prerequisites (What You Need)

### 1. Software Requirements

Your server must have:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)

**Check if installed:**
```bash
docker --version
docker-compose --version
```

**Don't have them?** Install from: https://docs.docker.com/get-docker/

### 2. OpenAI API Key

You need an OpenAI API key for the AI generation.

**How to get it:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. **Save it securely** - you'll need it in Step 3

**Cost estimate:** ~$0.01-0.03 per summary generated

### 3. Server Requirements

**Minimum:**
- 2 CPU cores
- 4 GB RAM
- 10 GB disk space
- Port 8000 available (or any port you prefer)

---

## 📦 Deployment Files

You should have received these files:

```
treatment-summary-ai/
├── docker-compose.yml          # Service configuration
├── Dockerfile                  # API container definition
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── app/                       # Application code
├── docs/                      # Documentation
└── DEPLOYMENT_HANDOFF.md      # This file
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Upload Files to Server

Transfer all project files to your server. Recommended location:
```bash
/opt/bitesoft-ai/
```

Or use any directory you prefer.

### Step 2: Navigate to Project Directory

```bash
cd /opt/bitesoft-ai/
```

### Step 3: Configure Environment Variables

**Create the `.env` file:**
```bash
cp .env.example .env
```

**Edit the `.env` file:**
```bash
nano .env
# or use: vim .env
# or use any text editor
```

**Required changes:**

1. **Add your OpenAI API key** (from Prerequisites step 2):
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

2. **Change the secret key** (use any random string):
   ```env
   SECRET_KEY=your-random-secure-string-here
   ```

3. **Optional - Change the port** (if 8000 is already in use):
   - Edit `docker-compose.yml`
   - Change `"8000:8000"` to `"YOUR_PORT:8000"`
   - Example: `"8080:8000"` to use port 8080

**Save and close** the file.

### Step 4: Start the Services

**Run this single command:**
```bash
docker-compose up -d --build
```

**What this does:**
- Downloads required Docker images
- Builds the FastAPI application
- Starts PostgreSQL database
- Starts the API service
- Seeds the database with CDT codes
- Runs everything in the background

**This may take 2-5 minutes on first run.**

### Step 5: Verify Deployment

**Check if services are running:**
```bash
docker-compose ps
```

**You should see:**
```
NAME                              STATUS
treatment-summary-ai-db-1         Up (healthy)
treatment-summary-ai-api-1        Up (healthy)
```

**Test the API:**

Open in your browser:
```
http://YOUR_SERVER_IP:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Access API documentation:**
```
http://YOUR_SERVER_IP:8000/docs
```

You should see interactive API documentation.

---

## ✅ Post-Deployment Checklist

- [ ] Services are running (`docker-compose ps` shows "Up")
- [ ] Health check returns `{"status": "healthy"}`
- [ ] API docs are accessible at `/docs`
- [ ] Admin panel loads at `/admin`
- [ ] CDT codes are visible in admin panel (confirms database seeding worked)

---

## 🔗 Integration with Your Portal

### API Endpoint

Your portal should call:
```
POST http://YOUR_SERVER_IP:8000/api/v1/generate-treatment-summary
```

### Example Request

```bash
curl -X POST "http://YOUR_SERVER_IP:8000/api/v1/generate-treatment-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_age": 25,
    "tier": "moderate",
    "treatment_type": "clear aligners",
    "area_treated": "both",
    "duration_range": "6-9 months",
    "case_difficulty": "moderate",
    "monitoring_approach": "mixed",
    "attachments": "some",
    "whitening_included": false,
    "audience": "patient",
    "tone": "reassuring"
  }'
```

### Example Response

```json
{
  "success": true,
  "document": {
    "title": "Your Clear Aligner Treatment Plan",
    "summary": "Based on your assessment, this is a moderate alignment case..."
  },
  "cdt_codes": {
    "primary_code": "D8090",
    "primary_description": "Comprehensive orthodontic treatment – adult dentition"
  },
  "metadata": {
    "tokens_used": 450,
    "generation_time_ms": 1200
  }
}
```

**Full API documentation:** See `/docs` endpoint or `docs/features/prompt-structure.md`

---

## 🛠️ Common Operations

### View Logs

**See what's happening:**
```bash
docker-compose logs -f api
```

Press `Ctrl+C` to stop viewing logs.

### Stop Services

**Stop but keep data:**
```bash
docker-compose stop
```

**Start again:**
```bash
docker-compose start
```

### Restart Services

**After making changes:**
```bash
docker-compose restart
```

### Update the Application

**When you receive updates:**
```bash
# Pull new files (if using git)
git pull

# Or replace files manually

# Rebuild and restart
docker-compose up -d --build
```

### Backup Database

**Create backup:**
```bash
docker-compose exec db pg_dump -U postgres bitesoft_ai > backup_$(date +%Y%m%d).sql
```

**Restore backup:**
```bash
cat backup_20231226.sql | docker-compose exec -T db psql -U postgres bitesoft_ai
```

### Complete Reset

**If you need to start fresh:**
```bash
# Stop and remove everything
docker-compose down -v

# Start again
docker-compose up -d --build
```

---

## ❗ Troubleshooting

### Issue: "Port 8000 already in use"

**Solution:**
1. Edit `docker-compose.yml`
2. Change `"8000:8000"` to `"8080:8000"` (or any available port)
3. Run `docker-compose up -d --build`
4. Access API at `http://YOUR_SERVER:8080`

### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker
```

### Issue: API returns "401 Unauthorized" or "Invalid API key"

**Solution:**
1. Check your `.env` file
2. Verify `OPENAI_API_KEY` is set correctly
3. Restart services: `docker-compose restart`

### Issue: Database connection errors

**Solution:**
```bash
# Check database health
docker-compose exec db pg_isready -U postgres

# If unhealthy, restart database
docker-compose restart db

# Wait 30 seconds, then restart API
docker-compose restart api
```

### Issue: Services won't start

**Solution:**
```bash
# Check logs for errors
docker-compose logs api
docker-compose logs db

# Common fixes:
# 1. Ensure .env file exists and has OPENAI_API_KEY
# 2. Ensure ports are available
# 3. Ensure Docker has enough resources
```

---

## 🔒 Security Recommendations

### For Production Use:

1. **Change default passwords:**
   - Edit `docker-compose.yml`
   - Change PostgreSQL password from `postgres` to something secure

2. **Use strong SECRET_KEY:**
   - Generate random string: `openssl rand -hex 32`
   - Update in `.env` file

3. **Restrict network access:**
   - Use firewall to limit access to port 8000
   - Only allow connections from portal server

4. **Enable HTTPS:**
   - Use reverse proxy (nginx/traefik)
   - Add SSL certificate

5. **Regular backups:**
   - Schedule daily database backups
   - Store backups off-server

---

## 📞 Support & Documentation

### Documentation Files

- **`docs/deployment/README.md`** - Detailed deployment guide
- **`docs/features/`** - Feature documentation
- **`docs/README.md`** - Documentation index

### API Documentation

- **Swagger UI:** `http://YOUR_SERVER:8000/docs`
- **ReDoc:** `http://YOUR_SERVER:8000/redoc`
- **Admin Panel:** `http://YOUR_SERVER:8000/admin`

### Quick Reference

**Start services:**
```bash
docker-compose up -d
```

**Stop services:**
```bash
docker-compose stop
```

**View logs:**
```bash
docker-compose logs -f api
```

**Restart after changes:**
```bash
docker-compose restart
```

**Check status:**
```bash
docker-compose ps
```

---

## 📧 Next Steps

1. ✅ Deploy using this guide
2. ✅ Verify health check works
3. ✅ Test API with sample request
4. ✅ Share API endpoint with portal team
5. ✅ Portal team integrates API calls
6. ✅ Test end-to-end integration
7. ✅ Sign off on functionality

**Questions?** Contact the development team with:
- Server logs (`docker-compose logs`)
- Error messages
- Steps you've tried

---

*This service is ready for integration. All setup is automated - just follow the steps above.*
