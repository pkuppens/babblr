from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider selection (runtime swappable)
    llm_provider: str = "ollama"  # "ollama", "claude", "gemini", "mock"

    # Ollama settings (MVP primary)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:latest"

    # Claude/Anthropic settings
    anthropic_api_key: str = ""
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        validation_alias=AliasChoices("anthropic_model", "claude_model"),
    )

    # Google Gemini settings
    google_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"  # or gemini-1.5-flash-latest, gemini-1.5-pro

    # Conversation memory settings (Summary Buffer)
    conversation_max_token_limit: int = 2000  # Max tokens before summarizing old messages

    # Common LLM settings
    llm_max_tokens: int = 1000
    llm_temperature: float = 0.7
    llm_timeout: int = 60

    # Retry settings for rate limits
    llm_retry_attempts: int = 3
    llm_retry_base_delay: float = 1.0
    llm_retry_max_delay: float = 30.0

    # Whisper settings
    whisper_model: str = "base"
    whisper_device: str = "auto"  # "auto", "cuda", or "cpu"

    # TTS settings
    tts_voice_spanish: str = "es-ES-AlvaroNeural"
    tts_voice_italian: str = "it-IT-DiegoNeural"
    tts_voice_german: str = "de-DE-ConradNeural"
    tts_voice_french: str = "fr-FR-HenriNeural"
    tts_voice_dutch: str = "nl-NL-MaartenNeural"

    # User language settings
    user_native_language: str = Field(
        default="English",
        validation_alias=AliasChoices("user_native_language", "native_language"),
    )

    # Application settings (BABBLR_ prefixed for consistency)
    babblr_dev_mode: bool = Field(
        default=False,
        validation_alias=AliasChoices("babblr_dev_mode", "development_mode"),
    )
    stt_dump_uploads: bool = False
    babblr_audio_storage_path: str = Field(
        default="./audio_files",
        validation_alias=AliasChoices("babblr_audio_storage_path", "audio_storage_path"),
    )
    babblr_api_host: str = Field(
        default="127.0.0.1",
        validation_alias=AliasChoices("babblr_api_host", "host"),
    )
    babblr_api_port: int = Field(
        default=8000,
        validation_alias=AliasChoices("babblr_api_port", "port"),
    )
    babblr_conversation_database_url: str = Field(
        default="sqlite+aiosqlite:///./babblr.db",
        validation_alias=AliasChoices("babblr_conversation_database_url", "database_url"),
    )
    babblr_frontend_url: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("babblr_frontend_url", "frontend_url"),
    )
    babblr_timezone: str = Field(
        default="Europe/Amsterdam",
        validation_alias=AliasChoices("babblr_timezone", "timezone"),
    )

    # Note: `pydantic-settings` loads all `.env` keys and then validates them.
    # We intentionally ignore unknown keys to avoid breaking startup when `.env`
    # contains variables for other components or older configuration names.
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()
