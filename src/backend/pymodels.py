from pydantic import BaseModel
from typing import List

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    is_ready: bool
    input_files: List[str]

class ChatResponse(BaseModel):
    id: int
    question: str
    answer: str
    project_id: int

class SimpleResponse(BaseModel):
    msg: str