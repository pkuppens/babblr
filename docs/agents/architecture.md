# Architecture and patterns

For the full architecture, read [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md) and
the ADRs in [`docs/adr/`](../adr/). This file is the short version plus the
how-to steps that agents use most.

## Layout

### Backend (`backend/app/`)

```
app/
├── main.py                 # FastAPI entry point, router registration
├── config.py               # settings from environment variables
├── database/               # SQLAlchemy setup, async SQLite
├── models/
│   ├── models.py           # SQLAlchemy ORM models
│   └── schemas.py          # Pydantic request and response schemas
├── routes/                 # API endpoints
│   ├── chat.py             # POST /chat - conversation with the LLM
│   ├── conversations.py    # conversation CRUD
│   ├── topics.py           # GET /topics - topic suggestions
│   ├── stt.py              # speech to text (Whisper)
│   └── tts.py              # text to speech (Edge TTS)
└── services/
    ├── llm/                # swappable LLM provider architecture
    │   ├── base.py         # abstract BaseLLMProvider class
    │   ├── factory.py      # ProviderFactory.get_provider()
    │   └── providers/      # claude, gemini, ollama, mock
    ├── prompt_builder.py   # LangChain-based prompt construction
    ├── conversation_service.py
    ├── language_catalog.py # supported languages
    ├── whisper_service.py  # local Whisper STT
    ├── stt_correction_service.py
    └── tts_service.py      # Edge TTS
```

**LLM provider pattern**: every provider inherits from `BaseLLMProvider` and
implements `generate()` and `health_check()`. Call
`ProviderFactory.get_provider("ollama" | "claude" | "gemini" | "mock")` to get an
instance. The `LLM_PROVIDER` environment variable sets the default.

### Frontend (`frontend/src/`)

```
src/
├── App.tsx        # main app, tab navigation, global state
├── screens/       # one screen per tab (Home, Conversations, and so on)
├── components/    # reusable React components
├── hooks/         # custom hooks (useAudioRecorder, useTTS, useRetry)
├── services/      # API client and settings persistence
├── types/         # TypeScript type definitions
└── utils/         # helpers (CEFR, translations, TTS sanitizer)
```

**Tab navigation**: the app has one screen per tab, for Home, Vocabulary,
Grammar, Conversations, Assessments, and Configuration. The active conversation
keeps its state when the user changes tabs.

## How to add an API endpoint

1. Create the route in `backend/app/routes/my_feature.py`.
2. Define the Pydantic schemas in `models/schemas.py`.
3. Register the router in `main.py`: `app.include_router(my_feature.router)`.

## How to add an LLM provider

1. Create `backend/app/services/llm/providers/my_provider.py`.
2. Inherit from `BaseLLMProvider`. Implement `generate()` and `health_check()`.
3. Register the provider in `factory.py`.

## Testing strategy

- **Unit tests** (`test_unit.py`): schemas, models, config. No server needed.
- **LLM provider tests** (`test_llm_providers.py`): provider logic, with mocks.
- **Integration tests** (`test_integration.py`): full API. The server must run.

Mark integration tests with `@pytest.mark.integration`. For more detail, see
[`backend/tests/README.md`](../../backend/tests/README.md).
