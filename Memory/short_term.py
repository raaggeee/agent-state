from llm import llm
from pydantic import BaseModel
from typing import Optional
from make_file import make_file, delete_file, read_file

class Result(BaseModel):
    action:str
    output: Optional[str] = None

with open("/Users/raaggee/Documents/betas/agent_state/Memory/ltm_agent_prompt.md") as f:
    system_prompt = f.read()

# print(system_prompt)

class Agent:
    def __init__(self, max_limit = 20):
        self.conversation_history = [{
            "role": "system",
            "content": system_prompt
        }]
        self.llm = llm.with_structured_output(Result)
        self.max_limit = max_limit

    def call_tool(self, tool_name, output):
        if tool_name == "make_file":
            return make_file(output)
        
        elif tool_name == "delete_file":
            return delete_file(output)
        
        elif tool_name == "read_file":
            return read_file(output)
        
    def _summarize_conversation(self, messages: list) -> str:
        conversation_text = f"""
            {msg["role"].title()} : {msg["content"]}
        """
        for msg in messages

        conversation_text = "\n".join(conversation_text)

        result = llm.invoke(f"Summarize this conversation: {conversation_text}")

        return result.content


    def run(self, user_input: str):
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        if len(self.conversation_history) > self.max_limit:
            to_summarize = self.conversation_history[:self.max_limit//2]
            keep_recent = self.conversation_history[self.max_limit//2:]

            summarize = self._summarize_conversation(to_summarize)

            self.conversation_history = [{
                "role": "user",
                "content": summarize
            }] + keep_recent

        while True:
            result = self.llm.invoke(self.conversation_history)

            if result.action == "generate_result":
                response_text = result.output
                break

            else:
                response_text = self.call_tool(result.action, result.output)

                self.conversation_history.append({
                    "role": "user",
                    "content": response_text
                })

        self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })


        return result.output
    
    def clear_conversation_history(self):
        self.conversation_history = []

    def get_conversation_history(self):
        return self.conversation_history.copy()
    

agent = Agent()
print("\n")
print(agent.run("What is the capital of india?"))
print("\n")
print(agent.run("I live there!"))
print("\n")
print(agent.run("What is the best place there?"))
print("\n")
print(agent.run("Make a file with the name of capital of india."))
