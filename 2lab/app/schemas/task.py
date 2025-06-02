from typing import Optional
from pydantic import BaseModel

class TaskCreate(BaseModel):
    url: str
    max_depth: int
    format: str = "graphml"

class TaskOut(BaseModel):
    id: int
    url: str
    max_depth: int
    status: str

    class Config:
        orm_mode = True

class TaskStatus(BaseModel):
    status: str
    progress: int
    result: Optional[str] = None  # GraphML xml как строка, допускает None

    class Config:
        orm_mode = True
