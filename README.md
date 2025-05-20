# AI-Powered Web Automation Solution

## Overview

This project implements an AI-powered solution to automate interactions with cargo tracking websites for retrieving voyage numbers and arrival dates associated with booking IDs.

The currently scrapes from the HMM cargo tracking page at https://www.hmm21.com/e-service/general/trackNTrace/TrackNTrace.do

But it's built to be general-purpose and adaptable to work with most cargo tracking websites.

## Architecture

The application follows a modular architecture designed to handle web form identification, interaction, and data extraction with built-in intelligence:

1. **Page Analysis**: Cleans HTML and identifies interactive form elements
2. **AI Integration**: Interprets page structure and generates interaction steps
3. **Interaction Engine**: Executes browser automation commands
4. **Caching System**: Stores successful interaction patterns for reuse
5. **Self-Healing Logic**: Detects and repairs broken interaction patterns

## Technologies Used

- **SeleniumBase**: Browser automation with undetectable features
- **BeautifulSoup4**: HTML parsing, element identification, and noise removal
- **Google Gemini AI** (google-genai): AI-powered form detection and data extraction
- **hashlib**: Hash generation for unique cache keys
- **python-dotenv**: Environment variable management for API keys

## Features

### 🔍 Automatic Form Detection

- Automatically identifies tracking number input fields on shipping websites
- Uses BeautifulSoup and Google's Gemini AI to analyze page structure
- Adapts to different form submission methods (enter key, button click, form submit)

### 🧠 Intelligent Interaction Caching

- Stores successful interactions in a structured cache for future reuse
- Generates unique hash keys based on URL and tracking number
- Significantly improves response time for repeated tracking queries

### 🛠️ Self-Healing Interactions

- Detects when page selectors have changed since last interaction
- Automatically repairs and updates interaction patterns
- Maintains success/failure statistics to improve reliability over time

### 📊 Data Extraction and Analysis

- Cleans and processes tracking results using BeautifulSoup
- Extracts key shipping information (voyage number, ETA, status)
- Presents results in a clean, structured format

## Requirements

- Python 3.8+
- Google Gemini API key
- Dependencies as listed in `requirements.txt`

## Setup and Run

### Automatic Setup (Recommended)

#### Windows

1. Clone the repository:

   ```
   git clone https://github.com/thornxyz/sidecar-assignment.git
   cd sidecar-assignment
   ```

2. Run the setup script:

   ```
   .\run.ps1
   ```

   This script will:

   - Check for Python installation
   - Create and activate a virtual environment
   - Install all required dependencies
   - Create a `.env` file (prompting for your Gemini API key)
   - Run the application

#### Linux/macOS

1. Clone the repository:

   ```
   git clone https://github.com/thornxyz/sidecar-assignment.git
   cd sidecar-assignment
   ```

2. Make the bash script executable and run it:

   ```
   chmod +x run.sh
   ./run.sh
   ```

   This script performs the same setup steps as the PowerShell version.

### Manual Setup

1. Clone the repository:

   ```
   git clone https://github.com/thornxyz/sidecar-assignment.git
   cd sidecar-assignment
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Gemini API key:

   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. Run the application:
   ```
   python main.py
   ```

## Usage

The default tracking URL is set to HMM's cargo tracking page. To track shipments from different carriers:

1. Modify the `url` variable in `main.py` to point to the desired tracking website.
2. Modify the `bl_number` variable in `main.py` to use own id.
