# Data Requirements

## Purpose

Specifies data models and retention policies.

## Data Model

See [docs/DATABASE_SCHEMA.md](../../DATABASE_SCHEMA.md) for detailed schema.

### Core Tables
- conversations
- messages
- vocabulary
- assessments

## Data Retention

- **Conversations**: Retained indefinitely (user controlled)
- **Vocabulary**: Retained indefinitely
- **Assessments**: Retained indefinitely
- **No Telemetry**: No usage data collected

## Privacy

- **Local-First**: SQLite database in user's home directory
- **User Control**: User owns all data
- **No Cloud**: No required cloud sync

## Backup

User responsible for backing up:
- SQLite database file
- Configuration files

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
