# PowerShell script to install and run the AI-Powered Web Automation Solution

Write-Host "Setting up AI-Powered Web Automation Solution..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is required but not installed." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists, create if not
if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env file exists, prompt to create if not
if (-not (Test-Path -Path ".env")) {
    Write-Host ".env file not found. Creating one now..." -ForegroundColor Yellow
    $apiKey = Read-Host -Prompt "Please enter your Gemini API key"
    Set-Content -Path ".env" -Value "GEMINI_API_KEY=$apiKey"
    Write-Host ".env file created." -ForegroundColor Green
}

# Check for command line arguments and run
Write-Host "Running the application..." -ForegroundColor Green
if ($args.Count -eq 0) {
    # No arguments provided, run with default
    python main.py
} else {
    # Arguments provided, pass them to main.py
    python main.py $args
}

Write-Host "Program execution complete." -ForegroundColor Green
Read-Host -Prompt "Press Enter to exit"
