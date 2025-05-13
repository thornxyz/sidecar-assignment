from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from the .env file
api_key = os.getenv("GEMINI_API_KEY")

# Initialize the GenAI client
client = genai.Client(api_key=api_key)

chrome_options = Options()
chrome_options.add_argument(
    "--allow-insecure-localhost"
)  # Allow insecure connections for non-HTTPS sites
chrome_options.add_argument("--headless")  # Run browser in headless mode
chrome_options.add_argument(
    "--disable-gpu"
)  # Disable GPU for headless mode compatibility
chrome_options.add_argument(
    "--window-size=1920,1080"
)  # Set window size for headless mode
driver = webdriver.Chrome(options=chrome_options)

# Open a web page
driver.get("http://seacargotracking.net")

# Use the GenAI client to embed content
result = client.models.embed_content(
    model="gemini-embedding-exp-03-07",
    contents="What is the meaning of life?",
    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY"),
)

# Print the embeddings
print(result.embeddings)

# Close the browser
driver.quit()
