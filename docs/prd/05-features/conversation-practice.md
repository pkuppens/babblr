# Conversation Practice Feature - PRD

## Status

**Current Status**: MVP Complete ✓

## Executive Summary

AI-powered conversational practice is Babblr's core feature, enabling students to practice natural conversation at their CEFR proficiency level.

## User Stories

- STU-001: Start conversation (DONE)
- STU-002: AI responses (DONE)
- STU-003: Error corrections (DONE)
- STU-004: Voice input STT (DONE)
- STU-005: TTS output (DONE)

See [../02-user-stories/story-backlog.md](../02-user-stories/story-backlog.md)

## Requirements

### Functional
- FR-1: Conversation creation and management
- FR-2: LLM integration (Claude, Gemini, Ollama)
- FR-3: CEFR-adaptive responses

### Non-Functional
- NFR-P1: <3s response time (p90)
- NFR-R1: Graceful LLM failures

## Implementation

See:
- [docs/CONVERSATION_FLOW.md](../../CONVERSATION_FLOW.md)
- [backend/app/routes/chat.py](../../../backend/app/routes/chat.py)
- [backend/app/services/llm/](../../../backend/app/services/llm/)

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
**Status**: Implemented
