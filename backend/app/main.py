from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.db import init_db
from app.routes import chat, conversations, speech, tts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
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
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(speech.router)
app.include_router(tts.router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Babblr API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "whisper": "loaded",
            "claude": "configured" if settings.anthropic_api_key else "not configured",
            "tts": "available",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)


def main():
    """Entry point for uv script."""
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
