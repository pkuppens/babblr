# Docker Setup Guide

This guide explains how to run Babblr using Docker and Docker Compose, with support for both **development** (hot-reload) and **production** modes.

## Directory Structure

All Docker orchestration files are located in the `docker/` directory:
- `docker-compose.base.yml` - Shared infrastructure (volumes, networks)
- `docker-compose.dev.yml` - Development services with hot-reload
- `docker-compose.yml` - Production services
- `.env.template` - Environment configuration template
- `README.md` - This file

**Modular Design:**
The compose files are separated by concern:
- **Base**: Infrastructure (volumes, networks) - can be tested independently
- **Dev/Prod**: Services that use the base infrastructure

Application-specific Docker files remain in their respective directories:
- `backend/Dockerfile`, `backend/Dockerfile.dev`, `backend/.dockerignore`
- `frontend/Dockerfile`, `frontend/Dockerfile.dev`, `frontend/.dockerignore`, `frontend/nginx.conf`

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0+)
- At least 8GB RAM available for Docker
- (Optional) NVIDIA GPU with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU acceleration

## Quick Start (Development Mode)

**1. Clone the repository:**
```bash
git clone https://github.com/pkuppens/babblr.git
cd babblr
```

**2. Create environment file:**
```bash
cd docker
cp .env.template .env
# Edit .env and add your API keys if using Claude or Gemini
```

**3. Start all services:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d
```

**Note:** The `-f` flag is used twice to compose multiple files together. The base file defines infrastructure, and the dev file defines services.

**4. Pull Ollama model (first time only):**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec ollama ollama pull llama3.2:latest
```

**5. Access the application:**
- **Frontend:** http://localhost:5173 (Vite dev server with HMR)
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Development vs Production Mode

### Development Mode (`docker-compose.dev.yml`)

**Features:**
- ✅ Hot-reload for backend (uvicorn --reload)
- ✅ Hot-reload for frontend (Vite HMR)
- ✅ Source code mounted as volumes
- ✅ Includes dev dependencies
- ✅ Fast iteration for active development

**Use when:** Making code changes and need instant feedback

**Command:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d
```

### Production Mode (`docker-compose.yml`)

**Features:**
- ✅ Multi-stage Docker builds (optimized images)
- ✅ Frontend served via Nginx
- ✅ Smaller image sizes
- ✅ Production-ready configuration
- ⚠️ Requires rebuild after code changes

**Use when:** Testing production builds before deployment

**Command:**
```bash
docker-compose up -d
```

## Service Architecture

The Docker Compose setup includes these services:

| Service | Port | Description |
|---------|------|-------------|
| **backend** | 8000 | FastAPI backend with Whisper STT |
| **frontend** | 5173 (dev) / 3000 (prod) | React web app (Vite dev or Nginx) |
| **postgres** | 5432 | PostgreSQL 16 database |
| **ollama** | 11434 | Local LLM service (Ollama) |
| **redis** | 6379 | Optional caching layer |

## Common Commands

### Starting Services

```bash
# Development mode (hot-reload)
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d

# Production mode
docker-compose up -d

# Start specific service only
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d backend
```

### Viewing Logs

```bash
# All services
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml logs --tail=100 backend
```

### Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml down -v
```

### Rebuilding After Code Changes

**Development mode:** No rebuild needed (code is mounted)

**Production mode:**
```bash
# Rebuild specific service
docker-compose up -d --build backend

# Rebuild all services
docker-compose up -d --build
```

### Database Management

```bash
# Access PostgreSQL shell
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec postgres psql -U babblr -d babblr

# Run SQL file
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec -T postgres psql -U babblr -d babblr < backup.sql

# Create database backup
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec postgres pg_dump -U babblr babblr > backup.sql
```

### Running Tests Inside Containers

```bash
# Backend tests
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec backend uv run pytest tests/ -v

# Frontend tests
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec frontend npm run test
```

### Accessing Container Shells

```bash
# Backend shell
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec backend /bin/bash

# Frontend shell
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec frontend /bin/sh

# PostgreSQL shell
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec postgres /bin/sh
```

### Managing Whisper Container Independently

The Whisper container can be managed separately from the backend for easier testing and debugging:

```bash
# Start Whisper container only (CPU)
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml up -d

# Start Whisper container only (GPU)
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml -f docker-compose.gpu.yml up -d

# Stop Whisper container only
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml stop babblr-whisper

# Restart Whisper container (useful for testing)
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml restart babblr-whisper

# View Whisper logs
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml logs -f babblr-whisper

# Check Whisper health (still in backend container)
curl http://localhost:8000/health

# Remove Whisper container (keeps volumes)
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml rm -f babblr-whisper
```

**Note**: The backend does NOT depend on the Whisper container. You can start/stop/restart Whisper independently without affecting the backend. See [WHISPER.md](WHISPER.md) for detailed Whisper container documentation.

## Environment Configuration

The `.env` file controls LLM provider, API keys, and model selection:

```env
# LLM Provider (ollama, claude, gemini, mock)
LLM_PROVIDER=ollama

# Ollama model
OLLAMA_MODEL=llama3.2:latest

# API keys (only needed if using cloud providers)
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...

# Whisper model (tiny, base, small, medium, large)
WHISPER_MODEL=base
```

**Note:** Environment changes require service restart:
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml restart backend
```

## Troubleshooting

### Services won't start

**Check service status:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml ps
```

**Check logs for errors:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml logs backend
```

### Backend can't connect to database

**Verify PostgreSQL is healthy:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec postgres pg_isready -U babblr
```

**Manually test connection:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec backend python -c "from app.database.db import engine; print('DB OK')"
```

### Frontend can't reach backend

**Verify backend health:**
```bash
curl http://localhost:8000/health
```

**Check network connectivity:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec frontend wget -O- http://backend:8000/health
```

### Hot-reload not working (dev mode)

**Verify volume mounts:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec backend ls -la /app
```

**Restart services:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml restart backend frontend
```

### Ollama model not found

**Pull the model manually:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec ollama ollama pull llama3.2:latest
```

**List available models:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec ollama ollama list
```

### Port conflicts

If ports 5173, 8000, or 5432 are already in use, edit the compose file:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change host port (left side)
```

## GPU Support (Optional)

By default, Whisper uses `WHISPER_DEVICE=auto` and will fall back to CPU when
CUDA is not available. To enable GPU acceleration on machines that have a
supported NVIDIA setup, use the GPU override file.

**1. Install NVIDIA Container Toolkit**

**2. Start services with the GPU override:**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml -f docker-compose.gpu.yml up -d
```

**3. Verify GPU access (optional):**
```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec backend nvidia-smi
```

**Notes:**
- If you run without the GPU override file, the backend stays on CPU.
- If you use the GPU override on a host without NVIDIA support, Docker will
  fail fast and you should remove the override file.

For more detail, see `docker/GPU.md`.

## Whisper Container Mode (Optional)

You can run a dedicated Whisper container and point the backend to it. This is
useful when you want GPU-backed Whisper without running the model inside the
backend container. See `docker/WHISPER.md` for setup and configuration details.

## Data Persistence

Data is stored in Docker volumes and persists across container restarts:

| Volume | Purpose | Location |
|--------|---------|----------|
| `postgres_data` | Database files | PostgreSQL data directory |
| `audio_data` | User audio recordings | `/data/audio` |
| `whisper_cache` | Downloaded Whisper models | `~/.cache/whisper` |
| `ollama_models` | Downloaded Ollama models | `~/.ollama` |
| `redis_data` | Redis cache | `/data` |

**Backup volumes:**
```bash
# Create backup directory
mkdir -p backups

# Backup PostgreSQL
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec postgres pg_dump -U babblr babblr > backups/db-$(date +%Y%m%d).sql

# Backup audio files
docker run --rm -v babblr_audio_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/audio-$(date +%Y%m%d).tar.gz -C /data .
```

**Restore volumes:**
```bash
# Restore PostgreSQL
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml exec -T postgres psql -U babblr -d babblr < backups/db-20260126.sql

# Restore audio files
docker run --rm -v babblr_audio_data:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/audio-20260126.tar.gz -C /data
```

## Production Deployment Considerations

When deploying to production (not just testing locally):

1. **Use managed PostgreSQL** (AWS RDS, Google Cloud SQL) instead of containerized database
2. **Use object storage** (S3, GCS) for audio files instead of volumes
3. **Set strong passwords** - replace `devpassword` with secure credentials
4. **Use secrets management** - AWS Secrets Manager, HashiCorp Vault, etc.
5. **Configure SSL/TLS** - Add reverse proxy (Traefik, Nginx) with certificates
6. **Set up monitoring** - Prometheus, Grafana, or cloud-native solutions
7. **Enable autoscaling** - Kubernetes or Docker Swarm for production orchestration

See `tmp/devops/02-kubernetes.md` for Kubernetes deployment guide.

## Next Steps

Once comfortable with Docker Compose:

1. ✅ Containers running locally with hot-reload
2. ⏭️ Explore Kubernetes deployment (`tmp/devops/02-kubernetes.md`)
3. ⏭️ Set up CI/CD for automated container builds
4. ⏭️ Configure infrastructure as code (Terraform)

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Backend README](../backend/README.md)
- [Frontend README](../frontend/README.md)
- [DevOps Transformation Plan](../tmp/devops/00-OVERVIEW.md)
