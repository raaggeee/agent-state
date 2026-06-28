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
        self.conversation_history = [{"role": "system", "content": "You are a helpful assistant with two tools: calculator_add (takes two parameters), memory (adds user info to memory. With key and value pair.). When not using any tool use action as generate. When using a tool use action as tool"}]
        self.tools = {
            "calculator_add": self._calculator_add,
            "memory": self._memory
        }

        self.memory: Dict[str, str] = {}

    def _calculator_add(self, a:int, b:int):
        return a + b
    
    def _memory(self, action: str, key: str="", value: str="s"):
        if action == "save":
            self.memory[key] = value
            return "Saved to memory"
        
        else:
            return {"value": self.memory.get(key, "not found")}

    def percieve_and_act(self, user_input:str):

        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        while True:
            result = ollama.chat(model=model, messages=self.conversation_history, format=Response.model_json_schema())

            print(result["message"]["content"])

            action = result["message"]["content"]

            self.conversation_history.append({
                        "role": "assistant",
                        "content": result["message"]["content"]["response"]["result"]
            })

            if result["message"]["content"]["response"]["action"] == "generate":
                print(result["message"]["content"]["response"]["result"])
                break


agent = AgentWithPerception()
agent.percieve_and_act("hey")







