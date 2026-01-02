# Copilot Instructions for babblr

## Project Overview
babblr is a Duolingo successor designed to help users learn foreign languages in a conversational way with adaptive difficulty. The project aims to provide an engaging, interactive language learning experience through natural AI-powered conversations with support for Spanish, Italian, German, French, and Dutch.

## Technology Stack

### Frontend
- **Framework**: Electron (desktop application)
- **UI Library**: React 18.3+
- **Language**: TypeScript 5.7+
- **Build Tool**: Vite 6.0+
- **Key Libraries**: axios, lucide-react, react-hot-toast

### Backend
- **Framework**: FastAPI (modern Python web framework)
- **Language**: Python 3.12+
- **Package Manager**: uv (fast Python package manager)
- **Database**: SQLite with SQLAlchemy ORM and aiosqlite
- **AI Services**: 
  - Anthropic Claude (conversation and error correction)
  - OpenAI Whisper (speech-to-text, runs locally)
  - Edge TTS (text-to-speech synthesis)
- **Key Libraries**: pydantic, pydantic-settings, python-multipart, python-dotenv

## Code Style and Conventions

### Python (Backend)
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes (follow PEP 257)
- Use descriptive variable and function names
- Keep functions focused and single-purpose
- Configure and use Ruff for linting (configured in pyproject.toml)
- Line length: 100 characters
- Import order: E, F, I, N, W (configured in Ruff)

### TypeScript/React (Frontend)
- Use TypeScript for type safety
- Follow React best practices and hooks conventions
- Use functional components over class components
- Define interfaces/types for props and state
- Keep components small and focused
- Use meaningful component and variable names

## Project Structure
```
babblr/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration management
│   │   ├── database/            # Database setup and connection
│   │   ├── models/              # SQLAlchemy & Pydantic models
│   │   ├── routes/              # API endpoint definitions
│   │   └── services/            # AI service integrations (Claude, Whisper, TTS)
│   ├── tests/                   # Backend tests (unit & integration)
│   ├── pyproject.toml           # Python project configuration & dependencies
│   └── .env.example             # Example environment variables
├── frontend/
│   ├── electron/
│   │   └── main.js              # Electron main process
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API client and service integrations
│   │   ├── types/               # TypeScript type definitions
│   │   └── App.tsx              # Main application component
│   ├── package.json             # Node.js dependencies and scripts
│   └── vite.config.ts           # Vite build configuration
├── setup.sh                     # Automated setup script
├── run-backend.sh               # Backend startup script
└── run-frontend.sh              # Frontend startup script
```

**Architecture principles:**
- Keep language learning logic separate from UI/presentation
- Backend services handle all AI integrations and data persistence
- Frontend communicates with backend via REST API
- Organize code by feature/module within each layer

## Dependencies and Environment

### Backend
- **Python Version**: 3.12+ required
- **Package Manager**: uv (recommended) or pip
- **Virtual Environment**: `.venv` directory (excluded from git)
- **Environment Variables**: Required API keys in `.env` file (see `.env.example`)
  - `ANTHROPIC_API_KEY` - Required for Claude AI integration
  - See `ENVIRONMENT.md` for complete configuration guide
- **Key Dependencies**:
  - fastapi, uvicorn - Web framework and server
  - anthropic - Claude AI client
  - openai-whisper - Local speech-to-text
  - edge-tts - Text-to-speech
  - sqlalchemy, aiosqlite - Database ORM and async SQLite
  - pydantic - Data validation and settings

### Frontend
- **Node.js Version**: 22+ LTS (or 24+ for latest features)
- **Package Manager**: npm
- **Dependencies**: Listed in `frontend/package.json`
- **Build Output**: `frontend/dist/` (excluded from git)
- **Release Builds**: `frontend/release/` (excluded from git)

### Setup Commands
```bash
# Automated setup (recommended)
./setup.sh

# Manual backend setup
cd backend
uv venv
uv pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your API keys

# Manual frontend setup
cd frontend
npm install
```

## Build, Run, and Development Commands

### Backend

**Run the backend server:**
```bash
# Using the run script (from project root)
./run-backend.sh

# Or manually (from backend directory)
cd backend
source .venv/bin/activate
babblr-backend

# Or with uvicorn directly
uvicorn app.main:app --reload
```

**Backend runs at:** http://localhost:8000
- Swagger UI docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Linting:**
```bash
cd backend
ruff check .           # Check for issues
ruff check --fix .     # Auto-fix issues
ruff format .          # Format code
```

### Frontend

**Development mode:**
```bash
# Using the run script (from project root)
./run-frontend.sh

# Or manually (from frontend directory)
cd frontend
npm run electron:dev   # Starts Vite dev server + Electron
```

**Build for production:**
```bash
cd frontend
npm run build          # TypeScript compilation + Vite build
npm run electron:build # Create distributable application
```

**Development server runs at:** http://localhost:5173

**TypeScript checking:**
```bash
cd frontend
npm run build          # Also runs tsc for type checking
```

## Language Learning Specific Guidelines
- Design features with adaptive difficulty in mind
- Focus on conversational and interactive learning approaches
- Consider various language learning methodologies (immersion, spaced repetition, etc.)
- Keep the user experience engaging and motivating

## Testing

### Backend Tests
Located in `backend/tests/` with pytest configuration in `pyproject.toml`.

**Run all tests:**
```bash
cd backend
pytest tests/ -v
```

**Run unit tests only** (don't require backend running):
```bash
cd backend
pytest tests/test_unit.py -v
```

**Run integration tests** (require backend server to be running):
```bash
# Terminal 1: Start backend
./run-backend.sh

# Terminal 2: Run integration tests
cd backend
pytest tests/test_integration.py -v
```

**Test configuration:**
- Test framework: pytest with pytest-asyncio
- Test paths: `tests/` directory
- Async mode: auto (configured in pyproject.toml)

**Testing guidelines:**
- Write tests for new features
- Ensure existing tests pass before submitting changes
- Test edge cases, especially for language processing logic
- Mock external API calls (Claude, Whisper) in unit tests
- Use integration tests for end-to-end API testing

### Frontend Tests
Currently no automated tests configured. Manual testing via Electron app.

## Development Workflow
- Make incremental, focused changes
- Test changes thoroughly before committing (run relevant tests and linting)
- Write clear commit messages that explain the "why" behind changes
- Consider the user experience when implementing new features
- Run linters before committing:
  - Backend: `ruff check --fix . && ruff format .`
  - Frontend: Ensure TypeScript compiles with `npm run build`
- For backend changes, ensure the API server starts successfully
- For frontend changes, test the Electron app in development mode

## Documentation
- Update README.md when adding major features
- Document complex algorithms or unusual approaches
- Keep inline comments focused on "why" rather than "what"
