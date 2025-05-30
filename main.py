from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
from convert_agent_result import convert_result_to_json

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

task = """
OBJECTIVE: Extract cargo tracking information for B/L number SINI25432400 from HMM shipping website.

STEP-BY-STEP INSTRUCTIONS:
1. Navigate to http://seacargotracking.net
2. Locate and click the "HMM" or "Hyundai Merchant Marine" link/button
3. Once on the HMM website, find and click "e-Services" or similar navigation
4. IMPORTANT: Immediately close any popups, modal dialogs, or overlay windows that appear
5. Look for cargo tracking section - typically labeled "Track & Trace", "Cargo Tracking", or "B/L Tracking"
6. Enter the B/L number: SINI25432400
7. Click "Search", "Retrieve", "Track", or similar submit button
8. Wait for results to load completely
9. Extract ONLY these two pieces of information:
    - Voyage number (may include vessel name + voyage code)
    - ETA/Arrival date at destination port

OUTPUT FORMAT: Return results as clean JSON:
{
  "voyage_number": "[exact voyage number found]",
  "eta": "[exact ETA date and time found]"
}

IMPORTANT NOTES:
- If any popups appear at ANY step, close them immediately
- If information is not found, use "Information not found" as the value
- Do not include any explanations, additional text, or formatting outside the JSON
- Ensure dates are in the format shown on the website
- Include full voyage information (vessel name + voyage number if shown together)
"""


async def main():
    agent = Agent(task=task, llm=llm)
    result = await agent.run()

    print(result)

    # Save result to text file
    with open("agent_result.txt", "w", encoding="utf-8") as f:
        f.write(str(result))

    print("✅ Result saved to agent_result.txt")

    # Convert the result to JSON format using Gemini
    print("🔄 Converting result to Selenium-compatible JSON...")
    json_result = convert_result_to_json()

    if json_result:
        print("✅ Conversion completed successfully!")
    else:
        print("❌ Conversion failed")


asyncio.run(main())
