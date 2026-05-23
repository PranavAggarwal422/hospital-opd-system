from models.schemas import ExecutionPlan, ExecutionResult, TaskResult, IntentType
from services.reasoning_service import *
from services.response_service import handle_general_chat
from vectorstore.retriever import retrieve_context

def execute_plan(session_id: str, user_query: str, plan: ExecutionPlan):
    results = []
    for task in plan.tasks:
        try:
            # GENERAL CHAT
            if task.intent == IntentType.GENERAL_CHAT:
                response = handle_general_chat(session_id=session_id, user_query=user_query)
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data=response
                    )
                )
            
            # SYMPTOM ANALYSIS
            elif task.intent == IntentType.SYMPTOM_ANALYSIS:
                if not task.symptoms:
                    results.append(
                        TaskResult(
                            intent=task.intent,
                            success=False,
                            requires_clarification=True,
                            clarification_question=(
                                "Please describe your symptoms."
                            )
                        )
                    )
                    continue

                analysis = analyze_symptoms(task.symptoms)
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data=analysis
                    )
                )
            
            # DEPARTMENT RECOMMENDATION
            elif task.intent == IntentType.DEPARTMENT_RECOMMENDATION:
                if not task.symptoms:
                    results.append(
                        TaskResult(
                            intent=task.intent,
                            success=False,
                            requires_clarification=True,
                            clarification_question=(
                                "Please describe your symptoms."
                            )
                        )
                    )
                    continue

                recommendation = recommend_departments(symptoms=task.symptoms)
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data=recommendation
                    )
                )

            # REPORT GUIDANCE
            elif task.intent == IntentType.REPORT_GUIDANCE:
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        message=(
                            "Report guidance pipeline not implemented yet."
                        )
                    )
                )

            # FAQ QUERY
            elif task.intent == IntentType.FAQ_QUERY:
                retrieved_context = retrieve_context(user_query)
                if not retrieved_context:
                    retrieved_context = "No relevant information in the knowledge base"
            
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data={
                            "retrieved_context": retrieved_context
                        }
                    )
                )

        except Exception as e:
            results.append(
                TaskResult(
                    intent=task.intent,
                    success=False,
                    message=str(e)
                )
            )

    return ExecutionResult(results=results)
