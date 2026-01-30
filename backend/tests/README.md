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

### Manual Live API Check (Not a Pytest Test)

This repository also includes a small manual script that calls the live HTTP API.
It requires the backend to be running, and it is **not** collected by pytest.

```bash
# From the repository root:
python backend/tests/manual_api_check.py

# Or from within backend/:
cd backend
python tests/manual_api_check.py
```

## Test Structure

- `conftest.py` - Shared fixtures and configuration
- `test_unit.py` - Unit tests (schemas, models, config)
- `test_integration.py` - Integration tests (API endpoints)
 - `manual_api_check.py` - Manual live API check (requires backend running)

## Requirements

Tests require the following packages (included in pyproject.toml):
- pytest>=8.3.4
- pytest-asyncio>=0.24.0
- pytest-xdist>=3.6.1 (optional, for parallel runs)
- httpx>=0.28.1

Install with:
```bash
uv pip install -e ".[dev]"
```

Or with pip:
```bash
pip install pytest pytest-asyncio pytest-xdist httpx
```

## Asyncio tests (marker)

Some tests use `@pytest.mark.asyncio`. If you see warnings like `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio`,
ensure you installed the dev dependencies (so `pytest-asyncio` is available) and keep the marker registered in the pytest config.

## Running tests in parallel

You can run tests in parallel using `pytest-xdist`:

```bash
# Use one worker per CPU core (CI / powerful machines)
pytest -n auto

# Use a fixed number of workers (safer when tests load heavy resources)
pytest -n 2
pytest -n 4
```

Pre-commit runs backend tests with `-n 2` (not `-n auto`) because some unit tests load PyTorch and the Whisper model. Using one worker per CPU can spawn many processes each loading a model and lock the system.
