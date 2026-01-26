# Whisper Container Mode

Babblr can use a dedicated Whisper container instead of the local Whisper
library inside the backend. This is useful when you want a GPU-backed Whisper
service with its own model cache.

## Overview

- Container image: `onerahmet/openai-whisper-asr-webservice`
- Service name: `babblr-whisper`
- API endpoint: `http://babblr-whisper:9000/asr`

## Start the Whisper Container

### CPU

```bash
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml up -d
```

### GPU (if available)

```bash
docker-compose -f docker-compose.base.yml -f docker-compose.whisper.yml -f docker-compose.gpu.yml up -d
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
```

Then restart the backend:

```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml -f docker-compose.whisper.yml up -d --build backend
```

## Model Downloads and Warm-Up

The whisper webservice downloads models on first use. For large-v3, the first
download can take several minutes. You can warm it up by making a request:

```bash
curl -X POST "http://localhost:9000/asr?task=transcribe&output=txt" \
  -F "audio_file=@path/to/sample.wav"
```

## Notes

- Model switching is handled by the whisper container. To change models, restart
  `babblr-whisper` with `WHISPER_CONTAINER_MODEL` set to the target model.
- When the container runs with GPU, set `WHISPER_CONTAINER_DEVICE=cuda`.
- The model cache is stored in the shared `babblr-volume-whisper-models` volume.
