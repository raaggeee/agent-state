import os
from Memory.llm import llm
import re

class AgentState:
    def __init__(self) -> None:
        self.conversation_history = []

    def needs_calculation(self, text):
        # Simple heuristic: look for math expressions
        return bool(re.search(r'\d+\s*[\+\-\*\/]\s*\d+', text))
    
    def calculate(self, expression):
        # Extract and evaluate the math expression
        match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', expression)
        if match:
            a, op, b = match.groups()
            a, b = int(a), int(b)
            if op == '+': return a + b
            elif op == '-': return a - b
            elif op == '*': return a * b
            elif op == '/': return a / b if b != 0 else "Error: division by zero"
        return None

    def run(self, user_input: str) -> str:

        self.conversation_history.append(
            {"role": "user", "content": user_input}
        )

        if self.needs_calculation(user_input):
            result = self.calculate(user_input)
            response_text = f"Answer is {result}"   

        else:
            result = llm.invoke(self.conversation_history)
            response_text = result.content

        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })

        return response_text
    
class AgentState:
    def __init__(self):
        self.llm = llm
        self.state = {
            "conversation_history": [],
            "tool_used": [],
            "current_goal": None,
            "memory": []
        }

    def update_state(self, key: str, value: str):
        self.state[key] = value

    def add_to_history(self, role, content):
        self.state["conversation_history"].append(
            {
                "role": role,
                "content": content
            }
        )

    def calculate(self, expression):
        # Extract and evaluate the math expression
        match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', expression)
        if match:
            a, op, b = match.groups()
            a, b = int(a), int(b)
            if op == '+': return a + b
            elif op == '-': return a - b
            elif op == '*': return a * b
            elif op == '/': return a / b if b != 0 else "Error: division by zero"
        return None

    def decide_action(self, user_input: str):
        if "calculate" in user_input.lower() or any(op in user_input for op in ['+', '-', '*', '/']):
            return "use_calculator"
        
        elif "remember" in user_input.lower():
            return "store_memory"
        
        else:
            return "generate_answer"

    def use_calculator(self, user_input: str):
        self.state["tool_used"] =  "calculator"
        return f"Calculator Result: {self.calculate(user_input)}"

    def store_memory(self, user_input: str):
        self.state["tool_used"] = "memory"
        self.state["memory"] = user_input
        return f"Stored in memory"

    def generate_answer(self, user_input: str):
        result = llm.invoke(self.state["conversation_history"])
        response_text = result.content
        return response_text

    def execute_action(self, action: str, user_input: str):
        if action == "use_calculator":
            return self.use_calculator(user_input)
        
        elif action == "store_memory":
            return self.store_memory(user_input)
        
        else:
            return self.generate_answer(user_input)
        
    def run(self, user_input):
        self.add_to_history("user", user_input)

        action = self.decide_action(user_input)
        result = self.execute_action(action, user_input)
        self.add_to_history("assistant", result)

        return result
    
from pydantic import BaseModel
from typing import Optional
class Answer(BaseModel):
    action: str
    response: Optional[str] = None

description = """
You are an AI Assistant with access to a set of tools/actions.

Follow these rules strictly:
- If the action is `generate_result`: respond directly to the user with a clear, helpful answer.
- For any other action: select the appropriate tool silently — do NOT generate a user-facing response. Just use None in response
- Don't calculate anything
Always determine the correct action before deciding whether to respond or invoke a tool.

Actions/Tools:
-use_calculator: Use calculator.
-store_memory
-generate_result
"""
class AgentState:
    def __init__(self) -> None:
        self.llm = llm.with_structured_output(Answer)
        self.state = {
            "conversation": [{
                "role": "system",
                "content": description
            }],
            "memory": [],
            "tool_used": []

        }
        self.tools = []

    def calculate(self, expression):
        # Extract and evaluate the math expression
        match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', expression)
        if match:
            a, op, b = match.groups()
            a, b = int(a), int(b)
            if op == '+': return a + b
            elif op == '-': return a - b
            elif op == '*': return a * b
            elif op == '/': return a / b if b != 0 else "Error: division by zero"
        return None
    
    def add_to_history(self, role, content):
        self.state["conversation"].append({
            "role": role,
            "content": content
        })

    def use_calculator(self, user_input: str):
        self.state["tool_used"] =  "calculator"
        return f"Calculator Result: {self.calculate(user_input)}. Now you can respond to user."

    def store_memory(self, user_input: str):
        self.state["tool_used"] = "memory"
        self.state["memory"] = user_input
        return f"Stored in memory. Now you can respond to user."

    def execute_action(self, action: str, user_input: str):
        if action == "use_calculator":
            return self.use_calculator(user_input)
        
        elif action == "store_memory":
            return self.store_memory(user_input)
        
        else:
            return


    def run(self, user_input: str):
        self.add_to_history("user", user_input)
        
        while True:
            result = self.llm.invoke(self.state["conversation"])
            print(f"\n{result}")

            response = self.execute_action(result.action, user_input)

            if result.action == "generate_result":
                self.add_to_history("user", result.response)
                break
            else:
                self.add_to_history("system", response)


        return result.response

        

agent = AgentState()
print(agent.run("I am Raaggee Singh. remember it."))
print(agent.run("What is my name?"))
print(agent.run("What is 36+98?"))
print(agent.run("What did we discuss?"))
