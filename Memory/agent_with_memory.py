"""
An agent with memory has two things.
1. Short Term Memory 
It is the conversational memory of an agent. What a user interacts with the agent gets stored here along with 
llm's response.

2. Long Term Memory
This is what makes an agent functional and authentic to user. With Long Term Memory, the LLM's response is more 
towards the user. 
"""
import json
import os 
from datetime import datetime
import ollama
import numpy as np

model = "deepseek-r1:1.5b"

#1. Short Term Memory
class ConversationManagement:
    def __init__(self, max_message: int = 10):
        self.conversation_history = [{"role": "system", "content": "You are a helpful assistant. Always respond in english"}]
        self.max_message = max_message

    def _trim_if_needed(self):
        if len(self.conversation_history) > self.max_message:
            self.conversation_history = self.conversation_history[-self.max_message:]

    def add_user_message(self, user_input: str):
        self.conversation_history.append({
            "role": "user",
            "message": user_input
        })

        self._trim_if_needed()

    def add_assistant_message(self, response: str):
        self.conversation_history.append({
            "role": "assistant",
            "message": response
        })

        self._trim_if_needed()

    def get_messages(self):
        return self.conversation_history.copy()
    
    def clear(self):
        self.conversation_history = []


class KnowledgeStore:
    def __init__(self, storage_file: str = "knowledge.json") -> None:
        self.storage_file = storage_file
        self.facts = self._load_facts()

    def _load_facts(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                json.load(f)

        return []
    
    def _save_facts(self):
        with open(self.storage_file, "w") as f:
            json.dump(self.facts, f, indent=2)

    def add_fact(self, fact: str, category: str):
        memory = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }

        self.facts.append(memory)
        self._save_facts()

    def search_fact(self, query: str):
        query_lower = query.lower()
        result = []
        
        for entry in self.facts:
            if query_lower in entry["fact"]:
                result.append(entry["query"])

            elif entry["category"] and query_lower in entry["category"]:
                result.append(entry["fact"])

        return result
    
    def get_all_facts(self):
        return self.facts.copy()


class SemeanticKnowledgeStore:
    def __init__(self, knowldge_store):
        self.knowlegde_store = knowldge_store
        self.facts = []
        self.embeddings = []
        self._load_facts()
        # self.encoder = ollama

    def _load_facts(self):
        if os.path.exists(self.knowlegde_store):
            with open(self.knowlegde_store, "r") as f:
                data = json.load(f)
                self.facts = data

                for entry in self.facts:
                    embeds = ollama.embed(model="embeddinggemma:latest", input=entry["fact"])
                    self.embeddings.append(embeds)

    def _save_data(self):
        with open(self.knowlegde_store, "w") as f:
            json.dump(self.facts, f, indent=2)

    def add_fact(self, fact: str, category:str):
        knowledge = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }

        embeds = ollama.embed(model="embeddinggemma:latest", input=fact)
        self.facts.append(knowledge)
        self.embeddings.append(embeds)
        self._save_data()

    def search_fact(self, query:str, top_k:int = 2, threshold:float = 0.8):
        if not self.facts:
            return []

        query_embedding = ollama.embed(model="embeddinggemma:latest", input=query)
        query_embedding = query_embedding["embeddings"][0]

        similarities = []

        for i, fact_embedding in enumerate(self.embeddings):
            # print(fact_embedding)
            similarity = np.dot(query_embedding, fact_embedding["embeddings"][0]) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(fact_embedding["embeddings"][0])
            )
            similarities.append((similarity, self.facts[i]["fact"]))

        similarities.sort(reverse=True, key=lambda x: x[0])
        results = [fact for score, fact in similarities[:top_k] if score >= threshold]
        
        return results
    

class Agent:
    def __init__(self):
        self.conversation = ConversationManagement()
        self.knowledge = SemeanticKnowledgeStore("knowledge.json")

    def chat(self, user_input: str): 
        #check if user_input is for storing in memory
        if self._is_memory(user_input):
            print("\n**Yes keep in memory**\n")
            return self._keep_in_memory(user_input)

        #get relevant facts
        relevant_facts = self.knowledge.search_fact(user_input)
        print(f"\n**Relevant Facts found: {relevant_facts}**\n")

        #build system prompt
        relevant_fact = self.build_system_prompt(relevant_facts)
        self.conversation.add_user_message(relevant_fact)
        self.conversation.add_assistant_message("Okay")


        #add user input to history
        self.conversation.add_user_message(user_input)
        print(self.conversation.get_messages())

        #get llm reponse (add LLm here)
        response = ollama.chat(model, self.conversation.get_messages(), think="medium")
        print(response["message"]["content"])

        #add response to history
        self.conversation.add_assistant_message(response["message"]["content"])
        
        return response

    def _is_memory(self, user_input: str):
        detect_keywords = ["remember", "know", "save", "store", "keep", "mind"]
        
        for word in detect_keywords:
            if word in user_input:
                return True

        return False
    
    def _keep_in_memory(self, user_input: str):
        #we generally keep 
        response = ollama.chat(model, f"check what the user has said and extract key facts which are to be remebered.\n{user_input}", think="medium")
        category = "sample"

        self.knowledge.add_fact(response, category)
        return f"Remembered in memory."

    def build_system_prompt(self, relevant_fact):
        base_prompt = ""
        if not relevant_fact:
            base_prompt += f"No pre-requisite information about the user"
            return base_prompt

        base_prompt += "What I know about user regarding this query:"
        base_prompt += "\n".join(relevant_fact)

        return base_prompt


agent = Agent()
agent.chat("hey")
agent.chat("remember about my birthday. I was born on 8th July 2003.")
print("\n")
agent.chat("Tell me my birthdate.")
