import json
import os
from datetime import datetime
import numpy as np

class SimpleMemory:
    """
    It is a simple memory
    """
    def __init__(self, memory_file_name="conversation_memeory.json"):
        self.memory_file=memory_file_name
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
            
        return {}
    
    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def store_memory(self, key, val):
        self.memory[key] = val
        self._save_memory()
        return f"Remembered: {key}"
    
    def retrieve(self, key):
        return self.memory.get(key, "I don't know about this!")
    

# memory = SimpleMemory()
# print(memory.store_memory("birhtday", "July 8, 2003"))
# print(memory.store_memory("age", "23"))
# print(memory.retrieve("age"))
# print(memory.retrieve("wo"))

class SearchableMemory:
    """
    It is the memory which can be searched.
    """
    def __init__(self, memory_file_name="conversation_memory.json"):
        self.memory_file = memory_file_name
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
            
        return []
    
    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)
    
    def add_fact(self, fact, category=None):
        entry = {
            "fact": fact,
            "category":category,
            "timestamp":str(datetime.now())
        }
        self.memory.append(entry)
        self._save_memory()
        return f"Stored: {fact} in memory"
    
    def search(self, query:str):
        result = []
        query = query.lower()

        for entry in self.memory:
            if query in entry["fact"]:
                if entry["fact"] in result:
                    continue
                result.append(entry["fact"])

            elif entry["category"] and query in entry["category"]:
                if entry["category"] in result:
                    continue
                result.append(entry["category"])

        return result if result else "I don't have any info"
    

# search_memory = SearchableMemory()
# print(search_memory.add_fact("I have a great car", "personality"))
# print(search_memory.add_fact("I have a birthday on 8th July", "birthday"))
# print(search_memory.add_fact("I have a pet", "pet"))
# print(search_memory.search("birthday"))
from sentence_transformers import SentenceTransformer

class VectorMemory:
    def __init__(self):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.facts = []
        self.vectors = []

    def add_facts(self, facts: str):
        vector = self.encoder.encode(facts)
        self.facts.append(facts)
        self.vectors.append(self.vectors)

        return f"Stored: {facts}"
    
    def search(self, query, top_k=2):
        if not self.facts:
            return ["No information in facts"]
        
        query_vector = self.encoder.encode(query)

        similarities = []

        for i, fact_vector in enumerate(self.vectors):
            similarity = np.dot(query_vector, fact_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(fact_vector))
            similarities.append(similarity)

        similarity.sort(reverse=True, key=lambda x: x[0])

        return [fact for score, fact in similarities[:top_k] if score > 0.5]
    
# mem = VectorMemory()
# mem.add_facts("I have birthday on 8th july.")
# mem.add_facts("I live in delhi")
# mem.add_facts("India is my birthplace.")
# mem.search("When was I born?")

class AssistantWithMemory:
    def __init__(self) -> None:
        self.llm = llm 
        self.memory = VectorMemory()
        self.conversation_history = []

    def _is_memory_request(self, user_message: str):
        words = [
            "request",
            "please",
            "find",
            "search",
            "remember",
            "save"
        ]

        for word in words:
            if word in user_message:
                return True
        
        return False
    
    def _store_in_memory(self, user_message: str):
        self.memory.add_facts(user_message)

    def _build_context(self, info) -> str:
        if len(info) == 0:
            return "You are a helpful assistant"
        
        facts = "\n".join(f"{fact}" for fact in info)

        return f"""
        you are a helful assistant. you know this about the user
        {facts}
        """



    def chat(self, user_message: str) -> str:
        if self._is_memory_request(user_message):
            return self._store_in_memory(user_message)
        

        relevant_info = self.memory.search(user_message, top_k=2)

        context = self._build_context(relevant_info)

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        result = self.llm.invoke(self.conversation_history)
    
        self.conversation_history.append({
            "role": "assistant",
            "content": result.content
        })

        return result.content



        




