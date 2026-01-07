# Babblr Backend

FastAPI backend for the Babblr language learning application.

## Features

- **Speech-to-Text**: OpenAI Whisper for accurate transcription
- **AI Conversation**: Anthropic Claude for natural conversation and error correction
- **Text-to-Speech**: Edge TTS for audio playback
- **Database**: SQLite with SQLAlchemy for conversation and vocabulary storage
- **Languages**: Spanish, Italian, German, French, Dutch

## Setup

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

**Important:** The virtual environment (`.venv`) must be created in the `backend/` directory, not in the project root.

#### Quick Setup (Recommended)

```bash
cd backend
./setup-venv.sh
```

This script creates the virtual environment and installs all dependencies.

#### Manual Setup

1. Install uv if not already installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Navigate to backend directory:
```bash
cd backend
```

3. Create virtual environment and install dependencies:
```bash
# Create venv (creates .venv in current directory)
uv venv

# Install all dependencies from pyproject.toml (including dev dependencies)
uv pip install -e ".[dev]"

# Or install without dev dependencies
# uv pip install -e .
```

**Note:** Always run `uv venv` and `uv pip install` from the `backend/` directory to ensure the virtual environment is created in the correct location.

### Using pip (Alternative)

**On Linux/macOS (bash):**
```bash
# Create venv
python -m venv .venv
source .venv/bin/activate

# Install from pyproject.toml
pip install -e ".[dev]"
```

**On Windows (CMD):**
```cmd
# Create venv
python -m venv .venv
.venv\Scripts\activate

# Install from pyproject.toml
pip install -e ".[dev]"
```

**Note**: `requirements.txt` is kept for backward compatibility but `pyproject.toml` is the primary source.

2. **Configure environment variables:**

   See **[../ENVIRONMENT.md](../ENVIRONMENT.md)** for complete documentation on:
   - How to get your Anthropic API key
   - All configuration options
   - Platform-specific instructions
   - Troubleshooting

   **Quick start:**

   **On Linux/macOS (bash):**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

   **On Windows (CMD):**
   ```cmd
   copy .env.example .env
   REM Edit .env and add your ANTHROPIC_API_KEY
   ```

## Running

**Option 1: Using the convenience script (recommended)**

**Linux/macOS:**
```bash
# From project root
./run-backend.sh
```

**Windows:**
```cmd
REM From project root
run-backend.bat
```

This script automatically uses uv if available, falling back to standard Python if not.

**Option 2: Using uv directly**

**Linux/macOS:**
```bash
cd backend
source .venv/bin/activate  # Activate venv (optional with uv)
babblr-backend            # Run the installed script
```

**Windows:**
```cmd
cd backend
.venv\Scripts\activate.bat  # Activate venv (optional with uv)
babblr-backend              # Run the installed script
```

**Option 3: Using uv run (no activation needed)**
```bash
cd backend
uv run babblr-backend
```

**Option 4: Manual run with Python**

**On Linux/macOS (bash):**
```bash
cd backend
export PYTHONPATH=$(pwd)
cd app
python main.py
```

Or with uvicorn:
```bash
cd backend
export PYTHONPATH=$(pwd)
uvicorn app.main:app --reload
```

**On Windows (CMD):**
```cmd
cd backend
set PYTHONPATH=%CD%
cd app
python main.py
```

Or with uvicorn:
```cmd
cd backend
set PYTHONPATH=%CD%
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Conversations
- `POST /conversations` - Create new conversation
- `GET /conversations` - List all conversations
- `GET /conversations/{id}` - Get specific conversation
- `GET /conversations/{id}/messages` - Get conversation messages
- `GET /conversations/{id}/vocabulary` - Get learned vocabulary
- `DELETE /conversations/{id}` - Delete conversation

### Chat
- `POST /chat` - Send message and get AI response

### Speech-to-Text
- `POST /stt/transcribe` - Transcribe audio to text
- `GET /stt/languages` - Get supported STT locales and metadata
- `GET /stt/models` - Get available Whisper models

### Text-to-Speech
- `POST /tts/synthesize` - Convert text to speech

## Database

SQLite database (`babblr.db`) will be created automatically on first run.

Tables:
- `conversations` - Conversation sessions
- `messages` - Individual messages
- `vocabulary_items` - Learned vocabulary

## Architecture

```
app/
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── database/
│   └── db.py           # Database setup
├── models/
│   ├── models.py       # SQLAlchemy models
│   └── schemas.py      # Pydantic schemas
├── routes/
│   ├── conversations.py # Conversation endpoints
│   ├── chat.py         # Chat endpoints
│   ├── stt.py          # Speech-to-text endpoints
│   └── tts.py          # TTS endpoints
└── services/
    ├── whisper_service.py  # Whisper integration
    ├── claude_service.py   # Claude integration
    └── tts_service.py      # TTS integration
```
