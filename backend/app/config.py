import sys

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider selection (runtime swappable)
    llm_provider: str = "ollama"  # "ollama", "claude", "gemini", "mock"

    # Common LLM settings
    llm_max_tokens: int = 1000
    llm_temperature: float = 0.7
    llm_timeout: int = 60

    # Retry settings for rate limits
    llm_retry_attempts: int = 3
    llm_retry_base_delay: float = 1.0
    llm_retry_max_delay: float = 30.0

    # Ollama settings (MVP primary)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"

    # Anthropic settings (grouped with ANTHROPIC_ prefix)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Google Gemini settings
    google_api_key: str = ""
    gemini_model: str = "gemini-pro"

    # Whisper settings (Speech-to-Text)
    whisper_model: str = "base"
    whisper_device: str = "auto"  # "auto", "cuda", or "cpu"

    # Babblr API server settings
    babblr_api_host: str = "127.0.0.1"
    babblr_api_port: int = 8000

    # Babblr database settings
    babblr_conversation_database_url: str = "sqlite+aiosqlite:///./babblr.db"

    # Babblr application settings
    babblr_frontend_url: str = "http://localhost:3000"
    babblr_timezone: str = "Europe/Amsterdam"
    babblr_dev_mode: bool = False
    babblr_audio_storage_path: str = "./audio_files"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @model_validator(mode="after")
    def validate_provider_requirements(self) -> "Settings":
        """Validate that required settings are present for the selected provider."""
        provider = self.llm_provider.lower()

        if provider == "claude":
            if (
                not self.anthropic_api_key
                or self.anthropic_api_key == "your_anthropic_api_key_here"
            ):
                print(
                    "[ERROR] LLM_PROVIDER=claude requires ANTHROPIC_API_KEY to be set.\n"
                    "       Get your API key at: https://console.anthropic.com/settings/keys\n"
                    "       Then set it in backend/.env",
                    file=sys.stderr,
                )
                # Don't exit - allow app to start, will fail on first API call with clear error

        elif provider == "gemini":
            if not self.google_api_key:
                print(
                    "[ERROR] LLM_PROVIDER=gemini requires GOOGLE_API_KEY to be set.\n"
                    "       Get your API key at: https://makersuite.google.com/app/apikey\n"
                    "       Then set it in backend/.env",
                    file=sys.stderr,
                )

        return self


settings = Settings()
