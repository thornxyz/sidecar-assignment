import json


class JSONActionRunner:
    def __init__(self, sb_instance):
        self.sb = sb_instance
        self.driver = sb_instance.driver

    def run_actions_from_json(self, json_file="selenium_actions.json"):
        # Load actions and final_result from JSON
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            actions = data.get("actions", [])
            final_result = data.get("final_result", {})

        for action in actions:
            self.execute_action(action)
            self.sb.sleep(1)  # Optional: pause between actions

        print("✅ Automation completed successfully!")
        print(f"📊 Final result: {final_result}")

    def execute_action(self, action):
        action_type = action.get("action_type")
        if action_type == "navigate":
            self.sb.open(action.get("url"))
            self.sb.sleep(2)
        elif action_type == "scroll":
            amount = action.get("amount", 1000)
            self.sb.execute_script(f"window.scrollBy(0, {amount})")
            self.sb.sleep(1)
        elif action_type == "click":
            self.click_element(action)
        elif action_type == "input":
            self.input_text(action)
        elif action_type == "switch_tab":
            self.switch_to_tab(action.get("page_id", 1))
        elif action_type == "close_popup":
            self.close_popup(action)
        else:
            print(f"Unknown action type: {action_type}")

    def click_element(self, action):
        element_info = action.get("element_info", {})
        selector = self.get_best_selector(element_info)
        if selector:
            self.sb.click(selector)
        else:
            print(f"Could not find selector for click: {element_info}")

    def input_text(self, action):
        element_info = action.get("element_info", {})
        text = action.get("text", "")
        selector = self.get_best_selector(element_info)
        if selector:
            self.sb.type(selector, text)
        else:
            print(f"Could not find selector for input: {element_info}")

    def switch_to_tab(self, tab_index):
        handles = self.driver.window_handles
        if len(handles) > tab_index:
            self.sb.switch_to_window(tab_index)
        else:
            print(f"Tab {tab_index} does not exist")

    def close_popup(self, action):
        element_info = action.get("element_info", {})
        selector = self.get_best_selector(element_info)
        if selector:
            self.sb.click(selector)
        else:
            # Try pressing Escape as fallback
            self.driver.find_element("tag name", "body").send_keys(
                "\ue00c"
            )  # Keys.ESCAPE

    def get_best_selector(self, element_info):
        # Prefer CSS selector, then XPath, then ID, then class
        if element_info.get("css_selector"):
            return element_info["css_selector"]
        elif element_info.get("xpath"):
            return element_info["xpath"]
        elif element_info.get("attributes", {}).get("id"):
            return f'#{element_info["attributes"]["id"]}'
        elif element_info.get("attributes", {}).get("class"):
            return f'.{element_info["attributes"]["class"].replace(" ", ".")}'
        return None


if __name__ == "__main__":
    from seleniumbase import SB

    # Run as a script with SeleniumBase context manager
    with SB(uc=True, test=True) as sb:
        runner = JSONActionRunner(sb)
        runner.run_actions_from_json("selenium_actions.json")
