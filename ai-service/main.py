from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ChatRequest, ChatResponse, SessionResponse
from services.llm_service import create_chat_session, send_message, delete_chat_session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start-chat", response_model=SessionResponse)
def start_chat():
    session_id = create_chat_session()
    return SessionResponse(session_id=session_id)

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    response_text = send_message(request.session_id, request.prompt)
    return ChatResponse(response=response_text)


@app.delete("/end-chat/{session_id}")
def end_chat(session_id: str):
    delete_chat_session(session_id)
    return {
        "message": "Chat Session Deleted"
    }
