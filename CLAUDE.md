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

## Startup: Branch Check

**At the start of every conversation**, check which git branch you're on:

```bash
git branch --show-current
```

**If on `main` branch:**
1. **Stop and alert the user** - Direct commits to main are not allowed
2. Ask the user to switch to an existing feature branch or create a new one:
   ```bash
   # List existing branches
   git branch -a

   # Switch to existing branch
   git checkout feature/existing-branch

   # Or create new branch
   git checkout -b feature/new-feature-name
   ```
3. **Do not make any code changes until on a feature branch**

This ensures all changes go through pull requests for proper review and CI checks.

## Project Overview

Babblr is a desktop language learning app for conversational practice with an AI tutor. It supports Spanish, Italian, German, French, Dutch, and English with adaptive CEFR difficulty levels (A1-C2).

## Quick Commands

### Backend (from `backend/` directory)

```bash
# Run backend server
./run-backend.sh                    # From project root
uv run uvicorn app.main:app --reload  # Or directly

# Run tests
uv run pytest tests/test_unit.py -vv --tb=short -n 8           # Unit tests (no server needed)
uv run pytest tests/test_llm_providers.py -vv --tb=short -n 8  # LLM provider tests
uv run pytest tests/test_integration.py -vv --tb=short -n 8    # Integration tests (server must be running)
uv run pytest tests/ -vv --tb=short -n 8                        # All tests

# Single test (no parallelization needed)
uv run pytest tests/test_unit.py::test_function_name -vv --tb=short

# Test flags explained:
# -vv: Very verbose output (shows test names and progress)
# --tb=short: Shorter traceback format for failed tests
# -n 8: Run tests in parallel using 8 workers (optimal for local development)

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

# Run tests
npm run test                  # Run tests once
npm run test:watch            # Run tests in watch mode
npm run test:coverage         # Run tests with coverage

# Linting and formatting
npm run lint                  # ESLint check
npm run lint:fix              # Auto-fix
npm run format                # Prettier format

# Build
npm run build                 # TypeScript + Vite build
npm run electron:build        # Create distributable
```

### Docker (from `docker/` directory)

```bash
# Development mode with hot-reload
docker-compose -f docker-compose.dev.yml up -d        # Start all services
docker-compose -f docker-compose.dev.yml logs -f      # View logs
docker-compose -f docker-compose.dev.yml down         # Stop services

# Production mode
docker-compose up -d                                  # Start all services
docker-compose down                                   # Stop services

# Rebuild after dependency changes
docker-compose -f docker-compose.dev.yml up -d --build backend

# Access service shells
docker-compose -f docker-compose.dev.yml exec backend /bin/bash
docker-compose -f docker-compose.dev.yml exec frontend /bin/sh

# Run tests in containers
docker-compose -f docker-compose.dev.yml exec backend uv run pytest tests/ -v
docker-compose -f docker-compose.dev.yml exec frontend npm run test
```

**Development Mode Benefits:**
- All services start with one command
- Hot-reload enabled (uvicorn --reload, Vite HMR)
- PostgreSQL included (no manual setup)
- Ollama LLM service included
- Code changes reflect immediately

See [docker/README.md](docker/README.md) for detailed Docker documentation.

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
│   ├── topics.py           # GET /topics - topic suggestions
│   ├── stt.py              # Speech-to-text (Whisper)
│   └── tts.py              # Text-to-speech (Edge TTS)
└── services/
    ├── llm/                # Swappable LLM provider architecture
    │   ├── base.py         # Abstract BaseLLMProvider class
    │   ├── factory.py      # ProviderFactory.get_provider()
    │   └── providers/      # Implementations: claude, gemini, ollama, mock
    ├── prompt_builder.py   # LangChain-based prompt construction
    ├── conversation_service.py  # Conversation business logic
    ├── language_catalog.py # Supported languages configuration
    ├── whisper_service.py  # Local Whisper STT
    ├── stt_correction_service.py  # STT output correction
    └── tts_service.py      # Edge TTS
```

**LLM Provider Pattern**: All LLM providers inherit from `BaseLLMProvider` and implement `generate()` and `health_check()`. Use `ProviderFactory.get_provider("ollama"|"claude"|"gemini"|"mock")` to get instances. Default provider is set via `LLM_PROVIDER` env var.

### Frontend (`frontend/src/`)

```
src/
├── App.tsx                 # Main app, tab navigation, global state
├── screens/                # Tab-based screens (Home, Conversations, etc.)
├── components/             # Reusable React components
├── hooks/                  # Custom hooks (useAudioRecorder, useTTS, useRetry)
├── services/               # API client and settings persistence
├── types/                  # TypeScript type definitions
└── utils/                  # Helpers (CEFR, translations, TTS sanitizer)
```

**Tab Navigation**: The app uses a tab-based architecture with screens for Home, Vocabulary, Grammar, Conversations, Assessments, and Configuration. State for active conversation is preserved across tab switches.

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
- `LLM_PROVIDER`: `ollama` (default), `claude`, `gemini`, or `mock`
- `ANTHROPIC_API_KEY`: Required if using Claude provider
- `GOOGLE_API_KEY`: Required if using Gemini provider
- `OLLAMA_MODEL`: Default `llama3.2:latest`

## Git Workflow

See `POLICIES.md` for complete policies. Key points:

**Branch naming**: `feature/ISSUE_NUMBER-short-description` (e.g., `feature/123-add-user-auth`)

**Commit message format**: `#ISSUE_NUMBER: type: description`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Example: `#123: feat: add user authentication endpoint`

**PR requirements**: Link to issue, tests pass, pre-commit hooks pass.

## Shell Script Convention

**Never use Unicode/emoji in `.sh` or `.bat` files.** Use ASCII prefixes:
- `[OK]`, `[ERROR]`, `[WARNING]`, `[INFO]`, `[SETUP]`, `[START]`

## GitHub Actions and CI/CD

### Workflow Overview

Babblr uses three main workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`)
   - Runs on: Push to main, PRs, feature branches
   - Jobs: Backend lint/test (Python 3.11, 3.12), frontend test, markdown checks
   - Duration: ~4 min (PR), ~12 min (main with integration tests)

2. **Security Workflow** (`.github/workflows/security.yml`)
   - Runs on: Push to main, PRs, weekly schedule (Mondays)
   - Jobs: CodeQL, Gitleaks, pip-audit, npm audit
   - Duration: ~10 min

3. **Release Workflow** (`.github/workflows/release.yml`)
   - Runs on: Git tags (`v*.*.*`), manual dispatch
   - Jobs: Build backend/frontend, generate attestations, create release
   - Duration: ~15 min

### Composite Actions

Reusable actions in `.github/actions/`:
- `setup-python` - Python + UV setup with caching
- `setup-node` - Node.js setup with npm caching
- `ruff` - Ruff format and lint checks
- `run-backend-tests` - Backend pytest runner
- `run-frontend-tests` - Frontend test runner

### Key Features

**Concurrency Control**: Cancels stale PR runs automatically
**Fail-Fast Matrices**: Stops Python 3.11 tests if 3.12 fails
**Conditional Execution**: Integration tests only on main or labeled PRs
**Smart Caching**: UV deps, Whisper models, pytest cache, npm cache
**Least Privilege**: Default `contents: read`, elevate per-job

### Integration Tests

Integration tests only run on `main` branch by default. To run on PR:
1. Add `run-integration` label to PR
2. Push commit or re-run workflow

### Modifying Workflows

**IMPORTANT**: All changes to `.github/workflows/**` and `.github/actions/**` require approval from @pkuppens per CODEOWNERS.

**Testing workflow changes**:
1. Create feature branch
2. Modify workflow file
3. Push to trigger workflow
4. View results in Actions tab
5. Iterate until working

### Pre-push Checks

Before pushing, run local checks to predict CI success:

```bash
# Backend
cd backend
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest tests/test_unit.py -vv --tb=short -n 8

# Frontend
cd frontend
npm run lint
npm run format -- --check
npm run test
npm audit --audit-level=moderate
```

### CI Failure Debugging

If CI fails:
1. View logs in Actions tab
2. Reproduce locally with exact command
3. Fix issue
4. Push or re-run workflow

See `docs/ci/GITHUB_ACTIONS_GUIDE.md` for detailed troubleshooting.

### Security Scanning

Weekly security scans run automatically:
- CodeQL for Python and TypeScript
- Gitleaks for secrets
- pip-audit for Python dependencies
- npm audit for Node.js dependencies

View results in Security tab → Code scanning.

See `docs/ci/SECURITY_SCANNING.md` for details.

## Documentation Location

Documentation files are currently in the project root. Key files:
- `POLICIES.md` - Git workflow, commit messages, PR requirements, GitHub Actions policies
- `VALIDATION.md` - Smoke test checklist
- `ENVIRONMENT.md` - API key configuration
- `DEVELOPMENT.md` - Development workflow
- `backend/tests/README.md` - Test documentation
- `docs/ci/CI_PIPELINE.md` - CI/CD pipeline architecture
- `docs/ci/GITHUB_ACTIONS_GUIDE.md` - GitHub Actions developer guide
- `docs/ci/SECURITY_SCANNING.md` - Security scanning tools and processes
