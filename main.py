from seleniumbase import SB
import os
from dotenv import load_dotenv
from google import genai
from bs4 import BeautifulSoup
import json
import re
import hashlib
import datetime
from pathlib import Path

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

gemini_client = genai.Client(api_key=gemini_api_key)

# Create cache directory if it doesn't exist
CACHE_DIR = Path("interaction_cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_cache_key(url, value):
    """Generate a unique cache key based on URL and input value."""
    key_string = f"{url}:{value}"
    return hashlib.md5(key_string.encode()).hexdigest()


def save_to_cache(url, value, interaction_data):
    """Save interaction data to cache file."""
    cache_key = get_cache_key(url, value)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    cache_data = {
        "url": url,
        "value": value,
        "interaction_data": interaction_data,
        "timestamp": datetime.datetime.now().isoformat(),
        "success_count": 1,
    }

    with open(cache_file, "w") as f:
        json.dump(cache_data, f, indent=2)

    print(f"Interaction cached with key: {cache_key}")
    return cache_key


def get_from_cache(url, value):
    """Retrieve interaction data from cache if available."""
    cache_key = get_cache_key(url, value)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)

            print(f"Cache hit for key: {cache_key}")

            cache_data["success_count"] += 1
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

            return cache_data["interaction_data"]
        except Exception as e:
            print(f"Error reading cache: {e}")

    return None


def update_cache_success(url, value, success=True):
    """Update success/failure statistics for cached interaction."""
    cache_key = get_cache_key(url, value)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)

            if success:
                cache_data["success_count"] += 1
            else:
                cache_data["failure_count"] = cache_data.get("failure_count", 0) + 1

            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Error updating cache statistics: {e}")


def identify_input_field(page_html):
    """Identify input field in the tracking page."""
    soup = BeautifulSoup(page_html, "html.parser")

    for tag in soup(["script", "style", "noscript", "meta", "link", "iframe"]):
        tag.decompose()

    for tag in soup.find_all(style=True):
        style = tag.get("style", "").lower()
        if (
            "display:none" in style
            or "visibility:hidden" in style
            or "opacity:0" in style
        ):
            tag.decompose()

    noise_keywords = ["ads", "banner", "popup", "cookie", "footer"]
    for attr in ["id", "class"]:
        for keyword in noise_keywords:
            for tag in soup.find_all(
                attrs={attr: lambda x: x and keyword in x.lower()}
            ):
                tag.decompose()

    cleaned_html = str(soup)

    prompt = f"""
    Analyze the HTML of this shipping tracking page and identify the input field where a customer would enter a tracking number.
    
    Return ONLY a JSON object with this exact structure:
    {{
        "selector_type": "one of: id, name, xpath, css",
        "selector_value": "the actual selector value",
        "submit_method": "one of: enter_key, button_click, form_submit",
        "submit_selector": "if button_click, provide the button selector"
    }}
    
    If you're uncertain about any field, make your best guess based on common patterns.
    Do not include any explanations, just the JSON object.
    
    HTML to analyze:
    {cleaned_html}
    """

    try:
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
        )
        result = response.text.strip()

        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if json_match:
            result = json_match.group(0)

        selector_info = json.loads(result)
        return selector_info
    except Exception as e:
        print(f"Error identifying input field: {e}")
        return {
            "selector_type": "xpath",
            "selector_value": "//input[@type='text']",
            "submit_method": "enter_key",
            "submit_selector": "",
        }


def clean_and_analyze(page_html):
    soup = BeautifulSoup(page_html, "html.parser")

    for tag in soup(
        [
            "script",
            "style",
            "header",
            "footer",
            "nav",
            "noscript",
            "iframe",
            "svg",
            "canvas",
            "meta",
            "link",
        ]
    ):
        tag.decompose()

    for tag in soup.find_all(style=True):
        style = tag["style"].lower()
        if (
            "display:none" in style
            or "visibility:hidden" in style
            or "opacity:0" in style
        ):
            tag.decompose()

    for attr in ["class", "id"]:
        for val in [
            "hidden",
            "hide",
            "invisible",
            "sr-only",
            "ads",
            "banner",
            "cookie",
            "popup",
            "breadcrumb",
        ]:
            for tag in soup.find_all(attrs={attr: lambda x: x and val in x.lower()}):
                tag.decompose()

    tracking_section = soup.find("div", {"id": "resultDiv"}) or soup.body

    tracking_text = tracking_section.get_text(separator="\n", strip=True)
    cleaned_text = "\n".join(
        [line.strip() for line in tracking_text.splitlines() if line.strip()]
    )

    prompt = f"""
    Analyze the following container tracking details and extract:
    1. The voyage number
    2. The date of arrival (ETA)
    3. The current status

    Only provide the answer in this format:
    Voyage Number: [number]
    Date of Arrival: [date]
    Current Status: [status]

    If any field is missing, say "Information not found".

    Tracking Details:
    {cleaned_text}
    """

    try:
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
        )
        analysis_result = response.text
    except Exception as e:
        analysis_result = f"Error analyzing the tracking page: {str(e)}"

    return cleaned_text, analysis_result


def analyze_and_repair_actions(page_html, current_actions):
    """Analyze page and repair actions if selectors have changed."""
    try:
        new_selector_info = identify_input_field(page_html)

        selectors_changed = False
        for action in current_actions:
            if action["action"] in ["wait_for_element", "type", "submit"]:
                if action["selector_type"] == "css" and (
                    new_selector_info["selector_type"] == "id"
                    and f"#{new_selector_info['selector_value']}" == action["selector"]
                    or new_selector_info["selector_type"] == "name"
                    and f"[name='{new_selector_info['selector_value']}']"
                    == action["selector"]
                ):
                    continue
                elif (
                    action["selector_type"] == "xpath"
                    and new_selector_info["selector_type"] == "xpath"
                    and new_selector_info["selector_value"] == action["selector"]
                ):
                    continue
                else:
                    selectors_changed = True
                    break

        if selectors_changed:
            prompt = f"""
            The selectors on this page have changed. Given the following new selector information:
            {json.dumps(new_selector_info, indent=2)}
            
            And the previous actions:
            {json.dumps(current_actions, indent=2)}
            
            Generate updated actions to perform the same task with the new selectors.
            Return ONLY a JSON array of actions with the same structure as the previous actions.
            """

            response = gemini_client.models.generate_content(
                model="gemini-1.5-flash", contents=prompt
            )
            result = response.text.strip()

            json_match = re.search(r"\[.*\]", result, re.DOTALL)
            if json_match:
                result = json_match.group(0)

            print("Selectors changed, generated repaired actions")
            return json.loads(result)

        return current_actions
    except Exception as e:
        print(f"Error in analyze_and_repair_actions: {e}")
        return current_actions


def execute_form_interaction(sb, selector_info, value, url=None):
    """Execute form interaction with caching support."""
    cached_actions = None
    if url:
        cached_actions = get_from_cache(url, value)

    if cached_actions:
        print("Using cached interaction pattern")
        actions = cached_actions

        try:
            for action in actions:
                if action["action"] == "wait_for_element":
                    try:
                        if action["selector_type"] == "xpath":
                            element_exists = sb.is_element_present(action["selector"])
                        else:
                            element_exists = sb.is_element_visible(action["selector"])

                        if not element_exists:
                            raise Exception("Element not found, need to repair actions")
                    except:
                        page_html = sb.get_page_source()
                        actions = analyze_and_repair_actions(page_html, actions)
                        break
        except Exception as e:
            print(f"Warning: Cached actions validation failed: {e}")
            actions = None

    if not cached_actions:
        input_selector_type = selector_info["selector_type"]
        input_selector_value = selector_info["selector_value"]
        submit_method = selector_info["submit_method"]
        submit_selector = selector_info.get("submit_selector", "")

        formatted_selector_info = {
            "input_selector_type": input_selector_type,
            "input_selector_value": input_selector_value,
            "submit_method": submit_method,
            "submit_selector": submit_selector,
        }

        prompt = f"""
        Given the following selector information for a web form:
        {json.dumps(formatted_selector_info, indent=2)}
        
        Determine the exact steps needed to:
        1. Locate the input element
        2. Enter the value: "{value}"
        3. Submit the form
        
        Return ONLY a JSON array of actions with this structure:
        [
          {{
            "action": "wait_for_element", 
            "selector_type": "xpath|css", 
            "selector": "the_selector",
            "timeout": 10
          }},
          {{
            "action": "type",
            "selector_type": "xpath|css",
            "selector": "the_selector",
            "value": "the_value"
          }},
          {{
            "action": "submit",
            "method": "enter_key|click|form_submit",
            "selector_type": "xpath|css",
            "selector": "the_selector"
          }}
        ]
        
        IMPORTANT: 
        - For name selectors, use CSS format like "[name='value']"
        - For id selectors, use CSS format like "#value"
        - For xpath selectors, use the xpath as is
        - For css selectors, use the css as is
        """

        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
        )
        result = response.text.strip()

        json_match = re.search(r"\[.*\]", result, re.DOTALL)
        if json_match:
            result = json_match.group(0)

        print(f"Generated actions from Gemini: {result}\n")

        actions = json.loads(result)

    success = True
    try:
        for action in actions:
            if action["action"] == "wait_for_element":
                if action["selector_type"] == "xpath":
                    sb.wait_for_element_present(
                        action["selector"], timeout=action.get("timeout", 10)
                    )
                else:
                    sb.wait_for_element(
                        action["selector"], timeout=action.get("timeout", 10)
                    )

            elif action["action"] == "type":
                if action["selector_type"] == "xpath":
                    sb.type_xpath(action["selector"], action.get("value", value))
                else:
                    sb.type(action["selector"], action.get("value", value))

            elif action["action"] == "submit":
                if action["method"] == "enter_key":
                    if action["selector_type"] == "xpath":
                        sb.send_keys_xpath(action["selector"], "\n")
                    else:
                        sb.send_keys(action["selector"], "\n")
                elif action["method"] == "click":
                    if action["selector_type"] == "xpath":
                        sb.click_xpath(action["selector"])
                    else:
                        sb.click(action["selector"])
                elif action["method"] == "form_submit":
                    sb.execute_script(
                        f"document.querySelector('{action['selector']}').form.submit();"
                    )
    except Exception as e:
        print(f"Error executing actions: {e}")
        success = False

    if url and success and not cached_actions:
        save_to_cache(url, value, actions)
    elif url and not success and cached_actions:
        update_cache_success(url, value, success=False)

    return success


with SB(uc=True) as sb:
    bl_number = "SINI25432400"
    url = "https://www.hmm21.com/e-service/general/trackNTrace/TrackNTrace.do"

    sb.open(url)

    sb.sleep(2)
    initial_page_html = sb.get_page_source()

    selector_info = identify_input_field(initial_page_html)
    print(f"Identified selector: {selector_info}\n")

    execute_form_interaction(
        sb,
        selector_info,
        bl_number,
        url,
    )

    sb.sleep(5)

    page_html = sb.get_page_source()

    cleaned_text, analysis_result = clean_and_analyze(page_html)

    print("RESULTS:")
    print(analysis_result)

    print("Search completed")
