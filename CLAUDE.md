# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Note**: This is a living document. Update it when project conventions change (e.g., documentation moves to `docs/` folder, new commands are added).

## Working Style

**Be a critical thinker, not a yes-machine.** The user may not know everything, and that's fine. Your job is to:

- **Challenge assumptions** when you see potential issues, gaps, or better alternatives
- **Point out risks** before they become problems (security, performance, maintainability)
- **Ask clarifying questions** rather than guessing or making silent assumptions
- **Disagree respectfully** when you have technical concerns - explain your reasoning
- **Suggest improvements** even when not explicitly asked, if you notice something off

However, **the user remains in control**. After voicing concerns:
- Accept the user's final decision
- Implement what they ask, even if you suggested otherwise
- Don't repeat objections after they've been acknowledged

This applies to code, architecture, documentation, and process decisions.

## Project Overview

Babblr is a desktop language learning app for conversational practice with an AI tutor. It supports Spanish, Italian, German, French, and Dutch with adaptive CEFR difficulty levels (A1-C2).

## Quick Commands

### Backend (from `backend/` directory)

```bash
# Run backend server
./run-backend.sh                    # From project root
uv run uvicorn app.main:app --reload  # Or directly

# Run tests
uv run pytest tests/test_unit.py -v           # Unit tests (no server needed)
uv run pytest tests/test_llm_providers.py -v  # LLM provider tests
uv run pytest tests/test_integration.py -v    # Integration tests (server must be running)
uv run pytest tests/ -v                        # All tests

# Single test
uv run pytest tests/test_unit.py::test_function_name -v

# Linting and formatting
uv run ruff check .           # Check
uv run ruff check --fix .     # Auto-fix
uv run ruff format .          # Format

# Type checking
uv run pyright
```

### Frontend (from `frontend/` directory)

```bash
# Development
npm run electron:dev          # Start Vite + Electron

# Linting and formatting
npm run lint                  # ESLint check
npm run lint:fix              # Auto-fix
npm run format                # Prettier format

# Build
npm run build                 # TypeScript + Vite build
npm run electron:build        # Create distributable
```

## Architecture

### Backend (`backend/app/`)

```
app/
├── main.py                 # FastAPI entry point, router registration
├── config.py               # Settings from environment variables
├── database/               # SQLAlchemy setup, async SQLite
├── models/
│   ├── models.py           # SQLAlchemy ORM models
│   └── schemas.py          # Pydantic request/response schemas
├── routes/                 # API endpoints
│   ├── chat.py             # POST /chat - conversation with LLM
│   ├── conversations.py    # Conversation CRUD
│   ├── stt.py              # Speech-to-text (Whisper)
│   └── tts.py              # Text-to-speech (Edge TTS)
└── services/
    ├── llm/                # Swappable LLM provider architecture
    │   ├── base.py         # Abstract BaseLLMProvider class
    │   ├── factory.py      # ProviderFactory.get_provider()
    │   └── providers/      # Implementations: claude, ollama, mock
    ├── whisper_service.py  # Local Whisper STT
    └── tts_service.py      # Edge TTS
```

**LLM Provider Pattern**: All LLM providers inherit from `BaseLLMProvider` and implement `generate()` and `health_check()`. Use `ProviderFactory.get_provider("ollama"|"claude"|"mock")` to get instances. Default provider is set via `LLM_PROVIDER` env var.

### Frontend (`frontend/src/`)

```
src/
├── App.tsx                 # Main app, state management
├── components/             # React components
└── services/api.ts         # Axios API client
```

## Key Patterns

### Adding a New API Endpoint

1. Create route in `backend/app/routes/my_feature.py`
2. Define Pydantic schemas in `models/schemas.py`
3. Register router in `main.py`: `app.include_router(my_feature.router)`

### Adding a New LLM Provider

1. Create `backend/app/services/llm/providers/my_provider.py`
2. Inherit from `BaseLLMProvider`, implement `generate()` and `health_check()`
3. Register in `factory.py`

## Testing Strategy

- **Unit tests** (`test_unit.py`): Schemas, models, config - run without server
- **LLM provider tests** (`test_llm_providers.py`): Provider logic with mocks
- **Integration tests** (`test_integration.py`): Full API - require running server

Use `@pytest.mark.integration` marker for integration tests.

## Environment

Backend requires `.env` file (copy from `.env.example`):
- `LLM_PROVIDER`: `ollama` (default), `claude`, or `mock`
- `ANTHROPIC_API_KEY`: Required if using Claude provider
- `OLLAMA_MODEL`: Default `llama3.2:latest`

## Shell Script Convention

**Never use Unicode/emoji in `.sh` or `.bat` files.** Use ASCII prefixes:
- `[OK]`, `[ERROR]`, `[WARNING]`, `[INFO]`, `[SETUP]`, `[START]`

## Documentation Location

Documentation files are currently in the project root. Key files:
- `VALIDATION.md` - Smoke test checklist
- `ENVIRONMENT.md` - API key configuration
- `DEVELOPMENT.md` - Development workflow
- `backend/tests/README.md` - Test documentation
