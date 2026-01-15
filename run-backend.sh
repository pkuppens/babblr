#!/bin/bash

# Start backend server using uv
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Allow running the script again from a different working directory by
# adding the project root (where this script lives) to PATH.
export PATH="$SCRIPT_DIR:$PATH"

DEV_MODE=0
if [ "$1" = "dev" ] || [ "$1" = "development" ] || [ "$1" = "--dev" ] || [ "$1" = "--development" ]; then
    DEV_MODE=1
fi

# Change to backend directory
cd "$BACKEND_DIR" || {
    echo "[ERROR] Cannot access backend directory: $BACKEND_DIR"
    exit 1
}

# Unset VIRTUAL_ENV if it points to a different location (e.g., root .venv)
# This ensures uv uses the backend/.venv instead
if [ -n "$VIRTUAL_ENV" ]; then
    if [ "$VIRTUAL_ENV" != "$(pwd)/.venv" ] && [ "$VIRTUAL_ENV" != "$BACKEND_DIR/.venv" ]; then
        echo "[INFO] Unsetting VIRTUAL_ENV to use backend/.venv"
        unset VIRTUAL_ENV
    fi
fi

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "[START] Starting Babblr backend with uv..."
    echo "   Working directory: $(pwd)"
    echo "   Virtual environment: $(pwd)/.venv"
    if [ "$DEV_MODE" = "1" ]; then
        echo "   Mode: development (auto-reload on changes)"
    else
        echo "   Mode: production"
    fi
    
    # Ensure .venv exists in backend directory
    if [ ! -d ".venv" ]; then
        echo "[WARNING] Virtual environment not found. Creating .venv in backend directory..."
        uv venv
    fi
    
    # Set PYTHONPATH to backend directory
    export PYTHONPATH="$(pwd)"

    # Ensure .env is loaded from backend directory
    if [ -f ".env" ]; then
        echo "   Using .env from: $(pwd)/.env"
    else
        echo "[WARNING] .env file not found in backend directory"
    fi
    
    # Run the server
    if [ "$DEV_MODE" = "1" ]; then
        # Dev mode: use uvicorn CLI directly for reliable reload
        # Read host/port from env or use defaults matching config.py
        API_HOST="${BABBLR_API_HOST:-127.0.0.1}"
        API_PORT="${BABBLR_API_PORT:-8000}"
        uv run uvicorn app.main:app --reload --host "$API_HOST" --port "$API_PORT"
    else
        # Production mode: use the entry point (no reload)
        uv run babblr-backend
    fi
else
    echo "[WARNING] uv not found, falling back to standard Python..."
    echo "   For better performance, install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    
    # Fallback: manually activate venv if it exists
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    export PYTHONPATH="$(pwd)"
    if [ "$DEV_MODE" = "1" ]; then
        # Dev mode: use uvicorn CLI directly for reliable reload
        API_HOST="${BABBLR_API_HOST:-127.0.0.1}"
        API_PORT="${BABBLR_API_PORT:-8000}"
        python -m uvicorn app.main:app --reload --host "$API_HOST" --port "$API_PORT"
    else
        # Production mode
        cd app
        python main.py
    fi
fi
