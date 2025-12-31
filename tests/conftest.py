"""
Pytest configuration and shared fixtures for BiteSoft AI tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_session
from app.core.config import get_settings

# Configure pytest-asyncio to auto mode
pytest_plugins = ('pytest_asyncio',)


def pytest_configure(config):
    """Configure pytest-asyncio mode."""
    config.option.asyncio_mode = "auto"


@pytest.fixture(scope="function")
async def test_db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
def test_client():
    """Create a test client for API testing."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing."""
    return {
        "title": "Your Clear Aligner Treatment Plan",
        "summary": "You'll be using clear aligners to gently guide your teeth into their ideal positions over the next 4-6 months.",
    }


@pytest.fixture
def sample_treatment_request():
    """Sample treatment summary request for testing."""
    return {
        "patient_name": "John Smith",
        "practice_name": "BiteSoft Orthodontics",
        "patient_age": 25,
        "treatment_type": "clear aligners",
        "area_treated": "both",
        "duration_range": "4-6 months",
        "case_difficulty": "moderate",
        "monitoring_approach": "mixed",
        "attachments": "some",
        "whitening_included": False,
        "dentist_note": "Patient is highly motivated",
        "audience": "patient",
        "tone": "reassuring"
    }


@pytest.fixture
def minimal_treatment_request():
    """Minimal treatment request (tests defaults)."""
    return {}


@pytest.fixture
def settings():
    """Get application settings."""
    return get_settings()
