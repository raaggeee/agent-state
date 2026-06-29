class AgentCycle:
    def __init__(self):
        self.state = {
            "conversation_history": [],
            "current_goal": None
            
        }

    def percieve(self, user_input:str):
        self.state["conversation_history"].append({
            "role": "user",
            "content": user_input
        })

        return user_input

    def decide(self, perception: str):
        #usually an LLM Call
        if "weather" in perception.lower():
            return {"action": "tool_call", "tool": "weather"}
        else:
            return {"action": "respond", "message": "Okay!"}
    
    def act(self, decide):
        if decide["action"] == "tool_call":
            return {"temperature": 45, "scale": "F"}

        else:
            return decide["message"]


    def run_cycle(self, user_input: str):
        perception = self.percieve(user_input)

        decision = self.decide(perception)

        action = self.act(decision)

        return action


# cycle = AgentCycle()
# res = cycle.run_cycle("What is the weather?")
# print(res)
# res = cycle.run_cycle("Thanks")
# print(res)

import ollama
from pydantic import BaseModel
from typing import Dict
import json

class ToolCall(BaseModel):
    action: str
    tool_name: str
    tool_params: Dict[str, str]

class Result(BaseModel):
    action: str
    result: str


class Response(BaseModel):
    response: ToolCall | Result
    # content: str

model = "gemma3:1b"

class AgentWithPerception:
    def __init__(self):
        self.conversation_history = [{"role": "system", "content": """
           You are a helpful AI assistant.

You have two tools:

* **calculator_add(a, b)**: Adds two numbers.
* **memory(key, value)**: Stores user information.

Your output **must always** match this schema:

```python
class ToolCall:
    action: str
    tool_name: str
    tool_params: Dict[str, str]

class Result:
    action: str
    result: str

class Response:
    response: ToolCall | Result
```

## Rules

1. Always return **exactly one** `response` object.
2. Never return plain text outside the schema.
3. Choose **one** of the following:

### If a tool is needed

Return:

```json
{
  "response": {
    "action": "tool",
    "tool_name": "<tool name>",
    "tool_params": {
      "...": "..."
    }
  }
}
```

Use only these tool names:

* `calculator_add`
* `memory`

Do not answer the user's question yourself if a tool is required.

### If no tool is needed

Return:

```json
{
  "response": {
    "action": "generate",
    "result": "<answer>"
  }
}
```

## Tool Selection

Use `calculator_add` only for arithmetic.

Use `memory` only when the user explicitly asks you to remember something or provides persistent personal information worth storing.

Otherwise use `generate`.

## Examples

User: What is 2 + 5?

```json
{
  "response": {
    "action": "tool",
    "tool_name": "calculator_add",
    "tool_params": {
      "a": "2",
      "b": "5"
    }
  }
}
```

User: Remember my favorite color is blue.

```json
{
  "response": {
    "action": "tool",
    "tool_name": "memory",
    "tool_params": {
    "action": "save",
      "key": "favorite_color",
      "value": "blue"
    }
  }
}
```

User: Who wrote Hamlet?

```json
{
  "response": {
    "action": "generate",
    "result": "William Shakespeare wrote Hamlet."
  }
}
```


"""}]
        self.tools = {
            "calculator_add": self._calculator_add,
            "memory": self._memory
        }

        self.memory: Dict[str, str] = {}

    def _calculator_add(self, a:int, b:int):
        return a + b
    
    def _memory(self, action: str, key: str="", value: str=""):
        if len(value) <= 0:
            self.memory[key] = value
            return "Saved to memory"
        
        return {"value": self.memory.get(key, "not found")}

    def call_tool(self, tool_name: str, tool_params):
        if tool_name == "calculator_add":
            result = self._calculator_add(tool_params["a"], tool_params["b"])

        if tool_name == "_memory":
            result = self._memory(tool_params["action"], tool_params["key"], tool_params["value"])

        return result

    def percieve_and_act(self, user_input:str):

        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        while True:
            result = ollama.chat(model=model, messages=self.conversation_history, format=Response.model_json_schema())

            res = json.loads(result["message"]["content"])
            print(res)

            action = res["response"]["action"]

            if action == "tool":
                tool_name = res["response"]["tool_name"]
                tool_params = res["response"]["tool_params"]

                result = self.call_tool(tool_name, tool_params)
                print(result)

                self.conversation_history.append({
                            "role": "user",
                            "content": "Fetched Tool result"
                })

                self.conversation_history.append({
                            "role": "assistant",
                            "content": result
                })

            if action == "generate":
                self.conversation_history.append({
                        "role": "assistant",
                        "content": res["response"]["result"]
                })
                print(res["response"]["result"])
                break


agent = AgentWithPerception()
agent.percieve_and_act("hey")
agent.percieve_and_act("what is 10 + 20")
agent.percieve_and_act("My name is Raaggee. ")









