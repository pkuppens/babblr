# Whisper Container Mode

WORK IN PROGRESS: Currently, Whisper is implemented as part of the backend. The goal is to have a
separate service for it (containerized microservice), that can be reused, separately developed and
tested, etc.

Goal:
Babblr can use a dedicated Whisper container instead of the local Whisper
library inside the backend. This is useful when you want a GPU-backed Whisper
service with its own model cache, or when you need to restart and test Whisper
independently from the backend.

Notes:
* since loading a large-v3 model can take some time, we may want to hot-load and cache the model.
* model selection with its trade-offs for speed, performance, cost, is still work in process - therefore configurable

## Overview

- Container image: to be developed as separate component.
- Service name: `babblr-whisper`
- API endpoint: `http://babblr-whisper:9000` (internal) or `http://localhost:9000` (host)
- **Independent**: The Whisper container can be started, stopped, and restarted without affecting the backend
- The application may still need a proper interface (Protocol) and bridge for dependency injection.

## Quick Start

### Start Whisper Container Only (CPU)

```bash
cd docker
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml up -d
```

### Start Whisper Container Only (GPU)

```bash
cd docker
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml -f docker-compose.gpu.yml up -d
```

### Stop Whisper Container Only

```bash
cd docker
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml stop babblr-whisper
# Or remove it completely:
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml rm -f babblr-whisper
```

### Restart Whisper Container (for testing)

```bash
cd docker
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml restart babblr-whisper
```

### View Whisper Container Logs

```bash
cd docker
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml logs -f babblr-whisper
```

## Configure Babblr to Use the Container

Set these variables in `docker/.env`:

```env
STT_PROVIDER=whisper_webservice
STT_WEBSERVICE_URL=http://babblr-whisper:9000
STT_WEBSERVICE_TIMEOUT=300
STT_WEBSERVICE_DEVICE=auto
WHISPER_CONTAINER_MODEL=large-v3
WHISPER_CONTAINER_ENGINE=openai_whisper
WHISPER_CONTAINER_DEVICE=cuda  # or 'cpu' if no GPU
```

**Important**: The backend does NOT depend on the Whisper container. You can:
- Start the backend without Whisper (it will use local Whisper if `STT_PROVIDER=local`)
- Start Whisper independently and restart it without affecting the backend
- Switch between local and external Whisper by changing `STT_PROVIDER` and restarting only the backend

### Restart Backend to Use Whisper Container

```bash
cd docker
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml restart backend
```

**Note**: You don't need to include `docker-compose.whisper.yml` when restarting the backend - the backend connects to Whisper via the network, not via Docker dependencies.

## Model Downloads and Warm-Up

The whisper webservice downloads models on first use. For large-v3, the first
download can take several minutes. You can warm it up by making a request:

```bash
curl -X POST "http://localhost:9000/asr?task=transcribe&output=txt" \
  -F "audio_file=@path/to/sample.wav"
```

## Independent Management

The Whisper container is **completely independent** from the backend:

- ✅ Backend can start without Whisper container (uses local Whisper)
- ✅ Whisper can be restarted without restarting backend
- ✅ Whisper can be stopped/started for testing without affecting backend
- ✅ Backend gracefully handles Whisper container being unavailable (returns error on transcription)

### Example: Testing Whisper Changes

```bash
# 1. Start backend (with local Whisper or external if configured)
cd docker
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml up -d backend

# 2. Start Whisper container separately
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml up -d

# 3. Test Whisper directly
curl http://localhost:9000/health

# 4. Restart Whisper to test changes (backend keeps running)
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml restart babblr-whisper

# 5. View Whisper logs
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml logs -f babblr-whisper
```

## Notes

- Model switching is handled by the whisper container. To change models, restart
  `babblr-whisper` with `WHISPER_CONTAINER_MODEL` set to the target model.
- When the container runs with GPU, set `WHISPER_CONTAINER_DEVICE=cuda` in `.env`.
- The model cache is stored in the shared `babblr-volume-whisper-models` volume.
- The backend connects to Whisper via Docker network (`babblr-whisper:9000`), so both containers must be on the same network (they share `babblr-network` from `docker-compose.base.yml`).
