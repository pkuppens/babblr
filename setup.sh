#!/bin/bash

echo "Setting up Babblr Language Learning App with uv"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed. Please install Python 3.12 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed. Please install Node.js 22 or higher."
    exit 1
fi

echo "[OK] Python $(python3 --version) found"
echo "[OK] Node.js $(node --version) found"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "[INFO] uv is not installed. Installing uv..."
    echo ""
    echo "uv is a fast Python package installer and resolver."
    echo "Installing via official installer..."
    echo ""
    
    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Check if installation succeeded
    if ! command -v uv &> /dev/null; then
        echo "[ERROR] Failed to install uv. Please install manually:"
        echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "   Or: pip install uv"
        exit 1
    fi
    
    echo "[OK] uv installed successfully"
else
    echo "[OK] uv $(uv --version) found"
    echo "Updating uv to latest version..."
    uv self update || echo "[WARNING] Could not auto-update uv (may need manual update)"
fi

echo ""

# Setup backend
echo "[SETUP] Setting up backend with uv..."
cd backend

# Create virtual environment with uv
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment with uv..."
    uv venv
fi

if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "[WARNING] Please add your ANTHROPIC_API_KEY to backend/.env before running the app"
fi

echo "Installing Python dependencies with uv..."
uv pip install -e ".[dev]"

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install backend dependencies"
    exit 1
fi

echo "[OK] Backend setup complete"
echo ""

# Setup frontend
echo "[SETUP] Setting up frontend..."
cd ../frontend

echo "Installing Node.js dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install frontend dependencies"
    exit 1
fi

echo "[OK] Frontend setup complete"
echo ""

# Done
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your Anthropic API key to backend/.env"
echo "2. Start the backend: ./run-backend.sh"
echo "3. Start the frontend: ./run-frontend.sh"
echo ""
echo "Documentation:"
echo "   - See UV_SETUP.md for detailed uv usage"
echo "   - See QUICKSTART.md for quick start guide"
echo ""
echo "Note: Backend uses uv for fast package management (.venv)"
echo "Happy learning!"
