# Babblr Validation Plan

This document provides a comprehensive smoke test and validation plan for Babblr. Use it to verify the project is running correctly after setup, or to validate functionality after changes.

## Table of Contents

- [1. Environment Setup Validation](#1-environment-setup-validation)
- [2. Backend Validation](#2-backend-validation)
- [3. LLM Provider Validation](#3-llm-provider-validation)
- [4. Speech Services Validation](#4-speech-services-validation)
- [5. Frontend Validation](#5-frontend-validation)
- [6. End-to-End Validation](#6-end-to-end-validation)
- [7. Pending Features](#7-pending-features)

---

## 1. Environment Setup Validation

### Goal: Verify the development environment is correctly configured

#### 1.1 Clone the Repository

```bash
git clone https://github.com/pkuppens/babblr.git
cd babblr
```

#### 1.2 Prerequisites Check

**Linux/macOS:**
```bash
# Check Python version (requires 3.12+)
python3 --version
# Expected: Python 3.12.x

# Check Node.js version (requires 22+)
node --version
# Expected: v22.x.x or v24.x.x

# Check uv is installed (optional - setup script will install it)
uv --version
```

**Windows (PowerShell or CMD):**
```powershell
# Check Python 3.12 specifically
py -3.12 -V
# Expected: Python 3.12.x

# Check Node.js version (requires 22+)
node --version
# Expected: v22.x.x or v24.x.x

# Check uv is installed (optional - setup script will install it)
uv --version
```

<details>
<summary>Installing Python 3.12</summary>

**Windows (recommended):**
```powershell
winget install -e --id Python.Python.3.12
```

**Linux/macOS with pyenv:**
```bash
pyenv install 3.12.8
pyenv local 3.12.8
```

**Or download from:** https://www.python.org/downloads/
</details>

<details>
<summary>Installing Node.js 22+</summary>

**Windows:**
```powershell
winget install -e --id OpenJS.NodeJS.LTS
```

**Linux/macOS with nvm:**
```bash
nvm install 22
nvm use 22
```

**Or download from:** https://nodejs.org/
</details>

<details>
<summary>Installing uv (if not using setup script)</summary>

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
</details>

#### 1.3 Run Setup Script

```bash
# Linux/macOS:
./setup.sh

# Windows:
setup.bat
```

**Expected output:**
- No errors during setup
- `backend/.venv` directory created
- `frontend/node_modules` directory created
- `.env` file created in `backend/`

<details>
<summary>Troubleshooting: Setup script fails</summary>

1. Ensure you're in the project root directory
2. Check Python 3.12 and Node.js 22+ are installed (see 1.2)
3. Try manual setup:
   ```bash
   cd backend
   uv venv --python 3.12
   uv pip install -e ".[dev]"
   cd ../frontend
   npm install
   ```
</details>

#### 1.4 Environment Configuration

```bash
# Verify .env file exists
cat backend/.env

# Should contain (at minimum):
# ANTHROPIC_API_KEY=sk-ant-...  (optional if using Ollama)
# LLM_PROVIDER=ollama           (default provider)
```

---

## 2. Backend Validation

### Goal: Verify the backend API is running and responding correctly

#### 2.1 Start Backend Server

```bash
# From project root
# Linux/macOS:
./run-backend.sh

# Windows:
run-backend.bat
```

**Expected output:**
```
🚀 Starting Babblr backend with uv...
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

<details>
<summary>Troubleshooting: Backend won't start</summary>

1. Check port 8000 is not in use:
   ```bash
   # Linux/macOS
   lsof -i :8000
   # Windows
   netstat -ano | findstr :8000
   ```
2. Verify virtual environment:
   ```bash
   cd backend
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   python -c "import fastapi; print('OK')"
   ```
3. Check logs for specific errors
</details>

#### 2.2 Health Check Endpoints

```bash
# Root endpoint
curl http://localhost:8000/
# Expected: {"status":"ok","service":"Babblr API","version":"1.0.0"}

# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected","services":{...}}
```

#### 2.3 API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Expected:** Interactive API documentation loads without errors

#### 2.4 Run Unit Tests

```bash
cd backend
uv run pytest tests/test_unit.py -v
```

**Expected:** All tests pass (currently 16 tests)

<details>
<summary>Troubleshooting: Tests fail</summary>

1. Ensure you're in the `backend` directory
2. Check virtual environment is activated
3. Reinstall dependencies: `uv pip install -e ".[dev]"`
4. Check specific error messages
</details>

---

## 3. LLM Provider Validation

### Goal: Verify LLM providers are correctly configured and working

#### 3.1 Run LLM Provider Tests

```bash
cd backend
uv run pytest tests/test_llm_providers.py -v
```

**Expected:** All 56 tests pass

#### 3.2 Validate Ollama Provider (MVP Primary)

##### 3.2.1 Check Ollama Installation

```bash
# Check Ollama is running
ollama list
```

**Expected:** List of available models

<details>
<summary>Troubleshooting: Ollama not running</summary>

```bash
# Start Ollama service
ollama serve

# Pull a model if none available
ollama pull llama3.2:latest
```
</details>

##### 3.2.2 Test Ollama Directly

```bash
ollama run llama3.2 "Say hello in Spanish"
```

**Expected:** Response in Spanish (e.g., "¡Hola!")

##### 3.2.3 Test via Python API

```python
# Run in Python (from backend directory with venv activated)
import asyncio
from app.services.llm import ProviderFactory

async def test_ollama():
    provider = ProviderFactory.get_provider("ollama")

    # Health check
    healthy = await provider.health_check()
    print(f"Ollama healthy: {healthy}")

    # Generate response
    response = await provider.generate(
        messages=[{"role": "user", "content": "Hola!"}],
        system_prompt=provider.build_tutor_prompt("Spanish", "A2"),
    )
    print(f"Response: {response.content}")
    print(f"Model: {response.model}")

asyncio.run(test_ollama())
```

**Expected:**
- `Ollama healthy: True`
- Response content in Spanish
- Model name displayed

#### 3.3 Validate Claude Provider (Optional)

> **Note:** Requires `ANTHROPIC_API_KEY` in `.env`

```python
import asyncio
from app.services.llm import ProviderFactory

async def test_claude():
    try:
        provider = ProviderFactory.get_provider("claude")
        response = await provider.generate(
            messages=[{"role": "user", "content": "Say hello in French"}],
            system_prompt="You are a helpful assistant.",
        )
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Claude not available: {e}")

asyncio.run(test_claude())
```

<details>
<summary>Troubleshooting: Claude authentication error</summary>

1. Verify API key in `backend/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
2. Check key is valid at https://console.anthropic.com/
3. Restart backend after changing `.env`
</details>

#### 3.4 Validate Mock Provider (Testing)

```python
import asyncio
from app.services.llm import ProviderFactory

async def test_mock():
    ProviderFactory.clear_cache()
    provider = ProviderFactory.get_provider("mock")

    response = await provider.generate(
        messages=[{"role": "user", "content": "Hello"}],
        system_prompt="Test prompt",
    )
    print(f"Mock response: {response.content}")
    print(f"Model: {response.model}")

asyncio.run(test_mock())
```

**Expected:**
- Response: "This is a mock response from the language tutor."
- Model: "mock-v1"

---

## 4. Speech Services Validation

### Goal: Verify speech-to-text (Whisper) and text-to-speech services

#### 4.1 Whisper STT Validation

##### 4.1.1 Check Whisper API Endpoints

```bash
# Get supported languages
curl http://localhost:8000/stt/languages
# Expected: ["es", "it", "de", "fr", "nl", "en", ...]

# Get available models
curl http://localhost:8000/stt/models
# Expected: ["tiny", "base", "small", "medium", "large"]
```

##### 4.1.2 Check CUDA/GPU Status (Optional)

```bash
cd backend
python check_cuda.py
```

**Expected (with GPU):**
```
[OK] PyTorch version: 2.x.x+cu121
     CUDA available in PyTorch: True
[OK] CUDA version: 12.1
[OK] GPU device: NVIDIA ...
```

<details>
<summary>Troubleshooting: CUDA not available</summary>

1. Verify NVIDIA drivers: `nvidia-smi`
2. Reinstall PyTorch with CUDA:
   ```bash
   cd backend
   uv pip uninstall torch torchvision torchaudio
   uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```
</details>

#### 4.2 TTS Validation

```bash
# Check TTS endpoint structure (requires audio file)
curl http://localhost:8000/tts/speak -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "language": "en"}'
```

**Expected:** Audio file response or appropriate error

---

## 5. Frontend Validation

### Goal: Verify the Electron/React frontend loads and connects to backend

#### 5.1 Start Frontend

```bash
# From project root (in a second terminal)
# Linux/macOS:
./run-frontend.sh

# Windows:
run-frontend.bat
```

**Expected:**
- Electron window opens
- No console errors in DevTools

<details>
<summary>Troubleshooting: Frontend won't start</summary>

1. Ensure backend is running first
2. Check port 5173 is available
3. Reinstall dependencies:
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   ```
</details>

#### 5.2 UI Elements Check

Verify the following UI elements are visible:
- [ ] Language selector (Spanish, Italian, German, French, Dutch)
- [ ] Difficulty level selector
- [ ] Start Learning button
- [ ] Chat interface (after starting)
- [ ] Microphone button
- [ ] Message input field

#### 5.3 DevTools Check

Open DevTools (View → Toggle Developer Tools):
- [ ] No red errors in Console
- [ ] Network tab shows API calls to `localhost:8000`

---

## 6. End-to-End Validation

### Goal: Verify complete user flows work correctly

#### 6.1 Basic Conversation Flow

1. **Select Language**: Click "Spanish"
2. **Select Difficulty**: Click "Beginner"
3. **Start Conversation**: Click "Start Learning"
4. **Send Message**: Type "Hola" and press Enter
5. **Verify Response**: AI responds in Spanish

**Expected:**
- Conversation created successfully
- AI response appears in chat
- No errors in console

#### 6.2 Conversation with LLM Provider

```bash
# Create a conversation
curl -X POST http://localhost:8000/conversations \
  -H "Content-Type: application/json" \
  -d '{"language": "spanish", "difficulty_level": "beginner"}'
# Note the conversation ID from response

# Send a message (replace {id} with actual ID)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": {id},
    "user_message": "Hola, ¿cómo estás?",
    "language": "spanish",
    "difficulty_level": "beginner"
  }'
```

**Expected:**
- `assistant_message` contains Spanish response
- No errors

<details>
<summary>Troubleshooting: Chat returns error</summary>

1. Check LLM provider is configured:
   - Ollama running: `ollama list`
   - Or Claude API key set
2. Check backend logs for detailed error
3. Verify database is initialized: `ls backend/babblr.db`
</details>

---

## 7. Pending Features

The following features are tracked in GitHub issues and are not yet implemented. Validation for these will be added when implemented.

### 7.1 LLM Provider Enhancements

> **Waiting for:** [#11 - Implement swappable LLM provider architecture](https://github.com/pkuppens/babblr/issues/11) (Phase 2-4)

- [ ] SSE streaming endpoint for real-time responses
- [ ] Provider selection via API request parameter (`provider` field)
- [ ] Health check endpoint for all providers (`GET /providers/status`)
- [ ] Rate limit handling with exponential backoff
- [ ] Gemini provider placeholder

### 7.2 System Prompts

> **Waiting for:** [#12 - Create adaptive system prompts for different CEFR levels](https://github.com/pkuppens/babblr/issues/12)

- [ ] JSON templates for A1-C2 levels
- [ ] Prompt builder service
- [ ] Language-specific examples

### 7.3 TTS Playback

> **Waiting for:** [#10 - Implement TTS playback using Web Speech API](https://github.com/pkuppens/babblr/issues/10)

- [ ] Web Speech API integration
- [ ] Audio playback in frontend

### 7.4 Transcription Correction

> **Waiting for:** [#13 - Use Claude to correct Whisper transcription errors](https://github.com/pkuppens/babblr/issues/13)

- [ ] Transcription correction based on context
- [ ] Improved accuracy for language learners

### 7.5 User Interface

> **Waiting for:** Multiple frontend issues

- [#14 - Chat-like conversation interface](https://github.com/pkuppens/babblr/issues/14)
- [#15 - Topic selection UI](https://github.com/pkuppens/babblr/issues/15)
- [#16 - Vocabulary extraction and flashcards](https://github.com/pkuppens/babblr/issues/16)
- [#17 - Settings panel](https://github.com/pkuppens/babblr/issues/17)
- [#18 - Progress dashboard](https://github.com/pkuppens/babblr/issues/18)

### 7.6 Documentation & Templates

> **Waiting for:** [#19 - Complete documentation](https://github.com/pkuppens/babblr/issues/19), [#20 - GitHub templates](https://github.com/pkuppens/babblr/issues/20)

- [ ] Complete API documentation
- [ ] Issue and PR templates

---

## Validation Summary Checklist

### Minimum Viable Validation

- [ ] Python 3.12+ installed
- [ ] Node.js 22+ installed
- [ ] Backend starts without errors
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Unit tests pass (72 tests)
- [ ] Ollama is running with a model
- [ ] Frontend opens without errors
- [ ] Basic conversation flow works
- [ ] TTS (Web Speech API): click **Play** on a user message and on an assistant message; both must speak (ANY text is allowed, including user input)

### Full Validation (All Features)

- [ ] All minimum validation items
- [ ] LLM provider tests pass (56 tests)
- [ ] Ollama provider generates responses
- [ ] Claude provider works (if API key configured)
- [ ] STT languages endpoint returns data
- [ ] CUDA available (if GPU present)
- [ ] End-to-end conversation flow works

---

## Running Automated Validation

```bash
# Quick validation (unit tests only)
cd backend
uv run pytest tests/test_unit.py tests/test_llm_providers.py -v

# Full validation (requires backend running)
cd backend
uv run pytest tests/ -v

# With coverage report
uv run pytest tests/ -v --cov=app --cov-report=html
```

---

*Last updated: 2026-01-05*
