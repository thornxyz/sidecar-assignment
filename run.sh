#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Setting up AI-Powered Web Automation Solution..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, prompt to create if not
if [ ! -f ".env" ]; then
    echo ".env file not found. Creating one now..."
    echo "Please enter your Gemini API key:"
    read api_key
    echo "GEMINI_API_KEY=${api_key}" > .env
    echo ".env file created."
fi

# Check for command line arguments and run
echo "Running the application..."
if [ $# -eq 0 ]; then
    # No arguments provided, run with default
    python main.py
else
    # Arguments provided, pass them to main.py
    python main.py "$@"
fi

echo "Program execution complete."
