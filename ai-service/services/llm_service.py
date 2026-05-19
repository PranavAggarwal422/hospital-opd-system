from google import genai
from google.genai import types
from fastapi import HTTPException

from core.config import GEMINI_API_KEY, MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS
from core.prompts import SYSTEM_PROMPT
from core.session_manager import chat_sessions

import uuid

client = genai.Client(api_key=GEMINI_API_KEY)


def create_chat_session():
    session_id = str(uuid.uuid4())
    chat = client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS
        )
    )
    chat_sessions[session_id] = chat
    return session_id


def send_message(session_id, prompt):
    if session_id not in chat_sessions:
        raise HTTPException(
            status_code=404,
            detail="Invalid or expired session"
        )

    try:
        chat = chat_sessions[session_id]
        response = chat.send_message(prompt)
        return response.text

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="AI service temporarily unavailable"
        )


def delete_chat_session(session_id):
    if session_id in chat_sessions:
        del chat_sessions[session_id]

