#!/bin/bash
# Launcher script for GestureMate

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 to run GestureMate."
    exit 1
fi

# Check if PyQt6 is installed
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "PyQt6 is not installed. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the application
python3 gesturemate.py "$@"
