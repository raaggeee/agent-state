class AgentEnvironment:
    def __init__(self):
        self.available_tool = {
            "weather": self.get_weather,
            "calender": self.get_calender,
            "personal_tasks": self.personal_tasks
        }
        self.conversation_history = []

    def get_weather(self, location: str):
        return {"date": "26-06-26", "location": location, "Temperature": "26"}
    

    def get_calender(self, date: str = ""):
        return {"Time": "9:00AM", "Assignment":"Need to go for groceries"}


    def personal_tasks(self):
        return {"Task 1": "Grocery Shopping", "Task 2": "Homework", "Task 3": "Movie"}

    def percieve(self, user_input: str):
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

    def act(self, action: str, **params):
        if action in self.available_tool:
            result = self.available_tool[action](**params)
            return result
        else:
            return {"error": "tool not found"}

# env = AgentEnvironment()
# env.percieve("What I should do?")
# res = env.act("personal_tasks")
# print(res)


#Agent with Boundary
class BoundedEnvironment:
    def __init__(self, allowed_folders=None, requires_confirm=None):
        self.allowed_folders = allowed_folders or ["/backup-disk/agent-state/temp"]
        self.required_confirmation = requires_confirm or ["send_email", "send_message"]
        self.permission_required = []

    def can_access_folder(self, file_path: str):
        return any(file_path.startswith(folder)
                   for folder in self.allowed_folders)
    
    def request_action(self, action_name: str, **params):
        if action_name in self.required_confirmation:
            self.permission_required.append(
                {
                    "action": action_name,
                    "params":params,
                    "status": "pending"
                }
            )

            return "Action queued for confirmation"
        
        else:
            return self.execute_action(action_name)
        
    def execute_action(self, action_name: str):
        return f"Execute: {action_name}"
    

env = BoundedEnvironment()
res = env.request_action("send_email", to="raaggee@gmail.com")
print(res)




            



