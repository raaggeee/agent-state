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

model = "qwen3.5:4b"

class AgentWithPerception:
    def __init__(self):
        self.conversation_history = [{"role": "system", "content": """
           You are a helpful AI assistant that responds ONLY in JSON matching the schema below. Never include explanation, markdown, or text outside the JSON object.

## Schema

Every response is exactly one JSON object with this shape:

For a tool call:
{
  "response": {
    "action": "tool",
    "tool_name": "<calculator_add | memory>",
    "tool_params": { "...": "..." }
  }
}

For a final answer:
{
  "response": {
    "action": "generate",
    "result": "<your answer as a string>"
  }
}

There are no other valid values for "action". Every field shown above is REQUIRED — never omit tool_name or tool_params when action is "tool", and never omit result when action is "generate".

## Tools

calculator_add
- Use only for arithmetic addition.
- tool_params MUST contain exactly: {"a": "<number>", "b": "<number>"}
- Do not add, rename, or remove keys.

memory
- Use only when the user explicitly asks you to remember something, or states a persistent personal fact worth storing (e.g. name, preference, ongoing project detail).
- tool_params MUST contain exactly: {"key": "<short identifier>", "value": "<the information to store>"}
- Do not add extra keys like "action" inside tool_params.
- Do NOT use memory for facts that are not about the user, or for one-off questions.

If no tool fits, use "generate" and answer directly from your own knowledge.

## Critical rules

1. Output exactly one JSON object. No prose, no markdown fences, no commentary before or after.
2. Never call a tool with empty, missing, or placeholder values in tool_params. If you don't have enough information to fill every required param, ask the user for it using action "generate" instead of guessing.
3. Never invent tool_params keys that aren't listed for that tool.
4. If a previous message in this conversation shows a tool result, use that result to produce a "generate" response — do not call the same tool again with the same inputs.
5. Only one tool call per response. If multiple steps are needed, return one tool call now; you'll be asked again after seeing its result.

## Examples

User: What is 2 + 5?
{"response": {"action": "tool", "tool_name": "calculator_add", "tool_params": {"a": "2", "b": "5"}}}

(Tool result returned: "7")
{"response": {"action": "generate", "result": "2 + 5 is 7."}}

User: Remember my favorite color is blue.
{"response": {"action": "tool", "tool_name": "memory", "tool_params": {"key": "favorite_color", "value": "blue"}}}

(Tool result returned: "saved")
{"response": {"action": "generate", "result": "Got it, I'll remember your favorite color is blue."}}

User: Who wrote Hamlet?
{"response": {"action": "generate", "result": "William Shakespeare wrote Hamlet."}}

User: Add five and ten please
{"response": {"action": "tool", "tool_name": "calculator_add", "tool_params": {"a": "5", "b": "10"}}}

User: Remember something for me.
{"response": {"action": "generate", "result": "Sure — what would you like me to remember?"}}
"""}]
        self.tools = {
            "calculator_add": self._calculator_add,
            "memory": self._memory
        }

        self.memory: Dict[str, str] = {}

    def _calculator_add(self, a:int, b:int):
        return int(a) + int(b)
    
    def _memory(self, action: str, key: str="", value: str=""):
        if len(value) <= 0:
            self.memory[key] = value
            return "Saved to memory"
        
        return {"value": self.memory.get(key, "not found")}

    def call_tool(self, tool_name: str, tool_params):
        if tool_name == "calculator_add":
            try:
                result = self._calculator_add(tool_params["a"], tool_params["b"])
                return result
            except:
                return "No params found"

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
                            "content": f"Tool {tool_name} returned {result}",
                })
                continue

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









