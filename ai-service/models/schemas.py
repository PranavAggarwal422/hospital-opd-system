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
    # General conversation or unrecognized healthcare intent
    GENERAL_CHAT = "general_chat"

    # User describes symptoms, pain, illness, or medical problems
    SYMPTOM_ANALYSIS = "symptom_analysis"

    # User wants to search hospitals using hospital names, cities, states, or locations
    HOSPITAL_SEARCH = "hospital_search"

    # User wants specialist or department recommendations based on symptoms/problems
    DEPARTMENT_RECOMMENDATION = "department_recommendation"

    # User wants to search/retrieve departments from hospitals
    DEPARTMENT_SEARCH = "department_search"

    # User wants doctor availability, OPD sessions, timings, schedules, or appointment slots
    SESSION_SEARCH = "session_search"

    # User wants help booking, cancelling, rescheduling, or managing appointments
    APPOINTMENT_GUIDANCE = "appointment_guidance"

    # User asks about reports, medical tests, MRI, X-ray, prescriptions, or report access
    REPORT_GUIDANCE = "report_guidance"

    # Hospital workflows, policies, token systems, required documents, timings, FAQs
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


class ClarificationResult(BaseModel):
    question: str

class TaskResult(BaseModel):
    intent: IntentType
    success: bool
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    data: Optional[dict] = None
    message: Optional[str] = None

class ExecutionResult(BaseModel):
    results: List[TaskResult]

