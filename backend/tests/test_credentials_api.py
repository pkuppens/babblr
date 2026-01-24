"""
Integration tests for credential API endpoints.

Tests the FastAPI credential endpoints including:
- POST /credentials/store
- GET /credentials/list
- DELETE /credentials/{provider}/{type}
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.credentials import credential_store


@pytest.fixture(autouse=True)
def clear_credential_store():
    """Clear the credential store before and after each test."""
    # Clear before test
    credential_store._credentials.clear()
    yield
    # Clear after test
    credential_store._credentials.clear()


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


class TestCredentialAPI:
    """Test suite for credential API endpoints."""

    def test_store_credential_endpoint(self, client):
        """Test POST /credentials/store endpoint."""
        response = client.post(
            "/credentials/store",
            json={
                "provider": "anthropic",
                "type": "api-key",
                "value": "test-anthropic-key-123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "anthropic" in data["message"]

        # Verify credential was stored
        assert credential_store.get_credential("anthropic", "api-key") == "test-anthropic-key-123"

    def test_store_credential_validation_missing_provider(self, client):
        """Test validation when provider is missing."""
        response = client.post(
            "/credentials/store",
            json={
                "type": "api-key",
                "value": "test-key",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_store_credential_validation_missing_type(self, client):
        """Test validation when type is missing."""
        response = client.post(
            "/credentials/store",
            json={
                "provider": "anthropic",
                "value": "test-key",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_store_credential_validation_missing_value(self, client):
        """Test validation when value is missing."""
        response = client.post(
            "/credentials/store",
            json={
                "provider": "anthropic",
                "type": "api-key",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_store_credential_validation_invalid_type(self, client):
        """Test validation when type is invalid."""
        response = client.post(
            "/credentials/store",
            json={
                "provider": "anthropic",
                "type": "invalid-type",  # Only "api-key" and "token" are valid
                "value": "test-key",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_list_credentials_endpoint(self, client):
        """Test GET /credentials/list endpoint."""
        # Store some credentials first
        credential_store.set_credential("anthropic", "api-key", "anthropic-key")
        credential_store.set_credential("google", "api-key", "google-key")
        credential_store.set_credential("openai", "token", "openai-token")

        response = client.get("/credentials/list")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["credentials"]) == 3

        # Verify credentials metadata (no values)
        credentials = data["credentials"]
        assert {"provider": "anthropic", "type": "api-key"} in credentials
        assert {"provider": "google", "type": "api-key"} in credentials
        assert {"provider": "openai", "type": "token"} in credentials

    def test_list_credentials_empty(self, client):
        """Test listing credentials when none are stored."""
        response = client.get("/credentials/list")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["credentials"]) == 0

    def test_delete_credential_endpoint(self, client):
        """Test DELETE /credentials/{provider}/{type} endpoint."""
        # Store a credential first
        credential_store.set_credential("anthropic", "api-key", "test-key")
        assert credential_store.has_credential("anthropic", "api-key")

        # Delete it
        response = client.delete("/credentials/anthropic/api-key")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "anthropic" in data["message"]

        # Verify it was deleted
        assert not credential_store.has_credential("anthropic", "api-key")

    def test_delete_nonexistent_credential(self, client):
        """Test deleting a credential that doesn't exist."""
        response = client.delete("/credentials/nonexistent/api-key")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_provider_cache_invalidation_on_store(self, client):
        """Test that storing a credential clears the LLM provider cache."""
        from app.services.llm import ProviderFactory

        # Get a provider (caches it)
        provider = ProviderFactory.get_provider("mock")
        assert provider is not None

        # Verify it's cached
        assert "mock" in ProviderFactory._instances

        # Store a credential
        response = client.post(
            "/credentials/store",
            json={
                "provider": "anthropic",
                "type": "api-key",
                "value": "new-key",
            },
        )

        assert response.status_code == 200

        # Verify cache was cleared
        assert len(ProviderFactory._instances) == 0

    def test_provider_cache_invalidation_on_delete(self, client):
        """Test that deleting a credential clears the LLM provider cache."""
        from app.services.llm import ProviderFactory

        # Store a credential and get a provider
        credential_store.set_credential("anthropic", "api-key", "test-key")
        provider = ProviderFactory.get_provider("mock")
        assert provider is not None

        # Verify it's cached
        assert "mock" in ProviderFactory._instances

        # Delete the credential
        response = client.delete("/credentials/anthropic/api-key")

        assert response.status_code == 200

        # Verify cache was cleared
        assert len(ProviderFactory._instances) == 0
