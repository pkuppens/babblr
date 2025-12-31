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

1. Install uv if not already installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment and install dependencies:
```bash
# Create venv
uv venv

# Install all dependencies from pyproject.toml
uv pip install -e .

# Or install with dev dependencies (includes pytest, ruff, etc.)
uv pip install -e ".[dev]"
```

### Using pip (Alternative)

```bash
# Create venv
python -m venv .venv
source .venv/bin/activate

# Install from pyproject.toml
pip install -e ".[dev]"
```

**Note**: `requirements.txt` is kept for backward compatibility but `pyproject.toml` is the primary source.

2. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Running

**Option 1: Using the convenience script (recommended)**
```bash
cd /path/to/babblr
./run-backend.sh
```

This script automatically uses uv if available, falling back to standard Python if not.

**Option 2: Using uv directly**
```bash
cd backend
source .venv/bin/activate  # Activate venv
babblr-backend            # Run the installed script
```

**Option 3: Using uv run**
```bash
cd backend
uv run babblr-backend
```

**Option 4: Manual run with Python**
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

### Speech
- `POST /speech/transcribe` - Transcribe audio to text

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
│   ├── speech.py       # STT endpoints
│   └── tts.py          # TTS endpoints
└── services/
    ├── whisper_service.py  # Whisper integration
    ├── claude_service.py   # Claude integration
    └── tts_service.py      # TTS integration
```
