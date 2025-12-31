# Babblr

A desktop language learning app that lets you speak naturally with an AI tutor. Learn Spanish, Italian, German, French, or Dutch through immersive conversations with adaptive difficulty.

## Features

🗣️ **Natural Conversation**: Speak naturally with Claude AI, not like a textbook  
🎤 **Voice Recording**: Record your speech and get instant transcription via Whisper  
✨ **Error Correction**: Get gentle, contextual corrections on grammar and vocabulary  
🔊 **Text-to-Speech**: Hear natural pronunciation with multi-language TTS  
📚 **Vocabulary Tracking**: Automatically track new words and phrases  
🎯 **Adaptive Difficulty**: Beginner to advanced levels that match your skills  
💾 **Conversation History**: Save and continue your learning sessions

## Tech Stack

### Frontend
- **Electron**: Desktop application framework
- **React**: UI library
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool

### Backend
- **FastAPI**: Modern Python web framework
- **OpenAI Whisper**: Speech-to-text transcription
- **Anthropic Claude**: AI conversation and error correction
- **Edge TTS**: Free text-to-speech synthesis
- **SQLite**: Local database for conversations and vocabulary

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Anthropic API Key** (free tier available at https://console.anthropic.com/)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
```

5. Run the backend:
```bash
cd app
python main.py
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run in development mode:
```bash
npm run electron:dev
```

This will start both the Vite dev server and Electron.

### Building for Production

Build the frontend:
```bash
cd frontend
npm run build
npm run electron:build
```

The built application will be in `frontend/release/`.

## Usage

1. **Start a Conversation**: Select your target language and difficulty level
2. **Talk or Type**: Use the microphone button to speak, or type your message
3. **Get Feedback**: See corrections and explanations for your mistakes
4. **Listen**: Hear the AI tutor's response with natural pronunciation
5. **Track Progress**: Review your conversation history and vocabulary

## Supported Languages

- 🇪🇸 Spanish
- 🇮🇹 Italian
- 🇩🇪 German
- 🇫🇷 French
- 🇳🇱 Dutch

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

```
babblr/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── database/            # Database setup
│   │   ├── models/              # SQLAlchemy & Pydantic models
│   │   ├── routes/              # API endpoints
│   │   └── services/            # AI service integrations
│   └── requirements.txt
│
└── frontend/
    ├── electron/
    │   └── main.js              # Electron main process
    ├── src/
    │   ├── components/          # React components
    │   ├── services/            # API client
    │   ├── types/               # TypeScript types
    │   └── App.tsx              # Main app component
    └── package.json
```

## Development Philosophy

This app focuses on:
- **Natural conversation** over gamification
- **Adaptive difficulty** that grows with you
- **Immersive learning** through practical use
- **Free/affordable** APIs and local processing

## Free Tier Limits

- **Claude (Anthropic)**: Check current free tier at anthropic.com
- **Whisper**: Runs locally, no API limits
- **Edge TTS**: Free Microsoft TTS service

## Contributing

This is an MVP for portfolio purposes. Feel free to fork and customize for your own use!

## License

MIT

## Acknowledgments

- OpenAI for Whisper
- Anthropic for Claude
- Microsoft for Edge TTS
