# Sidecar Assignment

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- UV package manager

### Installation

```bash
#install dependencies
uv add -r requirements.txt

#install playwright
uv run playwright install
```

### Make env file

```env
GOOGLE_API_KEY=your google api key
```

### Running the Project

To run the browser-use script:

```bash
uv run main.py
```

This will create a `result.txt` file and a `selenium_actions.json` where all the browser interactions are stored.

To run the selenium automation script which reads from the cached json:

```bash
uv run selenium_automation.py
```
