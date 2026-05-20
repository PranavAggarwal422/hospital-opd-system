from models.schemas import ExecutionPlan, ExecutionResult, TaskResult, IntentType
from tools.hospital_tools import search_hospitals, search_departments


def execute_plan(plan: ExecutionPlan):
    results = []
    for task in plan.tasks:
        try:
            # HOSPITAL SEARCH
            if task.intent == IntentType.HOSPITAL_SEARCH:
                if not task.hospital_query :  
                    continue 

                hospitals = search_hospitals(hospital_query=task.hospital_query)
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
                if not task.departments : 
                    continue 

                # MISSING CONTEXT
                if not task.hospital_query:
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

                department_matches = search_departments(
                    hospital_query=task.hospital_query,
                    departments=task.departments
                )

                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        data={
                            "matches": department_matches
                        }
                    )
                )

            # PLACEHOLDER TASKS
            else:
                results.append(
                    TaskResult(
                        intent=task.intent,
                        success=True,
                        message="Execution not implemented yet"
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

