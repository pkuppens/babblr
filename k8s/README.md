# k8s — Kubernetes manifests for babblr

Kubernetes deployment of the babblr web stack (the Nginx/web variant; Electron is
the desktop distribution). Derived from `docker/docker-compose.yml`,
`docker-compose.whisper.yml`, `docker-compose.gpu.yml` and the generic building
blocks in [`pkuppens/ckad-catalog`](https://github.com/pkuppens/ckad-catalog).
Tracks pkuppens/pkuppens#117 (EPIC pkuppens/pkuppens#109).

## Layout

```
k8s/
  base/             # Deployments, Services, PVCs, ConfigMap, Secret, Ingress
  overlays/gpu/     # schedules ollama + whisper on GPU nodes (1 GPU each)
```

| Workload | State | Notes |
| --- | --- | --- |
| `backend` | stateless + audio PVC | `/health` probes, **HPA** |
| `frontend` | stateless | nginx serving the Vite build on :80 |
| `postgres` | stateful (PVC) | `pg_isready` probe |
| `ollama` | stateful (PVC) | GPU via overlay |
| `babblr-whisper` | stateful (model PVC) | **independent STT service + HPA**, GPU via overlay |

The backend is wired to the external Whisper service (`STT_PROVIDER=whisper_webservice`,
`STT_WEBSERVICE_URL=http://babblr-whisper:9000`) so **STT scales independently** of
the API — the key showcase for this app.

Redis from compose is intentionally omitted: it is currently unused by the backend
(decorative). Add it later only if real caching is implemented.

## Deploy (local kind)

```powershell
docker build -t babblr-backend:dev backend
docker build -t babblr-frontend:dev frontend
kind load docker-image babblr-backend:dev babblr-frontend:dev --name ckad

kubectl apply -k k8s/base               # CPU-only
# or, on a GPU cluster:
kubectl apply -k k8s/overlays/gpu

kubectl get pods -n babblr
curl -H "Host: babblr.local" http://localhost/
```

## Scaling showcase

- `backend` and `babblr-whisper` each have an HPA (CPU 70%). Generate STT load and
  watch `kubectl get hpa -n babblr` scale the Whisper Deployment independently of the API.
- The `gpu` overlay moves `ollama` and `babblr-whisper` onto GPU nodes
  (`nodeSelector: gpu=true`, `nvidia.com/gpu: 1`) and switches Whisper to `ASR_DEVICE=cuda`.

## Notes

- Development baseline: single-replica stateful services, placeholder secrets, no TLS.
- Secrets use placeholders only — never commit real credentials.
