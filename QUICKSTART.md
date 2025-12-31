# Quick Start Guide

Get Babblr running in 5 minutes!

## Prerequisites

Before you start, make sure you have:

1. **Python 3.12+** - Check with: `python3 --version`
2. **Node.js 22+** - Check with: `node --version`
3. **Anthropic API Key** - Get free tier at: https://console.anthropic.com/

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/pkuppens/babblr.git
cd babblr

# Run setup script (installs uv and everything else)
./setup.sh
```

The setup script will:
- Install **uv** (fast Python package manager) if not present
- Create a Python virtual environment with uv
- Install backend dependencies with uv
- Install frontend dependencies with npm
- Create configuration file

**What is uv?** uv is a blazingly fast Python package installer (10-100x faster than pip). The setup script installs it automatically. See [UV_SETUP.md](UV_SETUP.md) for details.

## Step 2: Configure API Key (1 minute)

Open `backend/.env` and add your Anthropic API key:

```bash
# Edit the file
nano backend/.env  # or use your favorite editor

# Add this line:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Save and close.

## Step 3: Start Backend (30 seconds)

Open a terminal and run:

```bash
./run-backend.sh
```

You should see:
```
🚀 Starting Babblr backend with uv...
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal open!**

## Step 4: Start Frontend (30 seconds)

Open a **second terminal** and run:

```bash
./run-frontend.sh
```

The Electron app window will open automatically.

## Step 5: Start Learning! (30 seconds)

1. **Select a language** - Click on Spanish, Italian, German, French, or Dutch
2. **Choose difficulty** - Beginner, Intermediate, or Advanced
3. **Click "Start Learning"**
4. **Start talking!** 
   - Click the 🎤 microphone button and speak
   - Or type your message and press Enter

That's it! You're now conversing with an AI language tutor.

## First Conversation Example

Try this to test everything:

1. Select **Spanish** and **Beginner**
2. Click **Start Learning**
3. Type: "Hola, ¿cómo estás?"
4. Press Enter or click Send
5. The AI will respond in Spanish and you'll hear it speak!

## Optional: Install Voice & Audio (5 minutes)

For voice input and audio output, install these optional features:

### Voice Input (Whisper)

```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Install Whisper
pip install openai-whisper

# On Ubuntu/Debian, also install:
sudo apt-get install ffmpeg

# On macOS:
brew install ffmpeg
```

### Audio Output (TTS)

```bash
# Already included in requirements.txt
# Just make sure edge-tts is installed:
pip install edge-tts
```

Restart the backend after installing these.

## Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Make sure you activated the virtual environment
cd backend
source venv/bin/activate
```

### Frontend won't start

```bash
# Make sure backend is running first
# Check if port 5173 is available
lsof -i :5173

# Try reinstalling dependencies
cd frontend
rm -rf node_modules
npm install
```

### "API key not configured" error

Make sure you:
1. Created `.env` file in `backend/` directory
2. Added your actual API key (starts with `sk-ant-`)
3. Restarted the backend server

### Voice recording not working

1. Check microphone permissions in your browser/OS
2. Install Whisper: `pip install openai-whisper`
3. Install ffmpeg (see instructions above)
4. Restart backend

## Testing Without Frontend

Want to test the backend API directly?

```bash
# Make sure backend is running
./run-backend.sh

# In another terminal:
python examples/test_api.py
```

## What's Next?

### Learn More
- Read [README.md](README.md) for full feature list
- Check [DEVELOPMENT.md](DEVELOPMENT.md) for developer guide
- See [VISUAL_GUIDE.md](VISUAL_GUIDE.md) for UI walkthrough

### Customize
- Change languages: Edit `frontend/src/components/LanguageSelector.tsx`
- Adjust AI model: Set `CLAUDE_MODEL` in `backend/.env`
- Change Whisper model: Set `WHISPER_MODEL` in `backend/.env`

### Practice!
- Try different difficulty levels
- Practice introducing yourself
- Ask about topics you're interested in
- Pay attention to corrections and learn from them

## Tips for Best Experience

1. 🎧 **Use headphones** - Prevents audio feedback with TTS
2. 🎤 **Good microphone** - Better transcription accuracy
3. 🗣️ **Speak naturally** - Don't over-enunciate
4. 📝 **Note corrections** - They're learning opportunities
5. ⏰ **Short sessions** - 10-15 minutes daily beats long cramming

## Common Commands

```bash
# Start everything
./run-backend.sh    # Terminal 1
./run-frontend.sh   # Terminal 2

# Stop everything
# Just close both terminals or press Ctrl+C

# Reset database (fresh start)
rm backend/babblr.db
# Restart backend to recreate

# View API docs
# Start backend, then open:
# http://localhost:8000/docs

# Test backend
python examples/test_api.py
```

## Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Backend logs: Check terminal where backend is running
- Frontend logs: Open DevTools (View → Toggle Developer Tools)

## Minimum Requirements

- **OS**: macOS, Linux, or Windows
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB for app + dependencies
- **Network**: Internet connection for AI features

## Free Tier Limits

- **Claude**: Check anthropic.com for current limits
- **Whisper**: Runs locally, no API costs
- **Edge TTS**: Free unlimited
- **Storage**: SQLite, local only

---

**Happy Learning! 🗣️**

Start with simple phrases and build from there. The AI adapts to your level!
