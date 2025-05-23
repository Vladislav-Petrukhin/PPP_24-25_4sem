from pydantic import BaseModel, HttpUrl

class ParseRequest(BaseModel):
    url: HttpUrl
    max_depth: int = 3
    format: str = "graphml"

class ParseResponse(BaseModel):
    task_id: str

class ParseStatusResponse(BaseModel):
    status: str
    progress: int
    result: str = None
