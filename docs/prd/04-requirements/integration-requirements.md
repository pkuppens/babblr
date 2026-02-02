# Integration Requirements

## Purpose

Specifies external API and service dependencies.

## External Services

### LLM Providers

**Anthropic Claude**:
- API: Anthropic Messages API
- Auth: API key (user-provided)
- Models: claude-sonnet-4

**Google Gemini**:
- API: Google AI API
- Auth: API key (user-provided)
- Models: gemini-pro

**Ollama**:
- API: Local Ollama API
- Auth: None (local)
- Models: llama3.2, mistral, etc.

### Speech Services

**OpenAI Whisper**: Local STT (no API)
**Edge TTS**: Free Microsoft TTS

## Offline Operation

- **Ollama**: Fully offline LLM
- **Whisper**: Local STT
- **Edge TTS**: Requires internet (future: local TTS)

## Graceful Degradation

- LLM unavailable → Error message, retry
- STT unavailable → Text input fallback
- TTS unavailable → Silent mode

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
