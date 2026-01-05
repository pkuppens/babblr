"""
Custom exceptions for LLM providers.

These exceptions provide structured error handling across all providers.
"""


class LLMError(Exception):
    """Base exception for LLM-related errors."""

    pass


class RateLimitError(LLMError):
    """Raised when the provider's rate limit is exceeded.

    Attributes:
        retry_after: Suggested wait time in seconds before retrying.
    """

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class ProviderUnavailableError(LLMError):
    """Raised when a provider is not available or cannot be reached.

    Attributes:
        provider: Name of the unavailable provider.
        reason: Detailed reason for unavailability.
    """

    def __init__(self, provider: str, reason: str = ""):
        self.provider = provider
        self.reason = reason
        message = f"Provider '{provider}' is unavailable"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class LLMAuthenticationError(LLMError):
    """Raised when authentication with the provider fails.

    Typically indicates an invalid or missing API key.
    """

    pass


class LLMTimeoutError(LLMError):
    """Raised when a request to the provider times out."""

    pass


class LLMContentError(LLMError):
    """Raised when the provider returns invalid or unexpected content."""

    pass
