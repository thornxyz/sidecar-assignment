from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from google import genai
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import time
import re
import json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--allow-insecure-localhost")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-site-isolation-trials")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=chrome_options
)

container_number = "MSCU5285725"

try:
    driver.get("http://seacargotracking.net")
    time.sleep(2)

    body_html = driver.find_element(By.TAG_NAME, "body").get_attribute("outerHTML")

    prompt = f"""
You are controlling a web browser via automation. 
Your task is to find the input field where a user is supposed to enter a shipping container number on the following webpage HTML. 
Return your answer in JSON format like this:
{{
  "description": "...",
  "xpath": "...",
  "value": "{container_number}"
}}

Here is the body HTML:
{body_html}
"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    reply = response.text

    json_str = re.search(r"\{.*?\}", reply, re.DOTALL)
    if not json_str:
        raise ValueError("No JSON found in Gemini response.")

    data = json.loads(json_str.group(0))

    xpath = data["xpath"]
    value = data["value"]

    input_field = driver.find_element(By.XPATH, xpath)
    input_field.send_keys(value)
    input_field.send_keys(Keys.RETURN)

    time.sleep(5)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(5)

    print("Current URL:", driver.current_url)

    output_html = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")

    # Parse HTML to get clean visible text content
    soup = BeautifulSoup(output_html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    visible_text = soup.get_text(separator="\n", strip=True)

    info_prompt = f"""
From the following webpage content, extract the **Voyage Number** and **Arrival Date** if they exist. 
Return only a clean JSON output like this:
{{
  "voyage_number": "...",
  "arrival_date": "..."
}}

Content:
{visible_text}
"""

    info_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=info_prompt,
    )

    print("Extracted Info:")
    print(info_response.text)

finally:
    driver.quit()
