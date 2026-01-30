"""
Test configuration and fixtures.
"""

import os
import sys
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add backend to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.db import Base, get_db
from app.main import app
from app.services.stt.mock_whisper import MockSTTService

# =============================================================================
# pytest configuration for --production flag
# =============================================================================


def pytest_addoption(parser):
    """Add --production flag to pytest."""
    parser.addoption(
        "--production",
        action="store_true",
        default=False,
        help="Run production tests against actual services and APIs",
    )


def pytest_configure(config):
    """Register production marker."""
    config.addinivalue_line(
        "markers", "production: mark test as production (requires running backends/APIs)"
    )


@pytest.fixture(autouse=True)
def setup_stt_service():
    """Set up mock STT service for all tests."""
    # Create mock STT service
    mock_stt = MockSTTService()
    # Add attributes that health endpoint expects
    mock_stt.model_size = "base"
    mock_stt.device = "cpu"

    # Set in app state
    app.state.stt_service = mock_stt
    yield
    # Cleanup
    if hasattr(app.state, "stt_service"):
        del app.state.stt_service


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app.

    Use this fixture for async tests that need to make HTTP requests
    to the FastAPI app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Use in-memory SQLite for tests
    test_db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with async_session() as session:
        # Override get_db dependency
        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db

        yield session

        # Cleanup
        app.dependency_overrides.clear()

    # Dispose engine
    await engine.dispose()
