#!/bin/bash

# Start backend server using uv
cd "$(dirname "$0")/backend"

# Check if uv is available
if command -v uv &> /dev/null; then
    echo "🚀 Starting Babblr backend with uv..."
    
    # Activate virtual environment if it exists
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    export PYTHONPATH="$(pwd)"
    
    # Run using uv (preferred method)
    uv run babblr-backend
else
    echo "⚠️  uv not found, falling back to standard Python..."
    echo "   For better performance, install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    
    # Fallback to venv/pip method
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    export PYTHONPATH="$(pwd)"
    cd app
    python main.py
fi
