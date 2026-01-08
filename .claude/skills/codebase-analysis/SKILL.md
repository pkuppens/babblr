---
name: codebase-analysis
description: Analyze codebase for existing implementations, test coverage, and code patterns. Use when checking what's already implemented, finding related code, or assessing test coverage for features.
allowed-tools: Glob, Grep, Read, Bash(uv run pytest:*)
---

# Codebase Analysis

This skill provides capabilities for analyzing code implementations and test coverage.

## Finding Related Code

### Search by Keywords
```bash
# Find files containing keyword
grep -r "keyword" --include="*.py" backend/app/

# Find function/class definitions
grep -rn "def function_name\|class ClassName" backend/app/
```

### Search by File Pattern
```bash
# Find all Python files in a directory
find backend/app -name "*.py" -type f

# Find specific file types
ls backend/app/**/*.py
```

### Using Glob Tool
Search for files matching patterns:
- `backend/app/**/*.py` - All Python files
- `backend/app/routes/*.py` - Route files
- `backend/app/services/**/*.py` - Service files

### Using Grep Tool
Search file contents:
- Pattern: `class.*Provider` - Find provider classes
- Pattern: `def test_` - Find test functions
- Pattern: `@router\.(get|post)` - Find API endpoints

## Checking Implementation Status

### For a Feature
1. Search for related keywords in codebase
2. Check route files for endpoints
3. Check service files for business logic
4. Check model files for data structures

### For an API Endpoint
```bash
# Find route registration
grep -rn "@router" backend/app/routes/

# Find specific endpoint
grep -rn "def endpoint_name" backend/app/routes/
```

### For a Service
```bash
# Find service class
grep -rn "class.*Service" backend/app/services/
```

## Test Coverage Analysis

### List Available Tests
```bash
cd backend && uv run pytest tests/ --collect-only -q
```

### Find Tests for Feature
```bash
cd backend && uv run pytest tests/ --collect-only -q | grep -i "keyword"
```

### Run Specific Tests
```bash
cd backend && uv run pytest tests/test_file.py -v
cd backend && uv run pytest tests/test_file.py::test_function -v
cd backend && uv run pytest tests/ -k "keyword" -v
```

### Check Test Coverage
```bash
cd backend && uv run pytest tests/ -v --tb=short
```

## Architecture Analysis

### Backend Structure
```
backend/app/
├── main.py           # Entry point, router registration
├── config.py         # Settings
├── database/         # Database setup
├── models/           # ORM models, Pydantic schemas
├── routes/           # API endpoints
└── services/         # Business logic
```

### Finding Dependencies
```bash
# What imports a module
grep -rn "from app.services.llm" backend/app/

# What a module imports
head -30 backend/app/services/llm/factory.py | grep "^from\|^import"
```

## Analysis Checklist

When analyzing for implementation status:

- [ ] Search for related keywords/patterns
- [ ] Check if routes exist
- [ ] Check if services exist
- [ ] Check if models exist
- [ ] Check if tests exist
- [ ] Run tests to verify they pass

## Output Format

When reporting analysis results:

```markdown
## Implementation Analysis

### Already Implemented
- [x] Feature A - `backend/app/routes/feature.py:45`
- [x] Feature B - `backend/app/services/service.py:123`

### Test Coverage
- [x] Unit tests for Feature A - `tests/test_feature.py`
- [ ] Integration tests - Not found

### Missing/Needed
- [ ] Feature C endpoint
- [ ] Database migration for new field
```

## Common Patterns

### Check if Feature Exists
1. Search for feature name in codebase
2. Check routes for endpoints
3. Check services for logic
4. Check tests for coverage

### Assess Completeness
1. Compare issue requirements vs implementation
2. Check all acceptance criteria
3. Verify test coverage for each requirement
