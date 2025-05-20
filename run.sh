#!/bin/bash
# Bash script to install and run the AI-Powered Web Automation Solution

echo -e "\e[32mSetting up AI-Powered Web Automation Solution...\e[0m"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo -e "\e[32mPython detected: $python_version\e[0m"
else
    echo -e "\e[31mError: Python 3 is required but not installed.\e[0m"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo -e "\e[33mCreating virtual environment...\e[0m"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "\e[33mActivating virtual environment...\e[0m"
source venv/bin/activate

# Install requirements
echo -e "\e[33mInstalling dependencies...\e[0m"
pip install -r requirements.txt

# Check if .env file exists, prompt to create if not
if [ ! -f ".env" ]; then
    echo -e "\e[33m.env file not found. Creating one now...\e[0m"
    read -p "Please enter your Gemini API key: " api_key
    echo "GEMINI_API_KEY=$api_key" > .env
    echo -e "\e[32m.env file created.\e[0m"
else
    # Check if GEMINI_API_KEY is present in the .env file
    if ! grep -q "GEMINI_API_KEY=.*" .env; then
        echo -e "\e[33mGEMINI_API_KEY not found in .env file.\e[0m"
        read -p "Please enter your Gemini API key: " api_key
        
        # Check if .env file is empty
        if [ ! -s ".env" ]; then
            # File is empty
            echo "GEMINI_API_KEY=$api_key" > .env
        else
            # Check if file ends with newline
            if [ "$(tail -c 1 .env)" != "" ]; then
                echo "" >> .env
            fi
            echo "GEMINI_API_KEY=$api_key" >> .env
        fi
        echo -e "\e[32mGEMINI_API_KEY added to .env file.\e[0m"
    fi
fi

# Check for command line arguments and run
echo -e "\e[32mRunning the application...\e[0m"
if [ $# -eq 0 ]; then
    # No arguments provided, run with default
    python main.py
else
    # Arguments provided, pass them to main.py
    python main.py "$@"
fi

echo -e "\e[32mProgram execution complete.\e[0m"
read -p "Press Enter to exit"
