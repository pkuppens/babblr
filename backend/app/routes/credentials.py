"""
Credentials management API

This module provides endpoints for managing API credentials received from the frontend.
Credentials are stored in-memory during runtime and provided by the Electron app
via secure storage (safeStorage).

Note: This API does NOT store credentials itself - it receives them from the frontend
which manages secure storage using Electron's platform-specific encryption.
"""

import logging
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/credentials", tags=["credentials"])


# ============================================================================
# In-Memory Credential Store
# ============================================================================
# This stores credentials provided by the frontend during runtime.
# The frontend manages persistence using Electron safeStorage.
class CredentialStore:
    """In-memory store for API credentials provided by frontend"""

    def __init__(self):
        self._credentials: dict[str, dict[str, str]] = {}

    def set_credential(self, provider: str, credential_type: str, value: str) -> None:
        """Store a credential"""
        if provider not in self._credentials:
            self._credentials[provider] = {}
        self._credentials[provider][credential_type] = value
        logger.info(f"Stored credential for {provider}:{credential_type}")

    def get_credential(self, provider: str, credential_type: str) -> Optional[str]:
        """Retrieve a credential"""
        return self._credentials.get(provider, {}).get(credential_type)

    def delete_credential(self, provider: str, credential_type: str) -> None:
        """Delete a credential"""
        if provider in self._credentials:
            self._credentials[provider].pop(credential_type, None)
            if not self._credentials[provider]:
                del self._credentials[provider]
            logger.info(f"Deleted credential for {provider}:{credential_type}")

    def list_credentials(self) -> list[dict[str, str]]:
        """List all stored credentials (returns metadata only, no values)"""
        credentials = []
        for provider, creds in self._credentials.items():
            for cred_type in creds.keys():
                credentials.append(
                    {
                        "provider": provider,
                        "type": cred_type,
                    }
                )
        return credentials

    def has_credential(self, provider: str, credential_type: str) -> bool:
        """Check if a credential exists"""
        return self.get_credential(provider, credential_type) is not None


# Global credential store
credential_store = CredentialStore()


# ============================================================================
# Pydantic Models
# ============================================================================
class CredentialStoreRequest(BaseModel):
    """Request to store a credential"""

    provider: str = Field(..., description="Provider name (e.g., 'anthropic', 'google', 'openai')")
    type: Literal["api-key", "token"] = Field(..., description="Credential type")
    value: str = Field(..., description="Credential value")


class CredentialResponse(BaseModel):
    """Response for credential operations"""

    success: bool
    message: Optional[str] = None


class CredentialListResponse(BaseModel):
    """Response for listing credentials"""

    success: bool
    credentials: list[dict[str, str]]


# ============================================================================
# API Endpoints
# ============================================================================
@router.post("/store", response_model=CredentialResponse)
async def store_credential(request: CredentialStoreRequest):
    """
    Store a credential in memory.

    The frontend provides credentials via Electron secure storage.
    This endpoint receives them and stores them in memory for LLM provider use.

    Note: Clears the LLM provider cache to ensure new credentials are used.
    """
    try:
        credential_store.set_credential(request.provider, request.type, request.value)

        # Clear provider cache so new credentials are picked up
        from app.services.llm import ProviderFactory

        ProviderFactory.clear_cache()

        return CredentialResponse(success=True, message=f"Credential stored for {request.provider}")
    except Exception as e:
        logger.error(f"Failed to store credential: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=CredentialListResponse)
async def list_credentials():
    """
    List all stored credentials (metadata only, no values).

    Returns a list of {provider, type} pairs.
    """
    try:
        credentials = credential_store.list_credentials()
        return CredentialListResponse(success=True, credentials=credentials)
    except Exception as e:
        logger.error(f"Failed to list credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{provider}/{credential_type}", response_model=CredentialResponse)
async def delete_credential(provider: str, credential_type: str):
    """
    Delete a credential from memory.

    Note: Clears the LLM provider cache to ensure deleted credentials are no longer used.
    """
    try:
        credential_store.delete_credential(provider, credential_type)

        # Clear provider cache so deleted credentials are no longer used
        from app.services.llm import ProviderFactory

        ProviderFactory.clear_cache()

        return CredentialResponse(
            success=True, message=f"Credential deleted for {provider}:{credential_type}"
        )
    except Exception as e:
        logger.error(f"Failed to delete credential: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Helper Functions (for use by other modules)
# ============================================================================
def get_api_key(provider: str) -> Optional[str]:
    """
    Get API key for a provider.
    Used by LLM provider factory to retrieve credentials.

    Args:
        provider: Provider name ('anthropic', 'google', 'openai')

    Returns:
        API key if available, None otherwise
    """
    return credential_store.get_credential(provider, "api-key")
