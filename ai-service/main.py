from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ChatRequest, ChatResponse, SessionResponse, IntentType
from services.llm_service import create_chat_session, delete_chat_session
from services.planner_service import generate_execution_plan
from services.executor_service import execute_plan
from services.llm_service import get_planner_chat
from services.response_service import synthesize_response

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
    # STEP 1: Generate execution plan
    plan = generate_execution_plan(session_id=request.session_id, prompt=request.prompt)
    if not plan.tasks:
        return ChatResponse(response="I'm sorry, I could not understand your request clearly. Could you please rephrase it?")

    print("\n========== EXECUTION PLAN ==========")
    print(plan)
    print("====================================\n")

    # STEP 2: Execute plan
    execution_result = execute_plan(session_id=request.session_id, user_query=request.prompt,plan=plan)

    # STEP 3: Inject execution context into planner memory
    try:
        planner_chat = get_planner_chat(request.session_id)

        for task_result in execution_result.results:
            if task_result.requires_clarification:
                planner_chat.send_message(
                    f"""
                    Conversation update:

                    User request:
                    {request.prompt}

                    System clarification required:
                    {task_result.clarification_question}

                    The conversation is waiting for the user's clarification.
                    """
                )

                print(f"System clarification required:\n{task_result.clarification_question}")

            elif task_result.success:
                planner_chat.send_message(
                    f"""
                    Conversation update:

                    User request:
                    {request.prompt}

                    Execution Result:
                    {task_result.data if task_result.data else task_result.message}

                    This context is part of the ongoing conversation.
                    Reuse it intelligently in future planning.
                    """
                )
                print(f"Execution result injected for {task_result.intent}:\n{task_result.data if task_result.data else task_result.message}")

    except Exception as e:
        print("Planner memory injection failed:")
        print(e)
    
    # Direct return optimization for pure general chat
    if (len(execution_result.results) == 1 and execution_result.results[0].intent == IntentType.GENERAL_CHAT and execution_result.results[0].success):
        print(f"Direct return for general chat:\n{execution_result.results[0].data['response']}")
        return ChatResponse(response=execution_result.results[0].data["response"])
    
    # STEP 4: Final response synthesis
    final_response = synthesize_response(session_id=request.session_id, user_query=request.prompt,execution_result=execution_result)

    return ChatResponse(response=final_response)


@app.delete("/end-chat/{session_id}")
def end_chat(session_id: str):
    delete_chat_session(session_id)
    return {
        "message": "Chat Session Deleted"
    }

