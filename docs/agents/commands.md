# Commands

Command cheat sheet for agents. For the full development workflow, see
[`DEVELOPMENT.md`](../../DEVELOPMENT.md). For Docker, see
[`docker/README.md`](../../docker/README.md).

## Backend (from `backend/`)

```bash
# Run the server
./run-backend.sh                      # from the project root
uv run uvicorn app.main:app --reload  # or directly

# Tests
uv run pytest tests/test_unit.py -vv --tb=short -n 8           # unit, no server
uv run pytest tests/test_llm_providers.py -vv --tb=short -n 8  # LLM providers, mocked
uv run pytest tests/test_integration.py -vv --tb=short -n 8    # integration, server must run
uv run pytest tests/ -vv --tb=short -n 8                       # all
uv run pytest tests/test_unit.py::test_name -vv --tb=short     # one test

# Lint, format, type-check
uv run ruff check .
uv run ruff check --fix .
uv run ruff format .
uv run pyright
```

Test flags: `-vv` verbose, `--tb=short` short tracebacks, `-n 8` run on 8 workers.

## Frontend (from `frontend/`)

```bash
npm run electron:dev     # start Vite and Electron

npm run test             # tests, once
npm run test:watch       # tests, watch mode
npm run test:coverage    # tests with coverage

npm run lint             # ESLint
npm run lint:fix
npm run format           # Prettier

npm run build            # tsc, then Vite build
npm run electron:build   # build the distributable
```

## Docker (from `docker/`)

```bash
# Development mode, with hot reload
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml logs -f
docker-compose -f docker-compose.dev.yml down

# Production mode
docker-compose up -d
docker-compose down

# Rebuild after a dependency change
docker-compose -f docker-compose.dev.yml up -d --build backend

# Open a shell in a service
docker-compose -f docker-compose.dev.yml exec backend /bin/bash
docker-compose -f docker-compose.dev.yml exec frontend /bin/sh

# Run tests in the containers
docker-compose -f docker-compose.dev.yml exec backend uv run pytest tests/ -v
docker-compose -f docker-compose.dev.yml exec frontend npm run test
```

Development mode starts every service with one command, with hot reload
(`uvicorn --reload`, Vite HMR). It includes PostgreSQL and the Ollama LLM
service, so you do not set them up by hand.
