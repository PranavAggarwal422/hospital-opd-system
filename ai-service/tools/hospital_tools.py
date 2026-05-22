from core.path_setup import *
from app.services.patient.hospital_service import get_active_hospitals, get_departments_by_hospital

def search_hospitals(hospital_queries: list[str]):
    all_hospitals = []
    seen_hospital_ids = set()

    for hospital_query in hospital_queries:
        hospitals = get_active_hospitals(search=hospital_query)

        for hospital in hospitals:
            hospital_id = hospital["hospital_id"]

            if hospital_id not in seen_hospital_ids:
                seen_hospital_ids.add(hospital_id)
                all_hospitals.append(hospital)

    return all_hospitals



def fetch_available_departments(hospital_queries: list[str]):
    hospitals = search_hospitals(hospital_queries=hospital_queries)
    matches = []

    for hospital in hospitals:
        departments = get_departments_by_hospital(hospital_id=hospital["hospital_id"])
        matches.append({
            "hospital": {
                "hospital_id": hospital["hospital_id"],
                "hospital_name": hospital["hospital_name"],
                "city": hospital["city"],
                "state": hospital["state"]
            },

            "departments": departments
        })

    return matches
