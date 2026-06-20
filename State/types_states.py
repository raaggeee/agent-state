"""
There are three types of states which are used by an agent:
1. Ephemeral State
It is the working memory. It keeps the information about the recent task. 
It looks into intermediate result for tools, current step in multi step, temporary data.
It is created when a task is created and cleaned when a task is completed.

2. Session State:
It is the conversation context for current session.
It comprises of recent conversation history, current topic and references.
It is created when a conversation is created or user starts interacting. It is cleared when a conversation ends.

3. Persistent State:
It is the long term memory. It comprises of user facts, things to remember.
It is created when a conversation starts and exists indefinetly. 
"""

#Implementing
import os
from Memory.llm import llm
import datetime 
import json

class AgentState:
    def __init__(self, user_id) -> None:
        self.llm = llm
        self.user_id = user_id

        self.ephimeral_state = {}
        self.session_state = {
            "conversation_history": [],
            "start_session": datetime.datetime.now(),
            "current_goal": None
        }
        self.persistent_state = self._load_persistent_state()

    def _load_persistent_state(self):
        try:
            with open(f"user_{self.user_id}_state.json", "r") as f:
                return json.load(f)
            
        except FileNotFoundError:
            return {
                "preferences": {},
                "facts": {},
                "history": []
            }

    def _save_persistent_state(self):
        with open(f"user_{self.user_id}_state.json", "w") as f:
            json.dump(self.persistent_state, f, indent=2)

    def start_task(self, task_desc: str):
        self.ephimeral_state = {
            "task_description": task_desc,
            "steps": [],
            "results": [],
            "tool_used": []
        }

    def complete_task(self):
        if self.ephimeral_state:
            summary = {
                "summary": self.ephimeral_state["task_description"],
                "time": f"Completed at: {datetime.datetime.now()}"
            }
            self.persistent_state["history"] = summary
            self._save_persistent_state()

        
        self.ephimeral_state = {}

    def end_session(self):
        if self.session_state["conversation_history"]:
            summary = {
                "date": datetime.datetime.now(),
                "message_count": len(self.session_state["conversation_history"]),
                "topics": self.session_state["current_goal"]
            }

            self.persistent_state["history"] = summary
            self._save_persistent_state()

        self.session_state = {
            "conversation_history": {},
            "start_session": datetime.datetime.now(),
            "current_goal": None
        }

    def _build_context(self):
        context = []

        if self.persistent_state["preferences"] or self.persistent_state["facts"]:
            system_info = "What I know about you:\n"

            for key, val in self.persistent_state["preferences"].items():
                system_info += f"- {key}: {val}\n"

            for key, val in self.persistent_state["facts"].items():
                system_info += f"- {key}: {val}"

            context.append({
                "role": "user",
                "content": system_info
            })

            context.append({
                "role": "assistant",
                "content": "Okay, I will remember that!"
            })

        recent_history = self.session_state["conversation_history"][-10:]
        context.extend([
            {"role": msg["role"], "content":msg["content"]}
            for msg in recent_history
        ])

        return context
    
    def _check_persistent_state(self, user_input):
        if "prefer" in user_input.lower() or "remember" in user_input.lower():
            self.persistent_state["preferences"][datetime.datetime.now().isoformat()] = user_input
            self._save_persistent_state()

    def run(self, user_input: str):
        self.session_state["conversation_history"].append({
            "role": "user",
            "content": user_input,
            "time": datetime.datetime.now().isoformat()
        })

        context = self._build_context()

        response = llm.invoke(context)
        # print(response)

        self.session_state["conversation_history"].append({
            "role": "assistant",
            "content": response.content,
            "time": datetime.datetime.now().isoformat()
        })

        self._check_persistent_state(user_input)

        return response.content
    

# agent = AgentState(user_id="123")
# print(agent.run("hey"))
# print(agent.run("What are good flight for China?"))