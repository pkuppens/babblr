# Babblr Backend Tests

This directory contains unit and integration tests for the Babblr backend.

## Running Tests

### Unit Tests Only

Unit tests don't require the backend to be running:

```bash
# Using pytest directly
pytest tests/test_unit.py

# With verbose output and parallelization (recommended)
pytest tests/test_unit.py -vv --tb=short -n 8
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
pytest tests/test_integration.py -vv --tb=short -n 8
```

### All Tests

Run all tests (unit + integration):

```bash
# Make sure backend is running first!
pytest tests/ -vv --tb=short -n 8
```

### Run Tests by Marker

```bash
# Only integration tests
pytest tests/ -m integration -vv --tb=short -n 8

# Only unit tests (exclude integration)
pytest tests/ -m "not integration" -vv --tb=short -n 8
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

You can run tests in parallel using `pytest-xdist` **for local development only**:

```bash
# Recommended for local development (high-end PC)
pytest -n 8 -vv --tb=short

# Alternative: Use one worker per CPU core (NOT recommended - can lock system)
pytest -n auto  # Avoid this - spawns too many workers
```

**Why not `-n auto`?** Some unit tests load PyTorch and the Whisper model. Using one worker per CPU core can spawn many processes, each loading a model, which can overwhelm memory and lock up the system.

**Why not use `-n` in CI?** pytest-xdist hangs in GitHub Actions environment without producing any output. CI runs tests sequentially for reliability.

**Recommended settings:**
- **Local development**: `-n 8` provides good parallelization without overwhelming resources
- **GitHub Actions**: Sequential (no `-n` flag) for stability
- **Pre-commit hooks**: `-n 2` with `--timeout=120` to catch hung tests
- **Verbosity flags**: `-vv --tb=short` shows test progress and concise failure info
