# Data Privacy Requirements

## Purpose

Data privacy principles and policies.

## Privacy Principles

### 1. Local-First
- SQLite database stored locally
- No required cloud account
- User controls all data

### 2. Transparency
- Clear about what data goes where
- Conversations sent only to chosen LLM
- No hidden telemetry

### 3. User Control
- User chooses LLM provider
- User can delete conversations
- User can export data

### 4. No Data Sales
- Never sell user data
- No advertising
- No tracking

## Data Flows

| Data Type | Where It Goes | Why |
|-----------|---------------|-----|
| Conversations | User-chosen LLM (Claude/Gemini/Ollama) | Generate responses |
| Speech Audio | Local Whisper (no network) | Transcription |
| Vocabulary | Local SQLite only | Storage |
| API Keys | Local .env file only | Authentication |

## Future GDPR Considerations

When expanding to EU:
- Right to access (export)
- Right to deletion (delete button)
- Right to portability (export formats)

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
