# Architecture Requirements

## Purpose

High-level architectural constraints and quality attributes.

## Architecture Style

**Client-Server (Local)**:
- Electron frontend (desktop app)
- FastAPI backend (local server)
- SQLite database (local)

## Quality Attributes

### Modularity
- Pluggable LLM providers
- Swappable STT/TTS services
- Clean separation of concerns

### Extensibility
- Third-party plugins (future)
- Custom integrations
- Community contributions

### Maintainability
- Well-documented codebase
- Comprehensive tests (80%+ coverage)
- CI/CD automation

## Technology Stack

See [CLAUDE.md](../../../CLAUDE.md) for details:
- **Frontend**: Electron, React, TypeScript, Vite
- **Backend**: FastAPI, Python 3.12+, SQLAlchemy
- **LLMs**: Claude, Gemini, Ollama
- **Speech**: Whisper (STT), Edge TTS

## Architectural Constraints

- **Local-First**: No required cloud services
- **Offline-Capable**: Works with Ollama + local Whisper
- **Cross-Platform**: Windows, macOS, Linux

## Related Docs

- [docs/ARCHITECTURE.md](../../ARCHITECTURE.md) - Implementation details
- [CLAUDE.md](../../../CLAUDE.md) - Development architecture

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
