# Babblr Architecture

This document describes the high-level architecture of Babblr.

## Overview

Babblr is a desktop language learning application built with:
- **Frontend**: Electron + React + TypeScript
- **Backend**: Python FastAPI
- **Database**: SQLite (async via SQLAlchemy)

```
+------------------+     HTTP/REST     +------------------+
|                  | <---------------> |                  |
|  Electron App    |                   |  FastAPI Server  |
|  (React + TS)    |                   |  (Python)        |
|                  |                   |                  |
+------------------+                   +--------+---------+
                                               |
                                               v
                                       +-------+--------+
                                       |                |
                                       |  SQLite DB     |
                                       |  (babblr.db)   |
                                       |                |
                                       +----------------+
```

## Backend Architecture

### Directory Structure

```
backend/app/
├── main.py                 # FastAPI entry point
├── config.py               # Settings from environment
├── database/               # SQLAlchemy setup
├── models/
│   ├── models.py           # ORM models
│   └── schemas.py          # Pydantic schemas
├── routes/                 # API endpoints
│   ├── chat.py             # Conversation with LLM
│   ├── conversations.py    # CRUD operations
│   ├── stt.py              # Speech-to-text
│   └── tts.py              # Text-to-speech
└── services/
    ├── llm/                # LLM provider abstraction
    │   ├── base.py         # Abstract base class
    │   ├── factory.py      # Provider factory
    │   └── providers/      # Implementations
    ├── whisper_service.py  # Local Whisper STT
    └── tts_service.py      # Edge TTS
```

### LLM Provider Pattern

All LLM providers implement `BaseLLMProvider`:

```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages, system_prompt) -> str: ...

    @abstractmethod
    async def health_check(self) -> bool: ...
```

Available providers:
- `claude`: Anthropic Claude API
- `ollama`: Local Ollama instance
- `mock`: Testing mock

Use `ProviderFactory.get_provider(name)` to instantiate.

## Frontend Architecture

### Directory Structure

```
frontend/src/
├── App.tsx                 # Main application
├── components/             # React components
└── services/
    └── api.ts              # Axios API client
```

## Data Flow

### Conversation Flow

```
User speaks
    |
    v
[Whisper STT] --> Text --> [LLM Provider] --> Response
    |                                              |
    v                                              v
Transcription                              [Edge TTS]
                                                   |
                                                   v
                                            Audio playback
```

### Database Schema

- `conversations`: Conversation sessions
- `messages`: Individual messages within conversations
- `settings`: User preferences

## Decision Records

### ADR-001: LLM Provider Abstraction

**Context**: Support multiple LLM backends (Claude, Ollama, local models).

**Decision**: Use abstract base class with factory pattern.

**Consequences**: Easy to add new providers, but adds abstraction layer.

---

*This document should be updated when architectural changes are made.*
