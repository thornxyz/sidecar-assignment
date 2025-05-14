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

## How to Run

```
python main.py --booking_id YOUR_BOOKING_ID
```

If no booking ID is provided, it will use the default "MSCU5285725".

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

- Python 3.6+
- Selenium
- BeautifulSoup4
- Google Gemini API Key (stored in .env file)
- Chrome WebDriver
