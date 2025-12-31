# Development Guide

## Project Structure

```
babblr/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI application entry
│   │   ├── config.py         # Configuration management
│   │   ├── database/         # Database setup and session management
│   │   ├── models/           # SQLAlchemy & Pydantic models
│   │   ├── routes/           # API route handlers
│   │   └── services/         # External service integrations
│   ├── requirements.txt
│   └── test_backend.py       # Basic validation tests
│
├── frontend/          # Electron + React frontend
│   ├── electron/             # Electron main process
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   ├── types/            # TypeScript definitions
│   │   ├── App.tsx           # Main application
│   │   └── main.tsx          # React entry point
│   ├── package.json
│   └── vite.config.ts        # Vite configuration
│
├── setup.sh           # One-time setup script
├── run-backend.sh     # Start backend server
└── run-frontend.sh    # Start frontend in dev mode
```

## Development Workflow

### Initial Setup

```bash
./setup.sh
```

This will:
1. Check for Python and Node.js
2. Install backend dependencies
3. Install frontend dependencies
4. Create .env file

### Running the Application

**Terminal 1 - Backend:**
```bash
./run-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./run-frontend.sh
```

### Making Changes

#### Backend Changes

1. Make your changes in `backend/app/`
2. The server will auto-reload if using `uvicorn --reload`
3. Test your changes:
   ```bash
   cd backend
   PYTHONPATH=$(pwd) python test_backend.py
   ```

#### Frontend Changes

1. Make your changes in `frontend/src/`
2. Vite hot-reloads automatically
3. Changes appear instantly in the Electron window

## API Development

### Adding a New Endpoint

1. Create route handler in `backend/app/routes/`
2. Define Pydantic schemas in `backend/app/models/schemas.py`
3. Add database models if needed in `backend/app/models/models.py`
4. Register router in `backend/app/main.py`

Example:
```python
# backend/app/routes/my_feature.py
from fastapi import APIRouter

router = APIRouter(prefix="/my-feature", tags=["my-feature"])

@router.get("/")
async def get_feature():
    return {"status": "ok"}
```

Then in `main.py`:
```python
from app.routes import my_feature
app.include_router(my_feature.router)
```

### Adding a New Service

1. Create service class in `backend/app/services/`
2. Make imports optional for external dependencies
3. Create singleton instance at module level

Example:
```python
# backend/app/services/my_service.py
try:
    import external_library
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

class MyService:
    def __init__(self):
        if not AVAILABLE:
            print("⚠️  Service not available")
    
    async def do_something(self):
        if not AVAILABLE:
            raise Exception("Service not installed")
        # Implementation

my_service = MyService()
```

## Frontend Development

### Adding a New Component

1. Create `.tsx` file in `frontend/src/components/`
2. Create corresponding `.css` file for styles
3. Import and use in parent component

Example:
```typescript
// frontend/src/components/MyComponent.tsx
import React from 'react';
import './MyComponent.css';

interface MyComponentProps {
  title: string;
}

const MyComponent: React.FC<MyComponentProps> = ({ title }) => {
  return <div className="my-component">{title}</div>;
};

export default MyComponent;
```

### Calling Backend APIs

Use the API service in `frontend/src/services/api.ts`:

```typescript
import { conversationService } from '../services/api';

const conversations = await conversationService.list();
```

To add a new API method:

```typescript
// frontend/src/services/api.ts
export const myService = {
  async getData(): Promise<MyType> {
    const response = await api.get('/my-endpoint');
    return response.data;
  },
};
```

## Testing

### Backend Testing

Basic validation:
```bash
cd backend
PYTHONPATH=$(pwd) python test_backend.py
```

Manual API testing:
```bash
# Start the server
./run-backend.sh

# In another terminal
curl http://localhost:8000/health
```

### Frontend Testing

Manual testing:
1. Start the app with `./run-frontend.sh`
2. Use Chrome DevTools (View → Toggle Developer Tools)
3. Check console for errors
4. Test UI interactions

## Common Issues

### Backend won't start

- Check Python version: `python3 --version` (need 3.9+)
- Verify dependencies: `pip list | grep fastapi`
- Check PYTHONPATH: `echo $PYTHONPATH`
- Look for error messages in terminal

### Frontend won't start

- Check Node version: `node --version` (need 18+)
- Clear node_modules: `rm -rf frontend/node_modules && cd frontend && npm install`
- Check for port conflicts on 5173 and 8000

### Whisper not working

Whisper is optional but required for voice input:
```bash
pip install openai-whisper
```

Note: Whisper requires `ffmpeg` to be installed on your system.

### API key errors

Make sure you've added your Anthropic API key to `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Best Practices

1. **Keep changes minimal** - Focus on one feature at a time
2. **Test as you go** - Don't wait until the end
3. **Use TypeScript types** - Leverage the type system
4. **Handle errors gracefully** - Show user-friendly messages
5. **Log appropriately** - Use `console.log` in frontend, `print()` in backend
6. **Keep services optional** - Not everyone will have all dependencies

## Database

SQLite database is created automatically at `backend/babblr.db`.

To reset the database:
```bash
rm backend/babblr.db
# Restart backend to recreate
```

## Building for Production

### Frontend

```bash
cd frontend
npm run build
npm run electron:build
```

Output will be in `frontend/release/`.

## Environment Variables

Backend (`.env`):
```
ANTHROPIC_API_KEY=your_key_here
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./babblr.db
FRONTEND_URL=http://localhost:3000
```

## Getting Help

Check the logs:
- Backend: Terminal output where you ran `./run-backend.sh`
- Frontend: Electron DevTools console
- Network: Browser DevTools Network tab

Common log locations:
- Backend errors: Terminal
- Frontend errors: DevTools Console
- API errors: DevTools Network tab
