# Babblr Frontend

Electron + React + TypeScript frontend for the Babblr language learning application.

## Development

```bash
# Install dependencies
npm install

# Run in development mode (starts Vite dev server + Electron)
npm run electron:dev

# Or run them separately:
npm run dev          # Vite dev server only
npm run electron     # Electron only (requires dev server to be running)

# Build
npm run build        # Build React app
npm run electron:build  # Build Electron app
```

## Scripts

- `npm run dev` - Start Vite dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run electron` - Start Electron
- `npm run electron:dev` - Start both Vite and Electron concurrently
- `npm run electron:build` - Build Electron app with electron-builder

## Structure

```
src/
├── components/
│   ├── LanguageSelector.tsx      # Language and difficulty selection
│   ├── ConversationList.tsx      # Recent conversations list
│   ├── ConversationInterface.tsx # Main chat interface
│   ├── VoiceRecorder.tsx         # Voice recording button
│   └── MessageBubble.tsx         # Individual message display
├── services/
│   └── api.ts                    # Backend API client
├── types/
│   └── index.ts                  # TypeScript type definitions
├── App.tsx                       # Main application component
└── main.tsx                      # React entry point
```

## Configuration

The frontend expects the backend API to be running at `http://localhost:8000`.

You can modify this in `src/services/api.ts` if needed.

## Building

The app is built using:
- **Vite** for fast development and building
- **electron-builder** for packaging the desktop app

Built apps will be in the `release/` directory.
