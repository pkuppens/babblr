# GPU Setup and Validation

This guide explains how to enable GPU support for Docker and verify it works
with Babblr services.

## Prerequisites

- NVIDIA GPU with recent drivers installed.
- Docker Desktop with WSL2 backend on Windows, or Docker Engine on Linux.
- NVIDIA Container Toolkit installed.

Reference: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

## Verify Docker GPU Access

Run a CUDA container and check `nvidia-smi` output:

```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

If you see your GPU listed, Docker has GPU access.

## Enable GPU for Babblr Services

Use the GPU override compose file:

```bash
docker-compose -f docker-compose.base.yml -f docker-compose.dev.yml -f docker-compose.gpu.yml up -d
```

This enables GPU passthrough for the backend and for the optional
`babblr-whisper` service (if you use it).

## Troubleshooting

- If the CUDA test fails, verify NVIDIA drivers and the container toolkit.
- On Windows, confirm WSL2 is enabled and Docker Desktop uses WSL2.
- If Docker GPU works but Babblr shows CPU, verify `WHISPER_DEVICE=cuda`
  (local mode) or `WHISPER_CONTAINER_DEVICE=cuda` (whisper container mode).
