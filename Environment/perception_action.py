def percieve_user_input(user_input: str):
    return {
        "type": "user_message",
        "content": user_input,
    }

def percieve_tool_output(tool_name: str, tool_result: str):
    return {
        "type": "tool",
        "tool": tool_name,
        "content": tool_result
    }

def action_generate_response(agent_message: str):
    return {
        "type": "user_message",
        "content": agent_message
    }

def action_call_tool(tool_name: str, tool_params: str):
    print(f"Calling tool: {tool_name} with params: {tool_params}")

    if tool_name == "weather_api":
        return {"temperature": "45", "scale": "C"}

    return None

user_query = percieve_user_input("What is the weather?")

weather_result = action_call_tool("weather_api", "san fransisco")

result = percieve_tool_output("weather_api", weather_result)

response = action_generate_response(f" The temperature is {weather_result["temperature"]}C.")

print(response)
