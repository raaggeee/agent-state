from pydantic import BaseModel
from typing import Annotated, List

class AgentOne(BaseModel):
    state_id: str
    question: str
    plan: List[str]
    direct_ans: bool
    proper_ans: bool

class AgentTwo(BaseModel):
    state_id: str
    plan: List[str]
    action: List[str]
    satisfied: bool