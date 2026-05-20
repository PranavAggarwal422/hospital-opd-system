from core.path_setup import *
from app.services.patient.hospital_service import get_active_hospitals, get_departments_by_hospital

def search_hospitals(hospital_query: str):
    hospitals = get_active_hospitals(search=hospital_query)
    return hospitals


def search_departments(hospital_query: str, departments: list[str]):
    hospitals = get_active_hospitals(search=hospital_query)

    matches = []

    for hospital in hospitals:
        for department in departments:
            matched_departments = get_departments_by_hospital(
                hospital_id=hospital["hospital_id"],
                search=department
            )

            if matched_departments:
                matches.append({
                    "hospital": {
                        "hospital_id": hospital["hospital_id"],
                        "hospital_name": hospital["hospital_name"],
                        "city": hospital["city"],
                        "state": hospital["state"]
                    },

                    "departments": matched_departments
                })

    return matches
