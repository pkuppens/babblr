#!/bin/bash

# Start backend server
cd "$(dirname "$0")/backend"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

export PYTHONPATH="$(pwd)"
cd app
python main.py
