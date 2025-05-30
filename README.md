# Sidecar Assignment

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- UV package manager

### Installation

1. **Initialize UV project** (if not already done):

   ```bash
   uv init --python 3.12 .
   ```

2. **Add required dependencies**:

   ```bash
   uv add browser-use[memory] seleniumbase
   ```

3. **Install dependencies**:
   ```bash
   uv sync
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
