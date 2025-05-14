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
import argparse
from datetime import datetime
import pathlib

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def load_interaction_patterns():
    pattern_file = pathlib.Path("interaction_patterns.json")
    if pattern_file.exists():
        with open(pattern_file, "r") as f:
            return json.load(f)
    return {}


def save_interaction_patterns(patterns):
    with open("interaction_patterns.json", "w") as f:
        json.dump(patterns, f, indent=2)


def update_interaction_pattern(domain, key, value):
    patterns = load_interaction_patterns()
    if domain not in patterns:
        patterns[domain] = {
            "input_field": None,
            "submit_action": "ENTER",
            "result_elements": {"voyage_number": None, "arrival_date": None},
            "last_updated": None,
        }

    if "." in key:
        parent_key, child_key = key.split(".", 1)
        if parent_key not in patterns[domain]:
            patterns[domain][parent_key] = {}
        patterns[domain][parent_key][child_key] = value
    else:
        patterns[domain][key] = value

    patterns[domain]["last_updated"] = datetime.now().isoformat()
    save_interaction_patterns(patterns)


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
    print(f"Searching for booking ID: {container_number}")
    driver.get("http://seacargotracking.net")
    domain = "seacargotracking.net"
    time.sleep(2)

    patterns = load_interaction_patterns()
    domain_patterns = patterns.get(domain, {})

    stored_xpath = domain_patterns.get("input_field")

    if stored_xpath:
        print("Using stored interaction pattern for input field")
        try:
            input_field = driver.find_element(By.XPATH, stored_xpath)
            input_field.send_keys(container_number)
            input_field.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"Error using stored pattern: {e}")
            stored_xpath = None

    if not stored_xpath:
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

        update_interaction_pattern(domain, "input_field", xpath)

        input_field = driver.find_element(By.XPATH, xpath)
        input_field.send_keys(value)
        input_field.send_keys(Keys.RETURN)

    time.sleep(5)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(5)

    print("Current URL:", driver.current_url)

    output_html = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")

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

    try:
        result_json_str = re.search(r"\{.*?\}", info_response.text, re.DOTALL)
        if result_json_str:
            result_data = json.loads(result_json_str.group(0))

            if result_data.get("voyage_number"):
                update_interaction_pattern(
                    domain,
                    "result_elements.voyage_number",
                    result_data["voyage_number"],
                )
            if result_data.get("arrival_date"):
                update_interaction_pattern(
                    domain, "result_elements.arrival_date", result_data["arrival_date"]
                )

            result_data["booking_id"] = container_number
            result_data["timestamp"] = datetime.now().isoformat()

            history_file = pathlib.Path("search_history.json")
            history = []
            if history_file.exists():
                with open(history_file, "r") as f:
                    try:
                        history = json.load(f)
                    except json.JSONDecodeError:
                        history = []

            is_duplicate = any(
                entry.get("booking_id") == result_data["booking_id"]
                and (
                    entry.get("voyage_number") == result_data.get("voyage_number")
                    or entry.get("arrival_date") == result_data.get("arrival_date")
                )
                for entry in history
            )

            if not is_duplicate:
                history.append(result_data)
                with open(history_file, "w") as f:
                    json.dump(history, f, indent=2)
                print(f"Results saved to {history_file}")
            else:
                print("Duplicate entry detected. Skipping save.")

            print("Extracted Info:")
            print(json.dumps(result_data, indent=2))

            if result_data.get("voyage_number") is None:
                print("WARNING: Voyage Number could not be found")
            if result_data.get("arrival_date") is None:
                print("WARNING: Arrival Date could not be found")

            print(f"Results saved to {history_file}")
        else:
            print("Failed to extract JSON data from the response")
            print("Raw response:", info_response.text)
    except Exception as e:
        print(f"Error processing results: {e}")
        print("Raw response:", info_response.text)

finally:
    driver.quit()
