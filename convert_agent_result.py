from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")


def convert_result_to_json():
    with open("agent_result.txt", "r", encoding="utf-8") as file:
        result_content = file.read()

    # Prompt for Gemini to convert the result to JSON
    prompt = f"""
    Please convert the following agent automation result into a clean, usable JSON format that can be used by a Selenium script.

    The result contains action sequences from web automation. Please structure it as follows:
    1. Extract all the actions performed (navigate, click, input, scroll, etc.)
    2. Include relevant element information (xpath, css_selector, attributes) for each action
    3. Include the final result data
    4. Make it Selenium-friendly with clear action types and parameters

    Here's the raw result data:
    {result_content}

    Please return only valid JSON without any markdown formatting or explanation.
    """  # Get response from Gemini
    response = llm.invoke(prompt)

    try:
        # Clean the response content - remove markdown formatting
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()

        # Parse the response as JSON to validate it
        json_data = json.loads(content)

        # Save to file
        with open("selenium_actions.json", "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)

        print("✅ Successfully converted result.txt to selenium_actions.json")
        print(f"📊 JSON contains {len(json_data.get('actions', []))} actions")

        return json_data

    except json.JSONDecodeError as e:
        print(f"❌ Error: Gemini response is not valid JSON: {e}")
        print("Raw response:")
        print(response.content)
        return None


if __name__ == "__main__":
    convert_result_to_json()
