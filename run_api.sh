#!/bin/bash
# Activate virtual environment and run the API

# Script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ ! -d "api_venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv api_venv
    
    echo "Installing dependencies..."
    source api_venv/bin/activate
    pip install -r api/requirements.txt
else
    # Activate virtual environment
    source api_venv/bin/activate
fi

# Run the application
echo "Starting TinyMQ API..."
./start_api.py "$@"

# Deactivation happens automatically when script ends 