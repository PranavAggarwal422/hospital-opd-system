from core.path_setup import *

from app.services.patient.hospital_service import get_departments_by_hospital
from app.services.patient.appointment_service import get_sessions_by_department
from tools.hospital_tools import search_hospitals


def search_sessions(hospital_queries: list[str], departments: list[str], search: str | None = None):
    hospitals = search_hospitals(hospital_queries=hospital_queries)
    matches = []

    for hospital in hospitals:
        for department in departments:
            matched_departments = get_departments_by_hospital(hospital_id=hospital["hospital_id"], search=department)

            for dept in matched_departments:
                sessions = get_sessions_by_department(department_id=dept["department_id"], search=search)

                if sessions:
                    matches.append({
                        "hospital": {
                            "hospital_id": hospital["hospital_id"],
                            "hospital_name": hospital["hospital_name"],
                            "city": hospital["city"],
                            "state": hospital["state"]
                        },

                        "department": {
                            "department_id": dept["department_id"],
                            "department_name": dept["department_name"]
                        },

                        "sessions": sessions
                    })

    return matches

