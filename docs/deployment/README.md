# BiteSoft AI - Deployment Guide

**Version 0.2.0** | December 29, 2025

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- PostgreSQL 15+ (handled by Docker Compose)

## Quick Start

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy from example
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_MODEL=gpt-4o
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/bitesoft_ai
SECRET_KEY=your-secure-random-secret-key-here
DEBUG=false
```

### 2. Build and Start Services

```bash
# Build and start all services (PostgreSQL + FastAPI)
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

**Note:** The application will automatically:
1. Connect to the PostgreSQL database
2. Create all necessary tables
3. Seed the database with CDT codes and rules
4. Start the API server

### 3. Verify Deployment

- **API Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin (Check that CDT codes are loaded)

## Service Architecture

```
┌─────────────────┐
│   PostgreSQL    │
│   (port 5432)   │
└────────┬────────┘
         │
         │ Database Connection
         │
┌────────▼────────┐
│   FastAPI App   │
│   (port 8000)   │
└─────────────────┘
```

## Database Management

### Backup Database

```bash
docker-compose exec db pg_dump -U postgres bitesoft_ai > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker-compose exec -T db psql -U postgres bitesoft_ai
```

### Access PostgreSQL CLI

```bash
docker-compose exec db psql -U postgres -d bitesoft_ai
```

## Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build

# Check logs for any issues
docker-compose logs -f api
```

## Stopping Services

```bash
# Stop services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data volumes)
docker-compose down

# Stop and remove everything including data
docker-compose down -v
```

## Troubleshooting

### API won't start

```bash
# Check logs
docker-compose logs api

# Common issues:
# 1. Database not ready - wait for health check
# 2. Missing OPENAI_API_KEY in .env
# 3. Port 8000 already in use
```

### Database connection errors

```bash
# Check database health
docker-compose exec db pg_isready -U postgres

# Restart database
docker-compose restart db
```

### Reset database

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm treatment-summary-ai_postgres_data

# Start fresh
docker-compose up -d
docker-compose exec api python seed_cdt_data.py
```

## Production Recommendations

1. **Security**:
   - Change `SECRET_KEY` to a strong random value
   - Use strong PostgreSQL credentials
   - Enable HTTPS with reverse proxy (nginx/traefik)
   - Restrict database port exposure

2. **Performance**:
   - Adjust PostgreSQL memory settings in docker-compose.yml
   - Configure connection pooling if needed
   - Monitor resource usage

3. **Monitoring**:
   - Set up log aggregation
   - Configure health check alerts
   - Monitor API response times

4. **Backups**:
   - Schedule automated database backups
   - Test restore procedures
   - Store backups off-server

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@db:5432/bitesoft_ai` |
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o` |
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | JWT secret key | `change-me-in-production` |
| `APP_NAME` | Application name | `BiteSoft AI Document Generation System` |
| `APP_VERSION` | Application version | `0.2.0` |

## API Endpoints

- `GET /health` - Health check
- `POST /api/treatment-summary` - Generate treatment summary
- `POST /api/insurance-summary` - Generate insurance summary (placeholder)
- `POST /api/progress-notes` - Generate progress notes (placeholder)
- `GET /admin` - Admin panel for CDT codes and audit logs
