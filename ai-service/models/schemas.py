from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    session_id: str
    prompt: str = Field(min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    response: str

class SessionResponse(BaseModel):
    session_id: str
