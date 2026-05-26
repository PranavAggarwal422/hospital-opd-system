from pydantic import BaseModel, Field
from enum import Enum
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

    # User want help understanding reports/medical documents
    REPORT_EXPLANATION = "report_explanation"

    # User asks about hospital workflows, appointment guidance, portal navigation, policies etc.
    FAQ_QUERY = "faq_query"

class Task(BaseModel):
    # Type of task to execute
    intent: IntentType

    # List of symptoms or medical issues mentioned by the user.
    symptoms: Optional[List[str]] = None

class ExecutionPlan(BaseModel):
    tasks: List[Task]

class TaskResult(BaseModel):
    intent: IntentType
    success: bool
    requires_clarification: bool = False
    clarification_question: Optional[str] = None
    data: Optional[dict] = None
    message: Optional[str] = None

class ExecutionResult(BaseModel):
    results: List[TaskResult]

class SymptomAnalysisResponse(BaseModel):
    analysis: str
    suggested_departments: Optional[list[str]] = None

