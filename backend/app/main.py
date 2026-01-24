import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse

from app.config import settings
from app.database.db import AsyncSessionLocal, init_db

logger = logging.getLogger(__name__)
from app.routes import (
    assessments,
    chat,
    conversations,
    credentials,
    grammar,
    lessons,
    progress,
    stt,
    topics,
    tts,
    user_levels,
    vocabulary,
)
from app.services.assessment_seed import seed_assessment_data
from app.services.llm import ProviderFactory
from app.services.tts_service import tts_service
from app.services.whisper_service import whisper_service

_STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup.

    Handles database initialization, migrations, and data seeding with proper error handling.
    """
    try:
        logger.info("Starting application initialization...")
        await init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        error_msg = (
            f"Failed to initialize database during startup: {e}\n"
            "The application cannot start without a properly initialized database.\n"
            "Please check the error above and ensure:\n"
            "1. Database file permissions are correct\n"
            "2. No other process is using the database\n"
            "3. The database file is not corrupted"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    # Seed assessment data for Spanish (idempotent - safe to call multiple times)
    try:
        logger.info("Seeding assessment data...")
        async with AsyncSessionLocal() as session:
            await seed_assessment_data(session, language="es")
        logger.info("Assessment data seeding completed successfully")
    except Exception as e:
        # Log error but don't fail startup - assessment seeding is not critical
        logger.warning(
            f"Failed to seed assessment data (non-critical): {e}\n"
            "The application will continue, but assessments may not be available."
        )

    yield


# Create FastAPI application
app = FastAPI(
    title="Babblr API",
    description="Language learning app with AI tutor - Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.babblr_frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(tts.router)
app.include_router(stt.router)
app.include_router(topics.router)
app.include_router(vocabulary.router)
app.include_router(grammar.router)
app.include_router(lessons.router)
app.include_router(assessments.router)
app.include_router(user_levels.router)
app.include_router(progress.router)
app.include_router(credentials.router)


@app.get("/favicon.svg", include_in_schema=False)
async def favicon_svg():
    """Serve the Babblr favicon as an SVG.

    The SVG is stored under app/static to keep backend assets co-located
    with the FastAPI app, and to avoid relying on the current working
    directory when the server is started.
    """
    return FileResponse(_STATIC_DIR / "favicon.svg", media_type="image/svg+xml")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon_ico():
    """Redirect /favicon.ico to the SVG favicon to avoid 404s in browsers."""
    return RedirectResponse(url="/favicon.svg", status_code=307)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Babblr API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Detailed health check."""
    # Check if Claude API key is properly configured (not placeholder)
    claude_configured = (
        settings.anthropic_api_key and settings.anthropic_api_key != "your_anthropic_api_key_here"
    )

    # Ollama model listing is best-effort: backend should still be healthy if Ollama is down.
    ollama_available_models: list[str] | None = None
    try:
        ollama = ProviderFactory.get_provider("ollama")
        # Check if provider has list_models method (OllamaProvider specific)
        if hasattr(ollama, "list_models") and callable(getattr(ollama, "list_models", None)):
            ollama_available_models = await ollama.list_models()  # type: ignore[attr-defined]
    except Exception:
        ollama_available_models = None

    whisper_cuda = (
        whisper_service.get_cuda_info() if hasattr(whisper_service, "get_cuda_info") else {}
    )

    return {
        "status": "healthy",
        "database": "connected",
        "llm_provider": settings.llm_provider,
        "services": {
            "whisper": {
                "status": "loaded",
                "current_model": settings.whisper_model,
                "supported_models": whisper_service.get_available_models(),
                "supported_locales": (
                    whisper_service.get_supported_locales()  # type: ignore[attr-defined]
                    if hasattr(whisper_service, "get_supported_locales")
                    else whisper_service.get_supported_languages()
                ),
                "runtime": whisper_cuda,
            },
            "claude": "configured" if claude_configured else "not configured",
            "ollama": {
                "status": "configured",
                "base_url": settings.ollama_base_url,
                "configured_model": settings.ollama_model,
                "available_models": ollama_available_models,
            },  # Availability checked at request time
            "tts": {
                "status": "available" if tts_service.is_edge_tts_available() else "unavailable",
                "backend": "edge-tts" if tts_service.is_edge_tts_available() else None,
                "supported_locales": tts_service.get_supported_locales(),
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    # When run directly (python main.py), start without reload.
    # For development with auto-reload, use: uvicorn main:app --reload
    uvicorn.run(
        "main:app",
        host=settings.babblr_api_host,
        port=settings.babblr_api_port,
    )


def main():
    """Start the Babblr backend API server (production mode, no reload).

    For development with auto-reload, use: uv run uvicorn app.main:app --reload
    or run the helper script: ./run-backend.sh dev
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.babblr_api_host,
        port=settings.babblr_api_port,
    )
