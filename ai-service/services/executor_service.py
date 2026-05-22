from models.schemas import ExecutionPlan, ExecutionResult, TaskResult, IntentType
from tools.hospital_tools import *
from tools.appointment_tools import *
from services.reasoning_service import *
from services.response_service import handle_general_chat

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

                analysis = analyze_symptoms(session_id=session_id, symptoms=task.symptoms)
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

                recommendation = recommend_departments(session_id=session_id, symptoms=task.symptoms)
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data=recommendation
                    )
                )

            # HOSPITAL SEARCH
            elif task.intent == IntentType.HOSPITAL_SEARCH:
                if not task.hospital_queries :
                    results.append(
                        TaskResult(
                            intent=task.intent,
                            success=False,
                            requires_clarification=True,
                            clarification_question=(
                                "Which hospital, city, or location would you like to search?"
                            )
                        )
                    )
  
                    continue 

                hospitals = search_hospitals(task.hospital_queries)
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data={
                            "hospitals": hospitals
                        }
                    )
                )

            # DEPARTMENT SEARCH
            elif task.intent == IntentType.DEPARTMENT_SEARCH:
                if not task.hospital_queries:
                    results.append(
                        TaskResult(
                            intent=task.intent,
                            success=False,
                            requires_clarification=True,
                            clarification_question=(
                                "Which hospital or city would you like to search in?"
                            )
                        )
                    )
                    continue

                matches = fetch_available_departments(task.hospital_queries)
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data={
                            "matches": matches
                        }
                    )
                )
                
            # SESSION SEARCH
            elif task.intent == IntentType.SESSION_SEARCH:
                if not task.departments:
                    results.append(
                        TaskResult(
                            intent=task.intent,
                            success=False,
                            requires_clarification=True,
                            clarification_question=(
                                "Which department or specialist are you looking for?"
                            )
                        )
                    )

                    continue

                if not task.hospital_queries:
                    results.append(
                        TaskResult(
                            intent=task.intent,
                            success=False,
                            requires_clarification=True,
                            clarification_question=(
                                "Which hospital or city would you like to search in?"
                            )
                        )
                    )
                    continue

                sessions = search_sessions(hospital_queries=task.hospital_queries, departments=task.departments)

                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data={
                            "sessions": sessions
                        }
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
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        message=(
                            "FAQ retrieval pipeline not implemented yet."
                        )
                    )
                )

            # APPOINTMENT GUIDANCE
            elif task.intent == IntentType.APPOINTMENT_GUIDANCE:
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        message=(
                            "Appointment guidance not implemented yet."
                        )
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
