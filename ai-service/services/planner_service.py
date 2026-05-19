from google import genai
from google.genai import types

from core.config import GEMINI_API_KEY
from core.prompts import PLANNER_SYSTEM_PROMPT
from models.schemas import ExecutionPlan

client = genai.Client(api_key=GEMINI_API_KEY)
def generate_execution_plan(prompt: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExecutionPlan,
            system_instruction=PLANNER_SYSTEM_PROMPT,
            temperature=0
        )
    )

    return response.parsed