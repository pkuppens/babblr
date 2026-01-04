from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    anthropic_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"
    whisper_model: str = "base"
    host: str = "127.0.0.1"
    port: int = 8000
    database_url: str = "sqlite+aiosqlite:///./babblr.db"
    frontend_url: str = "http://localhost:3000"
    timezone: str = "Europe/Amsterdam"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
