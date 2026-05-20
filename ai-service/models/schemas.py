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
    # General conversation or unrecognized intent
    GENERAL_CHAT = "general_chat"

    # user describes symptoms, pain, illness, or medical problems
    SYMPTOM_ANALYSIS = "symptom_analysis"

    # user wants to search hospitals using hospital names, cities, states, or locations
    HOSPITAL_SEARCH = "hospital_search"

    # user wants department recommendations or specialist guidance.
    DEPARTMENT_SEARCH = "department_search"

    # user wants doctor availability, OPD sessions, timings, schedules, or appointment slots.
    SESSION_SEARCH = "session_search"

    # user wants help booking, cancelling, rescheduling, or managing appointments.
    APPOINTMENT_GUIDANCE = "appointment_guidance"

    # user asks about reports, medical tests, MRI, X-ray, prescriptions, or report access
    REPORT_GUIDANCE = "report_guidance"

    # Used for hospital workflows, policies, token systems, required documents, timings, or general hospital FAQs.
    FAQ_QUERY = "faq_query"

class Task(BaseModel):
    # Type of task to execute
    intent: IntentType

    # Flexible hospital-related search context.
    # Can contain hospital name, city, state, or general location query.
    hospital_query: Optional[str] = None

    # List of departments extracted from the query.
    # Used for department recommendations and session lookup.
    departments: Optional[List[str]] = None

    # List of symptoms or medical issues mentioned by the user.
    symptoms: Optional[List[str]] = None

    # List of doctor names if explicitly mentioned.
    doctor_names: Optional[List[str]] = None

class ExecutionPlan(BaseModel):
    tasks: List[Task]
