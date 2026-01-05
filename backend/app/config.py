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
    claude_model: str = "claude-sonnet-4-20250514"

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

    # Application settings
    development_mode: bool = False
    audio_storage_path: str = "./audio_files"
    host: str = "127.0.0.1"
    port: int = 8000
    database_url: str = "sqlite+aiosqlite:///./babblr.db"
    frontend_url: str = "http://localhost:3000"
    timezone: str = "Europe/Amsterdam"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
