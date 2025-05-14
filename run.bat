@echo off
echo Setting up AI-Powered Web Automation Solution...

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is required but not installed.
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists, prompt to create if not
if not exist .env (
    echo .env file not found. Creating one now...
    set /p api_key=Please enter your Gemini API key: 
    echo GEMINI_API_KEY=%api_key%> .env
    echo .env file created.
)

REM Check for command line arguments and run
echo Running the application...
if "%~1"=="" (
    REM No arguments provided, run with default
    python main.py
) else (
    REM Arguments provided, pass them to main.py
    python main.py %*
)

echo Program execution complete.
pause
