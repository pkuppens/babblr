# Troubleshooting Guide

Common issues and solutions for Babblr.

## Installation Issues

### Python Dependencies Fail to Install

**Problem:** `pip install -r requirements.txt` fails

**Solutions:**
1. Upgrade pip: `pip install --upgrade pip`
2. Use Python 3.9+: `python3 --version`
3. Install system dependencies:
   - Ubuntu/Debian: `sudo apt-get install python3-dev ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download ffmpeg from https://ffmpeg.org/

### Node Dependencies Fail to Install

**Problem:** `npm install` fails in frontend

**Solutions:**
1. Clear npm cache: `npm cache clean --force`
2. Delete node_modules: `rm -rf node_modules package-lock.json`
3. Use Node 18+: `node --version`
4. Try: `npm install --legacy-peer-deps`

## Runtime Issues

### Backend Won't Start

**Problem:** Backend crashes on startup

**Check:**
1. Python path is set:
   ```bash
   cd backend
   export PYTHONPATH=$(pwd)
   cd app
   python main.py
   ```

2. Dependencies are installed:
   ```bash
   pip list | grep -E "fastapi|uvicorn|anthropic"
   ```

3. .env file exists:
   ```bash
   ls backend/.env
   ```

4. Check logs for specific errors

### Frontend Won't Start

**Problem:** Electron window doesn't open

**Check:**
1. Backend is running first (frontend needs API)
2. Port 5173 is available: `lsof -i :5173`
3. Install dependencies: `cd frontend && npm install`
4. Check console output for errors

### "Module not found" Errors

**Problem:** Import errors in Python

**Solution:**
Always set PYTHONPATH when running backend:
```bash
export PYTHONPATH=/path/to/babblr/backend
```

Or use the provided script:
```bash
./run-backend.sh
```

## API Issues

### "Anthropic API key not configured"

**Problem:** API calls fail with authentication error

**Solution:**
1. Get API key from https://console.anthropic.com/
2. Add to `backend/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```
3. Restart backend

### "Connection refused" Errors

**Problem:** Frontend can't reach backend

**Check:**
1. Backend is running: `curl http://localhost:8000/health`
2. Backend is on correct port (8000)
3. CORS is configured correctly
4. No firewall blocking localhost

### Speech-to-Text Not Working

**Problem:** Voice recording doesn't transcribe

**Solutions:**
1. Install Whisper:
   ```bash
   pip install openai-whisper
   ```

2. Install ffmpeg (required by Whisper):
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

3. Check microphone permissions in browser/OS

4. Test microphone access:
   - Open DevTools Console
   - Should see microphone permission prompt

### Text-to-Speech Not Working

**Problem:** No audio playback

**Solutions:**
1. Install edge-tts:
   ```bash
   pip install edge-tts
   ```

2. Check backend logs for TTS errors

3. Test manually:
   ```bash
   curl -X POST http://localhost:8000/tts/synthesize \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello", "language": "english"}' \
     --output test.mp3
   ```

## Database Issues

### "Database is locked"

**Problem:** SQLite database lock errors

**Solution:**
1. Stop all backend instances
2. Delete lock file if exists: `rm backend/babblr.db-journal`
3. Restart backend

### Corrupted Database

**Problem:** Database errors, corrupt data

**Solution:**
1. Backup current database: `cp backend/babblr.db backend/babblr.db.backup`
2. Delete database: `rm backend/babblr.db`
3. Restart backend (will recreate clean database)

## Performance Issues

### Slow Transcription

**Problem:** Whisper takes too long

**Solutions:**
1. Use smaller model in `whisper_service.py`:
   ```python
   self.model = whisper.load_model("tiny")  # or "base", "small"
   ```

2. Consider using Whisper API instead of local model

### High Memory Usage

**Problem:** Application uses too much RAM

**Solutions:**
1. Use smaller Whisper model (see above)
2. Restart application periodically
3. Close unused conversations
4. Clear old audio files from `backend/audio_output/`

## Electron Issues

### Window Doesn't Open

**Problem:** Electron starts but no window appears

**Check:**
1. DevTools for errors: Start with `npm run electron:dev`
2. Check main.js for errors
3. Try: `npm rebuild electron`

### Window is Blank

**Problem:** Window opens but shows nothing

**Check:**
1. Vite dev server is running (should auto-start)
2. Open DevTools and check Console
3. Check Network tab for failed requests
4. Try: `cd frontend && npm run dev` separately

## Development Issues

### Hot Reload Not Working

**Problem:** Changes don't appear without restart

**Frontend:**
- Vite should auto-reload
- Check terminal for errors
- Try: Ctrl+R in Electron window

**Backend:**
- Use uvicorn with --reload:
  ```bash
  export PYTHONPATH=$(pwd)
  uvicorn app.main:app --reload
  ```

### TypeScript Errors

**Problem:** Type errors in VS Code

**Solution:**
1. Install dependencies: `cd frontend && npm install`
2. Restart TypeScript server in VS Code
3. Check tsconfig.json is correct

## Platform-Specific Issues

### macOS

**Problem:** "App is damaged" message

**Solution:**
```bash
xattr -cr /path/to/Babblr.app
```

### Linux

**Problem:** No sound in Electron

**Solution:**
Install ALSA or PulseAudio:
```bash
sudo apt-get install alsa-utils pulseaudio
```

### Windows

**Problem:** Python not found

**Solution:**
1. Install from python.org
2. Add to PATH during installation
3. Use `py` instead of `python3`

## Getting More Help

If you're still stuck:

1. **Check logs carefully** - errors usually indicate the problem
2. **Search GitHub issues** - someone may have had the same problem
3. **Backend logs**: Terminal where you ran `./run-backend.sh`
4. **Frontend logs**: DevTools Console (View → Toggle Developer Tools)
5. **API logs**: DevTools Network tab

## Debug Mode

Enable verbose logging:

**Backend:**
```python
# In app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```bash
# Open DevTools automatically
npm run electron:dev
```

## Clean Slate

If all else fails, start fresh:

```bash
# Backend
cd backend
rm -rf __pycache__ *.db
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules dist
npm install

# Restart both
./run-backend.sh  # Terminal 1
./run-frontend.sh  # Terminal 2
```
