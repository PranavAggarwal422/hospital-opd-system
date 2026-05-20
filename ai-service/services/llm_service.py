from google import genai
from google.genai import types
from fastapi import HTTPException

from core.config import GEMINI_API_KEY, MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS
from core.prompts import SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT
from core.session_manager import chat_sessions, planner_sessions

from models.schemas import ExecutionPlan

import uuid

client = genai.Client(api_key=GEMINI_API_KEY)

def create_chat_session():
    try:
        session_id = str(uuid.uuid4())

        # USER RESPONSE CHAT
        response_chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS
            )
        )

        # PLANNER CHAT
        planner_chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=PLANNER_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=ExecutionPlan,
                temperature=0
            )
        )

        chat_sessions[session_id] = response_chat
        planner_sessions[session_id] = planner_chat
        return session_id

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unable to create chat session")


def get_response_chat(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Invalid or expired session")
    
    return chat_sessions[session_id]


def get_planner_chat(session_id: str):
    if session_id not in planner_sessions:
        raise HTTPException(status_code=404, detail="Invalid or expired session")
    
    return planner_sessions[session_id]


def send_message(session_id, prompt):
    try:
        chat = get_response_chat(session_id)
        response = chat.send_message(prompt)
        return response.text 
    
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="AI service temporarily unavailable")


def delete_chat_session(session_id):
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    if session_id in planner_sessions:
        del planner_sessions[session_id]

