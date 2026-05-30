# k8s — Kubernetes manifests for babblr

Kubernetes deployment of the babblr web stack (the Nginx/web variant; Electron is
the desktop distribution). Derived from `docker/docker-compose.yml`,
`docker-compose.whisper.yml`, `docker-compose.gpu.yml` and the generic building
blocks in [`pkuppens/ckad-catalog`](https://github.com/pkuppens/ckad-catalog).
Tracks pkuppens/pkuppens#117 (EPIC pkuppens/pkuppens#109).

## New to Kubernetes?

Kubernetes (often shortened to **K8s**) is a platform that runs your application
as many small, replaceable pieces instead of one big server process. You describe
*what* you want (for example: “run two copies of the API, keep the database data
safe, scale speech-to-text when load goes up”), and Kubernetes keeps the cluster
in that state.

### Core ideas (plain language)

| Term | What it means for babblr |
| --- | --- |
| **Pod** | One running instance of a container (backend, frontend, Whisper STT, …). |
| **Deployment** | “Keep N pods of this app running.” If a pod crashes, Kubernetes starts a new one. |
| **Service** | A stable network name inside the cluster (`backend`, `babblr-whisper`, …) so pods can find each other even when they restart or move. |
| **ConfigMap / Secret** | Non-secret and secret settings (API keys, database URL) injected into pods without baking them into the image. |
| **Ingress** | The front door from outside the cluster (here: `babblr.local` → frontend). |
| **HPA** (Horizontal Pod Autoscaler) | Adds or removes pods when CPU (or other metrics) goes up or down. |

### Why use Kubernetes here?

Babblr is not one monolith in this layout — it is a **set of services** that work
together:

- **frontend** — static web UI (nginx)
- **backend** — FastAPI API
- **postgres** — conversation database
- **ollama** — local LLM
- **babblr-whisper** — speech-to-text (STT)

Kubernetes helps you **deploy**, **update**, and **operate** each part on its
own schedule:

- Roll out a new backend image without rebuilding Whisper or Postgres.
- Restart a failed pod without touching the rest of the stack.
- Scale only the service that is under load.

That is the same “microservices” idea as Docker Compose, but with built-in
healing, scaling, and rolling updates across a cluster of machines.

### Example: scaling speech-to-text

Without enough STT capacity, many users sending voice at once would **queue**
requests. The UI feels slow or stuck while one process works through the backlog.

With Kubernetes you can run **multiple Whisper pods** (see `babblr-whisper` and
its HPA in `base/whisper.yaml`). Each pod can transcribe audio in parallel, so
more users get a response at the same time. The backend talks to the Whisper
**Service** (`http://babblr-whisper:9000`); Kubernetes load-balances across
healthy pods. You do not hard-code pod IP addresses in the app.

The backend has its own HPA too, so API traffic and STT load can scale
**independently** — the main showcase of this manifest set.

### Example: keeping data on disk (PV and PVC)

Some parts of babblr must **remember data** after a pod restarts:

- Postgres database files
- Ollama downloaded models
- Whisper model cache
- User audio files on the backend

In Kubernetes:

1. A **PersistentVolume (PV)** is a piece of storage in the cluster (often
   provisioned automatically by your cloud or by `kind` locally).
2. A **PersistentVolumeClaim (PVC)** is a **request** for storage: “give this
   workload 20 GiB.” The manifests in `k8s/base/` define PVCs such as
   `postgres-data`, `ollama-models`, and `whisper-models`.
3. A pod **mounts** the PVC at a path (for example `/var/lib/postgresql/data`).
   When the pod is replaced, the new pod attaches the **same** claim, so data
   survives.

Stateless apps (frontend, and mostly backend) can use ephemeral disk; stateful
ones (postgres, ollama, whisper) use PVCs.

### What is in this folder?

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
the API.

Redis from compose is intentionally omitted: it is currently unused by the backend
(decorative). Add it later only if real caching is implemented.

## Deploy (local kind)

**Prerequisites:** Docker, [kind](https://kind.sigs.k8s.io/), and `kubectl`
installed. `kind` creates a small Kubernetes cluster on your machine for learning
and smoke tests.

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

## Further reading

- [Kubernetes concepts (official docs)](https://kubernetes.io/docs/concepts/)
- [Persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
