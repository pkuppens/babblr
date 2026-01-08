---
name: codebase-analysis
description: Analyze codebase for existing implementations, test coverage, and code patterns. Use when checking what's already implemented, finding related code, or assessing test coverage for features.
allowed-tools: Glob, Grep, Read, Bash(uv run pytest:*)
---

# Codebase Analysis

Analyze code implementations and test coverage using Glob, Grep, and Read tools.

## Search Patterns

**Find code by pattern:**
- `backend/app/**/*.py` - All Python files
- `backend/app/routes/*.py` - Route files
- `backend/app/services/**/*.py` - Service files

**Grep patterns:**
- `class.*Provider` - Provider classes
- `def test_` - Test functions
- `@router\.(get|post)` - API endpoints

## Check Implementation Status

1. Search for related keywords in codebase
2. Check route files for endpoints
3. Check service files for business logic
4. Check model files for data structures

## Test Coverage

```bash
# List tests
cd backend && uv run pytest tests/ --collect-only -q

# Run specific tests
cd backend && uv run pytest tests/test_file.py -v
cd backend && uv run pytest tests/ -k "keyword" -v
```

## Backend Structure

```
backend/app/
├── main.py           # Entry point, router registration
├── config.py         # Settings
├── database/         # Database setup
├── models/           # ORM models, Pydantic schemas
├── routes/           # API endpoints
└── services/         # Business logic
```

## Output Format

```markdown
## Implementation Analysis

### Already Implemented
- [x] Feature A - `backend/app/routes/feature.py:45`

### Test Coverage
- [x] Unit tests - `tests/test_feature.py`
- [ ] Integration tests - Not found

### Missing/Needed
- [ ] Feature C endpoint
```
