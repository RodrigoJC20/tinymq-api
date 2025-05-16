#!/bin/bash
# Activate virtual environment and run the GUI

# Script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ ! -d "gui_venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv gui_venv
    
    echo "Installing dependencies..."
    source gui_venv/bin/activate
    pip install -r gui/requirements.txt
else
    # Activate virtual environment
    source gui_venv/bin/activate
fi

# Run the application
echo "Starting TinyMQ GUI..."
./start_gui.py

# Deactivation happens automatically when script ends 