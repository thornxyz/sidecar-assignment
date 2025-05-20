from seleniumbase import SB
import os
from dotenv import load_dotenv
from google import genai
from bs4 import BeautifulSoup
import json
import re

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

gemini_client = genai.Client(api_key=gemini_api_key)


def identify_input_field(page_html):
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


def execute_form_interaction(sb, selector_info, value):
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


with SB(uc=True) as sb:
    bl_number = "SINI25432400"

    sb.open("https://www.hmm21.com/e-service/general/trackNTrace/TrackNTrace.do")

    sb.sleep(2)
    initial_page_html = sb.get_page_source()

    selector_info = identify_input_field(initial_page_html)
    print(f"Identified selector: {selector_info}\n")

    execute_form_interaction(sb, selector_info, bl_number)

    sb.sleep(5)

    page_html = sb.get_page_source()

    cleaned_text, analysis_result = clean_and_analyze(page_html)

    print("RESULTS:")
    print(analysis_result)

    print("Search completed")
