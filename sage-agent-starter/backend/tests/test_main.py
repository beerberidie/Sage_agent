"""Basic tests for the Sage Agent backend."""

import pytest
from fastapi.testclient import TestClient


def test_import_app():
    """Test that the app can be imported."""
    from app.main import app

    assert app is not None


def test_app_creation():
    """Test that the FastAPI app is created correctly."""
    from app.main import app

    assert app.title is not None
    assert hasattr(app, "routes")


@pytest.mark.asyncio
async def test_health_check():
    """Test basic health check if endpoint exists."""
    from app.main import app

    client = TestClient(app)

    # Try to access root endpoint
    response = client.get("/")
    # Accept any successful response or 404 (if no root endpoint)
    assert response.status_code in [200, 404, 307]
