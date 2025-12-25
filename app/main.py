from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import init_db, async_engine as engine
from app.api.routes import router as api_router
from app.admin import setup_admin

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## BiteSoft AI Document Generation System

A clinical communication assistant for dentists that generates draft documents 
based on structured case data.

### Available Modules

- **Treatment Summary** (Active): Generate professional treatment summaries
- **Insurance Summary** (Coming Soon): Generate insurance documentation
- **Progress Notes** (Coming Soon): Generate clinical progress notes

### Authentication

All endpoints require Bearer token authentication. In development mode, 
requests without tokens are allowed with a default user ID.

### Compliance

All generated documents adhere to strict clinical communication guidelines:
- No diagnostic terminology
- No outcome guarantees
- No financial information
- Fact integrity across all tone variations
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Setup admin panel
setup_admin(app, engine)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint returning API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
    }


@ app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "app_version": settings.app_version,
    }
