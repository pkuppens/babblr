# Environment Variables Configuration

This document is the single source of truth for all environment variable configuration in Babblr.

## Quick Start

1. **Copy the example file:**

   **Linux/macOS (bash):**
   ```bash
   cp backend/.env.example backend/.env
   ```

   **Windows (CMD):**
   ```cmd
   copy backend\.env.example backend\.env
   ```

2. **Choose your LLM provider** (Ollama is the default - runs locally, no API key needed!)

3. **If using a cloud provider**, add your API key to `backend/.env`:
   - For Claude: `ANTHROPIC_API_KEY=sk-ant-api03-...`
   - For Gemini: `GOOGLE_API_KEY=AI...`

4. **Restart the backend** if it's already running

## LLM Provider Selection

Babblr supports multiple LLM providers. Set `LLM_PROVIDER` in your `.env` file:

```bash
# Choose one: ollama (default), claude, gemini, mock
LLM_PROVIDER=ollama
```

| Provider | API Key Required | Runs Locally | Best For |
|----------|-----------------|--------------|----------|
| `ollama` | No | Yes | Development, privacy-conscious users |
| `claude` | Yes | No | High-quality responses, production |
| `gemini` | Yes | No | Cost-effective cloud option |
| `mock` | No | Yes | Testing only |

### Ollama (Default - No API Key Needed)

Ollama runs open-source models locally on your machine. **This is the default provider.**

**Setup:**
1. Install Ollama from [ollama.com](https://ollama.com/)
2. Pull a model: `ollama pull llama3.2:latest`
3. Ollama runs automatically on `http://localhost:11434`

**Configuration:**
```bash
LLM_PROVIDER=ollama
# Optional customization:
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2:latest
```

## API Keys (Required for Cloud Providers)

> **Note:** If using Ollama (the default), no API key is needed!

### Anthropic Claude API Key

Required if `LLM_PROVIDER=claude`.

**Where to get it:**
1. Visit [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Sign up for a free account (if you don't have one)
3. Click "Create Key" to generate a new API key
4. Copy the key (starts with `sk-ant-api03-...`)

**Free Tier:**
- New users get **$5 free credits**
- After free credits, pay-as-you-go pricing applies
- Check current pricing: https://www.anthropic.com/pricing

**Add to `.env`:**
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

**Documentation:**
- [Anthropic Quickstart](https://docs.anthropic.com/en/docs/quickstart)
- [API Reference](https://docs.anthropic.com/en/api)
- [Models Overview](https://docs.anthropic.com/en/docs/models-overview)

### Google Gemini API Key

Required if `LLM_PROVIDER=gemini`.

**Where to get it:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the generated API key (starts with `AI...`)

**Free Tier:**
- Gemini 1.5 Flash: Free tier available with rate limits
- Gemini 1.5 Pro: Pay-as-you-go
- Check current pricing: https://ai.google.dev/pricing

**Add to `.env`:**
```bash
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIza...your-actual-key-here
```

**Available models:**
- `gemini-1.5-flash` (Default - fast, cost-effective)
- `gemini-1.5-pro` (Higher quality, more expensive)
- `gemini-2.0-flash-exp` (Latest experimental)

**Documentation:**
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini Models](https://ai.google.dev/models/gemini)

## Optional Configuration

### Claude Model Selection

You can optionally specify which Claude model to use. If not set, defaults to `claude-3-5-sonnet-20241022`.

```bash
# Optional - uncomment to customize
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

**Available models:**
- `claude-3-5-sonnet-20241022` (Recommended - best balance of quality and cost)
- `claude-3-haiku-20240307` (Faster, cheaper, slightly lower quality)
- `claude-3-opus-20240229` (Highest quality, most expensive)

See full list: https://docs.anthropic.com/en/docs/models-overview

### Whisper Model Size

Whisper runs **locally** (no API key needed) for speech-to-text. You can choose the model size:

```bash
# Optional - uncomment to customize
WHISPER_MODEL=base
```

**Options:**
- `tiny` - Fastest, least accurate (~39M parameters)
- `base` - **Default** - Good balance (~74M parameters)
- `small` - Better accuracy (~244M parameters)
- `medium` - High accuracy (~769M parameters)
- `large` - Best accuracy (~1550M parameters, requires GPU)

**Note:** Larger models require more RAM and processing time.

### Server Configuration

```bash
# Default backend server settings
HOST=127.0.0.1
PORT=8000
```

### Development mode (debug helpers)

The backend has a few development-only helpers. Enable them only on your local machine.

```bash
# When true, enables dev-only behavior in some endpoints
DEVELOPMENT_MODE=true

# When true (and DEVELOPMENT_MODE=true), `/stt/transcribe` will also save each uploaded
# recording to the repo `tmp/` folder as `stt_YYYYMMDDHHMMSS.<ext>` for reproducible testing.
STT_DUMP_UPLOADS=true
```

**When to change:**
- Deploy to production: Change `HOST` to `0.0.0.0`
- Port conflict: Change `PORT` to another port (e.g., `8001`)

### Timezone

Used for timestamp formatting in database records.

```bash
# Default timezone
TIMEZONE=Europe/Amsterdam
```

**Common options:**
- `Europe/Amsterdam`
- `Europe/Madrid`
- `America/New_York`
- `America/Los_Angeles`
- `Asia/Tokyo`

Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Database

```bash
# SQLite database location
DATABASE_URL=sqlite+aiosqlite:///./babblr.db
```

**Default:** Creates `babblr.db` in the backend directory.

**To change location:**
```bash
# Absolute path
DATABASE_URL=sqlite+aiosqlite:////path/to/custom/location/babblr.db

# Relative path (from backend directory)
DATABASE_URL=sqlite+aiosqlite:///./data/babblr.db
```

### CORS (Frontend URL)

```bash
# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

**When to change:**
- Frontend runs on different port: Update to match
- Deploy to production: Set to your production frontend URL

## Complete `.env` File Example

```bash
# ============================================
# LLM PROVIDER (choose one)
# ============================================

# Options: ollama (default), claude, gemini, mock
LLM_PROVIDER=ollama

# --- Ollama (default, no API key needed) ---
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2:latest

# --- Claude (requires API key) ---
# Get your key from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
# CLAUDE_MODEL=claude-sonnet-4-20250514

# --- Gemini (requires API key) ---
# Get your key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=AIza-your-actual-key-here
# GEMINI_MODEL=gemini-1.5-flash

# ============================================
# CONVERSATION MEMORY
# ============================================

# Maximum tokens before summarizing old messages (defaults to 2000)
# CONVERSATION_MAX_TOKEN_LIMIT=2000

# ============================================
# OTHER SETTINGS (with defaults)
# ============================================

# Whisper Model (defaults to base)
# WHISPER_MODEL=base

# Server Configuration
HOST=127.0.0.1
PORT=8000

# Timezone (defaults to Europe/Amsterdam)
TIMEZONE=Europe/Amsterdam

# Database
DATABASE_URL=sqlite+aiosqlite:///./babblr.db

# CORS Configuration
FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

### Error: "Invalid Anthropic API key"

**Symptoms:**
- Backend logs show: `authentication_error: invalid x-api-key`
- Frontend shows: "Invalid Anthropic API key configured on the server"

**Solutions:**
1. Verify your API key is correct (check for extra spaces, typos)
2. Ensure the key starts with `sk-ant-api03-`
3. Verify the key is active in [Anthropic Console](https://console.anthropic.com/settings/keys)
4. Check you have available credits (free tier or paid)
5. Restart the backend after updating `.env`

### Error: "Invalid Google API key"

**Symptoms:**
- Backend logs show: `API key not valid` or `authentication` errors
- Frontend shows: "The AI tutor service is not configured"

**Solutions:**
1. Verify your API key is correct (check for extra spaces, typos)
2. Ensure the key starts with `AI`
3. Verify the key is active in [Google AI Studio](https://aistudio.google.com/app/apikey)
4. Check that your Google Cloud project has the Generative AI API enabled
5. Check you haven't exceeded rate limits (free tier has limits)
6. Restart the backend after updating `.env`

### Error: "Ollama connection refused"

**Symptoms:**
- Backend logs show: `Connection refused` to `localhost:11434`
- Chat endpoint returns 503 error

**Solutions:**
1. Ensure Ollama is installed: Download from [ollama.com](https://ollama.com/)
2. Start Ollama: Run `ollama serve` or check if it's running as a service
3. Pull a model: `ollama pull llama3.2:latest`
4. Verify it's running: `curl http://localhost:11434/api/tags`
5. If using a different port, set `OLLAMA_BASE_URL` in `.env`

### Error: ".env file not found"

**Symptoms:**
- Backend logs show warnings about missing environment variables
- API key defaults to empty string

**Solutions:**
1. Ensure `.env` file exists in `backend/` directory
2. Copy from example: `cp backend/.env.example backend/.env`
3. Verify file name is exactly `.env` (not `.env.txt` or similar)

### Environment variables not loading

**Symptoms:**
- Changes to `.env` don't take effect
- Settings still use defaults

**Solutions:**
1. Restart the backend completely (stop and start)
2. Check file encoding (should be UTF-8)
3. Verify no quotes around values: `KEY=value` not `KEY="value"`
4. Check for syntax errors (no spaces around `=`)

## Security Best Practices

1. **Never commit `.env` to version control**
   - Already in `.gitignore`
   - Keep API keys secret

2. **Don't share your API key**
   - Treat it like a password
   - Regenerate if exposed

3. **Use environment-specific files**
   - `.env.development` for development
   - `.env.production` for production
   - Never mix environments

4. **Monitor API usage**
   - Check [Anthropic Console](https://console.anthropic.com/) regularly
   - Set up billing alerts
   - Track credit usage

## Platform-Specific Notes

### Windows

- Use backslashes in file paths: `C:\path\to\babblr.db`
- Or forward slashes work too: `C:/path/to/babblr.db`
- Environment variable format is the same as Linux/macOS

### Linux/macOS

- Use forward slashes: `/path/to/babblr.db`
- Ensure file permissions are correct: `chmod 600 backend/.env`
- Use `source` or `.` to load in shell if needed

### Docker/Containers

If running in Docker, pass environment variables via:
```bash
docker run -e ANTHROPIC_API_KEY=your-key ...
```

Or use `--env-file`:
```bash
docker run --env-file backend/.env ...
```

## Additional Resources

### LLM Providers
- [Ollama](https://ollama.com/) - Run LLMs locally
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Anthropic Console (API Keys)](https://console.anthropic.com/settings/keys)
- [Anthropic Pricing](https://www.anthropic.com/pricing)
- [Google AI Studio](https://aistudio.google.com/) - Gemini API keys
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Gemini Pricing](https://ai.google.dev/pricing)

### Other Tools
- [OpenAI Whisper Documentation](https://github.com/openai/whisper)
- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [LangChain Documentation](https://python.langchain.com/)
