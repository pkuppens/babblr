#!/bin/bash

echo "🚀 Setting up Babblr Language Learning App"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo "✅ Python $(python3 --version) found"
echo "✅ Node.js $(node --version) found"
echo ""

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please add your ANTHROPIC_API_KEY to backend/.env before running the app"
fi

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies"
    exit 1
fi

echo "✅ Backend setup complete"
echo ""

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

echo "Installing Node.js dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

echo "✅ Frontend setup complete"
echo ""

# Done
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your Anthropic API key to backend/.env"
echo "2. Start the backend: ./run-backend.sh"
echo "3. Start the frontend: ./run-frontend.sh"
echo ""
echo "Note: Backend uses virtual environment (backend/venv)"
echo "Tip: For better package management, consider using 'uv' instead of pip"
echo "Happy learning! 🗣️"
