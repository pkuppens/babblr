# API Specifications

## Purpose

API design principles and specifications.

## Design Principles

- RESTful design
- JSON request/response
- Standard HTTP status codes
- Clear error messages

## API Documentation

**Live Docs**: http://localhost:8000/docs (Swagger UI)

## Key Endpoints

### POST /chat
- Start or continue conversation
- Request: message, conversation_id, language, cefr_level
- Response: AI message, corrections

### GET /conversations
- List conversation history

### POST /stt
- Speech-to-text transcription
- Request: audio file
- Response: transcribed text

### POST /tts
- Text-to-speech generation
- Request: text, language
- Response: audio file

## Future Versioning

- API versioning via /v1/, /v2/ prefixes
- Backward compatibility maintained for 1 major version

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
