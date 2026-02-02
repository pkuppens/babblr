# Vocabulary Tracking Feature - PRD

## Status

**Current Status**: In Progress (MVP-3)

## Executive Summary

Automatically track new words/phrases learned in conversations, enabling vocabulary review and spaced repetition.

## User Stories

- STU-011: Track vocabulary learned (In Progress)
- STU-012: Flashcard review (Planned)

## Requirements

### Functional
- FR-4.1: Extract vocabulary from conversations
- FR-4.2: Store with definitions and examples
- FR-4.3: Track mastery scores

### Non-Functional
- NFR-SC2: Support 10,000+ words per language

## Design

### Data Model
```sql
CREATE TABLE vocabulary (
  id INTEGER PRIMARY KEY,
  word TEXT NOT NULL,
  language TEXT NOT NULL,
  definition TEXT,
  example_sentence TEXT,
  mastery_score REAL,
  created_at TIMESTAMP
);
```

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
**Status**: In Development
