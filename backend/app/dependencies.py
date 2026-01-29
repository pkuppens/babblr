"""FastAPI dependencies for dependency injection.

This module provides dependency functions for injecting services into routes,
enabling easy testing and swapping implementations.
"""

from fastapi import Request

from app.services.stt.base import STTService


def get_stt_service(request: Request) -> STTService:
    """Dependency to get STT service from app state.

    This allows routes to use STT service via dependency injection,
    enabling easy mocking for testing.

    Args:
        request: FastAPI request object

    Returns:
        STT service instance from app state
    """
    return request.app.state.stt_service
