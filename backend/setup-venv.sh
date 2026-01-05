#!/bin/bash
# Setup script for backend virtual environment using uv
# This creates .venv in the backend directory (not root)

set -e  # Exit on error

echo "Setting up backend virtual environment with uv"
echo ""

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "[ERROR] This script must be run from the backend directory"
    echo "   Run: cd backend && ./setup-venv.sh"
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "[ERROR] uv is not installed"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "[OK] uv found: $(uv --version)"
echo ""

# Remove existing .venv if it exists
if [ -d ".venv" ]; then
    echo "[INFO] Removing existing .venv..."
    rm -rf .venv
fi

# Create new virtual environment
echo "[INFO] Creating virtual environment with uv..."
uv venv

if [ ! -d ".venv" ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "[OK] Virtual environment created: $(pwd)/.venv"
echo ""

# Install dependencies
echo "[INFO] Installing dependencies from pyproject.toml..."
uv pip install -e ".[dev]"

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[OK] Dependencies installed"
echo ""

if command -v git &> /dev/null && git rev-parse --is-inside-work-tree &> /dev/null; then
    HOOKS_DIR="$(git rev-parse --git-path hooks 2>/dev/null || true)"
    if [ -n "$HOOKS_DIR" ] && [ ! -f "$HOOKS_DIR/pre-commit" ]; then
        echo "[SETUP] Installing pre-commit hooks..."
        uv run pre-commit install || echo "[WARNING] Could not install pre-commit hooks"
    else
        echo "[OK] pre-commit hooks already installed"
    fi
fi

# Verify installation
echo "[INFO] Verifying installation..."
if uv run python -c "import fastapi; import whisper; print('[OK] Core dependencies verified')" 2>/dev/null; then
    echo "[OK] Installation verified successfully"
else
    echo "[WARNING] Some dependencies may not be installed correctly"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Virtual environment location: $(pwd)/.venv"
echo ""
echo "Next steps:"
echo "1. Create .env file if needed: cp .env.example .env"
echo "2. Add your ANTHROPIC_API_KEY to backend/.env"
echo "3. Run backend: ./run-backend.sh (from project root)"
echo ""

