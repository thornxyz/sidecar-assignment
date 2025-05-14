# AI-Powered Web Automation Solution

This project implements an AI-powered solution to automate interactions with seacargotracking.net for retrieving voyage numbers and arrival dates associated with booking IDs.

## Key Features

### 1. Initial Retrieval without Hardcoding

- The solution uses the Gemini AI model to interpret web page structure and find appropriate input fields
- No hardcoded XPaths or element selectors are used
- AI determines the correct fields to interact with based on natural language descriptions

### 2. Process Persistence and Storage

- The solution stores interaction patterns in `interaction_patterns.json`
- Each interaction (like finding input fields, identifying result elements) is saved for future use
- For repeat visits, the system tries the stored patterns first before falling back to AI-based detection
- Results are stored in `search_history.json` for future reference

### 3. Adaptability and Generalization

- Works with any booking ID via command-line parameter
- Adapts to website changes by falling back to AI detection when stored patterns fail
- Updates stored patterns based on successful interactions, creating a self-improving system

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/thornxyz/sidecar-assignment.git
   cd sidecar-assignment
   ```

2. **Automatic Setup**:

   - On Windows (PowerShell):

     ```
     .\run.ps1
     ```

   - On Windows (Command Prompt):

     ```
     run.bat
     ```

   - On Linux/Mac:
     ```
     chmod +x run.sh
     ./run.sh
     ```

3. **Manual Setup**:

   Create a virtual environment:

   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```

   Install dependencies:

   ```
   pip install -r requirements.txt
   ```

   Create a `.env` file in the root directory with your Gemini API key:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## How to Run

1. **Using the Run Scripts** (Recommended):

   - Run with default booking ID:

     ```
     # On Windows (PowerShell)
     .\run.ps1

     # On Windows (Command Prompt)
     run.bat

     # On Linux/Mac
     ./run.sh
     ```

   - Run with custom booking ID:

     ```
     # On Windows (PowerShell)
     .\run.ps1 --booking_id YOUR_BOOKING_ID

     # On Windows (Command Prompt)
     run.bat --booking_id YOUR_BOOKING_ID

     # On Linux/Mac
     ./run.sh --booking_id YOUR_BOOKING_ID
     ```

2. **Manual Execution**:

   - Run with default booking ID:

     ```
     python main.py
     ```

   - Run with custom booking ID:
     ```
     python main.py --booking_id YOUR_BOOKING_ID
     ```

3. The program will:
   - Connect to seacargotracking.net
   - Use stored interaction patterns or AI to find the input field
   - Submit the booking ID and extract the voyage number and arrival date
   - Store the interaction patterns for future use
   - Save the results to search_history.json

## Technical Implementation

1. **Interaction Pattern Storage**

   - Stores XPaths, element identifiers, and other interaction data
   - Timestamps patterns to track recency
   - Creates a history of successful interactions

2. **Fallback Mechanism**

   - First attempts to use stored patterns
   - Falls back to AI-based detection if stored patterns fail
   - Updates patterns with successful interactions

3. **Result Validation**
   - Uses AI to extract structured data from unstructured webpage content
   - Validates and stores the extracted data

## Requirements

- Python 3.8 or higher
- Chrome browser installed
- Google Gemini API Key

See `requirements.txt` for detailed Python dependencies.
