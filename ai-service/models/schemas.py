from pydantic import BaseModel, Field
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    session_id: str
    prompt: str = Field(min_length=1, max_length=1000)

class ChatResponse(BaseModel):
    response: str

class SessionResponse(BaseModel):
    session_id: str

class IntentType(str, Enum):
    GENERAL_CHAT = "general_chat"
    SYMPTOM_ANALYSIS = "symptom_analysis"
    HOSPITAL_SEARCH = "hospital_search"
    DEPARTMENT_SEARCH = "department_search"
    SESSION_SEARCH = "session_search"
    APPOINTMENT_GUIDANCE = "appointment_guidance"
    REPORT_GUIDANCE = "report_guidance"
    FAQ_QUERY = "faq_query"


class Task(BaseModel):
    intent: IntentType
    hospital: Optional[str] = None
    department: Optional[str] = None
    symptoms: Optional[str] = None
    doctor_name: Optional[str] = None


class ExecutionPlan(BaseModel):
    tasks: List[Task]
