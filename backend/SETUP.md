# Babblr Backend Setup Guide

Complete setup guide for the Babblr backend with Python 3.12, uv, and GPU acceleration.

## Quick Setup

### Prerequisites

- **Python 3.12** (not 3.13 - PyTorch CUDA requires 3.12)
- **uv** package manager
- **NVIDIA GPU** (optional, for CUDA acceleration)

### One-Command Setup

**Linux/macOS:**
```bash
cd backend
./setup-venv.sh
```

**Windows:**
```cmd
cd backend
setup-venv.bat
```

This script will:
- Create `.venv` in the backend directory (with Python 3.12)
- Install all dependencies
- Verify the installation

Then install PyTorch with CUDA (optional but recommended):
```bash
cd backend
uv pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Detailed Setup

### 1. Install uv (if not already installed)

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:
```bash
uv --version
```

### 2. Create Virtual Environment with Python 3.12

**Important:** The virtual environment MUST be in `backend/.venv` (not project root).

**Linux/macOS:**
```bash
cd backend
uv venv --python 3.12
```

**Windows:**
```cmd
cd backend
uv venv --python 3.12
```

###3. Install Dependencies

```bash
cd backend
uv pip install -e ".[dev]"
```

This installs:
- FastAPI, Uvicorn (web framework)
- Anthropic SDK (Claude AI)
- OpenAI Whisper (speech-to-text)
- PyTorch (CPU version initially)
- All dev dependencies (pytest, ruff, pre-commit)

### 3b. Enable pre-commit hooks (recommended)

```bash
cd backend
uv run pre-commit install
```

Then, before pushing a change, you can also run the hooks manually:

```bash
cd backend
uv run pre-commit run --all-files
```

### 4. Install PyTorch with CUDA (GPU Acceleration)

**Why:** Whisper runs 5-10x faster on GPU vs CPU.

**Requirements:**
- NVIDIA GPU
- CUDA drivers installed

**Installation:**
```bash
cd backend

# Uninstall CPU-only PyTorch
uv pip uninstall torch torchvision torchaudio

# Install CUDA-enabled PyTorch (CUDA 12.1 - compatible with CUDA 13.0+ drivers)
uv pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify CUDA:**
```bash
cd backend
python check_cuda.py
```

Expected output:
```
[OK] PyTorch version: 2.5.1+cu121
     CUDA available in PyTorch: True
[OK] CUDA version: 12.1
[OK] GPU device: NVIDIA GeForce GTX 1070
     Virtual environment: /path/to/backend/.venv
```

### 5. Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add:
```bash
ANTHROPIC_API_KEY=your_key_here
WHISPER_MODEL=base  # or small, medium, large
```

### 6. Run Backend

**Linux/macOS:**
```bash
# From project root
./run-backend.sh
```

**Windows:**
```cmd
REM From project root
run-backend.bat
```

Expected startup messages:
```
[START] Starting Babblr backend with uv...
   Working directory: /path/to/backend
   Virtual environment: /path/to/backend/.venv
   Using .env from: /path/to/backend/.env
[INFO] GPU detected: NVIDIA GeForce GTX 1070
[INFO] Whisper model loaded on GPU: cuda:0
```

## Virtual Environment Location

**Critical Rule:** Virtual environment MUST be in `backend/.venv` ONLY.

```
babblr/
├── backend/
│   ├── .venv/          ← Virtual environment (ONLY location)
│   ├── .env            ← Environment variables
│   ├── pyproject.toml  ← Dependencies
│   └── app/            ← Application code
├── frontend/           ← No virtual environment (uses npm)
└── (no .venv here)     ← No root virtual environment
```

**Why this matters:**
- Prevents package installation conflicts
- Ensures correct CUDA PyTorch location
- Scripts automatically use `backend/.venv`

## Troubleshooting

### Virtual Environment in Wrong Location

**Symptom:**
```
warning: `VIRTUAL_ENV=/path/to/root/.venv` does not match project environment
```

**Solution:**
```bash
# Remove root .venv if it exists
rm -rf .venv  # From project root

# Create in correct location
cd backend
./setup-venv.sh
```

### Python 3.13 Instead of 3.12

**Symptom:**
```
PyTorch CUDA wheels not available for Python 3.13
```

**Solution:**
```bash
cd backend
rm -rf .venv
uv venv --python 3.12
uv pip install -e ".[dev]"
# Then install CUDA PyTorch as shown above
```

### CUDA Not Available After Installation

**Diagnosis:**
```bash
cd backend
python check_cuda.py
```

**Common causes:**
1. **PyTorch installed in wrong location** → Check "Virtual environment" in output
2. **CPU-only PyTorch** → Reinstall with `--index-url https://download.pytorch.org/whl/cu121`
3. **NVIDIA drivers missing** → Run `nvidia-smi` to verify

**Solution:**
```bash
cd backend

# Verify you're in backend directory
pwd  # Should end with /backend

# Reinstall CUDA PyTorch
uv pip uninstall torch torchvision torchaudio
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Verify
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

### Packages Not Found When Running

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Installed in wrong virtual environment

**Solution:**
```bash
# Always run uv commands from backend directory
cd backend
uv pip install -e ".[dev]"
```

## Performance Expectations

### Whisper Transcription Speed (5-second audio)

| Model | CPU | GPU (CUDA) | Speed Improvement |
|-------|-----|------------|-------------------|
| base | 2-5s | 0.5-1s | 5-10x faster |
| small | 3-7s | 0.7-1.5s | 5-10x faster |
| medium | 8-15s | 2-4s | 4-6x faster |

**Recommendation:** Use `small` model with GPU for best balance of speed and accuracy.

## See Also

- [UV_SETUP.md](UV_SETUP.md) - Detailed uv usage guide
- [WHISPER_OPTIMIZATION.md](WHISPER_OPTIMIZATION.md) - Model selection and optimization
- [../WINDOWS_SCRIPTS.md](../WINDOWS_SCRIPTS.md) - Windows script reference
- [check_cuda.py](check_cuda.py) - CUDA diagnostic script

## Summary Checklist

- [ ] Python 3.12 installed (not 3.13)
- [ ] uv package manager installed
- [ ] Virtual environment in `backend/.venv` only
- [ ] Dependencies installed: `uv pip install -e ".[dev]"`
- [ ] PyTorch with CUDA: `uv pip install torch... --index-url .../cu121`
- [ ] CUDA verified: `python check_cuda.py` shows GPU
- [ ] Environment configured: `.env` file with API key
- [ ] Backend runs successfully with GPU detection
