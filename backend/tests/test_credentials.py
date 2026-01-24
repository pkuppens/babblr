"""
Unit tests for credential storage service.

Tests the in-memory credential store functionality including:
- Storing and retrieving credentials
- Deleting credentials
- Listing credentials
- Credential isolation between providers
"""

import pytest

from app.routes.credentials import CredentialStore


@pytest.fixture
def credential_store():
    """Provide a fresh credential store for each test."""
    return CredentialStore()


class TestCredentialStore:
    """Test suite for CredentialStore class."""

    def test_store_credential(self, credential_store):
        """Test storing a credential."""
        credential_store.set_credential("anthropic", "api-key", "test-key-123")

        result = credential_store.get_credential("anthropic", "api-key")
        assert result == "test-key-123"

    def test_get_credential(self, credential_store):
        """Test retrieving a stored credential."""
        credential_store.set_credential("google", "api-key", "google-key-456")

        result = credential_store.get_credential("google", "api-key")
        assert result == "google-key-456"

    def test_get_nonexistent_credential(self, credential_store):
        """Test retrieving a credential that doesn't exist returns None."""
        result = credential_store.get_credential("nonexistent", "api-key")
        assert result is None

    def test_delete_credential(self, credential_store):
        """Test deleting a credential."""
        # Store a credential
        credential_store.set_credential("openai", "api-key", "openai-key-789")
        assert credential_store.get_credential("openai", "api-key") == "openai-key-789"

        # Delete it
        credential_store.delete_credential("openai", "api-key")

        # Verify it's gone
        result = credential_store.get_credential("openai", "api-key")
        assert result is None

    def test_delete_nonexistent_credential(self, credential_store):
        """Test deleting a credential that doesn't exist is idempotent."""
        # Should not raise an error
        credential_store.delete_credential("nonexistent", "api-key")

        # Verify store is still empty
        credentials = credential_store.list_credentials()
        assert len(credentials) == 0

    def test_list_credentials(self, credential_store):
        """Test listing all stored credentials."""
        # Store multiple credentials
        credential_store.set_credential("anthropic", "api-key", "anthropic-key")
        credential_store.set_credential("google", "api-key", "google-key")
        credential_store.set_credential("openai", "token", "openai-token")

        # List them
        credentials = credential_store.list_credentials()

        # Verify all are listed
        assert len(credentials) == 3
        assert {"provider": "anthropic", "type": "api-key"} in credentials
        assert {"provider": "google", "type": "api-key"} in credentials
        assert {"provider": "openai", "type": "token"} in credentials

    def test_credential_isolation(self, credential_store):
        """Test that credentials for different providers are isolated."""
        # Store credentials for different providers
        credential_store.set_credential("anthropic", "api-key", "anthropic-value")
        credential_store.set_credential("google", "api-key", "google-value")

        # Verify each can be retrieved independently
        assert credential_store.get_credential("anthropic", "api-key") == "anthropic-value"
        assert credential_store.get_credential("google", "api-key") == "google-value"

        # Delete one
        credential_store.delete_credential("anthropic", "api-key")

        # Verify the other is unaffected
        assert credential_store.get_credential("anthropic", "api-key") is None
        assert credential_store.get_credential("google", "api-key") == "google-value"

    def test_has_credential(self, credential_store):
        """Test checking if a credential exists."""
        # Initially doesn't exist
        assert not credential_store.has_credential("anthropic", "api-key")

        # Store it
        credential_store.set_credential("anthropic", "api-key", "test-key")
        assert credential_store.has_credential("anthropic", "api-key")

        # Delete it
        credential_store.delete_credential("anthropic", "api-key")
        assert not credential_store.has_credential("anthropic", "api-key")

    def test_update_credential(self, credential_store):
        """Test updating an existing credential."""
        # Store initial value
        credential_store.set_credential("anthropic", "api-key", "old-key")
        assert credential_store.get_credential("anthropic", "api-key") == "old-key"

        # Update with new value
        credential_store.set_credential("anthropic", "api-key", "new-key")
        assert credential_store.get_credential("anthropic", "api-key") == "new-key"

    def test_multiple_types_same_provider(self, credential_store):
        """Test storing multiple credential types for the same provider."""
        # Store both api-key and token for the same provider
        credential_store.set_credential("openai", "api-key", "key-value")
        credential_store.set_credential("openai", "token", "token-value")

        # Verify both can be retrieved independently
        assert credential_store.get_credential("openai", "api-key") == "key-value"
        assert credential_store.get_credential("openai", "token") == "token-value"

        # List should show both
        credentials = credential_store.list_credentials()
        assert len(credentials) == 2
        assert {"provider": "openai", "type": "api-key"} in credentials
        assert {"provider": "openai", "type": "token"} in credentials
