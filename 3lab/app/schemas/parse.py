from pydantic import BaseModel, HttpUrl, Field

class ParseRequest(BaseModel):
    url: HttpUrl
    max_depth: int = Field(ge=1, le=5, default=3)
    format: str = "graphml"

class ParseResponse(BaseModel):
    task_id: str

class ParseStatus(BaseModel):
    status: str
    progress: int
    result: str | None = None
