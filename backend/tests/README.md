# Babblr Backend Tests

This directory contains unit and integration tests for the Babblr backend.

## Running Tests

### Unit Tests Only

Unit tests don't require the backend to be running:

```bash
# Using pytest directly
pytest tests/test_unit.py

# Or with verbose output
pytest tests/test_unit.py -v
```

### Integration Tests

Integration tests require the backend server to be running:

```bash
# Terminal 1: Start the backend
cd backend
source venv/bin/activate
export PYTHONPATH=$(pwd)
cd app
python main.py

# Terminal 2: Run integration tests
cd backend
source venv/bin/activate
pytest tests/test_integration.py -v
```

### All Tests

Run all tests (unit + integration):

```bash
# Make sure backend is running first!
pytest tests/ -v
```

### Run Tests by Marker

```bash
# Only integration tests
pytest tests/ -m integration -v

# Only unit tests (exclude integration)
pytest tests/ -m "not integration" -v
```

## Test Structure

- `conftest.py` - Shared fixtures and configuration
- `test_unit.py` - Unit tests (schemas, models, config)
- `test_integration.py` - Integration tests (API endpoints)

## Requirements

Tests require the following packages (included in pyproject.toml):
- pytest>=8.3.4
- pytest-asyncio>=0.24.0
- httpx>=0.28.1

Install with:
```bash
uv pip install -e ".[dev]"
```

Or with pip:
```bash
pip install pytest pytest-asyncio httpx
```
