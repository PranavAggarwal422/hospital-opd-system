from fastapi import HTTPException
from google.genai import types 
from core.prompts import PLANNER_SYSTEM_PROMPT

from services.llm_service import get_planner_chat
from models.schemas import ExecutionPlan


def generate_execution_plan(session_id: str,prompt: str):
    try:
        planner_chat = get_planner_chat(session_id)
        response = planner_chat.send_message(
            message = prompt,
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExecutionPlan,
                temperature=0
            )
        )

        return response.parsed

    except HTTPException:
        raise

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Planner service failed")
    

