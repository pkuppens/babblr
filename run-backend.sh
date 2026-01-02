#!/bin/bash

# Start backend server using uv
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

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
    
    # Run using uv (preferred method)
    # uv run automatically uses the .venv in the current directory
    uv run babblr-backend
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
    cd app
    python main.py
fi
