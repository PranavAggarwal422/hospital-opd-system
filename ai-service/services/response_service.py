from services.llm_service import get_response_chat
from models.schemas import ExecutionResult

def handle_general_chat(session_id: str, user_query: str):
    # Handles casual/general healthcare conversation.
    chat = get_response_chat(session_id)
    response = chat.send_message(user_query)

    return {
        "response": response.text
    }


def synthesize_response(session_id: str, user_query: str, execution_result: ExecutionResult):
    """
    Generates the final conversational response
    using structured execution results.
    """

    chat = get_response_chat(session_id)

    prompt = f"""
    User Query:
    {user_query}

    Structured Execution Result:
    {execution_result.model_dump_json(indent=2)}

    Generate the final patient-facing response using the execution results above.
    """
    
    response = chat.send_message(prompt)
    return response.text
